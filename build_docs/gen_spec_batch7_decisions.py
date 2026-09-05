#!/usr/bin/env python3
"""
Generate comprehensive ADRs matching user structure:
ADR-0001-linux-kernel.md
ADR-0002-fedora-base.md
ADR-0003-wayland.md
ADR-0004-rust.md
ADR-0005-wine.md
ADR-0006-proton.md
ADR-0007-no-vm.md
ADR-0008-atomic-updates.md
(ADR-0009-nebushell-ui-architecture.md is already comprehensive at 338 lines)
"""

import os

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {path} ({len(content.splitlines())} lines)")

adr1 = r"""# ADR-0001: Standard LTS Linux Kernel as Hardware and Operating System Foundation

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Linux OS Engineer  
**Consulted:** PRD §1, §5, §60  

---

## 1. Context and Problem Statement
NebuOS is designed to deliver a modern, high-performance desktop operating system capable of running native Linux applications and Windows binaries seamlessly on standard x86_64 hardware. Developing a custom operating system kernel from scratch would require decades of engineering effort, introduce severe hardware driver deficits, and lack mature graphics and containerization stacks. We must choose the underlying kernel foundation that delivers maximum hardware compatibility, advanced memory management, low latency, and robust container isolation.

## 2. Decision Drivers
- **Broad Hardware Ecosystem:** Out-of-the-box support for thousands of x86_64 motherboards, CPUs, Wi-Fi chipsets, and peripheral devices.
- **Direct Rendering Infrastructure (DRM/KMS):** Native integration with Mesa and modern GPU hardware drivers (Intel, AMD, NVIDIA).
- **Advanced Concurrency and Synchronization Primitives:** In-kernel `futex2` (`futex_waitv`), `io_uring`, and `epoll` essential for high-performance Windows API emulation.
- **Resource Control and Isolation:** Linux cgroups v2, user namespaces, and seccomp BPF filters required for per-application Bubblewrap sandboxing.
- **Long-Term Maintainability:** Regular upstream security patches and stable Long-Term Support (LTS) maintenance cycles.

## 3. Considered Options
- **Option 1: Upstream Long-Term Support (LTS) Linux Kernel (6.6+ or Fedora Stable 6.10+) [SELECTED]**
- **Option 2: Custom In-House Microkernel (e.g. seL4 or custom Rust kernel)**
- **Option 3: BSD Kernel Foundation (FreeBSD / OpenBSD)**
- **Option 4: Windows NT Emulation Kernel (ReactOS approach)**

## 4. Decision Outcome
**Chosen Option: Option 1 — Upstream Long-Term Support (LTS) Linux Kernel.**

We select the standard Linux kernel (6.6 LTS / 6.10+ from Fedora base) with specific sysctl tunables (`vm.max_map_count=2147483642`, `split_lock_mitigate=0`, `fs.file-max=2097152`).

### Positive Consequences
- Immediate zero-day support for modern PC hardware, NVMe drives, USB4/Thunderbolt, and Wi-Fi 6E/7.
- First-class support for `futex_waitv` (syscall 449), enabling Proton/Wine Fsync to match native Windows thread synchronization performance.
- Native integration with standard container engines (`bootc`, `bwrap`, `podman`).
- Zero kernel development or maintenance overhead for the NebuOS engineering team.

### Negative Consequences
- Susceptible to occasional upstream kernel regressions (mitigated via atomic image rollback).
- Proprietary NVIDIA out-of-tree kernel modules require pre-compiled kmod layering.

## 5. Pros and Cons of Alternatives

### Option 2: Custom Microkernel
- *Pros:* Strict formal verification, minimal attack surface.
- *Cons:* Zero device driver support for consumer GPUs, Wi-Fi, or audio; years of development before reaching a bootable desktop; completely unfeasible within project scope.

### Option 3: BSD Kernel
- *Pros:* Permissive licensing, clean monolithic architecture.
- *Cons:* Significantly lagging GPU driver support (Mesa Vulkan, DRM/KMS); lack of modern gaming optimizations (`futex_waitv`); smaller hardware compatibility footprint.

### Option 4: ReactOS Approach (NT Kernel Clone)
- *Pros:* Native NT architecture and driver model.
- *Cons:* Decades of incomplete reverse engineering; severe instability with modern 64-bit software; lack of support for modern web browsers, CAD suites, and DirectX 12.

## 6. Confirmation and Validation
- Automated boot tests on physical hardware (Intel Gen9 through Core Ultra, AMD Ryzen 3000-8000 series).
- Sysctl verification asserting `vm.max_map_count` and `fsync` support at boot.
"""

