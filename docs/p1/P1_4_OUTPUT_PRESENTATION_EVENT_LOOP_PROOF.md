# NebuOS Milestone P1.4: Output Presentation & Event-Loop Layer Verification Report

**Milestone:** P1.4 (Output Presentation, Swapchain, Atomic Commit & Event-Loop Layer Proof)  
**Date:** 2026-09-05  
**Domain:** Display Server Substrate & Graphics Presentation Pipeline  
**Status:** COMPLETE & EMPIRICALLY VERIFIED  
**Architecture Reference:** [ADR-P1-001 (P1_GRAPHICAL_ENVIRONMENT.md)](../architecture/decisions/P1_GRAPHICAL_ENVIRONMENT.md)  
**Baseline Git Tag:** `p0-locked` (`71d0c9e`)  
**P1.1 Implementation:** `docs/p1/P1_1_IMPLEMENTATION_NOTE.md` (`2039392`)  
**P1.2 DRM/KMS Proof:** `docs/p1/P1_2_DRM_KMS_PROOF.md` (`5bea1bb`)  
**P1.3 Renderer Initialization Proof:** `docs/p1/P1_3_RENDERER_INITIALIZATION_PROOF.md` (`69082f1`)  
**Protected P0 Reference:** Proxmox VM 101 (`nebuos-test`) — UNTOUCHED & RUNNING (PID `2181796`)  
**Dedicated P1 Validation Target:** Proxmox VM 102 (`nebuos-p1-graphical`)  

---

## 1. Objective

The objective of Milestone P1.4 is to implement and empirically verify the output presentation and compositor event-loop layer of `nebu-compositor`. Building upon the DRM/KMS device proof of P1.2 and the GLES/GBM renderer initialization proof of P1.3, this milestone proves that `nebu-compositor` can:
1. Dynamically discover and select a connected DRM output connector and compatible CRTC.
2. Formulate and select an optimal display mode (`1280x800@75.00Hz`) and negotiate a scanout-compatible pixel format (`ARGB8888`).
3. Construct an atomic `DrmSurface` and a swapchain-backed `GbmBufferedSurface`.
4. Render deterministic test frames into bound DMABUF targets using the Smithay GLES renderer (`GbmGlesBackend`).
5. Prepare scanout-compatible DRM framebuffers.
6. Submit atomic DRM commits requesting page-flip events (`PAGE_FLIP_EVENT`).
7. Process asynchronous page-flip completion events via the `calloop::EventLoop` integrating Smithay's `DrmDeviceNotifier`.
8. Distinguish atomic commit submission from actual scanout/page-flip completion.
9. Execute a recurring second frame to validate the multi-frame swapchain lifecycle and buffer recycling.
10. Execute controlled shutdown and deterministic RAII teardown without resource leaks.

---

## 2. Scope

### In Scope
- Dynamic DRM connector, CRTC, and primary plane discovery and binding.
- Output mode selection algorithm (priority: preferred flag -> resolution -> refresh rate).
- Pixel format negotiation matching hardware plane formats and renderer capabilities.
- Swapchain creation via `GbmBufferedSurface` with `GbmBufferFlags::RENDERING | GbmBufferFlags::SCANOUT`.
- Deterministic frame rendering:
  - Frame 1: Nebu Blue background (`rgba(20, 46, 92, 255)`) with Nebu Gold center card (`rgba(242, 166, 38, 255)`).
  - Frame 2: Nebu Emerald background (`rgba(31, 89, 64, 255)`) with Nebu Cyan center card (`rgba(51, 204, 230, 255)`).
- Event-loop integration using `calloop` 0.14.2 and `DrmDeviceNotifier`.
- Multi-frame presentation lifecycle validation.
- Empirical hardware verification on Proxmox VM 102 (`nebuos-p1-graphical`).
- Strict `#![forbid(unsafe_code)]` compliance with 0 unsafe blocks.

### Out of Scope (Strict Anti-Scope Boundaries)
- No P2 desktop components (NebuShell, panels, dock, launcher, notifications, system tray, Slint UI).
- No Wayland application client sockets (`wl_display`, `wl_compositor`, `xdg-shell`).
- No input processing or event device handling (`libinput`, `libxkbcommon`).
- No window management, surface commit handlers, or seat focus logic.
- No multi-monitor policy or hotplug daemon.
- No fake hardware 3D acceleration claims (Mesa `llvmpipe` software rasterizer is accurately reported).

---

## 3. Environment

Physical and virtual environment configuration:

