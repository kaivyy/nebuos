#!/usr/bin/env python3
"""
Generator for Batch 8: Roadmap phase implementation specifications:
- roadmap/01-p0-foundation.md
- roadmap/02-p1-compositor.md
- roadmap/03-p2-shell.md
- roadmap/04-p3-runtime.md
- roadmap/05-p4-compatibility.md
- roadmap/06-p5-graphics.md
- roadmap/07-p6-applications.md
- roadmap/08-p7-testing.md
- roadmap/09-p8-production-validation.md
- roadmap/10-future-phases.md
"""

import os

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {path} ({len(content.splitlines())} lines)")

r1 = r"""# Phase P0: Foundation Specification — NebuOS

**Status:** APPROVED  
**Phase:** P0  
**Target Duration:** Sprint 1–2  

---

## 1. Objective
Establish the absolute minimal, verifiable bootable base operating system for NebuOS. P0 proves that the Fedora Atomic container image builds reproducibly in CI, deploys to disk via `bootc`, boots on physical/virtual x86_64 hardware to a serial/virtual terminal (`agetty`), initializes systemd PID 1 cleanly, establishes Btrfs subvolume mounts, brings up basic networking, and provides core diagnostic tools.

P0 is intentionally kept extremely small and focused.

## 2. Scope (What's IN)
- Minimal `Containerfile.p0` based on `quay.io/fedora/fedora-bootc:40`.
- Standard upstream LTS Linux kernel 6.x.
- Btrfs subvolume filesystem topology (`@`, `@home`, `@var`).
- Read-only `/usr` sysroot mount validation.
- Minimal package set: `systemd`, `util-linux`, `NetworkManager`, `iproute`, `btrfs-progs`, `dracut`.
- Boot to text console / TTY (`multi-user.target`).
- Virtual terminal diagnostics: `journalctl`, `systemd-analyze blame`, `dmesg`.
- Local QEMU test automation script (`scripts/test-p0-boot.sh`).

## 3. Anti-Scope (What's NOT IN)
- NO graphical display server (`nebu-compositor` or Wayland).
- NO desktop shell (`nebu-shell`).
- NO Mesa GPU acceleration or DRM modesetting validation.
- NO Wine, Proton, DXVK, or Windows compatibility layers.
- NO PipeWire audio server or Bluetooth.
- NO custom Rust application daemons (`nebu-runtime-daemon`).
- NO graphical installers or software stores.

## 4. Dependencies
- Container build toolchain (`podman` / `buildah`).
- `bootc` >= 0.1.14.
- Upstream Fedora 40 package repositories.
- QEMU / KVM for virtual verification.

## 5. Deliverables
- `Containerfile.p0` located at repository root.
- System configuration files:
  - `/etc/sysctl.d/99-nebuos-p0.conf`
  - `/etc/dracut.conf.d/50-nebu.conf`
- Build script `scripts/build-p0-image.sh`.
- Test harness `scripts/test-p0-boot.sh`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P0-01 (Build Reproducibility):** `podman build -f Containerfile.p0` completes with exit code 0 in under 5 minutes on CI runner.
2. **EC-P0-02 (Boot Verification):** QEMU boots `Containerfile.p0` to login prompt (`login:`) in <= 3.0 seconds (kernel + userspace).
3. **EC-P0-03 (Immutability Gate):** Attempting `touch /usr/bin/testfile` fails with `Read-only file system` error.
4. **EC-P0-04 (Network Readiness):** `NetworkManager` starts and acquires DHCP IPv4 address within 2.0s of boot.
5. **EC-P0-05 (Zero Failed Services):** `systemctl --failed` outputs `0 loaded units listed`.

## 7. Known Risks & Mitigations
- **Risk:** Missing kernel modules in dracut initramfs causes boot hang on non-standard storage controllers.
  - *Mitigation:* Include standard storage driver bundle (`nvme`, `ahci`, `virtio_blk`, `virtio_scsi`) in `dracut.conf`.
"""