adr2 = r"""# ADR-0002: Fedora Atomic / Image-Based Base Operating System

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Linux OS Engineer  
**Consulted:** PRD §7, §9, §10, §72  

---

## 1. Context and Problem Statement
Traditional package-based Linux distributions (Debian, Arch, standard Fedora Workstation) allow runtime package mutation. Over time, user-installed packages, aborted upgrades, and conflicting library dependencies cause system state drift, broken environments, and unbootable states. NebuOS requires an immutable, verifiable, and atomic base operating system that guarantees reproducibility, seamless atomic upgrades, and instant rollback.

## 2. Decision Drivers
- **Immutability:** System root (`/usr`) must be mounted read-only to prevent tampering and corruption.
- **Atomic Image Upgrades:** OS updates must apply as a single atomic transaction without intermediate broken states.
- **OCI Container Integration (`bootc`):** Ability to build, layer, test, and distribute the base OS using standard Containerfile and OCI registry workflows.
- **Modern Package Ecosystem:** Access to fresh Mesa drivers, PipeWire audio, systemd v254+, and Wayland libraries.
- **Enterprise-Grade Stability:** Backed by an established, active upstream enterprise Linux community.

## 3. Considered Options
- **Option 1: Fedora Atomic Base with `bootc` and `rpm-ostree` [SELECTED]**
- **Option 2: Traditional Mutable Distribution (Ubuntu LTS / Debian Stable)**
- **Option 3: Custom Scratch Distribution (Linux From Scratch / Yocto)**
- **Option 4: Arch Linux Base with Btrfs Snapshots**

## 4. Decision Outcome
**Chosen Option: Option 1 — Fedora Atomic Base with `bootc` / `rpm-ostree`.**

NebuOS adopts the Fedora Atomic bootc container base (`quay.io/fedora/fedora-bootc:40`). The base system is constructed via a multi-stage `Containerfile` and deployed immutably to target systems.

### Positive Consequences
- Root filesystem `/usr` is mounted strictly read-only, preventing accidental deletion or malware persistence.
- Updates are staged in the background as complete OCI container layers; activation occurs cleanly upon reboot.
- Automated rollback via GRUB boot-counting ensures the system is self-healing.
- Developers build and test NebuOS base images using standard Podman/Docker tooling.

### Negative Consequences
- Users cannot run ad-hoc `dnf install` commands to mutate the base OS (native apps must be installed via Flatpak or user containers).
- Base image rebuild required to add host-level system dependencies.

## 5. Pros and Cons of Alternatives

### Option 2: Traditional Mutable Ubuntu / Debian
- *Pros:* Familiar package management for end-users.
- *Cons:* Susceptible to broken dependencies ("dependency hell"); no native atomic rollback; mutable system files easily corrupted.

### Option 3: Custom Yocto / LFS Distribution
- *Pros:* Extreme minimalism, zero upstream bloat.
- *Cons:* Massive maintenance burden; compiling every package from source in CI; lagging security updates for thousands of packages.

### Option 4: Arch Linux Base
- *Pros:* Rolling release, latest upstream software.
- *Cons:* Inherent instability and frequent manual intervention required; lack of native immutable image deployment architecture.

## 6. Confirmation and Validation
- Image builds validated via `bootc container lint`.
- Automated QEMU boot test verifying read-only `/usr` and successful A/B deployment switching.
"""

