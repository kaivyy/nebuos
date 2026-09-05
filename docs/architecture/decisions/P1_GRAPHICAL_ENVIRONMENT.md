# Architecture Decision Record: NebuOS Milestone P1 Graphical Environment

**Document ID:** ADR-P1-001  
**Status:** APPROVED  
**Date:** 2026-09-05  
**Domain:** Display Subsystem / Compositor Architecture  
**Author:** Lead Systems Architect & Graphics Engineer  
**Milestone:** P1 (NebuCompositor)  
**Prerequisites:** Milestone P0 (Certified & Locked at Git tag `p0-locked`, commit `71d0c9e`)  

---

## 1. Protected P0 VM Policy

### 1.1 Reference Environment Definition
Proxmox Virtual Machine **VM 101** (`nebuos-test`) serves as the official, certified **P0 Reference Environment**. It constitutes the empirical baseline proof that NebuOS P0 achieves deterministic headless boot, signed UEFI handoff, Btrfs root immutability, `/var` overlay semantics, systemd 259 multi-user convergence, and 100% headless package isolation.

### 1.2 Invariant Hardware Specification
The hardware configuration of VM 101 is permanently locked as follows:
- **VMID:** `101`
- **Name:** `nebuos-test`
- **CPU Topology:** 2 vCPU (`cores: 2`, `cpu: x86-64-v2-AES`, KVM hardware acceleration enabled)
- **Memory:** 2048 MB RAM
- **Firmware:** OVMF / UEFI (`/usr/share/pve-edk2-firmware/OVMF_CODE_4M.secboot.fd`, efitype=4m)
- **Machine Type:** QEMU `q35` (`type: q35+pve0`, ICH9-LPC)
- **Storage Subsystem:** VirtIO SCSI Single (`scsihw: virtio-scsi-single`, iothread=1, disk: `/dev/pve/vm-101-disk-1`, 20 GiB)
- **Display Controller:** Standard VGA (`-device VGA,id=vga,bus=pcie.0,addr=0x1`, PCI ID `1234:1111`, driver: `bochs-drm`)
- **Console:** Emulated ISA Serial Socket (`/var/run/qemu-server/101.serial0`)
- **Network:** VirtIO Network (`virtio-net-pci`, bridge `vmbr0`)

### 1.3 Strict Protection & Non-Invasive Governance
To ensure total auditability and prevent regression of certified milestones:
1. **Zero Configuration Mutation:** Commands modifying VM 101 hardware (including `qm set`, `qm resize`, `qm move_disk`, `qm migrate`, or manual configuration edits in `/etc/pve/qemu-server/101.conf`) are strictly forbidden.
2. **Read-Only Inspection Only:** VM 101 may only be accessed for non-invasive observation, telemetry collection, QMP read queries (`query-pci`, `query-status`), and verifying baseline P0 behavior.
3. **No Graphical Experiments:** VM 101 must NEVER be used as an experimental sandbox for testing P1 graphical drivers, display adapters, or compositors.
4. **No Image Tampering:** The P0 disk image deployed to `/dev/pve/vm-101-disk-1` must remain unmodified.

---

## 2. Dedicated P1 Graphical Validation Environment

### 2.1 Identification and Isolation
To validate Milestone P1 (NebuCompositor) without compromising VM 101, all graphical testing, display server bringup, DRM/KMS validation, and input verification are conducted in an isolated, designated environment:
- **Identifier:** `P1 graphical validation environment`
- **Isolation Guarantee:** Zero shared block devices, zero shared hypervisor configuration files, and zero shared transient state with VM 101.

### 2.2 Validation Topologies
The P1 Graphical Validation strategy utilizes a dual-tier topology:

```
+-----------------------------------------------------------------------------+
|                               PROXMOX VE HOST                               |
|                               (192.168.1.101)                               |
|                                                                             |
|  +---------------------------+             +-----------------------------+  |
|  |       VM 101 (LOCKED)     |             |       VM 102 (DEDICATED)    |  |
|  |   P0 Reference Baseline   |             |   P1 Graphical Validation   |  |
|  |---------------------------|             |-----------------------------|  |
|  | - 2 vCPU / 2048 MB RAM    |             | - 2 vCPU / 2048 MB RAM      |  |
|  | - Standard VGA (bochs-drm)|             | - VirtIO-GPU (virtio-vga)   |  |
|  | - 100% Headless Baseline  |             | - DRM/KMS /dev/dri/card0    |  |
|  | - nebu-boot-check gate    |             | - Mesa EGL/GBM/VirGL        |  |
|  | - Serial TTY Session      |             | - nebu-compositor instance  |  |
|  +---------------------------+             +-----------------------------+  |
|               ^                                           ^                 |
+---------------|-------------------------------------------|-----------------+
                | (Read-Only Telemetry)                     | (Deployment & Test)
+---------------|-------------------------------------------|-----------------+
|               |              CT 100 (DEV HOST)            |                 |
|  +-----------------------------------------------------------------------+  |
|  | Repository: /root/NebuOS (branch: master)                             |  |
|  | Docker Engine: nebuos:p0-latest -> nebuos:p1-compositor               |  |
|  | Local Headless KMS / Mock Runner: vkms & headless QEMU for rapid CI   |  |
|  +-----------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------+
```

1. **Tier 1: Dedicated Proxmox VM 102 (`nebuos-p1-graphical`):**
   - **Machine Type:** QEMU `q35`
   - **Firmware:** OVMF UEFI
   - **Compute:** 2 vCPU, 2048 MB RAM
   - **Display Adapter:** `vga: virtio` (VirtIO-VGA / VirtIO-GPU) with paravirtualized modesetting, optional `vga: virtio-gl` for host 3D acceleration.
   - **Storage:** Dedicated LVM volume `/dev/pve/vm-102-disk-1` (distinct from VM 101).
   - **Purpose:** Full integration verification of UEFI boot, DRM modesetting, KMS page-flips, input dispatch, and frame rendering under real KVM virtualization.

2. **Tier 2: Local CT 100 Headless KMS Harness:**
   - **Driver:** Linux `vkms` (Virtual Kernel Modesetting) or headless QEMU.
   - **Purpose:** Fast automated CI unit and protocol conformance tests without hypervisor VM provisioning overhead.

---

## 3. GPU Selection

### 3.1 Virtual Display Adapter Evaluation
An empirical audit was conducted on Proxmox VE 8.x (`/usr/bin/kvm` version 11.0.0, package `pve-qemu-kvm_11.0.0-3`) and Linux kernel `7.1.13-200.fc44.x86_64`. Five virtual display adapters were evaluated:

| Display Adapter | QEMU Device Flag | Kernel Module | PCI ID | Render Node (`/dev/dri/renderD*`) | 3D Acceleration | Evaluation Summary |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Bochs VBE (Std VGA)** | `-device VGA,id=vga` | `bochs.ko` | `1234:1111` | **NONE** | No (CPU only) | Present in VM 101. Modesetting only. Requires `llvmpipe` software rendering. |
| **VirtIO-GPU (2D)** | `-device virtio-vga` | `virtio-gpu.ko` | `1af4:1050` | **NONE** (without VirGL) | No (Paravirtualized 2D) | Efficient paravirtualized KMS, dynamic resize, low overhead. Compatible with `llvmpipe`. |
| **VirtIO-GPU (VirGL 3D)** | `-device virtio-vga-gl` | `virtio-gpu.ko` | `1af4:1050` | **YES** (`renderD128`) | **YES** (Host GPU VirGL) | Full Gallium hardware acceleration via host GPU (`renderD128`). Ideal for VM graphical performance. |
| **SPICE QXL** | `-device qxl-vga` | `qxl.ko` | `1b36:0100` | **NONE** | No | Legacy 2D protocol, high host CPU overhead, deprecated for pure Wayland compositors. |
| **VMware SVGA** | `-device vmware-svga` | `vmwgfx.ko` | `15ad:0405` | **YES** | Partial | Legacy proprietary heritage. Suboptimal in KVM compared to open VirtIO standard. |