r2 = r"""# Phase P1: NebuCompositor Specification — NebuOS

**Status:** APPROVED  
**Phase:** P1  
**Target Duration:** Sprint 3–5  
**Prerequisite:** Phase P0  

---

## 1. Objective
Implement `nebu-compositor`, the native Rust Wayland display server built upon Smithay primitives. P1 establishes hardware DRM/KMS modesetting, libinput event dispatch, EGL/GBM hardware-accelerated rendering, core Wayland protocol support, and zero-copy direct scanout for fullscreen surfaces.

## 2. Scope (What's IN)
- Standalone Rust crate `crates/nebu-compositor`.
- Linux DRM/KMS atomic modesetting backend (`/dev/dri/card0`).
- Hardware input processing via `libinput` and `xkbcommon`.
- GBM (Generic Buffer Management) and EGL/GLES2 rendering pipeline.
- Core Wayland protocols: `wl_compositor`, `wl_subcompositor`, `wl_seat`, `wl_output`, `wl_shm`.
- Extension protocols: `xdg_shell`, `wlr-layer-shell-unstable-v1`, `linux_dmabuf_v1`, `wp_fractional_scale_v1`, `viewporter`.
- Explicit synchronization via `linux-drm-syncobj-v1`.
- Rootless Xwayland socket bridge for legacy X11 applications.
- Idle memory footprint <= 35 MB RSS.

## 3. Anti-Scope (What's NOT IN)
- NO desktop shell widgets, panels, or taskbars (governed by P2).
- NO Wine/Proton runtime integration or PE executable launching (governed by P3).
- NO custom compositor plugin architecture.
- NO software rendering fallback for desktop (GPU acceleration mandatory).

## 4. Dependencies
- Phase P0 Foundation base image.
- Rust 1.80+ toolchain.
- `smithay` = "0.3", `calloop` = "0.13".
- `mesa-dri-drivers` (radeonsi, iris, intel-anv, radv).
- `libdrm` >= 2.4.120, `libinput` >= 1.25.

## 5. Deliverables
- Rust Crate: `crates/nebu-compositor/`.
- Binary: `/usr/bin/nebu-compositor`.
- Systemd Unit: `/usr/lib/systemd/user/nebu-compositor.service`.
- Integration Tests: `tests/compositor_conformance/`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P1-01 (Wayland Socket Emergence):** Compositor initializes and binds `$XDG_RUNTIME_DIR/wayland-0` within 400ms.
2. **EC-P1-02 (Client Rendering):** Standard Wayland client (`weston-terminal` / `foot`) and X11 client (`glxgears` via Xwayland) render at locked 60 FPS without graphical tearing.
3. **EC-P1-03 (Direct Scanout):** Fullscreen test surface scans out directly to DRM primary plane without compositing shader passes.
4. **EC-P1-04 (Memory Budget):** Steady-state idle memory <= 35 MB RSS on a 1080p display.
5. **EC-P1-05 (Hotplug Handling):** Connecting and disconnecting an external HDMI/DisplayPort monitor adjusts layout within 500ms without crashing compositor.

## 7. Known Risks & Mitigations
- **Risk:** Atomic commit failures on legacy multi-monitor setups.
  - *Mitigation:* Fall back cleanly to single-plane composited backbuffer commit if multi-plane atomic test fails.
"""