adr3 = r"""# ADR-0003: Pure Wayland Display Architecture and Rejection of X11

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Graphics Engineer  
**Consulted:** PRD §11, §52, §53  

---

## 1. Context and Problem Statement
The X Window System (X11) has served Linux for nearly four decades but possesses fatal architectural flaws: universal client snooping (no security boundaries between windows), lack of native tearing-free atomic frame pacing, complex multi-DPI scaling limitations, and high latency. NebuOS must provide a modern, secure, stutter-free display foundation with crisp fractional scaling for mixed Linux and Windows applications.

## 2. Decision Drivers
- **Security and Isolation:** Windows applications and web browsers must not be able to snoop keystrokes or capture pixels from adjacent windows.
- **Frame Presentation and Latency:** Tearing-free atomic KMS presentation, zero-copy direct scanout for games, and variable refresh rate (VRR) support.
- **Fractional Scaling:** Crisp HiDPI scaling without blurry nearest-neighbor bitmap scaling.
- **Maintenance Horizon:** Major Linux ecosystems (GNOME, KDE, Fedora, Red Hat) have deprecated X11 in favor of Wayland.

## 3. Considered Options
- **Option 1: Pure Wayland Architecture with Rootless Xwayland Fallback [SELECTED]**
- **Option 2: Hybrid X11 / Wayland Session Selection**
- **Option 3: Legacy X11 Display Server (Xorg)**

## 4. Decision Outcome
**Chosen Option: Option 1 — Pure Wayland Architecture with Rootless Xwayland.**

NebuOS runs exclusively on Wayland. All native userland desktop components (`nebu-compositor`, `nebu-shell`) communicate via core Wayland protocols and modern extensions (`xdg-shell`, `wlr-layer-shell`, `linux-dmabuf-v1`, `wp_fractional_scale_v1`). Legacy X11 applications and games run through an on-demand, rootless Xwayland compatibility bridge.

### Positive Consequences
- Total process security isolation: no window can snoop another window's buffers or input stream.
- Stutter-free atomic modesetting and presentation timing.
- Wine 9.0+ native `winewayland.drv` driver eliminates X11 translation overhead for modern Windows software.
- HiDPI fractional scaling works seamlessly across heterogeneous multi-monitor setups.

### Negative Consequences
- Legacy Windows games demanding raw X11 mode-switching require Xwayland emulation and `wp_viewporter`.
- Screen recording tools must use privileged desktop portals (`xdg-desktop-portal-wlr`) rather than raw window capture.

## 5. Pros and Cons of Alternatives

### Option 2: Hybrid X11 / Wayland Sessions
- *Pros:* Maximum backward compatibility for very old software.
- *Cons:* Doubles QA testing matrix; requires maintaining two display server stacks; perpetuates X11 security vulnerabilities.

### Option 3: Legacy X11
- *Pros:* Broad legacy compatibility.
- *Cons:* Terrible multi-monitor fractional scaling; zero window security isolation; tearing and presentation jitter; obsolete upstream support.

## 6. Confirmation and Validation
- Wayland protocol conformance verified using `wayland-scanner` and automated protocol fuzzing.
- Direct scanout validated on fullscreen Vulkan benchmarks with zero compositor overhead.
"""

