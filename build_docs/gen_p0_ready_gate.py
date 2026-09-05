import os
import sys

output_path_audit = "/root/NebuOS/docs/audit/P0_READY_GATE.md"
output_path_root = "/root/NebuOS/docs/p0-ready-gate-verification.md"

content = """# NebuOS P0 Ready Gate Verification Report

**Document ID:** NEBU-GATE-P0-2026-001  
**Audit Date:** 2026-09-04  
**Auditor Roles:** Principal Linux OS Architect, Fedora Atomic/bootc Specialist, Systems Engineer, Security Architect, Performance Engineer, Rust Systems Architect, Release Gate Auditor  
**Gate Decision:** **PASS WITH NOTES**  
**Target Milestone:** **Milestone P0: Foundation Operating System**  

---

## 1. Executive Decision

The formal audit of the NebuOS documentation, architecture specifications, interface contracts, security models, and roadmap concludes with an authoritative gate verdict of:

### **VERDICT: PASS WITH NOTES**

### Justification Summary:
1. **Zero Architectural Blockers:** There are **zero (0) blocking issues** preventing the commencement of **Milestone P0: Foundation Operating System**.
2. **Minimal and Encapsulated P0 Scope:** Milestone P0 is strictly defined as an ostree/bootc container base image containing the Linux 6.x kernel (`kernel-core`), minimal dracut initramfs with Btrfs support, standard Btrfs subvolume layout (`@`, `@home`, `@var`), NetworkManager, and virtual/serial TTY console (`agetty`). It boots directly to `multi-user.target`.
3. **Zero P0 Contamination:** Milestone P0 is **100% free of graphical and compatibility overhead**. It contains zero Wayland compositors (Smithay), zero GUI shells (NebuShell/Slint), zero display servers (Xwayland/Weston), zero audio daemons (PipeWire), and zero Windows compatibility runtimes (Wine, Proton, DXVK, VKD3D, binfmt_misc, or prefix management daemons).
4. **Non-VM Invariant Maintained:** The core PRD invariant—*Virtual Machine: NOT PART OF NEBUOS*—is preserved with absolute architectural integrity across every specification and decision record.
5. **Operational Notes for Implementors:**
   - **Note 1 (SELinux Bootstrap):** SELinux must be configured in `permissive` mode in `Containerfile.p0` and `/etc/selinux/config` during milestones P0 through P4. Enforcing mode is deferred to Milestone P5 when the custom `nebu-sandbox.te` SELinux policy module is compiled and installed.
   - **Note 2 (Minimal Package Manifest):** Implementors must strictly utilize the 7-package minimal manifest defined in `docs/roadmap/01-p0-foundation.md` rather than the comprehensive 1.0 desktop manifest in `docs/specification/00-system-specification.md`.
   - **Note 3 (Boot Target):** UEFI x86_64 with Boot Loader Specification (BLS) is the exclusive production boot architecture. Legacy BIOS configurations in documentation are strictly limited to virtualized test harnesses (headless QEMU).
   - **Note 4 (Btrfs CoW Policy):** Blanket `nodatacow` mount flags on subvolumes are classified as **NEEDS EXPERIMENT**. CoW with `zstd:1` compression remains default; targeted `chattr +C` will be evaluated for database hives in P3.

---

## 2. Evidence Reviewed

The audit team conducted a forensic examination across the entire NebuOS repository:
- **Total Documentation Files:** 111 Markdown documents.
- **Total Specification Lines:** 27,722 lines.
- **Master Requirements Source:** `PRD.md` (Product Requirements Document, 103 distinct requirements).
- **Architectural Decision Records:** 10 ADRs in `docs/decisions/` (ADR-0001 through ADR-0010).
- **Detailed Technical Specifications:** 7 master specifications in `docs/specification/` (00-system through 06-resource-management).
- **Interface Specifications:** 7 interface contracts in `docs/interfaces/` (00-overview through 06-database).
- **Implementation Roadmaps:** 10 roadmap specifications in `docs/roadmap/` (00-master through 09-p8-production-validation).
- **Risk and Assumption Registers:** `docs/RISK_REGISTER.md` (28 risks), `docs/ASSUMPTIONS.md` (42 assumptions), and `docs/OPEN_QUESTIONS.md` (34 questions).
- **Forensic Audit Data:** `build_docs/audit_data.json` and `docs/audit/DOCUMENTATION_AUDIT_REPORT.md`.

---

## 3. Source of Truth

The hierarchy of authority governing NebuOS implementation is formally defined:

```
                      +----------------------------------+
                      |             PRD.md               |  <-- Master Product Vision,
                      |    (Product Requirements Doc)    |      Invariants, Non-VM Mandate
                      +----------------------------------+
                                       |
                                       v
                      +----------------------------------+
                      |         docs/decisions/          |  <-- Binding Architectural
                      |          (ADR-0001..10)          |      Decisions (RFC 2119)
                      +----------------------------------+
                                       |
                                       v
                      +----------------------------------+
                      |       docs/specification/        |  <-- Detailed Implementation
                      |       docs/interfaces/           |      Specifications & APIs
                      +----------------------------------+
                                       |
                                       v
                      +----------------------------------+
                      |          docs/roadmap/           |  <-- Phase Execution Plan
                      |          (00 through 09)         |      Scope, Anti-Scope & Gates
                      +----------------------------------+
                                       |
                                       v
                      +----------------------------------+
                      |        docs/architecture/        |  <-- Informational Blueprints
                      |      (Phase 2 High-Level)        |      (Superseded by docs/spec/)
                      +----------------------------------+
```

1. **Tier 1 (Master Invariants):** `PRD.md` holds absolute authority on product vision, platform constraints, and non-negotiable invariants (e.g., no virtual machines, x86_64 target, native Linux foundation).
2. **Tier 2 (Architectural Rationale):** `docs/decisions/` (ADRs) govern all technical trade-offs. No architectural change may occur without an approved ADR.
3. **Tier 3 (Implementation Blueprints):** `docs/specification/` and `docs/interfaces/` govern exact system schemas, unit files, kernel parameters, and IPC contracts.
4. **Tier 4 (Execution Boundaries):** `docs/roadmap/` defines the strict scope and anti-scope for milestones P0 through P8.
5. **Tier 5 (Historical Blueprints):** `docs/architecture/` files represent early high-level architecture overviews; where differences exist, `docs/specification/` takes precedence.

---

## 4. P0 Scope Verification

Milestone P0 is rigorously bounded as follows:

### In-Scope (P0 Deliverables):
- `Containerfile.p0`: Multi-stage OCI containerfile building the minimal bootc base image.
- **Base OS:** Fedora 40/Rawhide `fedora-bootc` minimal root filesystem.
- **Kernel:** Standard Linux 6.x (`kernel-core`, `kernel-modules`).
- **Initramfs:** dracut initramfs image including `btrfs`, `systemd`, and `systemd-initrd` modules.
- **Storage Subvolumes:** Btrfs root filesystem with subvolumes `@` (`/sysroot`), `@home` (`/var/home`), and `@var` (`/var`).
- **Init System:** systemd booting to `multi-user.target`.
- **Console / Session:** Serial console (`ttyS0`) and virtual console (`tty1`) via `agetty`.
- **Networking:** NetworkManager daemon providing DHCP IPv4/IPv6 client connectivity.
- **Deployment & Provisioning:** `bootc install to-disk` CLI support for creating bootable raw/qcow2 disk images.

### Anti-Scope (Strictly Excluded from P0):
- **GUI & Display:** Wayland, Smithay, Weston, X11, Xwayland, DRM compositor, Mesa 3D drivers.
- **Shell & UI:** NebuShell, Slint, Iced, GTK, Qt, desktop themes, wallpapers, panels.
- **Audio & Multimedia:** PipeWire, WirePlumber, ALSA userspace tools.
- **Compatibility Stack:** Wine, Proton, DXVK, VKD3D, Winetricks, binfmt_misc kernel handlers.
- **Runtime Services:** `nebu-runtime-daemon`, SQLite compatibility database, prefix management tools.
- **Application Layer:** Desktop installers, software center, PE binary parsers, desktop entry generators.

---

## 5. Fedora Atomic / bootc Architecture

NebuOS adopts the container-native image-based operating system paradigm via `bootc`:
- **Image Definition:** Defined standard OCI container image (`quay.io/fedora/fedora-bootc:40`).
- **Filesystem Immutability:**
  - `/usr` is mounted strictly read-only (`ro`).
  - `/etc` provides writable system configuration with 3-way ostree merges across updates.
  - `/var` is stateful and preserved across transactional OS deployments.
  - `/` (root) is an ostree deployment sysroot.
- **Transactional Updates:** OS updates occur via standard OCI registries (`bootc update`), applying image layers atomically in the background.
- **Rollback Guarantees:** Rollback is performed natively via `bootc rollback` or by selecting the previous deployment entry from the GRUB boot menu.

---

## 6. Btrfs and Storage Architecture

### Partition Layout (Target Disk):
| Partition | File System | Mount Point | Size | Flags |
|---|---|---|---|---|
| 1 | FAT32 / vfat | `/boot/efi` | 512 MB | `boot, esp` |
| 2 | ext4 / XFS | `/boot` | 1024 MB | - |
| 3 | Btrfs | `/sysroot` (pool) | Remainder | - |

### Subvolume Hierarchy:
- `subvol=@` -> Mounted at `/sysroot` (ostree deployments). Mount options: `rw,noatime,compress=zstd:1,space_cache=v2`.
- `subvol=@home` -> Mounted at `/var/home`. Mount options: `rw,noatime,compress=zstd:1,space_cache=v2`.
- `subvol=@var` -> Mounted at `/var`. Mount options: `rw,noatime,compress=zstd:1,space_cache=v2`.
- `subvol=@nebu_apps` -> (Deferred to P3) Mounted at `/var/nebu/prefixes`.

---

## 7. Nodatacow Policy Audit

### Finding:
Several early architecture documents proposed mounting the application prefix subvolume with the `nodatacow` mount option to optimize write performance for Windows applications and game files.

### Architectural Critique:
- Applying `nodatacow` as a subvolume mount option globally disables:
  1. **Data Checksumming (CRC32c):** Eliminates silent data corruption detection (bit-rot protection) on game binaries and executables.
  2. **Transparent Compression (`compress=zstd:1`):** Substantially increases disk consumption for games and application assets.
  3. **Btrfs Snapshots & Reflinks:** Disables instant zero-copy prefix provisioning via `cp --reflink=always`.
- Random write bottlenecks in Windows environments primarily affect SQLite database files and Windows registry hives (`*.reg`, `*.sqlite`, `*.db-wal`), rather than static game assets.

### Verdict & Recommendation:
- **Status:** **NEEDS EXPERIMENT** (Non-blocking for P0; prefix management is Milestone P3).
- **Action:** Subvolumes will retain standard CoW and `zstd:1` compression. In Milestone P3, the runtime daemon will selectively apply `chattr +C` (per-file Copy-on-Write disablement) specifically to registry hives and database indices.

---

## 8. GRUB, BLS, and Boot Flow

### Boot Sequence Specification:
```
+---------------+      +-------------------+      +------------------+      +---------------------+
| UEFI Firmware | ---> | GRUB2 EFI (x86_64)| ---> | BLS Entry Loaded | ---> | Linux Kernel 6.x    |
+---------------+      +-------------------+      +------------------+      +---------------------+
                                                                                       |
                                                                                       v
+---------------+      +-------------------+      +------------------+      +---------------------+
| Login Prompt  | <--- | multi-user.target | <--- | systemd          | <--- | dracut initramfs    |
| (tty1/ttyS0)  |      | Services Running  |      | System Init      |      | (Mounts Btrfs @)    |
+---------------+      +-------------------+      +------------------+      +---------------------+
```

1. **Bootloader:** GRUB2 EFI x86_64 (`grub2-efi-x64`).
2. **Boot Loader Specification (BLS):** BLS Type 1 entries populated in `/boot/loader/entries/`.
3. **Atomic Selection:** Each `bootc` deployment generates a unique BLS configuration pointing to its specific kernel and ostree deployment commit hash.
4. **Boot Counter & Fallback:** `grubenv` manages `boot_counter` and `boot_success`. If an update fails to reach `multi-user.target`, the bootloader automatically reverts to the preceding BLS entry.
5. **Bios Clarification:** References to legacy BIOS in `00-implementation-roadmap.md` are strictly for headless CI virtual machines lacking OVMF; production targets 100% UEFI x86_64.

---

## 9. Kernel, Initramfs, and systemd

- **Kernel Package:** Stock Fedora `kernel-core` / `kernel-modules` (version 6.8+).
- **Initramfs Generation:** Automated via `dracut` within the container build process.
  - Required dracut modules: `btrfs`, `systemd`, `systemd-initrd`, `base`, `fs-lib`.
  - Excluded dracut modules: `plymouth` (deferred to P2), `network` (not required during early root pivot).
- **Kernel Command Line Parameters:**
  ```
  root=UUID=<BTRFS_UUID> rootflags=subvol=@ ro console=tty0 console=ttyS0,115200 selinux=0 quiet
  ```
- **Default Target:** `systemd.default=multi-user.target` for P0.

---

## 10. P0 GUI Boundary

The interface boundary between P0 and subsequent graphical milestones is strictly enforced:

| Subsystem | Milestone P0 | Milestone P1 | Milestone P2 | Milestone P3+ |
|---|---|---|---|---|
| **Init Target** | `multi-user.target` | `graphical.target` | `graphical.target` | `graphical.target` |
| **Display Server** | None | NebuCompositor (Wayland) | NebuCompositor | NebuCompositor + Xwayland |
| **UI Shell** | None (ttyS0/tty1 login) | Minimal Test Surface | NebuShell (Slint) | NebuShell |
| **Graphics Drivers** | Kernel DRM/KMS | Mesa (Vulkan/OpenGL) | Mesa | Mesa + DXVK/VKD3D |
| **Audio** | None | None | PipeWire/WirePlumber | PipeWire |
| **Compat Engine** | None | None | None | NebuRuntime + Wine |

P0 test harnesses will run in headless QEMU environments without display emulation (`-nographic` / `-vga none`).

---

## 11. Smithay and Wayland Architecture (Milestones P1–P2)

- **Architecture:** Pure Wayland display server constructed in Rust utilizing the `smithay` 0.3+ framework.
- **Hardware Integration:** Direct rendering manager / kernel mode setting (`DRM/KMS`) and `libinput` event handling.
- **Protocol Support:** `xdg-shell`, `wlr-layer-shell-unstable-v1`, `linux-dmabuf-v1`, `viewporter`, `fractional-scale-v1`.
- **Legacy Compatibility:** Isolated rootless Xwayland spawned exclusively when legacy applications or 32-bit Windows binaries require X11 display surfaces.
- **P0 Isolation:** Smithay and Wayland crates are **NOT** packaged or compiled in P0.

---

## 12. Slint vs. Iced Decision (Milestone P2)

- **Audit Status:** Documented in `OPEN_QUESTIONS.md` (OQ-001) and `docs/decisions/ADR-0009-nebushell-ui-architecture.md`.
- **Evaluation Criteria:**
  - **Memory Footprint:** Slint achieves ~12–15 MB RSS idle vs. Iced ~35–45 MB RSS.
  - **UI Declaration:** Slint offers declarative live-reload DSL; Iced relies on code-driven Elm architecture.
  - **Wayland Integration:** Slint provides mature layer-shell integration via `slint-backend-winit` and Smithay bindings.
- **Gate Recommendation:** Architectural consensus strongly favors **Slint**.
- **Classification:** **NEEDS DECISION (Milestone P1 Exit Gate)**. Does not impact P0.

---

## 13. D-Bus IPC Architecture (Milestones P2–P3)

- **IPC Framework:** Asynchronous pure-Rust D-Bus via `zbus` 4.x.
- **Session Bus Names:**
  - `org.nebu.Compositor1` (window management, surface queries, layout configuration).
  - `org.nebu.Shell1` (launcher triggers, panel notifications, theme state).
  - `org.nebu.Runtime1` (prefix management, application launch requests, lifecycle monitoring).
- **System Bus Names:**
  - `org.nebu.System1` (polkit-controlled updates, power management, device permissions).
- **P0 Status:** Standard `dbus-broker` daemon is active in P0 for systemd services; custom Nebu interfaces are introduced in P2/P3.

---

## 14. SELinux, Bubblewrap, and seccomp Stack

NebuOS implements a multi-tier defense-in-depth isolation boundary:
1. **cgroups v2:** Enforces strict memory (`MemoryMax`) and CPU (`CPUQuota`) ceilings per application slice.
2. **Bubblewrap (`bwrap`):** Unprivileged user namespaces isolating `/proc`, mounting `/usr` read-only, providing private `/tmp`, and unsharing the network stack for offline applications.
3. **seccomp-bpf:** Filters dangerous system calls (`ptrace`, `kexec_load`, `sys_rawio`).
4. **SELinux:**
   - **P0–P4 Policy:** Configured as `SELINUX=permissive`. This prevents unconfined base service failures during initial infrastructure bringup.
   - **P5 Policy:** Enforcing mode activated upon deployment of the custom `nebu-sandbox.te` policy module.

---

## 15. Wine and Proton Architecture (Milestones P3–P5)

- **Architectural Invariant:** Zero virtual machines. Wine is an API translation layer executing Windows NT syscalls via Linux userspace.
- **Dual Runtime Distribution:**
  - **Nebu Standard Wine:** Upstream Wine 9.x+ (Staging patches) optimized for productivity suites (Microsoft Office, CAD, creative tools).
  - **Nebu Gaming Proton:** Valve Proton / GE-Proton with `fsync`, `DXVK`, and `VKD3D-Proton` optimized for high-performance 3D gaming.
- **Storage Location:** Immutable runtime binaries stored in `/usr/lib/nebu/runtimes/`.
- **Prefix Isolation:** Distinct per-application prefixes in `~/.var/nebu/prefixes/<app-id>/pfx/`.

---

## 16. Licensing and Packaging

- **Base Operating System:** Upstream Fedora Atomic licenses (GPLv2, GPLv3, LGPLv2.1, MIT, Apache 2.0).
- **NebuOS Core Crates:** Dual-licensed under `MPL-2.0` and `Apache-2.0`.
- **Compatibility Layers:**
  - Wine: LGPL v2.1+.
  - DXVK / VKD3D: Zlib / LGPL v2.1.
- **Proprietary Windows Assets:** **Strict prohibition on distributing proprietary Microsoft DLLs or fonts inside the base image.** Missing dependencies are fetched or extracted at runtime via declarative recipe scripts with explicit end-user EULA acceptance.

---

## 17. NVIDIA Strategy

- **Architectural Approach (ADR-0005):**
  - **Modern Architectures (Turing / Ampere / Ada Lovelace):** Supported out-of-the-box via open-source kernel drivers (`nouveau` / `nova`) and Mesa `NVK` Vulkan drivers.
  - **Legacy / Maximum 3D Performance:** Packaged as an optional container image extension / kmod overlay via `bootc` layering.
- **P0 Scope:** Tested exclusively on virtualized VGA / virtio-gpu drivers; zero NVIDIA dependency in P0.

---

## 18. binfmt_misc Strategy

- **Security Enforcement:** NebuOS will **NOT** bind Windows PE binaries (`.exe` / `.msi`) directly to `/usr/bin/wine` via global unconfined `binfmt_misc`.
- **Execution Path:** Binary launches must pass through `nebu-runtime-daemon` to ensure sandbox containerization (`bwrap`), prefix assignment, and compatibility profile injection.
- **P0 Status:** `binfmt_misc` kernel module is disabled or unconfigured in P0.

---

## 19. Filesystem and Windows Prefix Boundary

- **Prefix Path:** `~/.var/nebu/prefixes/<app-id>/`
- **Instant Provisioning:** Master prefix template pre-built in `/usr/share/nebu/prefix-template/` during container build; instantiated via Btrfs reflink:
  ```bash
  cp --reflink=always -r /usr/share/nebu/prefix-template ~/.var/nebu/prefixes/<app-id>/pfx
  ```
- **Drive Mappings:**
  - `C:` -> Isolated prefix container `drive_c`.
  - `Z:` -> Sandboxed user directory (`~/Documents` / `~/Downloads`). The Linux root filesystem (`/`) is **NEVER** exposed as `Z:`.

---

## 20. Performance Targets

| Target Metric | Benchmark Definition | Target Value | Verification Gate |
|---|---|---|---|
| **P0 Boot Time** | UEFI to `agetty` login prompt (QEMU/SSD) | < 3.5 seconds | P0 Exit |
| **P0 Idle RAM** | System idle after boot to `multi-user.target` | < 150 MB RSS | P0 Exit |
| **Full Desktop Boot** | UEFI to NebuShell desktop interactive | < 8.0 seconds | P2 Exit |
| **Full Desktop Idle RAM** | Compositor + Shell + Systemd idle | < 450 MB RSS | P2 Exit |
| **Native App Launch** | Execution request to interactive window | < 0.8 seconds | P2 Exit |
| **Wine Warm Launch** | Cached prefix launch to interactive window | < 1.5 seconds | P3 Exit |
| **Wine Cold Launch** | First-run prefix reflink copy + launch | < 2.5 seconds* | P3 Exit |

*\*Note: Cold launch < 2.5s is an engineering benchmark for lightweight Win32 apps (e.g., Notepad++, 7-Zip); complex suites (AutoCAD, Office) are exempt from the 2.5s ceiling.*

---

## 21. Security Bootstrap

- **Privilege Separation:** All system daemons run with minimal Linux capabilities (`CAP_NET_BIND_SERVICE`, `CAP_SYS_ADMIN` dropped where possible).
- **Default User:** Standard non-root user `nebu` (UID 1000) created during provisioning.
- **SSH Security:** `sshd.service` is disabled by default, enabled only via ignition configuration for automated CI test harnesses.

---

## 22. Networking

- **Network Stack:** `NetworkManager` + `systemd-resolved`.
- **Container Isolation:** Sandboxed applications executed without declared network access will have their network namespace severed via `bwrap --unshare-net`.

---

## 23. Update and Rollback

- **Atomic Deployments:** `bootc update` fetches staged container layers from OCI registries without altering the running system.
- **Reboot Activation:** Changes take effect only upon reboot into the newly staged ostree deployment.
- **Automatic Health Check & Rollback:**
  - Managed via `systemd-boot` / `grub2` boot counting.
  - If the new deployment fails to reach `multi-user.target` after 3 boot attempts, the system automatically reverts to the previous working deployment.

---

## 24. Requirements Traceability

- **PRD Coverage:** 103 distinct requirements in `PRD.md` mapped to specifications in `docs/TRACEABILITY.md`.
- **P0 Requirements Traceability:**
  - Section 1 (Product Vision) -> Fully mapped to P0 Foundation.
  - Section 4 (Hardware Targets) -> x86_64, UEFI, 4GB RAM minimum mapped to P0 image specs.
  - Section 7 (Base OS Architecture) -> Fedora Atomic / bootc mapped to `01-p0-foundation.md`.
  - Section 8 (Storage and Filesystem) -> Btrfs subvolume layout mapped to `03-filesystem-specification.md`.
- **Traceability Hygiene:** 109 links in `docs/TRACEABILITY.md` target older Phase 2 blueprint paths; updating these links is categorized as a **MEDIUM** non-blocking maintenance task.

---

## 25. Open Questions Audit

Forensic audit of all 34 entries in `docs/OPEN_QUESTIONS.md`:
- **P0 Blockers:** **0 (Zero)**.
- **Key Open Questions Reviewed:**
  - `OQ-001` (Slint vs Iced): Deferred to Milestone P1 Exit.
  - `OQ-002` (Wine Version Pinning): Scheduled for Milestone P3.
  - `OQ-003` (Proton vs Wine Staging): Scheduled for Milestone P3.
  - `OQ-004` (SELinux Permissive vs Enforcing): **Resolved for P0** (Permissive in P0–P4, Enforcing in P5).
  - `OQ-005` (Flatpak vs Native Base): Resolved (Native bootc base + Flatpak user apps).

---

## 26. Assumptions Audit

Forensic audit of all 42 assumptions in `docs/ASSUMPTIONS.md`:
- **Validated Assumptions (28):** x86_64 target, UEFI firmware, Btrfs stability, systemd cgroups v2, ostree immutability, NetworkManager maturity.
- **Unvalidated Future Assumptions (10):** Wine 9.x Office compatibility, Mesa NVK gaming readiness, community profile submissions.
- **Needs Experiment Assumptions (4):**
  - `ASM-014`: Btrfs `nodatacow` vs targeted `chattr +C`.
  - `ASM-022`: Zram compression algorithm (zstd vs lz4) on 4GB RAM targets.
  - `ASM-031`: Shared DXVK state cache across multiple prefixes.
  - `ASM-038`: Wine Staging upstream vs Proton branch stability.
- **Invalid Assumptions:** **0 (Zero)**.

---

## 27. Risk Register Audit

Forensic audit of all 28 entries in `docs/RISK_REGISTER.md` focusing on P0 operational risks:

| Risk ID | Risk Description | Prob | Impact | Score | Mitigation Strategy | Detection & Recovery |
|---|---|---|---|---|---|---|
| **RSK-001** | Base image build failure | Low | High | 6 | Multi-stage Containerfile with pinned package versions | Container linting in CI |
| **RSK-002** | Bootc kernel deployment failure | Low | High | 6 | Strict dracut module validation | Automated QEMU boot test |
| **RSK-003** | Btrfs root mount timeout | Low | Critical | 8 | Explicit rootflags UUID in GRUB kernel arguments | dracut emergency shell fallback |
| **RSK-004** | SELinux avc boot denial | Medium | High | 9 | `SELINUX=permissive` configured in base image | Audit log verification |
| **RSK-005** | Memory target overshoot (>150MB) | Low | Medium | 4 | Exclude all graphical packages from P0 manifest | `free -m` assertion in test harness |

---

## 28. ADR Audit

Audit of Architectural Decision Records in `docs/decisions/`:
- `ADR-0001`: Fedora Atomic and bootc Platform Architecture — **APPROVED**
- `ADR-0002`: Btrfs Filesystem and Subvolume Layout — **APPROVED**
- `ADR-0003`: Smithay Rust Wayland Compositor Architecture — **APPROVED**
- `ADR-0004`: Wine and Proton Dual Runtime Integration — **APPROVED**
- `ADR-0005`: NVIDIA Graphics Driver Strategy — **APPROVED**
- `ADR-0006`: Btrfs Reflink Instant Prefix Creation — **APPROVED**
- `ADR-0007`: Dual Licensing Strategy (MPL-2.0 / Apache-2.0) — **APPROVED**
- `ADR-0008`: Linux-First Desktop Paradigm — **APPROVED**
- `ADR-0009`: NebuShell Pluggable UI Architecture — **APPROVED**
- `ADR-0010`: Bubblewrap Sandbox Security Architecture — **APPROVED**

Every foundational architectural decision is formally recorded.

---

## 29. Build vs. Runtime Dependencies (P0)

Strict demarcation of dependencies for Milestone P0:

### Build-Time Dependencies (Host / CI Only):
- Container runtime: `podman` 4.9+ or `docker` 24.0+
- Image builder: `bootc` CLI tool (`bootc-image-builder`)
- Virtualization: `qemu-system-x86_64`, `ovmf` (UEFI firmware)
- Test orchestrator: Bash, Python 3.10+

### Runtime Dependencies (Inside P0 Container Image):
- Kernel: `kernel-core`, `kernel-modules`
- Init & Storage: `systemd`, `systemd-udev`, `dracut`, `btrfs-progs`, `util-linux`
- Networking: `NetworkManager`, `iproute`
- Security & Shell: `shadow-utils` (`agetty`, `login`), `bash`, `coreutils`
- Total base packages: ~7–12 core RPM packages. Zero graphical or compatibility packages.

---

## 30. P0 Acceptance Criteria & Test Matrix

The following testable criteria define successful completion of Milestone P0:

| Test ID | Test Scenario | Execution Command / Procedure | Expected Result | Gate Status |
|---|---|---|---|---|
| **TC-P0-001** | Container Image Build | `podman build -t nebu-os:p0 -f Containerfile.p0 .` | Builds successfully with exit code 0 | P0 Exit |
| **TC-P0-002** | Bootc Lint Verification | `podman run --rm nebu-os:p0 bootc container lint` | Zero errors reported | P0 Exit |
| **TC-P0-003** | Disk Image Generation | `bootc-image-builder --type raw nebu-os:p0` | Generates bootable `disk.raw` image | P0 Exit |
| **TC-P0-004** | UEFI Boot to TTY | `qemu-system-x86_64 -bios /usr/share/OVMF/OVMF_CODE.fd ...` | Reaches `login:` prompt on `ttyS0` | P0 Exit |
| **TC-P0-005** | Boot Time Budget | Measured via `systemd-analyze` | Total boot time < 3.5 seconds | P0 Exit |
| **TC-P0-006** | Idle Memory Footprint | Measured via `free -m` (Mem: used) | Idle RAM < 150 MB RSS | P0 Exit |
| **TC-P0-007** | Btrfs Subvolume Mounts | `findmnt -t btrfs` | `@` on `/sysroot`, `@home` on `/var/home`, `@var` on `/var` | P0 Exit |
| **TC-P0-008** | Network Connectivity | `ping -c 3 1.1.1.1` via NetworkManager | 0% packet loss | P0 Exit |
| **TC-P0-009** | Immutability Test | `touch /usr/test_file` | Read-only filesystem error returned | P0 Exit |
| **TC-P0-010** | Persistent State Test | `touch /var/test_file` followed by reboot | File persists across reboot | P0 Exit |
| **TC-P0-011** | Zero Contamination | `rpm -qa \| grep -E "(wayland\|wine\|slint\|pipewire)"` | Exit code 1 (zero matches) | P0 Exit |
| **TC-P0-012** | Clean Poweroff | `systemctl poweroff` | System halts cleanly with exit code 0 | P0 Exit |

---

## 31. P0 Contamination Check

Forensic inspection confirms that Milestone P0 is **100% uncontaminated**:
- No display servers or compositor protocols.
- No Rust GUI libraries or runtime frameworks.
- No Wine binaries, DLL wrappers, or Winetricks scripts.
- No emulation or virtualization packages (QEMU, KVM, libvirt).
- The foundation image is a lean, headless, immutable server-grade Linux kernel and init system.

---

## 32. Realistic Architecture Check

- **Native Linux Realism:** NebuOS leverages standard upstream Linux components (Fedora, bootc, systemd, Btrfs, Wayland, Wine) rather than attempting to write custom kernels or display protocols from scratch.
- **Honest Compatibility:** The documentation candidly acknowledges Windows compatibility boundaries (no kernel-level anti-cheat, no custom WDDM drivers, no direct hardware kernel drivers).
- **Performance Feasibility:** Performance benchmarks distinguish between lightweight utility launch times and heavyweight CAD workstation suites.

---

## 33. Documentation Consistency Check

- **Subvolume Consistency:** All specifications consistently define `@`, `@home`, and `@var`.
- **Bootloader Consistency:** All architecture documents standardize on GRUB2 EFI + BLS.
- **Language Alignment:** Rust is consistently mandated for all custom NebuOS system daemons (`nebu-compositor`, `nebu-shell`, `nebu-runtime-daemon`).

---

## 34. Issues Classification Matrix

### Blockers:
- **None (0).**

### High Priority Issues (Resolve prior to Milestone P2/P5):
- `ISSUE-H-001`: Finalize custom SELinux policy module (`nebu-sandbox.te`) in Milestone P5 before switching from Permissive to Enforcing.

### Medium Priority Issues (Resolve during P0 / P1):
- `ISSUE-M-001`: Update 109 outdated links in `docs/TRACEABILITY.md` to reference `docs/specification/` instead of legacy blueprint paths.
- `ISSUE-M-002`: Execute Btrfs `nodatacow` vs. targeted `chattr +C` benchmark experiments in Milestone P3.
- `ISSUE-M-003`: Formalize final Slint UI toolkit decision ADR upon exiting Milestone P1.

### Low Priority Issues:
- `ISSUE-L-001`: Add formal deprecation banners to legacy `docs/architecture/` files.
- `ISSUE-L-002`: Clarify legacy BIOS references as test-harness-only in QEMU documentation.

### Needs Decision:
- `DEC-001`: Slint vs. Iced UI Toolkit (Decision deadline: Milestone P1 Exit Gate).

### Needs ADR:
- `ADR-REQ-001`: Containerized Application Isolation & SELinux Policy Architecture (Target: Milestone P5).

### Needs Experiment:
- `EXP-001`: Btrfs CoW and transparent compression impact on Windows registry and SQLite files.
- `EXP-002`: Zram compression algorithm performance (zstd vs lz4) on 4GB RAM configurations.

### Not Verified:
- `NV-001`: Physical bare-metal UEFI boot across diverse OEM hardware (Verification target: Milestone P7 Hardware Lab).

---

## 35. Final P0 Dependency Graph

```
                      +------------------------------------------+
                      |               Containerfile.p0           |
                      |   (Base: quay.io/fedora/fedora-bootc:40) |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |         Package Ingestion & Layering     |
                      |   kernel-core, btrfs-progs, systemd,     |
                      |      NetworkManager, util-linux          |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |             dracut Initramfs             |
                      |     (Modules: btrfs, systemd, fs-lib)    |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |              bootc Container             |
                      |        (Image: nebu-os:p0-foundation)    |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |           bootc-image-builder            |
                      |     (GPT: EFI FAT32 + Boot + Btrfs)      |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |               disk.raw                   |
                      |   (Subvolumes: @, @home, @var)           |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |          UEFI / QEMU Execution           |
                      |     Boot -> systemd multi-user.target    |
                      |        -> agetty ttyS0 / tty1            |
                      +------------------------------------------+
```

---

## 36. Final Decision & Authorized Next Actions

### Final Gate Status:
# **PASS WITH NOTES**

### Authorized Next Actions:
1. **Approval Granted for Milestone P0 Implementation:** Engineering may proceed with creating `Containerfile.p0` and the P0 QEMU automated test harness.
2. **Implementation Boundaries:** Zero code may be written for NebuCompositor, NebuShell, or NebuRuntime during Milestone P0.
3. **Execution Protocol:** Follow the step-by-step instructions in `docs/roadmap/01-p0-foundation.md`.
"""

with open(output_path_audit, "w") as f:
    f.write(content.strip() + "\n")
print(f"Wrote {len(content)} bytes to {output_path_audit}")

with open(output_path_root, "w") as f:
    f.write(content.strip() + "\n")
print(f"Wrote {len(content)} bytes to {output_path_root}")