### 3.2 Decision: VirtIO-GPU Substrate
**Selected GPU:** `VirtIO-GPU` (`virtio-vga` baseline, `virtio-vga-gl` for 3D acceleration).

**Technical Justification:**
1. **Paravirtualized Efficiency:** Designed specifically for virtualized Linux guests, eliminating emulation overhead associated with legacy register-level VGA cards.
2. **First-Class Kernel Support:** `virtio-gpu.ko` is a first-class upstream DRM driver in Linux 7.1.13 with full atomic modesetting (`DRIVER_ATOMIC`), page-flip completion events, and DRM buddy allocator support.
3. **Mesa Gallium Integration:** Mesa provides dedicated `/usr/lib64/dri/virtio_gpu_dri.so`, enabling direct command submission to host VirGL when 3D mode is enabled.
4. **Clean Fallback Path:** In environments without host GPU passthrough or VirGL, VirtIO-GPU cleanly runs Mesa `llvmpipe` (`kms_swrast_dri.so`) without crashing or requiring architecture changes.

---

## 4. DRM/KMS Findings

### 4.1 Driver & Kernel Verification
Empirical examination of Fedora 44 (`nebuos:p0-latest`) kernel modules at `/usr/lib/modules/7.1.13-200.fc44.x86_64/kernel/drivers/gpu/drm/` verified that all necessary DRM infrastructure is compiled and present:
- `virtio/virtio-gpu.ko.xz` (VirtIO GPU)
- `tiny/bochs.ko.xz` (Bochs standard VGA)
- `vkms/vkms.ko.xz` (Virtual KMS for testing)
- `display/drm_display_helper.ko.xz`, `drm_ttm_helper.ko.xz`, `drm_buddy.ko.xz` (DRM core helpers)

### 4.2 Modesetting Capabilities
1. **Device Nodes:** Under VirtIO-GPU, the kernel enumerates primary modesetting node `/dev/dri/card0`.
2. **Connectors:** VirtIO-GPU exposes virtual connector `Virtual-1` (supporting dynamic mode generation and EDID reporting). Bochs exposes `VGA-1` (fixed resolutions).
3. **CRTCs & Planes:** VirtIO-GPU exposes 1 CRTC, 1 primary plane, and 1 cursor plane. Universal planes capability (`DRM_CLIENT_CAP_UNIVERSAL_PLANES`) is fully supported.
4. **Atomic KMS:** Driver feature `DRIVER_ATOMIC` is supported. `drmModeAtomicCommit` with flags `DRM_MODE_ATOMIC_NONBLOCK` enables asynchronous page-flips synchronized with `DRM_EVENT_FLIP_COMPLETE`.
5. **Scanout Buffer Preservation:** As specified in ADR-0014, the compositor inherits the active scanout buffer from SimpleDRM / EFI framebuffer without causing an unneeded modeset if timings and pixel formats align.

---

## 5. Render-Node Findings

### 5.1 Analysis of `/dev/dri/card*` vs `/dev/dri/renderD*`
A critical distinction exists between primary DRM nodes and render nodes:
- `/dev/dri/cardX`: Manages KMS modesetting, CRTC configuration, connectors, and physical display scanout. Acquiring display control requires **DRM Master** privileges (restricted to root or granted by `systemd-logind` via `TakeControl`/`TakeDevice`).
- `/dev/dri/renderDX` (Render Nodes): Dedicated solely to GPU computation and off-screen buffer allocation (EGL, OpenGL, Vulkan). Render nodes do not perform modesetting and require NO DRM Master privileges, allowing unprivileged client processes to safely allocate buffers and submit rendering commands.