r3 = r"""# Phase P2: NebuShell Specification — NebuOS

**Status:** APPROVED  
**Phase:** P2  
**Target Duration:** Sprint 6–8  
**Prerequisite:** Phase P1  

---

## 1. Objective
Implement `nebu-shell`, the unified native Rust desktop shell implementing ADR-0009. P2 delivers the taskbar, application launcher, status tray (SNI), quick settings flyout, lock screen (`ext-session-lock-v1`), and the dynamic theme/layout engine supporting runtime switching between Nebu, Windows-like, and macOS-like paradigms in <= 150ms without process restart.

## 2. Scope (What's IN)
- Rust Crates: `crates/nebu-shell-core`, `crates/nebu-shell-layout`, `crates/nebu-shell-theme`.
- Native GUI rendering via Slint or Iced toolkit.
- Wayland layer-shell surfaces (`zwlr_layer_surface_v1`): Panel, Dock, Launcher, Quick Settings, OSD.
- Dynamic layout engine: runtime switching between Nebu Default, Windows-like, and macOS-like paradigms.
- Fast application launcher with sub-millisecond in-memory SQLite indexing.
- System tray host compliant with `org.kde.StatusNotifierWatcher`.
- PipeWire volume control and NetworkManager Wi-Fi/Ethernet flyout widgets.
- Memory budget <= 45 MB RSS idle.

## 3. Anti-Scope (What's NOT IN)
- NO Electron, CEF, Node.js, or HTML/CSS runtime components.
- NO arbitrary untrusted JavaScript applet plugins.
- NO software center store GUI (governed by P6).
- NO Windows EXE execution logic (governed by P3).

## 4. Dependencies
- Phase P1 NebuCompositor.
- GUI Toolkit: `slint` = "1.6" or `iced` = "0.12".
- `zbus` = "4.0", `rusqlite` = "0.31".
- PipeWire client libraries (`libpipewire-0.3`).

## 5. Deliverables
- Binaries: `/usr/bin/nebu-shell`, `/usr/bin/nebu-greeter`, `/usr/bin/nebu-screenshot`.
- Built-in Themes: `/usr/share/nebu/themes/{nebu-default,nebu-dark,windows-like,macos-like}.toml`.
- Systemd Unit: `/usr/lib/systemd/user/nebu-shell.service`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P2-01 (Launcher Responsiveness):** Pressing Super key renders application launcher UI in <= 80ms.
2. **EC-P2-02 (Live Paradigm Switch):** Invoking `nebu-shell-ctl switch macos-like` re-anchors layer surfaces in <= 150ms without dropping client windows.
3. **EC-P2-03 (Tray Compatibility):** Background application registering via SNI displays clickable tray icon with functional context menu.
4. **EC-P2-04 (Combined Memory Budget):** Combined Compositor + Shell idle memory <= 80 MB RSS.
5. **EC-P2-05 (Lock Screen Security):** Lock screen activates via `ext-session-lock-v1` and unlocks cleanly with valid PAM password authentication.

## 7. Known Risks & Mitigations
- **Risk:** Geometry calculation glitches on ultra-wide or rotated displays during paradigm switch.
  - *Mitigation:* Constraint solver enforces strict bounds clamp ($[32, 64]$ px) and tests layout across 10 display aspect ratios in CI.
"""

r4 = r"""# Phase P3: NebuRuntime Specification — NebuOS

**Status:** APPROVED  
**Phase:** P3  
**Target Duration:** Sprint 9–11  
**Prerequisite:** Phase P0, P1, P2  

---

## 1. Objective
Implement `nebu-runtime-daemon` and the Windows PE binary execution pipeline. P3 establishes kernel `binfmt_misc` interception for MZ executables, Bubblewrap sandbox jailing, per-application isolated Wine prefix provisioning via Btrfs reflink, process supervision, and clean lifecycle management.

## 2. Scope (What's IN)
- Rust Crates: `crates/nebu-runtime-daemon`, `crates/nebu-runtime-core`, `crates/nebu-prefix-manager`.
- Kernel `binfmt_misc` registration redirecting `.exe` execution to `/usr/bin/nebu-launch`.
- PE header inspection (zero-copy parsing via `pelite`).
- Btrfs reflink prefix provisioning (< 200ms) from `/usr/share/nebu/prefix-template/`.
- Unprivileged Bubblewrap (`bwrap`) containment with dropped capabilities and seccomp BPF filters.
- Wine process supervision under systemd user transient scopes (`app-nebu-<app_id>.scope`).
- D-Bus Service `org.nebu.Runtime1`.

## 3. Anti-Scope (What's NOT IN)
- NO automated compatibility patching engine (governed by P4).
- NO DXVK/VKD3D Vulkan translation tuning (governed by P5).
- NO graphical software center or installer wizard (governed by P6).
- NO Windows virtual machine fallback (strictly prohibited).

## 4. Dependencies
- Upstream Wine binaries in `/usr/lib/nebu/runtimes/wine-stable/`.
- `bubblewrap` >= 0.8.0.
- Btrfs filesystem with reflink (`FICLONE`) support.
- Rust crates: `pelite`, `zbus`, `nix`, `tokio`.

## 5. Deliverables
- Daemons & CLIs: `/usr/libexec/nebu/nebu-runtime-daemon`, `/usr/bin/nebu-launch`, `/usr/bin/nebu-path`.
- Systemd User Unit: `/usr/lib/systemd/user/nebu-runtime-daemon.service`.
- Prefix Template: `/usr/share/nebu/prefix-template/`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P3-01 (Transparent PE Interception):** Double-clicking or running `./notepad++.exe` in terminal routes to `nebu-launch` and executes Notepad++ cleanly.
2. **EC-P3-02 (Reflink Provisioning Latency):** Creating a fresh per-app prefix at `~/.nebu/apps/<app_id>/` takes <= 200ms and consumes 0 bytes of initial unique disk space.
3. **EC-P3-03 (Sandbox Isolation Gate):** Test application attempting to read `/root` or `~/.ssh` is blocked with `Permission denied`.
4. **EC-P3-04 (Clean Process Termination):** Closing main application window cleanly flushes Wine registry hives and terminates all wineserver child threads within 3.0s (zero orphan processes).
5. **EC-P3-05 (Daemon Memory Budget):** `nebu-runtime-daemon` idle memory <= 15 MB RSS.

## 7. Known Risks & Mitigations
- **Risk:** Wineserver socket file locking contention during rapid sequential launches.
  - *Mitigation:* Implement deterministic per-prefix `flock` and Unix domain socket paths partitioned under `/run/user/1000/nebu/`.
"""