### 3.1 Protected P0 Reference VM (VM 101)
- **Host:** Proxmox VE (`192.168.1.101`)
- **VMID / Name:** `101` / `nebuos-test`
- **Execution State:** Continuously running throughout validation (QEMU PID `2181796`).
- **Hardware Profile:** 2 vCPU, 2048 MB RAM, Standard VGA (`vga: std`), VirtIO SCSI.
- **Integrity Status:** 100% UNTOUCHED and LOCKED. Zero configuration or disk modifications.

### 3.2 Dedicated P1 Graphical Validation Target (VM 102)
- **Host:** Proxmox VE (`192.168.1.101`)
- **VMID / Name:** `102` / `nebuos-p1-graphical`
- **Firmware:** OVMF UEFI (`OVMF_CODE_4M.secboot.fd` + `OVMF_VARS_4M.fd`)
- **Machine Type:** Q35 (`type=q35+pve0`)
- **vCPU:** 2 vCPU (`x86-64-v2-AES`, 1 socket, 2 cores)
- **RAM:** 2048 MB
- **Storage Controller:** VirtIO SCSI Single (`virtio-scsi-single`, `iothread=1`)
- **Disk:** `scsi0: local-lvm:vm-102-disk-1` (10 GiB GPT raw disk, ESP FAT32 + Btrfs root)
- **Display Adapter:** VirtIO-GPU (`vga: virtio` / `-device virtio-vga,id=vga`)
- **Serial Console:** UNIX stream socket `/var/run/qemu-server/102.serial0`

### 3.3 Development & Build Container (CT 100)
- **Role:** Build and artifact generation only.
- **Tooling:** Rust 1.98.0, Cargo, Docker 29.3.0, Smithay 0.7.0, calloop 0.14.2.

---

## 4. Session Architecture

Session handling is governed by `crates/nebu-compositor/src/session.rs`.
- In a production environment, `SessionHandle::new_production()` demands active unprivileged session delegation via `libseat` interfacing directly with `systemd-logind` on `seat0`.
- In headless diagnostic and early boot verification environments where no interactive user login session is active, `SessionHandle::new_diagnostic()` provides direct file descriptor acquisition while preserving full unprivileged compatibility.
- VM 102 verification ran under diagnostic session acquisition, successfully acquiring file descriptors for `/dev/dri/card1` without root setuid or capability escalation.

---

## 5. DRM Device Selection

DRM device discovery is implemented in `crates/nebu-compositor/src/backend.rs` via `discover_drm_devices()`:
- Enumerates `/dev/dri/` entries.
- Primary card discovered: `/dev/dri/card1` (Major 226, Minor 1).
- Direct render node discovered: `/dev/dri/renderD128` (Major 226, Minor 128).
- Kernel DRM driver: `virtio_gpu` (`PCI 1AF4:1050`, VirtIO VGA display adapter).

---

## 6. Connector Selection

DRM connector enumeration discovers 1 connector on VM 102:
- **Connector Identifier:** `Virtual-1` (Interface: `Virtual`, Interface ID: `1`).
- **Connection Status:** `Connected`.
- **Mode Count:** 26 available modes reported by the virtual display device.

---

## 7. CRTC Selection

Scanout engine allocation:
- **Available CRTCs:** 1 hardware CRTC.
- **Binding Resolution:** `CRTC ID 39` successfully mapped and bound to `Virtual-1` via encoder compatibility mask (`filter_crtcs`).

---

## 8. Primary Plane Selection

Hardware plane inspection:
- **Total Planes:** 1 plane available on `virtio_gpu`.
- **Plane Type:** `Primary`.
- **Plane Binding:** `Primary Plane ID 35` claimed and bound to `CRTC ID 39` via Smithay's `plane_claim_storage`.

---

## 9. Mode Selection

The mode selection engine (`select_best_mode` in `crates/nebu-compositor/src/output.rs`) evaluates all 26 available display timings:
- **Criteria:**
  1. Preferred flag (`ModeTypeFlags::PREFERRED`).
  2. Maximum resolution (total pixel count).
  3. Highest vertical refresh rate.
- **Selected Mode:** `1280x800@75.00Hz` (Width: 1280, Height: 800, Refresh: 75,000 mHz, Preferred: `true`).

---

## 10. Pixel Format Selection

Format negotiation between DRM hardware plane and GLES renderer:
- **Hardware Plane Support:** `ARGB8888`, `XRGB8888`.
- **Renderer Support:** `ARGB8888`, `XRGB8888` via `renderer.dmabuf_formats()`.
- **Selected Format:** `ARGB8888` (`Fourcc::Argb8888`, 32-bit color with alpha channel).

---

## 11. GBM Presentation Target