adr4 = r"""# ADR-0004: Rust as Primary Implementation Language for Core Components

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Rust Systems Engineer  
**Consulted:** PRD §4, §83, §84  

---

## 1. Context and Problem Statement
Operating system userland daemons—specifically display compositors, desktop shells, and application sandboxing daemons—handle untrusted user input, direct hardware graphics devices, and complex IPC. Historically, C and C++ implementations have suffered from widespread memory safety vulnerabilities (buffer overflows, use-after-free, data races). NebuOS requires a programming language that guarantees memory safety, eliminates data races, provides zero-cost abstractions, and matches C/C++ execution performance.

## 2. Decision Drivers
- **Memory Safety:** Compile-time guarantees eliminating use-after-free, double free, and buffer overflow CVEs.
- **Concurrency Safety:** Compile-time prevention of data races (`Send` / `Sync` traits) essential for multi-threaded compositor and runtime event loops.
- **Predictable Performance:** Zero garbage collection pauses, predictable latency, minimal memory footprint.
- **Modern Ecosystem:** First-class async I/O (`tokio`, `calloop`), D-Bus integration (`zbus`), and modular compositor primitives (`smithay`).
- **Strict Resource Budget:** Capable of running within strict memory budgets (Compositor <= 35 MB, Shell <= 45 MB, Runtime <= 15 MB).

## 3. Considered Options
- **Option 1: Rust for All Core NebuOS Components [SELECTED]**
- **Option 2: Modern C++ (C++20 / C++23)**
- **Option 3: Go (Golang)**
- **Option 4: C (C11) with Sanitizers**

## 4. Decision Outcome
**Chosen Option: Option 1 — Rust as the Primary Systems Language.**

All newly developed NebuOS components—`nebu-compositor`, `nebu-shell`, `nebu-runtime-daemon`, `nebu-installer-ui`, and `compat.db` tooling—are implemented in 100% safe Rust, isolating unavoidable FFI bindings (`libdrm`, `libinput`, SQLite) into audited `unsafe` blocks.

### Positive Consequences
- Elimination of entire classes of memory corruption security vulnerabilities.
- Zero garbage collection overhead ensures smooth 60/120 FPS compositor frame pacing.
- Fearless concurrency across multi-threaded renderers and background I/O tasks.
- Cargo package management and unit test integration streamline developer workflows.

### Negative Consequences
- Slower compilation times compared to C/Go (mitigated via Cargo sccache and modular crate design).
- Steeper learning curve for new contributors.

## 5. Pros and Cons of Alternatives

### Option 2: Modern C++
- *Pros:* Immense graphics library ecosystem; mature tooling.
- *Cons:* Lack of borrow checker; memory safety depends on programmer discipline; legacy undefined behavior footguns.

### Option 3: Go
- *Pros:* Rapid development, fast compile times.
- *Cons:* Garbage collection pauses induce frame drops in display compositors; heavy runtime footprint; poor C FFI ergonomics for DRM/KMS.

### Option 4: C (C11)
- *Pros:* Universal portability, minimal footprint.
- *Cons:* Zero compile-time memory safety; manual resource management prone to memory leaks.

## 6. Confirmation and Validation
- Zero `unsafe` blocks permitted in core business logic; all FFI crates run under Miri and AddressSanitizer in CI.
"""

adr5 = r"""# ADR-0005: Upstream Wine as Core Windows Application Compatibility Engine

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Compatibility Engineer  
**Consulted:** PRD §16, §20, §70, §71  

---

## 1. Context and Problem Statement
NebuOS aims to provide seamless execution of Windows applications on Linux without running a Windows virtual machine. The Windows Win32/NT API is massive, encompassing thousands of undocumented system calls, registry semantics, OLE/COM interfaces, and userland DLLs. Re-implementing this API from scratch is impossible. We must decide how NebuOS integrates Wine to achieve maximum application compatibility while maintaining engineering sustainability.

## 2. Decision Drivers
- **Engineering Viability:** Wine represents over 30 years of continuous engineering by hundreds of systems developers.
- **Maintenance Sustainability:** Forking Wine would create an unsustainable maintenance burden and disconnect NebuOS from upstream fixes.
- **Modularity:** Ability to run decoupled Wine release trees (Stable, Staging) per application prefix.
- **Integration Potential:** Deep control over environment variables, DLL overrides, registry hives, and sandboxing without modifying Wine internals.

## 3. Considered Options
- **Option 1: Upstream Wine Integration via Dynamic Prefixes and Declarative Patching [SELECTED]**
- **Option 2: Hard Fork of Wine (NebuWine)**
- **Option 3: Binary Translation / Emulation (Box64 / QEMU User Space)**
- **Option 4: Windows Virtual Machine Fallback (Explicitly Rejected by PRD)**

## 4. Decision Outcome
**Chosen Option: Option 1 — Upstream Wine Integration Layer.**

NebuOS treats Wine as an external, immutable dependency. NebuOS packages official upstream Wine Stable and Wine Staging release builds in `/usr/lib/nebu/runtimes/wine/`. Compatibility adjustments are applied externally via declarative compatibility profiles, registry injection, DLL overrides, and environment configuration rather than source code modifications.

### Positive Consequences
- Zero source-code maintenance overhead for the Win32 emulation engine.
- Instant access to upstream Wine releases (e.g. Wine 9.0+ Wayland driver support).
- Clean separation of concerns: NebuOS focuses on orchestration, isolation, UI, and patching.
- Complete licensing compliance (LGPL-2.1).

### Negative Consequences
- Inability to fix internal Wine bugs immediately without upstream submission.
- Dependence on upstream Wine release cadence.

## 5. Pros and Cons of Alternatives

### Option 2: Hard Fork of Wine
- *Pros:* Ability to hack temporary workarounds directly into DLL source code.
- *Cons:* Disconnects from upstream improvements; rebasing becomes an insurmountable engineering nightmare; project failure mode observed in numerous dead Linux distributions.

### Option 3: Binary Translation (Box64/QEMU)
- *Pros:* Enables running x86_64 binaries on ARM64 hardware.
- *Cons:* Massive performance penalty (30–60% slowdown); unnecessary on native x86_64 hardware.

### Option 4: Virtual Machine Fallback
- *Pros:* High compatibility.
- *Cons:* Direct violation of PRD §1, §3; massive RAM overhead (2–4 GB); slow boot; Windows licensing requirements; completely rejected.

## 6. Confirmation and Validation
- Application compatibility lab executing 50 Windows applications against upstream Wine staging builds with automated verification.
"""