r5 = r"""# Phase P4: Compatibility Subsystem Specification — NebuOS

**Status:** APPROVED  
**Phase:** P4  
**Target Duration:** Sprint 12–14  
**Prerequisite:** Phase P3  

---

## 1. Objective
Implement the NebuOS Compatibility Engine and Relational Database. P4 provides automated application identification via PE header fingerprinting and SHA-256 matching, queries the centralized SQLite compatibility database, and applies declarative 9-tier compatibility patches (DLL overrides, registry injections, font aliases, environment variables) automatically at launch.

## 2. Scope (What's IN)
- Rust Crates: `crates/nebu-compat-db`, `crates/nebu-patcher`.
- Relational SQLite database schema (`/usr/share/nebu/compat.db`) in WAL mode.
- Declarative 9-tier patch engine with Kahn's topological DAG dependency resolution.
- Application detection engine: PE32/PE32+ header analysis, Authenticode extraction, installer classification.
- Pre-packaged, certified JSON compatibility profiles for top 50 productivity applications.
- CLI diagnostic and management tool: `/usr/bin/nebu-compat-tool`.

## 3. Anti-Scope (What's NOT IN)
- NO source-code modifications to upstream Wine.
- NO manual registry hacking by end users (all patches declarative).
- NO bypasses for ring-0 anti-cheat or Windows kernel drivers.

## 4. Dependencies
- SQLite 3.42+ with FTS5 search.
- Rust crates: `rusqlite`, `serde_json`, `sha2`, `pelite`.

## 5. Deliverables
- Database: `/usr/share/nebu/compat.db`.
- CLI: `/usr/bin/nebu-compat-tool`.
- Profile Store: `/usr/share/nebu/profiles/*.json`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P4-01 (Profile Query Latency):** Querying application profile by SHA-256 executes in <= 2.0ms (cold) and <= 0.3ms (warm).
2. **EC-P4-02 (Deterministic Patching):** Patch engine applies 15 sequential registry injections and 5 DLL overrides in <= 150ms with atomic rollback support.
3. **EC-P4-03 (Installer Detection):** Classifier correctly distinguishes Inno Setup, NSIS, and MSI installer packages with 100% accuracy on test corpus.
4. **EC-P4-04 (Seed Application Verification):** Certified applications (Microsoft Office 2024, AutoCAD 2024, Notepad++) launch without manual configuration.
5. **EC-P4-05 (Unsupported Feature Rejection):** Applications demanding ring-0 drivers trigger clear, informative error dialogs rather than silent crashes.

## 7. Known Risks & Mitigations
- **Risk:** Upstream application update alters executable hash, causing profile lookup miss.
  - *Mitigation:* Implement fuzzy fallback matching on `ProductName` and `OriginalFilename` metadata in `compat.db`.
"""