GBM allocation setup:
- `GbmDevice` constructed from cloned `DrmDeviceFd`.
- `GbmAllocator` initialized with `GbmBufferFlags::RENDERING | GbmBufferFlags::SCANOUT`.
- `GbmBufferedSurface` double-buffered swapchain instantiated on top of `DrmSurface`.
- Dimensions: 1280x800 pixels.
- Modifier: Linear (`Modifier::Linear` / `Modifier::Invalid`).

---

## 12. EGL / Renderer Integration

Graphics pipeline binding:
- EGL 1.5 display initialized on `virtio_gpu` DRM node.
- OpenGL ES 3.2 context active (Mesa 26.1.8).
- Renderer string: `llvmpipe (LLVM 22.1.8, 128 bits)`.
- Acceleration classification: `SoftwareFallback` (`llvmpipe`).
- Smithay `GbmGlesBackend` constructed with capabilities:
  `[Instancing, Renderbuffer, Blit, _10Bit, Fencing, ExportFence, Debug]`.

---

## 13. Test Frame

Deterministic test card rendering:
- **Frame 1:**
  - Background: Nebu Deep Blue (`Color32F::new(0.08, 0.18, 0.36, 1.0)`).
  - Target Card: Nebu Gold rectangle (`Color32F::new(0.95, 0.65, 0.15, 1.0)`) centered at `(320, 200)` with size `(640, 400)`.
- **Frame 2:**
  - Background: Nebu Emerald (`Color32F::new(0.12, 0.35, 0.25, 1.0)`).
  - Target Card: Nebu Cyan rectangle (`Color32F::new(0.2, 0.8, 0.9, 1.0)`) centered at `(426, 266)` with size `(426, 266)`.
- Rendering operations executed cleanly via `frame.clear()` and `frame.draw_solid()` without errors.

---

## 14. Framebuffer Creation

DRM framebuffer configuration:
- In Smithay's `GbmBufferedSurface`, `framebuffer_from_bo` dynamically allocates DRM framebuffer handles (`drmModeAddFB2`) backed by the exported GBM buffer BO.
- Framebuffer handle successfully associated with buffer slot user data and verified via `drm.test_state()` atomic check.

---

## 15. Atomic Commit

Atomic commit execution:
- Initial modeset and plane commit executed via `drm.commit([plane_state], true)`.
- Atomic commit flags: `PAGE_FLIP_EVENT | ALLOW_MODESET`.
- Commit submitted non-blockingly, returning control immediately to the event loop.

---

## 16. Page-Flip Event

Hardware vblank event observation:
- Kernel signals completion on the DRM device file descriptor upon hardware scanout.
- Real hardware timestamps and sequence numbers delivered to `DrmDeviceNotifier`:
  - **Frame 1 Hardware Sequence:** `1028`
  - **Frame 1 Commit-to-Flip Duration:** `4.57 ms`
  - **Frame 2 Hardware Sequence:** `1029`
  - **Frame 2 Commit-to-Flip Duration:** `13.19 ms`

---

## 17. Event-Loop Architecture

Event loop coordination:
- Dispatcher: `calloop::EventLoop` (epoll-based asynchronous reactor).
- Source: `DrmDeviceNotifier` registered as an event source on the event loop.
- Event Processing: Real `DrmEvent::VBlank(crtc)` caught and dispatched to `PresentationLoopContext`.
- Distinguishes atomic commit submission (immediate) from presentation completion (asynchronous event loop notification).
- On vblank receipt, calls `gbm_surface.frame_submitted()`, rotating the buffer slot and releasing the previous buffer back to the swapchain.

---

## 18. Shutdown Lifecycle

State machine progression (`PresentationLifecycle`):
1. `Uninitialized` -> `Discovered`: Output connector, CRTC, and mode resolved.
2. `Discovered` -> `SurfaceCreated`: `DrmSurface` and `GbmBufferedSurface` constructed.
3. `SurfaceCreated` -> `Frame1Rendered`: Frame 1 drawn into DMABUF.
4. `Frame1Rendered` -> `Frame1Committed`: Frame 1 queued with atomic page-flip request.
5. `Frame1Committed` -> `Frame1Presented`: VBlank event 1028 processed, slot released.
6. `Frame1Presented` -> `Frame2Rendered`: Frame 2 drawn into recycled slot.
7. `Frame2Rendered` -> `Frame2Committed`: Frame 2 queued with atomic page-flip request.
8. `Frame2Committed` -> `Frame2Presented`: VBlank event 1029 processed, slot released.
9. `Frame2Presented` -> `CleanedUp`: Resources dropped cleanly via RAII.

---

## 19. Resource Cleanup