adr6 = r"""# ADR-0006: Proton and DXVK/VKD3D Integration for 3D and Gaming Workloads

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Graphics Engineer  
**Consulted:** PRD §17, §25, §26, §73, §74  

---

## 1. Context and Problem Statement
Standard upstream Wine translates Microsoft Direct3D calls to OpenGL via WineD3D. While sufficient for basic 2D utilities, WineD3D suffers from poor performance, high CPU overhead, and limited compatibility with modern Direct3D 11 and Direct3D 12 applications (CAD software, 3D renderers, and modern games). Valve’s Proton, DXVK, and VKD3D-Proton project translate Direct3D 9/10/11/12 directly to Vulkan. We must determine how to incorporate these technologies into NebuOS.

## 2. Decision Drivers
- **Graphics Performance:** Native-level frame rates (>= 90% of bare-metal Windows performance) on modern GPUs.
- **Vulkan Efficiency:** Direct utilization of Mesa RADV, ANV, and NVIDIA Vulkan drivers with explicit synchronization.
- **Low CPU Overhead:** Asynchronous pipeline compilation and state caching to eliminate shader stutter.
- **Modern API Coverage:** Complete support for Direct3D 11 and Direct3D 12 workloads.

## 3. Considered Options
- **Option 1: Integrated Proton and DXVK/VKD3D-Proton Layer alongside Wine [SELECTED]**
- **Option 2: Rely Solely on Upstream WineD3D (OpenGL)**
- **Option 3: Write a Custom Direct3D-to-Vulkan Translator**

## 4. Decision Outcome
**Chosen Option: Option 1 — Integrated Proton and DXVK/VKD3D-Proton Stack.**

NebuOS bundles pre-compiled, upstream-validated DXVK (2.3+) and VKD3D-Proton (2.12+) libraries in `/usr/lib/nebu/graphics/`. For 3D CAD software and games, NebuRuntime automatically configures Wine prefixes to override `d3d11.dll`, `d3d12.dll`, and `dxgi.dll` with DXVK/VKD3D binaries. For standalone gaming titles, NebuOS provisions Proton runtimes directly.

### Positive Consequences
- Dramatic performance gains: 3x to 5x higher framerates compared to WineD3D on Direct3D 11 workloads.
- Flawless execution of modern Direct3D 12 applications on Vulkan 1.3 hardware.
- Persistent shader state caching (`.dxvk-cache`) eliminates visual hitching and stutter.

### Negative Consequences
- Requires Vulkan 1.3 capable GPU hardware (legacy GPUs fall back to WineD3D OpenGL).
- Increases disk footprint of compatibility runtimes by ~120 MB.

## 5. Pros and Cons of Alternatives

### Option 2: Rely Solely on WineD3D
- *Pros:* Works on older GPUs lacking Vulkan.
- *Cons:* Terrible performance; stuttering; inability to run Direct3D 12 software; unacceptable for modern desktop OS.

### Option 3: Custom Translator
- *Pros:* Theoretical custom tailoring.
- *Cons:* Multi-year engineering effort duplicating Valve's multimillion-dollar investment in DXVK/VKD3D.

## 6. Confirmation and Validation
- Automated benchmarking comparing D3D11 rendering performance on NebuOS vs. bare-metal Windows 11 on identical hardware.
"""