r6 = r"""# Phase P5: Graphics Subsystem Specification — NebuOS

**Status:** APPROVED  
**Phase:** P5  
**Target Duration:** Sprint 15–17  
**Prerequisite:** Phase P1, P3, P4  

---

## 1. Objective
Integrate the DirectX-to-Vulkan translation layers (DXVK and VKD3D-Proton), multi-GPU dynamic routing (PRIME offload), and the centralized shader caching engine. P5 enables hardware-accelerated 3D rendering for CAD software, video editing suites, and modern games with >= 90% of native Windows performance.

## 2. Scope (What's IN)
- Packaging and version pinning of DXVK (2.3+) and VKD3D-Proton (2.12+).
- Automated DLL override injection (`d3d9`, `d3d11`, `dxgi`, `d3d12`) into application prefixes.
- GPU detection CLI and library `crates/nebu-gpu-probe`.
- Dynamic PRIME multi-GPU offload (desktop on iGPU, 3D on dGPU).
- Centralized shader state caching (`~/.cache/nebu/shaders/<app_id>/`).
- Per-application `dxvk.conf` tuning generation.

## 3. Anti-Scope (What's NOT IN)
- NO recompilation or source-level forks of DXVK/VKD3D.
- NO DirectX 12 emulation on pre-Vulkan 1.3 hardware (OpenGL WineD3D fallback used).
- NO proprietary SLI/Crossfire multi-GPU rendering.

## 4. Dependencies
- Mesa Drivers >= 24.0 (RADV, ANV, NVK).
- Vulkan Loader >= 1.3.275.
- DXVK and VKD3D-Proton release binaries.

## 5. Deliverables
- Binary Stores: `/usr/lib/nebu/graphics/{dxvk,vkd3d-proton}/`.
- CLI: `/usr/bin/nebu-gpu-probe`.
- System Cache Directory: `/usr/share/nebu/preseeded-caches/`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P5-01 (D3D11 Parity Gate):** Direct3D 11 benchmark (Heaven / Valley) achieves >= 90% of bare-metal Windows framerate on identical hardware.
2. **EC-P5-02 (D3D12 Vulkan Execution):** Direct3D 12 benchmark initializes and renders cleanly via VKD3D-Proton with zero Vulkan validation errors.
3. **EC-P5-03 (PRIME Offload Routing):** Setting `gpu_preference: "discrete"` routes rendering to discrete GPU node while compositing scanout remains on primary display.
4. **EC-P5-04 (Shader Cache Deduplication):** Subsequent application runs exhibit zero shader compilation stutters (99th percentile frame time <= 16.6ms).
5. **EC-P5-05 (Idle Power Gate):** Discrete GPU enters PCIe D3Cold state (0 Watts) when no 3D applications are active.

## 7. Known Risks & Mitigations
- **Risk:** Shader compilation hitching during initial application run.
  - *Mitigation:* Enable `dxvk.enableAsync = true` and utilize persistent state caching (`DXVK_STATE_CACHE=1`).
"""

r7 = r"""# Phase P6: Applications Subsystem Specification — NebuOS

**Status:** APPROVED  
**Phase:** P6  
**Target Duration:** Sprint 18–20  
**Prerequisite:** Phase P2, P3, P4, P5  

---

## 1. Objective
Implement the user-facing application installer wizard, desktop registration engine, FreeDesktop MIME associations, 100% clean uninstallation agent, and the Nebu Software Center dual-catalog store. P6 ensures end-users can discover, install, manage, and remove both native Linux and Windows applications effortlessly.

## 2. Scope (What's IN)
- Native installer wizard GUI `crates/nebu-installer-ui`.
- Software Center dual-catalog store `crates/nebu-software-center` (Flatpak + Windows Recipes).
- Application registration: PE `.rsrc` icon extraction (PNG), FreeDesktop `.desktop` entry generation.
- Filesystem mapping: bidirectional path translation (`nebu-path`), `C:` drive mapping, sanitized `Z:` drive.
- Shared MIME database management (`update-mime-database`, `mimeapps.list`).
- Deterministic 100% clean uninstallation agent.

## 3. Anti-Scope (What's NOT IN)
- NO webview / Electron store UI.
- NO hosting proprietary Windows binaries on NebuOS servers (uses declarative recipes).
- NO payment processing inside the software store.

## 4. Dependencies
- Slint / Iced GUI frameworks.
- `libflatpak` >= 1.14.
- `pelite`, `image` Rust crates.

## 5. Deliverables
- GUI Binaries: `/usr/bin/nebu-installer-ui`, `/usr/bin/nebu-software-center`.
- App Registry DB: `~/.local/share/nebu/apps.db`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P6-01 (Installer Interception):** Double-clicking `setup.exe` opens `nebu-installer-ui` wizard; completed setup generates desktop shortcut with high-resolution icon in <= 2.0s.
2. **EC-P6-02 (MIME Association):** Double-clicking `.docx` or `.dwg` file launches associated application with translated POSIX path argument.
3. **EC-P6-03 (Clean Uninstall):** Clicking Uninstall in Software Center purges prefix, removes `.desktop` file, unregisters MIME types, and frees disk space in <= 500ms.
4. **EC-P6-04 (Store Responsiveness):** Software Center starts up in <= 350ms and searches 5,000 catalog applications in <= 10ms.
5. **EC-P6-05 (Recipe Installation):** Automated Windows recipe installs target application unattended using silent flags (`/S`).

## 7. Known Risks & Mitigations
- **Risk:** Multi-part installers fail to discover secondary disk files inside sandbox.
  - *Mitigation:* Installer wizard automatically binds parent download directory as read-only volume.
"""