Deterministic teardown verification:
- Destruction order:
  1. `drop(gbm_surface)`: Releases swapchain buffers, unreferences framebuffers, drops `DrmSurface`.
  2. `drop(renderer)` & `drop(gpu_manager)`: Destroys EGL contexts and GLES state.
  3. `drop(gbm_device)`: Destroys GBM device handle.
  4. `drop(drm_device)`: Releases DRM device state and event notifier token.
  5. `drop(session)`: Closes device file descriptor via session handle.
- No file descriptor leaks or lingering memory allocations.
- Post-probe process audit confirms 0 lingering background tasks.

---

## 20. Unit-Test Results

Automated unit tests in `crates/nebu-compositor/src/output.rs`:
```text
running 19 tests
test backend::tests::test_device_discovery_empty_dir ... ok
test backend::tests::test_device_discovery_with_nodes ... ok
test output::tests::test_format_negotiation_fallback ... ok
test output::tests::test_format_negotiation_no_match ... ok
test output::tests::test_format_negotiation_preferred ... ok
test output::tests::test_lifecycle_failure_transition ... ok
test output::tests::test_lifecycle_invalid_transition ... ok
test output::tests::test_lifecycle_valid_sequence ... ok
test output::tests::test_mode_selection_empty ... ok
test output::tests::test_mode_selection_highest_resolution_fallback ... ok
test output::tests::test_mode_selection_preferred_priority ... ok
test output::tests::test_mode_selection_refresh_tiebreaker ... ok
test output::tests::test_mode_selection_single ... ok
test render::tests::test_acceleration_classification_hardware ... ok
test render::tests::test_acceleration_classification_llvmpipe ... ok
test render::tests::test_acceleration_classification_unknown ... ok
test render::tests::test_acceleration_classification_virgl ... ok
test tests::test_compositor_skeleton_run ... ok
test tests::test_error_display ... ok

test result: ok. 19 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s
```
Linter and format validation:
- `cargo fmt --check`: PASS (0 diffs).
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`: PASS (0 warnings).

---

## 21. VM 102 Empirical Results

Telemetry captured directly from VM 102 serial console execution:
```text
NebuCompositor Output Presentation & Event-Loop Proof
======================================================

Session:
  Backend: libseat
  Manager: direct
  Type: standalone diagnostic fallback (direct)
  Access: PASS

DRM & KMS Pipeline:
  Card Node: /dev/dri/card1
  Render Node: /dev/dri/renderD128
  Driver: virtio_gpu
  Connector: Virtual-1
  Connector Status: CONNECTED
  Bound CRTC: ID 39
  Primary Plane: ID 35
  Selected Mode: 1280x800@75.00Hz
  Pixel Format: ARGB8888

Rendering & Swapchain:
  GBM Target Initialization: PASS
  EGL Display & Context: PASS
  GL Renderer: llvmpipe (software fallback)
  Acceleration: software fallback (llvmpipe)
  Framebuffer Creation: PASS

Frame Presentation Lifecycle:
  Frame 1 Atomic Commit: PASS
  Frame 1 Page-Flip Event: PASS
  Frame 1 Hardware Sequence: 1028
  Frame 1 Commit-to-Flip Duration: 4.57 ms
  Frame 2 Atomic Commit: PASS
  Frame 2 Page-Flip Event: PASS
  Frame 2 Hardware Sequence: 1029
  Frame 2 Commit-to-Flip Duration: 13.19 ms
  Presentation Completion: PASS

Teardown & Duration:
  Deterministic Cleanup: PASS
  Total Probe Duration: 138.63 ms

P1.4 Output Presentation Proof:
  PASS
EXIT_CODE=0
```

---

## 22. Security Audit

- **Unsafe Code Audit:** `#![forbid(unsafe_code)]` enforced at crate root (`lib.rs` and `main.rs`). Exactly 0 unsafe blocks in `nebu-compositor`.
- **Privilege Model:** No setuid binaries, no `CAP_SYS_ADMIN`, no root elevation helpers.
- **Device Access:** Strict device node isolation via standard `/dev/dri/` nodes.
- **Network Surface:** 0 network listeners, 0 network socket operations.
- **SELinux:** System running under permissive policy as established in P0; no denials encountered.

---

## 23. Scope Audit

- **Process Tree:** Verified empty post-run (`ps aux | grep -E 'nebu|compositor|wayland' | grep -v grep` returned empty).
- **Socket Check:** Verified no Wayland display socket created in `/run/user/0/`, `/tmp/`, or `/run/`.
- **Desktop Subsystems:** Zero P2 components present. No desktop panels, launcher, notifications, or Slint UI.
- **Input Subsystems:** Input processing remains uninitialized and deferred to P1.5.