adr7 = r"""# ADR-0007: Absolute Prohibition of Virtual Machines for Windows Compatibility

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Product Lead  
**Consulted:** PRD §1, §3, §80, §81, §93  

---

## 1. Context and Problem Statement
When running Windows applications on Linux, many projects take the easy path of launching a hidden Windows virtual machine (KVM, QEMU, VirtualBox). While this guarantees high compatibility, it introduces fatal product flaws: massive memory consumption (2–4 GB minimum), slow VM boot times (15–30s), dual operating system maintenance, Windows licensing requirements, poor GPU virtualization, and lack of seamless desktop window integration. The NebuOS PRD establishes a non-negotiable core vision: NebuOS is a lightweight OS that does NOT use virtual machines.

## 2. Decision Drivers
- **Product Vision Invariant:** PRD §1, §3 explicitly state: "Virtual Machine: NOT PART OF NEBUOS."
- **Hardware Inclusivity:** NebuOS must run on 4GB RAM low-end PCs; running a Windows VM would instantly exhaust all physical memory.
- **Instant Launch Latency:** Applications must launch within 1.5–2.5 seconds, not the 20+ seconds required to boot a Windows hypervisor instance.
- **Zero Windows Licensing:** Users must not be required to purchase, activate, or maintain a proprietary Microsoft Windows OS license.
- **Native Window Ergonomics:** Application windows must be first-class Wayland surfaces with native shadows, snapping, and Alt+Tab integration.

## 3. Considered Options
- **Option 1: Pure API Translation (Wine/Proton/DXVK) with Sandbox Isolation [SELECTED]**
- **Option 2: Micro-VM Fallback for Incompatible Applications (e.g. Firecracker/KVM)**
- **Option 3: Full Windows Virtual Machine (KVM/QEMU with GPU Passthrough)**

## 4. Decision Outcome
**Chosen Option: Option 1 — Pure API Translation Layer (Zero Virtual Machines).**

NebuOS strictly prohibits the inclusion, packaging, or runtime fallback to virtual machines for Windows application execution. All Windows executables run as native Linux processes in isolated user namespaces via Wine and Proton. Applications that require Windows kernel drivers or ring-0 virtualization are marked as unsupported and rejected cleanly.

### Positive Consequences
- True lightweight performance: steady-state system idle memory < 800 MB RAM.
- Application cold launch latency <= 2.5s; warm launch <= 800ms.
- Windows application windows are native Wayland surfaces composited directly on the desktop.
- 100% legal independence: zero Microsoft Windows ISO or license requirements.

### Negative Consequences
- Applications requiring proprietary Windows kernel-mode drivers (`.sys`), hardware dongle drivers, or ring-0 anti-cheat cannot run.

## 5. Pros and Cons of Alternatives

### Option 2 & 3: Micro-VMs or Full Virtual Machines
- *Pros:* Runs software requiring Windows kernel drivers.
- *Cons:* Violates PRD core principle; requires 2–4 GB RAM overhead; requires Windows license; introduces slow boot cycles; destroys the value proposition of NebuOS.

## 6. Confirmation and Validation
- Architectural audit confirming zero hypervisor dependencies (`qemu`, `libvirt`, `kvm`) in base image manifests.
"""