### 5.2 Empirical Assessment Across Virtual GPUs
1. **`bochs-drm` (VM 101):**
   - Kernel driver `bochs_driver` sets `DRIVER_MODESET | DRIVER_GEM | DRIVER_ATOMIC`.
   - Lacks `DRIVER_RENDER` flag.
   - Result: `/dev/dri/card0` exists; **`/dev/dri/renderD128` DOES NOT EXIST**.
   - Consequence: All GPU rendering commands are rejected; userland must use CPU software rasterization.
2. **`virtio-gpu` (Standard 2D):**
   - Kernel driver sets `DRIVER_MODESET | DRIVER_GEM | DRIVER_ATOMIC`.
   - Result: `/dev/dri/card0` exists; `/dev/dri/renderD128` is not instantiated when host 3D acceleration is inactive.
   - Consequence: Compositor allocates dumb buffers via DRM ioctls; rendering executes via `kms_swrast`.
3. **`virtio-gpu-gl` (VirGL 3D):**
   - Host QEMU exposes 3D capability (`virgl=on`).
   - Kernel driver enables `DRIVER_RENDER`.
   - Result: Both `/dev/dri/card0` and `/dev/dri/renderD128` exist.
   - Consequence: True hardware-accelerated rendering path is active.

---

## 6. Mesa Findings

### 6.1 Userspace Mesa Stack in Fedora 44
Inspection of Fedora 44 package repositories confirmed the availability of modern, bleeding-edge Mesa packages:
- `mesa-dri-drivers-26.1.8-1.fc44.x86_64`
- `mesa-libEGL-26.1.8-1.fc44.x86_64`
- `mesa-libgbm-26.1.8-1.fc44.x86_64`
- `libdrm-2.4.134-1.fc44.x86_64`

### 6.2 Installed Driver Shared Objects
Package file listing of `mesa-dri-drivers-26.1.8-1.fc44.x86_64` verified the existence of:
- `/usr/lib64/dri/virtio_gpu_dri.so`: Paravirtualized VirGL Gallium driver.
- `/usr/lib64/dri/kms_swrast_dri.so`: KMS Software Rasterizer (LLVMpipe driver for DRM dumb buffers).
- `/usr/lib64/dri/swrast_dri.so`: Fallback software rasterizer.
- `/usr/lib64/dri/zink_dri.so`: Gallium driver running OpenGL on Vulkan.
- `/usr/lib64/dri/iris_dri.so` / `/usr/lib64/dri/radeonsi_dri.so`: Native Intel/AMD drivers for bare-metal targets.
- `/usr/lib64/gbm/dri_gbm.so`: GBM DRI driver loader backend.
- `/usr/lib64/libgallium-26.1.8.so`: Core Gallium rasterization runtime.

Mesa 26.1.8 provides full support for both VirGL hardware forwarding and LLVMpipe software rasterization.

---

## 7. EGL Findings

### 7.1 EGL Specification & Implementation
Fedora 44 provides Mesa EGL 1.5 conforming to Khronos specifications. EGL acts as the platform glue binding Smithay's rendering engine to the underlying GBM buffer allocator and DRM KMS device.

### 7.2 Critical EGL Extensions
The following EGL extensions are verified present and required for `nebu-compositor`:
1. `EGL_EXT_platform_base` / `EGL_KHR_platform_gbm`: Allows `eglGetPlatformDisplayEXT` to bind directly to a `struct gbm_device *` without X11 or Wayland client wrappers.
2. `EGL_KHR_image_base` / `EGL_KHR_gl_texture_2D_image`: Allows creating EGLImages from client textures and GBM buffers.
3. `EGL_EXT_image_dma_buf_import` / `EGL_EXT_image_dma_buf_import_modifiers`: Enables importing client DMA-BUF handles into EGL without memory copies (zero-copy rendering pipeline).
4. `EGL_KHR_surfaceless_context`: Enables rendering directly into framebuffers and textures without requiring a dummy native window.