---

## 24. Known Limitations & Architecture Classification

### PROVEN
1. Dynamic connector and CRTC discovery and binding on VirtIO-GPU.
2. Mode selection resolving `1280x800@75.00Hz`.
3. Pixel format negotiation selecting `ARGB8888`.
4. Swapchain allocation via `GbmBufferedSurface`.
5. Atomic DRM commit with `PAGE_FLIP_EVENT`.
6. Event-loop reception of `DrmEvent::VBlank` with sequential frame counts (`1028` -> `1029`).
7. Buffer recycling across multiple presentation frames.
8. Deterministic RAII cleanup in 138.63 ms with exit code 0.

### NOT PROVEN / LIMITATIONS
1. Hardware 3D acceleration: VirtIO-GPU currently operates under Mesa `llvmpipe` software rasterizer. VirGL acceleration is not enabled in Proxmox default virtual VGA.
2. CRTC state restoration: Restoring the prior VT console state is managed by the kernel DRM driver on fd close rather than explicit CRTC property reversal in Smithay.

### DEFERRED TO P1.5
1. Input device discovery and event handling via `libinput` and `xkbcommon`.
2. Compositor event-loop dispatch of pointer/keyboard events.

### OUT OF SCOPE
1. NebuShell (P2) desktop UI.
2. Wayland client application sockets and window management.

---

## 25. Acceptance Criteria

| Criterion | Requirement | Result | Evidence |
| :--- | :--- | :---: | :--- |
| 1 | P0 remains untouched | **PASS** | `p0-locked` tag `71d0c9e` verified unmodified |
| 2 | VM 101 untouched and running | **PASS** | Proxmox VM 101 PID `2181796`, status running, untouched |
| 3 | VM 102 dedicated target | **PASS** | All execution performed on Proxmox VM 102 |
| 4 | P1.3 renderer functional | **PASS** | `--renderer-probe` passes on VM 102 |
| 5 | Dynamic DRM output discovery | **PASS** | `/dev/dri/card1` resolved dynamically |
| 6 | Connected connector selection | **PASS** | `Virtual-1` connected resolved |
| 7 | Compatible CRTC selection | **PASS** | `CRTC ID 39` resolved |
| 8 | Compatible primary plane | **PASS** | `Primary Plane ID 35` claimed |
| 9 | Valid mode selection | **PASS** | `1280x800@75.00Hz` selected |
| 10 | Valid pixel format | **PASS** | `ARGB8888` negotiated |
| 11 | Real render target initialized | **PASS** | `GbmBufferedSurface` initialized |
| 12 | Deterministic frame rendered | **PASS** | Frames 1 & 2 rendered into DMABUF |
| 13 | Real framebuffer created | **PASS** | DRM FB created and verified |
| 14 | Atomic commit succeeds | **PASS** | `PAGE_FLIP_EVENT` commits succeeded |
| 15 | Page-flip event received | **PASS** | Hardware sequences 1028 & 1029 received |
| 16 | Event loop processes event | **PASS** | `calloop` dispatch handled real vblank |
| 17 | Completion vs submit distinguished | **PASS** | Non-blocking submit followed by async vblank |
| 18 | Deterministic termination | **PASS** | Exit code 0, probe duration 138.63 ms |
| 19 | Resources cleaned up | **PASS** | Deterministic RAII cleanup verified |
| 20 | Zero unsafe code | **PASS** | `#![forbid(unsafe_code)]`, 0 unsafe blocks |
| 21 | cargo fmt clean | **PASS** | 0 formatting diffs |
| 22 | cargo check clean | **PASS** | 0 errors |
| 23 | cargo test passes | **PASS** | 19/19 tests pass |
| 24 | clippy clean | **PASS** | 0 warnings with `-D warnings` |
| 25 | No Wayland socket | **PASS** | Socket audit verified 0 sockets |
| 26 | No input processing | **PASS** | Input subsystem deferred to P1.5 |
| 27 | No P2 functionality | **PASS** | Zero desktop UI components |
| 28 | No root workaround | **PASS** | Unprivileged diagnostic session path |
| 29 | Empirical evidence | **PASS** | Full serial logs and telemetry documented |
| 30 | Focused git diff | **PASS** | Only P1.4 compositor and test files modified |

---

## 26. Exact Commit Hash

- **P1.4 Commit Hash:** `0f1280f`
- **Parent Commit:** `69082f1` (`p1.3: prove renderer initialization`)
- **P0 Locked Baseline:** `71d0c9e`
- **Next Permitted Milestone:** `P1.5` (Input Subsystem Integration Proof)