adr8 = r"""# ADR-0008: Atomic Image Deployments and Btrfs Subvolume Topology

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Storage Engineer  
**Consulted:** PRD §7, §9, §15, §43, §44  

---

## 1. Context and Problem Statement
Operating system updates and storage management must be resilient against power loss, filesystem corruption, and storage bloat. Windows application prefixes create thousands of small files and duplicate runtime DLLs. Furthermore, updates must never corrupt the active operating system. We must choose the underlying storage architecture and atomic deployment engine that provides copy-on-write snapshots, instant reflink prefix provisioning, and atomic OS deployments.

## 2. Decision Drivers
- **Atomic OS Updates:** Transactional container-based image upgrades via `bootc` and OSTree.
- **Fast Prefix Provisioning:** Ability to clone a 500 MB clean Wine prefix template in < 200ms without duplicating disk blocks.
- **Filesystem Compression:** Transparent data compression to reduce disk consumption on budget devices.
- **Data Safety:** Copy-on-Write (CoW) metadata guarantees protecting against power-loss corruption.

## 3. Considered Options
- **Option 1: Btrfs Subvolume Topology with `bootc` Atomic Deployments [SELECTED]**
- **Option 2: Ext4 Filesystem with Traditional LVM Snapshots**
- **Option 3: ZFS on Linux**
- **Option 4: OverlayFS on Read-Only SquashFS**

## 4. Decision Outcome
**Chosen Option: Option 1 — Btrfs Subvolumes with `bootc` Atomic Deployments.**

NebuOS formats storage using Btrfs with dedicated subvolumes:
- `@`: Root sysroot deployment mount (`/sysroot`)
- `@home`: User persistent personal files (`/home`)
- `@var`: System persistent state (`/var`)
- `@nebu_apps`: Windows application prefixes (`nodatacow` enabled to eliminate registry fragmentation).
OS images are managed immutably via `bootc`. Application prefixes are cloned instantly from templates using Btrfs reflink ioctl (`FICLONE`).

### Positive Consequences
- Zero-copy prefix provisioning: creating a new prefix takes < 150ms and consumes 0 bytes of disk space initially.
- Automated instant rollback: reverting an application or OS update takes < 500ms via Btrfs snapshots.
- Transparent `zstd:1` compression reduces OS and application footprint by 35–45%.

### Negative Consequences
- Btrfs Copy-on-Write can cause fragmentation on random-write files (mitigated by setting `nodatacow` on `@nebu_apps`).
- Btrfs free space reporting requires user-facing documentation.

## 5. Pros and Cons of Alternatives

### Option 2: Ext4 with LVM
- *Pros:* Simple, mature.
- *Cons:* Lacks file-level reflink cloning; creating a prefix requires copying 500 MB of data (taking 5–15 seconds); snapshots are coarse-grained at the volume level.

### Option 3: ZFS
- *Pros:* Enterprise snapshot features.
- *Cons:* Out-of-tree kernel module license conflict (CDDL vs GPLv2); heavy memory footprint incompatible with 4GB RAM budget.

### Option 4: OverlayFS on SquashFS
- *Pros:* Minimal read-only image.
- *Cons:* Poor random-write performance; lacks subvolume snapshotting and reflink capabilities.

## 6. Confirmation and Validation
- Btrfs FICLONE benchmark validating prefix clone latency < 200ms.
- Atomic image update and rollback test confirming data persistence in `/home` and `/var`.
"""

write_file("/root/NebuOS/docs/decisions/ADR-0001-linux-kernel.md", adr1)
write_file("/root/NebuOS/docs/decisions/ADR-0002-fedora-base.md", adr2)
write_file("/root/NebuOS/docs/decisions/ADR-0003-wayland.md", adr3)
write_file("/root/NebuOS/docs/decisions/ADR-0004-rust.md", adr4)
write_file("/root/NebuOS/docs/decisions/ADR-0005-wine.md", adr5)
write_file("/root/NebuOS/docs/decisions/ADR-0006-proton.md", adr6)
write_file("/root/NebuOS/docs/decisions/ADR-0007-no-vm.md", adr7)
write_file("/root/NebuOS/docs/decisions/ADR-0008-atomic-updates.md", adr8)