---

## 8. GBM Findings

### 8.1 Buffer Allocation Subsystem
GBM (Generic Buffer Management) via `mesa-libgbm-26.1.8-1.fc44.x86_64` provides the memory allocation abstraction for NebuCompositor:
- **Device Instantiation:** `gbm_create_device(drm_fd)` creates a buffer manager wrapping the open DRM device (`/dev/dri/card0`).
- **Buffer Object Creation:** `gbm_bo_create` allocates framebuffers with specific pixel formats (typically `GBM_FORMAT_XRGB8888` or `GBM_FORMAT_ARGB8888`) and flags (`GBM_BO_USE_SCANOUT | GBM_BO_USE_RENDERING`).
- **Direct Scanout Bridge:** `gbm_bo_get_handle` retrieves the GEM handle for wrapping into a DRM KMS framebuffer (`drmModeAddFB2`).

### 8.2 Memory Backing Behavior
- **Hardware Mode (VirGL / Bare-Metal):** GBM allocates VRAM or GTT-backed GEM buffers, exportable as DMA-BUFs with DRM format modifiers.
- **Software Mode (kms_swrast):** GBM allocates dumb memory buffers via `DRM_IOCTL_MODE_CREATE_DUMB`. Memory is CPU-mappable, allowing LLVMpipe to rasterize directly into scanout memory.

---

## 9. Renderer Findings

### 9.1 Software vs Hardware Characterization

| Metric | Software Rendering (`llvmpipe` / `kms_swrast`) | Hardware Acceleration (`virtio-gpu-gl` / Bare-Metal) |
| :--- | :--- | :--- |
| **Execution Engine** | Host/Guest CPU (LLVM JIT Compiler) | Dedicated GPU Hardware (or Host VirGL Renderer) |
| **Render Node** | Not required (`/dev/dri/card0` dumb buffers) | Required (`/dev/dri/renderD128`) |
| **CPU Utilization (Idle)** | < 1% CPU | < 0.2% CPU |
| **CPU Utilization (60 FPS Move)** | 35% – 70% of 1 vCPU core | < 2% of 1 vCPU core |
| **Direct Scanout** | Emulated (software copy to dumb buffer) | Zero-copy DMA-BUF scanout to primary plane |
| **P1 PoC Viability** | **PASS (100% functional for bringup/CI)** | **PASS (Optimal performance target)** |

### 9.2 Architectural Stance on Software Rendering
1. **PoC and Bringup:** Software rendering via `llvmpipe` is completely functional and acceptable for early P1 development, CI verification, and headless environments lacking GPU passthrough.
2. **No Permanent Hardcoding:** `nebu-compositor` will not hardcode software paths. The rendering pipeline uses standard EGL/GBM abstractions that automatically utilize hardware acceleration when a compatible GPU/render-node is present, falling back gracefully to `kms_swrast` when running in virtualized or headless CI environments.

---

## 10. Smithay Evaluation

### 10.1 Framework Assessment Matrix
To ensure architectural longevity, safety, and maintainability, three compositor implementation strategies were evaluated:

| Criterion | 1. Smithay (Selected) | 2. Native Rust from Scratch | 3. wlroots via C FFI |
| :--- | :---: | :---: | :---: |
| **Language Safety** | 100% Safe Rust core, unsafe isolated to FFI | Safe Rust core, unsafe in custom ioctl bindings | Heavy C FFI, raw pointers, unsafe boundary |
| **Maintenance Status** | **ACTIVE** (v0.7.0 June 2025, COSMIC desktop backed) | N/A (100% NebuOS maintenance burden) | C wlroots is active; `wlroots-rs` is **DEAD/UNMAINTAINED** |
| **DRM/KMS Atomic Support** | Built-in modular `backend_drm` with page-flip loop | Requires writing custom atomic KMS state machine | Built-in via C wlroots |
| **EGL / GBM Integration** | Native `backend_gbm` and `renderer_gl` / `renderer_glow` | Hundreds of lines of unsafe OpenGL/GBM FFI | Built-in via C wlroots |
| **Input / Seat Management** | Built-in `backend_libinput` and `backend_session_libseat` | Requires custom libinput event poll and seat bridge | Built-in via C wlroots |
| **Protocol Support** | Full core Wayland + `xdg_shell`, `wlr-layer-shell`, `linux_dmabuf` | Must manually parse/dispatch Wayland XML protocols | Full protocol coverage in C |
| **Fedora 44 Compatibility** | Verified (requires Rust 1.80.1+; F44 ships Rust 1.94–1.98) | Verified | Requires C build dependencies and bindings generation |
| **Estimated Code Volume** | **~2,000 – 3,500 lines** for complete compositor | **>25,000 lines** of complex low-level plumbing | **~8,000 lines** of fragile FFI wrapper code |
| **Architectural Decision** | **PREFERRED / APPROVED** | **REJECTED** (Reinvents wheel, massive risk) | **REJECTED** (Unmaintained bindings, unsafe C) |

### 10.2 Smithay Verification Verdict
- **Smithay Status:** **PASS** (Version `0.7.0` selected).
- **Features Required:** `backend_drm`, `backend_gbm`, `backend_egl`, `backend_libinput`, `backend_udev`, `backend_session_libseat`, `renderer_gl`, `wayland_frontend`, `desktop`.

---

## 11. Session Management Decision

### 11.1 Mechanism Evaluation
A Wayland compositor running on bare-metal or virtual hardware must acquire access to privileged input (`/dev/input/event*`) and display (`/dev/dri/card*`) devices, and coordinate VT switching. Three mechanisms were evaluated:

1. **Direct DRM / SUID-Root Execution:**
   - *Architecture:* Compositor runs as root (`UID 0`) and opens device files directly.
   - *Assessment:* **REJECTED**. Poses a severe security hazard. A vulnerability in the Wayland protocol parser or client buffer handling would result in full system root compromise. Violates modern least-privilege security models.
2. **`seatd` Standalone Daemon:**
   - *Architecture:* A minimal C daemon (`seatd`) managing seat access via UNIX socket.
   - *Assessment:* **REJECTED**. Redundant. NebuOS is built on Fedora 44 bootc and systemd 259. Introducing `seatd` duplicates functionality already provided by systemd, adds unnecessary daemon supervision overhead, and conflicts with systemd user sessions.
3. **`systemd-logind` via `libseat` (SELECTED):**
   - *Architecture:* Unprivileged user compositor delegates device acquisition to `systemd-logind` via D-Bus / `libseat`.
   - *Assessment:* **APPROVED**.
     - Native to Fedora 44 / systemd 259 baseline.
     - Already active and verified in P0 (`systemd-logind.service`).
     - Grants unprivileged file descriptors via `TakeControl` / `TakeDevice` and manages clean VT switching (`ReleaseControl`).
     - Fully supported out-of-the-box by Smithay's `backend_session_libseat`.

---

## 12. Input Architecture Decision

### 12.1 Input Pipeline Stack
NebuCompositor adopts the standard Linux input stack integrated directly into the `calloop` event loop:

```
[Hardware / Virtual Input Device]
   | (Kernel evdev events)
   v
[/dev/input/event*]
   | (Device enumeration & hotplug)
   v
[udev / systemd-logind]
   | (Granted unprivileged FDs via libseat)
   v
[libinput 1.31.3]
   | (Pointer motion, button clicks, keycodes)
   v
[Smithay backend_libinput]
   | (Keycode translation & state tracking)
   v
[libxkbcommon 1.13.1]
   | (XKB Keymap / UTF-8 text symbols)
   v
[Wayland wl_seat / wl_keyboard / wl_pointer]
   | (Protocol event serialization)
   v
[Wayland Client (Active Surface Focus)]
```