r8 = r"""# Phase P7: Testing Subsystem Specification — NebuOS

**Status:** APPROVED  
**Phase:** P7  
**Target Duration:** Sprint 21–23  
**Prerequisite:** Phase P0–P6  

---

## 1. Objective
Establish the automated Compatibility Test Lab, regression harness, and hardware validation matrix. P7 automates the continuous testing of the top 50 certified Windows applications and native Linux packages across three physical hardware tiers, executing the 11-stage compatibility invariant unattended.

## 2. Scope (What's IN)
- Rust Test Runner: `crates/nebu-test-harness`, `/usr/bin/nebu-test-runner`.
- 11-stage compatibility verification invariant automation (`INSTALL -> LAUNCH -> ... -> REOPEN`).
- Headless Wayland frame capture and perceptual image hashing (SSIM >= 0.98).
- Virtual input injection via `ydotool`.
- Physical Hardware Test Matrix:
  - Tier 0: Low-End (Intel Celeron, 4GB RAM, Intel UHD iGPU).
  - Tier 1: Mid-Tier (AMD Ryzen 5, 16GB RAM, Radeon iGPU).
  - Tier 2: High-End (Intel Core i7 / AMD Ryzen 7, 32GB RAM, NVIDIA RTX dGPU).
- Continuous CI regression reporting dashboard.

## 3. Anti-Scope (What's NOT IN)
- NO manual QA test passes for standard builds (100% automated).
- NO testing of unsupported applications requiring kernel drivers.

## 4. Dependencies
- Compatibility Lab physical test farm.
- `ydotool`, OpenCV / perceptual hashing libraries.
- Headless virtual display drivers (`vkms`).

## 5. Deliverables
- Test Harness: `/usr/bin/nebu-test-runner`.
- Automated Test Scripts: `tests/compat_suite/*.json`.
- Test Reporting Dashboard: `https://qa.nebuos.org`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P7-01 (Automated Lab Throughput):** Test harness executes complete 50-application test matrix unattended in <= 3.0 hours across all 3 hardware tiers.
2. **EC-P7-02 (Compatibility Pass Rate):** Tier 1 certified applications achieve 100% pass rate across all 11 invariant stages.
3. **EC-P7-03 (Flakiness Rate):** Re-running identical test runs produces < 0.5% variance in test results.
4. **EC-P7-04 (Memory Leak Detection):** 48-hour continuous loop execution reveals zero cumulative memory growth in core daemons.
5. **EC-P7-05 (Automated Regression Gating):** Intentionally broken compatibility profile is caught and rejected by gating pipeline.

## 7. Known Risks & Mitigations
- **Risk:** Minor UI popups in Windows applications cause synthetic input tests to desynchronize.
  - *Mitigation:* Implement visual template matching before dispatching keypresses and clicks.
"""