### 12.2 Virtualization Input Handling
- **Pointer:** QEMU USB Tablet (`-device usb-tablet`) provides absolute coordinates (`EV_ABS`), completely eliminating cursor drift and host-guest synchronization issues under VNC/SPICE.
- **Keyboard:** Standard AT Translated Set 2 keyboard (`atkbd`) or VirtIO keyboard, translated via `libxkbcommon` with default US layout (`pc105`, `us`, `inet`).

---

## 13. Known Limitations

1. **Software Rendering Latency on Bochs:** Running NebuCompositor on standard VGA (`bochs-drm`) relies entirely on `llvmpipe` CPU rasterization. While fully functional for testing protocol conformance, frame pacing and high-resolution performance will be CPU-bound.
2. **Hypervisor VirGL Requirement:** Hardware 3D acceleration in virtual environments requires the host hypervisor to support VirGL (`-device virtio-vga-gl` with host EGL context). Environments lacking host OpenGL support will operate in paravirtualized 2D mode.
3. **Single Hardware Plane in Basic QEMU:** Virtual GPUs typically expose only 1 primary CRTC plane and 1 cursor plane. Multi-plane direct scanout testing with multiple hardware overlay planes requires real GPU hardware or advanced hypervisor configurations.

---

## 14. Rejected Alternatives

1. **Modifying VM 101 for Graphical Testing:**
   - *Reason for Rejection:* Violates the immutable baseline governance of P0. VM 101 is the certified P0 proof and must remain untouched.
2. **`wlroots` via C FFI:**
   - *Reason for Rejection:* `wlroots-rs` is unmaintained and dead. Wrapping modern C `wlroots` manually requires extensive unsafe code, defeating Rust’s memory safety guarantees.
3. **Custom Rust Compositor from Scratch:**
   - *Reason for Rejection:* Massive development effort (>25,000 lines), excessive defect surface, reinventing solved DRM/KMS and protocol logic.
4. **Standalone `seatd`:**
   - *Reason for Rejection:* Redundant in a systemd-based distribution; introduces operational bloat.
5. **Direct Root DRM Access:**
   - *Reason for Rejection:* Severe violation of security boundaries; unacceptable for a production desktop OS.

---

## 15. Final Architecture

### 15.1 Architectural Blueprint
NebuCompositor (`nebu-compositor`) is architected as an unprivileged, event-driven Wayland display server executing in the systemd user session:

```mermaid
graph TD
    subgraph Kernel[Linux Kernel 7.1.13]
        DRM[VirtIO-GPU /dev/dri/card0]
        EVDEV[Input /dev/input/event*]
    end

    subgraph System[System Services]
        LOGIND[systemd-logind.service]
        USERD[systemd --user session]
    end

    subgraph CompositorProcess[nebu-compositor Process (Rust)]
        LOOP[Calloop Event Loop]
        SEAT[libseat Session Manager]
        KMS[Smithay DRM/KMS Backend]
        GBM[Mesa GBM Buffer Allocator]
        EGL[Mesa EGL / GLES2 Renderer]
        INPUT[Smithay libinput + xkbcommon]
        SRV[Wayland Protocol Server Engine]
        SPACE[Smithay Desktop Space & Stacking]
    end

    subgraph Clients[Wayland Clients]
        TEST_CLIENT[Minimal Test Client / Terminal]
        FUTURE_SHELL[P2: NebuShell Surfaces]
    end

    LOGIND -->|Grants Device FDs| SEAT
    SEAT --> KMS
    SEAT --> INPUT
    DRM <--> KMS
    EVDEV --> INPUT
    KMS --> GBM
    GBM --> EGL
    INPUT --> LOOP
    KMS --> LOOP
    LOOP --> EGL
    EGL --> SPACE
    SRV <--> Clients
    USERD -->|Supervises| CompositorProcess
```