r9 = r"""# Phase P8: Production Validation Specification — NebuOS

**Status:** APPROVED  
**Phase:** P8  
**Target Duration:** Sprint 24–26  
**Prerequisite:** Phase P0–P7  

---

## 1. Objective
Final production hardening, low-end 4GB RAM budget certification, security audit, atomic update/rollback verification, and release engineering for General Availability (GA) of NebuOS 1.0.

## 2. Scope (What's IN)
- Production binary hardening: Link-Time Optimization (LTO), CFI, stack-clash protection, symbol stripping.
- SELinux enforcing policy validation across all userland daemons and containers.
- Low-End 4GB RAM Mode tuning: zRAM (zstd), `systemd-oomd` PSI thresholds, cache trimming.
- Comprehensive third-party security penetration audit.
- Full atomic OS image upgrade and automated GRUB rollback verification.
- Production ISO installer generation (`nebuos-1.0.0-x86_64.iso`).
- GA Release Certification sign-off.

## 3. Anti-Scope (What's NOT IN)
- NO new architectural features or unproven dependencies added during P8.
- NO post-1.0 experimental features (deferred to Future Phases).

## 4. Dependencies
- All prior phases (P0 through P7).
- Independent security audit firm.
- Cosign production release signing keys.

## 5. Deliverables
- Bootable ISO: `nebuos-1.0.0-x86_64.iso`.
- Signed Container Image: `quay.io/nebuos/base:1.0.0`.
- Release Documentation, User Manual, and Release Notes.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P8-01 (Idle RAM Constraint):** System boots on a physical 4GB RAM machine to an idle graphical desktop with <= 680 MB total RAM consumption (well under the 800 MB limit).
2. **EC-P8-02 (Cold Boot SLA):** Cold boot from UEFI to interactive desktop <= 6.5s on SATA SSD, <= 4.0s on NVMe.
3. **EC-P8-03 (Zero Critical CVEs):** Trivy / Grype vulnerability scan of production base image reports 0 Critical and 0 High vulnerabilities.
4. **EC-P8-04 (Atomic Rollback Validation):** Hard reboot during image upgrade recovers previous working deployment in <= 12s with zero data corruption in `/home`.
5. **EC-P8-05 (Formal Sign-off):** Principal Systems Architect, Security Lead, and Product Lead sign off on GA release certification.

## 7. Known Risks & Mitigations
- **Risk:** Edge-case hardware quirks discovered during broad beta distribution.
  - *Mitigation:* Rapid Hotfix channel infrastructure enables shipping targeted kernel/profile fixes in < 24 hours.
"""

r10 = r"""# Future Phases Specification — NebuOS

**Status:** PROPOSED  
**Target:** Post-1.0 Milestones (P9+)  

---

## 1. Objective
Establish the strategic engineering roadmap and technical exploration pathways for NebuOS following the 1.0 General Availability release.

## 2. Post-1.0 Phase Roadmap

### Phase P9: ARM64 (AArch64) Architecture Support
- **Scope:** Porting NebuOS base image and native Rust daemons to 64-bit ARM architectures (Apple Silicon Macs via Asahi Linux, Snapdragon X Elite laptops, Raspberry Pi 5).
- **Compatibility Engine:** Integration of FEX-Emu or Box64 binary translation layers to execute x86_64 Windows PE binaries on ARM64 processors.
- **Challenges:** Page size discrepancies (4KB vs 16KB on Apple Silicon), translation memory overhead, SIMD translation latency.

### Phase P10: Enterprise Central Management & Directory Integration
- **Scope:** Fleet management, remote image provisioning, and centralized configuration policies.
- **Features:**
  - FreeIPA / Active Directory domain join for single-sign-on (SSO).
  - Remote compatibility database sync and enterprise-internal profile repositories.
  - Centralized software whitelist/blacklist policy enforcement.

### Phase P11: Advanced Gaming & VR Subsystem
- **Scope:** Enhanced gaming performance and virtual reality headset integration.
- **Features:**
  - Native OpenXR / Monado runtime integration for Windows VR titles.
  - Latency reduction through frame generation (FSR 3 / XeSS frame interpolation).
  - Advanced per-game GPU overclocking and fan curve management.

### Phase P12: NebuCloud Hybrid Workspace Sync
- **Scope:** Seamless, end-to-end encrypted backup and synchronization of application prefixes across devices.
- **Features:**
  - Incremental Btrfs send/receive delta sync to private user cloud storage.
  - Seamless desktop state resumption across desktop PC and laptop.

## 3. Guiding Principles for Future Phases
- Never compromise the core invariants: No VMs, lightweight performance, memory safety, and immutable base OS.
- All future features must continue to respect the 4GB RAM baseline constraints.
"""

write_file("/root/NebuOS/docs/roadmap/01-p0-foundation.md", r1)
write_file("/root/NebuOS/docs/roadmap/02-p1-compositor.md", r2)
write_file("/root/NebuOS/docs/roadmap/03-p2-shell.md", r3)
write_file("/root/NebuOS/docs/roadmap/04-p3-runtime.md", r4)
write_file("/root/NebuOS/docs/roadmap/05-p4-compatibility.md", r5)
write_file("/root/NebuOS/docs/roadmap/06-p5-graphics.md", r6)
write_file("/root/NebuOS/docs/roadmap/07-p6-applications.md", r7)
write_file("/root/NebuOS/docs/roadmap/08-p7-testing.md", r8)
write_file("/root/NebuOS/docs/roadmap/09-p8-production-validation.md", r9)
write_file("/root/NebuOS/docs/roadmap/10-future-phases.md", r10)