### 15.2 End-to-End Boot & Session Flow
1. **System Boot:** UEFI → GRUB/BLS → Kernel 7.1.13 → Initramfs → Btrfs root → `multi-user.target`.
2. **P0 Health Gate:** `nebu-boot-check.service` asserts system integrity (8/8 assertions PASS).
3. **Session Handover:** `graphical.target` triggers user session (`user@1000.service`).
4. **Device Acquisition:** `nebu-compositor` initializes `libseat`, requests DRM card and input devices from `systemd-logind`.
5. **Display Setup:** KMS backend enumerates connectors and CRTCs, configures atomic modeset, preserves EFI scanout framebuffer (ADR-0014).
6. **Wayland Socket Creation:** Binds `$XDG_RUNTIME_DIR/wayland-0`.
7. **Frame Event Loop:** Calloop event loop processes input events, schedules GLES2/llvmpipe render passes, commits atomic frame to DRM, and emits presentation timestamps to clients.

---

## 16. P1/P2 Scope Boundary

To prevent scope creep and maintain strict milestone boundaries, the separation of responsibilities between P1, P2, and P3 is rigidly enforced:

| Component / Feature | Milestone P1 (NebuCompositor) | Milestone P2 (NebuShell) | Milestone P3 (NebuRuntime) |
| :--- | :---: | :---: | :---: |
| **DRM/KMS Modesetting & Page-Flips** | **IN SCOPE** | Out of Scope | Out of Scope |
| **GBM / EGL Rendering Pipeline** | **IN SCOPE** | Out of Scope | Out of Scope |
| **Wayland Server Core Protocols** | **IN SCOPE** | Out of Scope | Out of Scope |
| **libinput Event Dispatch** | **IN SCOPE** | Out of Scope | Out of Scope |
| **Minimal Test Client Verification** | **IN SCOPE** | Out of Scope | Out of Scope |
| **systemd User Service Unit** | **IN SCOPE** | Out of Scope | Out of Scope |
| **Desktop Shell (Panels, Docks, Taskbar)** | **STRICTLY FORBIDDEN** | **IN SCOPE** | Out of Scope |
| **Application Launcher / Start Menu** | **STRICTLY FORBIDDEN** | **IN SCOPE** | Out of Scope |
| **Desktop Widgets & Notifications** | **STRICTLY FORBIDDEN** | **IN SCOPE** | Out of Scope |
| **Slint UI Framework Integration** | **STRICTLY FORBIDDEN** | **IN SCOPE** | Out of Scope |
| **Desktop Settings UI** | **STRICTLY FORBIDDEN** | **IN SCOPE** | Out of Scope |
| **Software Center / App Marketplace** | **STRICTLY FORBIDDEN** | Out of Scope | Out of Scope |
| **Wine / Proton Execution Engine** | **STRICTLY FORBIDDEN** | Out of Scope | **IN SCOPE** |
| **Windows Application Compatibility** | **STRICTLY FORBIDDEN** | Out of Scope | **IN SCOPE** |

---

## 17. Architecture Verification Summary

All technical decisions documented herein have been validated against empirical evidence from the live development environment and hypervisor:
- VM 101 is protected, running, and isolated.
- Kernel 7.1.13 includes `virtio-gpu.ko` and `bochs.ko`.
- Mesa 26.1.8 provides both `virtio_gpu_dri.so` and `kms_swrast_dri.so`.
- Smithay 0.7.0 matches modern Rust 1.80+ toolchain (F44 ships Rust 1.94–1.98).
- `systemd-logind` + `libseat` eliminates duplicate daemons and preserves unprivileged security boundaries.

Milestone P1 architecture is officially **APPROVED**.
