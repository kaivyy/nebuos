# NebuOS Engineering Assumptions Register

**Status:** APPROVED  
**Purpose:** Formal documentation, impact analysis, and empirical validation criteria for all foundational assumptions governing NebuOS systems architecture, hardware targets, external dependencies, user personas, and performance budgets.  
**Scope:** Covers 42 technical and operational assumptions across 6 distinct engineering categories.  
**Audience:** Systems Architects, Core Developers, Performance Engineers, and Quality Assurance Leads.

---

## 1. Summary Matrix

| Category | Assumption Range | Total | Primary Governance Subsystem |
|---|---|---|---|
| **Hardware Platform** | ASM-HW-001 to ASM-HW-008 | 8 | Hardware Architecture (`architecture/06-hardware.md`) |
| **Software Stack & Base OS** | ASM-SW-001 to ASM-SW-008 | 8 | System Architecture & Boot (`architecture/01-system-architecture.md`) |
| **Compatibility & Runtime** | ASM-CP-001 to ASM-CP-008 | 8 | Runtime Engine & Wine (`runtime/00-runtime-specification.md`) |
| **User & UX Expectations** | ASM-US-001 to ASM-US-006 | 6 | Desktop Environment & Shell (`desktop/00-desktop-overview.md`) |
| **Deployment & Lifecycle** | ASM-DP-001 to ASM-DP-006 | 6 | Updates & Storage Architecture (`updates/00-update-overview.md`) |
| **Performance & Resources** | ASM-PF-001 to ASM-PF-006 | 6 | Performance Engineering (`performance/00-performance-goals.md`) |

---

## 2. Detailed Assumptions by Category

### 2.1 Hardware Platform Assumptions

| ID | Category | Assumption Statement | Impact if Wrong | Validation Plan |
|---|---|---|---|---|
| **ASM-HW-001** | Hardware | x86_64 is the exclusive initial architecture target; instruction baseline requires SSE4.2 and CMPXCHG16B. | If ARM64 or older x86-64-v1 CPUs must be supported, CPU instruction emulation (FEX-Emu/Box64) is required, degrading performance. | Automated CI test harness checks `/proc/cpuinfo` flags on reference hardware pool in Compatibility Lab. |
| **ASM-HW-002** | Hardware | Target machines support standard UEFI 2.4+ firmware with GPT partitioning; legacy BIOS (CSM) is deprecated. | Legacy MBR/BIOS booting would require maintaining dual GRUB stages and MBR partition tables, increasing installer complexity. | Verify UEFI boot path on 10 bare-metal test benches in Compatibility Lab. |
| **ASM-HW-003** | Hardware | Baseline target hardware has a minimum of 4.0 GB physical RAM. | Running on 2.0 GB systems would cause constant ZRAM thrashing and prevent running any 64-bit Windows productivity suites. | Continuous memory stress tests on 4GB Intel Celeron N4020 test machines under full desktop load. |
| **ASM-HW-004** | Hardware | Primary storage benchmark baseline is SATA III SSD ($\ge 450\text{ MB/s}$ read); HDDs are functional but excluded from KPI gating. | Expecting sub-8s boot or sub-2.5s cold launch on 5400 RPM spinning mechanical disks is physically unachievable. | Benchmark boot and launch latencies separately across NVMe, SATA SSD, and 5400 RPM mechanical HDD. |
| **ASM-HW-005** | Hardware | Modern hardware targets support Vulkan 1.2+ hardware acceleration via Mesa or proprietary NVIDIA drivers. | Systems lacking Vulkan 1.2 must fall back to WineD3D OpenGL, reducing 3D performance by 25–40%. | Execute Vulkan Conformance Test Suite (CTS) and `vulkaninfo` validation during GPU bring-up. |
| **ASM-HW-006** | Hardware | Legacy GPUs (Intel HD Graphics Gen 7/8 / Haswell) support OpenGL 4.5 and DRI3 via Mesa Gallium drivers. | Inability to run OpenGL 4.5 breaks compositor desktop acceleration and forces software llvmpipe rendering. | Verify Mesa `crocus` and `iris` driver compatibility on 4th-gen Intel Core hardware. |
| **ASM-HW-007** | Hardware | Displays adhere to standard VESA EDID/DisplayID specifications for resolution, refresh rates, and timing. | Non-compliant displays require manual modeline configuration or display quirk databases. | Test EDID parser on 15 external monitors across HDMI 2.0, DisplayPort 1.4, and eDP panels. |
| **ASM-HW-008** | Hardware | Input devices (keyboards, trackpads, mice) expose standard Linux `evdev` events managed via `libinput`. | Proprietary vendor drivers would require out-of-tree kernel modules, violating immutability. | Automated input event capture tests on Synaptics, ELAN, and Apple trackpads via `libinput-record`. |

---

### 2.2 Base Operating System & Software Stack Assumptions

| ID | Category | Assumption Statement | Impact if Wrong | Validation Plan |
|---|---|---|---|---|
| **ASM-SW-001** | Software | Fedora Atomic (`bootc` / `ostree`) provides stable transactional OCI container image deployment. | Building a custom Linux distribution from scratch would require massive package maintenance infrastructure. | Daily build and deployment of NebuOS container images via `bootc switch` in CI. |
| **ASM-SW-002** | Software | Upstream Linux Kernel 6.6+ LTS provides stable `futex2` (`sys_futex_waitv`), cgroups v2, and memory pressure PSI. | Without `sys_futex_waitv`, Windows thread synchronization under Wine incurs high context-switch overhead. | Kernel capability unit test verifying syscall availability on target images. |
| **ASM-SW-003** | Software | Wayland display protocol has achieved full desktop production maturity and completely replaces X11. | If major applications fail under pure Wayland, Xwayland fallback must remain active for compatibility. | Test NebuCompositor with native Wayland clients and Xwayland-bridged Win32 applications. |
| **ASM-SW-004** | Software | Mesa graphics drivers provide feature-complete, conforming Vulkan (RADV/ANV) and OpenGL implementations. | Bugs in upstream Mesa require local patching or waiting for upstream point releases. | Daily Mesa automated regression runner against certified DXVK / VKD3D test benches. |
| **ASM-SW-005** | Software | `systemd` v254+ serves as the universal PID 1 init system and user session supervisor. | Alternative init systems (OpenRC, runit) lack cgroup v2 integration, transient scopes, and user session bus activation. | Verify service ordering and `systemd-run --user --scope` containment in test suites. |
| **ASM-SW-006** | Software | PipeWire and WirePlumber handle all low-latency audio, ALSA emulation, and PulseAudio API routing. | Broken audio routing would degrade conferencing, CAD multimedia, and Windows game audio. | Run continuous automated audio loopback tests via PipeWire JACK and PulseAudio emulators. |
| **ASM-SW-007** | Software | SQLite 3.42+ in WAL mode provides sub-millisecond concurrent multi-reader access for metadata queries. | High write contention would require migrating to a client-server daemon (e.g. custom IPC engine). | Execute concurrency benchmark simulating 50 parallel reader threads querying compatibility profiles. |
| **ASM-SW-008** | Software | Bubblewrap (`bwrap`) unprivileged user namespaces are supported without requiring setuid root binaries. | Restricted enterprise kernels with disabled user namespaces would block application sandbox initialization. | Automated test checking `unshare -U -m -p` permissions during pre-flight diagnostics. |

---

### 2.3 Compatibility, Wine & Proton Assumptions

| ID | Category | Assumption Statement | Impact if Wrong | Validation Plan |
|---|---|---|---|---|
| **ASM-CP-001** | Compatibility | Upstream Wine 9.0+ user-space API coverage is sufficient to execute $>85\%$ of standard Win32/Win64 software. | Large gaps in Win32 APIs would require maintaining an unsustainable internal fork of Wine. | Compatibility Lab automated execution of Top 100 Windows consumer software installers. |
| **ASM-CP-002** | Compatibility | Valve Proton runtime patches and DXVK/VKD3D libraries can be decoupled from Steam for standalone game execution. | If Proton strictly requires Steam runtime bridges, non-Steam games would require WineD3D fallback. | Test standalone execution of Direct3D 11/12 games using standalone Proton runtime wrapper. |
| **ASM-CP-003** | Compatibility | Process-level prefix isolation is sufficient to run complex Windows apps without a Windows Virtual Machine. | If applications require kernel-level Windows hypervisors, they must be marked UNSUPPORTED per PRD non-goals. | Verify zero VM dependencies across all certified application test suites (`TEST-RUN-002`). |
| **ASM-CP-004** | Compatibility | Win32 asynchronous I/O and APC dispatching function reliably via Linux `io_uring` and epoll bridges. | High latency or hangs in file-heavy Windows installers (AutoCAD, Office). | Automated I/O throughput and stress tests on large file copy routines within Wine prefixes. |
| **ASM-CP-005** | Compatibility | 64-bit Windows applications represent $>90\%$ of modern usage; 32-bit WoW64 support is retained for legacy tools. | Pure 64-bit systems without multilib libraries would break older installers and setup routines. | Verify WoW64 multilib execution path on 32-bit legacy installers (7-Zip 32-bit, older CAD utilities). |
| **ASM-CP-006** | Compatibility | Microsoft .NET Framework applications can run via Wine-Mono or automated native runtime injection. | Total failure of CAD and enterprise tools dependent on WPF and .NET 4.8. | Automated profile installation test for AutoCAD and 3ds Max .NET dependencies. |
| **ASM-CP-007** | Compatibility | Windows installer executables (InnoSetup, NSIS, InstallShield, MSI) can be detected via PE heuristic signatures. | Failed installer detection results in wrong prefix configuration or missed silent install switches. | Unit test PE parser against catalog of 500 distinct installer binaries. |
| **ASM-CP-008** | Compatibility | Applications requiring Windows ring-0 kernel drivers (`.sys`) can be rejected without compromising core project goals. | User expectations for anti-cheat games (Valorant) will not be met; clear communication is essential. | PE scanner detects driver dependencies; verifies clear user-facing error modal. |

---

### 2.4 User Expectations & Desktop Experience Assumptions

| ID | Category | Assumption Statement | Impact if Wrong | Validation Plan |
|---|---|---|---|---|
| **ASM-US-001** | User/UX | Target users require a complete graphical user interface and must never be forced to use the command line. | Technical shell requirements alienate non-technical general users migrating from Windows. | Usability testing with non-technical users completing install, run, and uninstall workflows without terminal. |
| **ASM-US-002** | User/UX | Users expect standard Windows application installation conventions (double-clicking `.exe` or `.msi` files). | Unintuitive installer workflows cause user confusion and failed onboarding. | Test `binfmt_misc` file association triggering automatic installer wizard on `.exe` double-click. |
| **ASM-US-003** | User/UX | Users possess legitimate licenses and original installer media for proprietary software (Office, CAD, Adobe). | NebuOS cannot distribute proprietary software; users must provide their own installers. | Legal review and EULA verification; zero proprietary binary redistribution in all builds. |
| **ASM-US-004** | User/UX | The operating system runs primarily in single-seat, single-active-user desktop and laptop environments. | Multi-seat enterprise terminal setups require complex multi-session Xwayland routing. | Verify desktop session management under single-user UID 1000 environment. |
| **ASM-US-005** | User/UX | Windows applications must integrate seamlessly into the native desktop (launcher icons, taskbar, file associations). | Poor desktop integration makes applications feel like second-class alien software. | Verify FreeDesktop `.desktop` icon generation and window grouping under NebuShell taskbar. |
| **ASM-US-006** | User/UX | Users accept that competitive multiplayer games with kernel anti-cheat are unsupported on NebuOS. | Persistent user complaints if architectural non-goals are not clearly articulated up front. | Prominently display supported/unsupported software criteria in Software Center and docs. |

---

### 2.5 Deployment, Storage & Operating System Lifecycle Assumptions

| ID | Category | Assumption Statement | Impact if Wrong | Validation Plan |
|---|---|---|---|---|
| **ASM-DP-001** | Deployment | Btrfs filesystem with subvolumes (`@`, `@home`, `@nebu_apps`) is the mandatory default filesystem format. | Missing Btrfs features (`reflink`, instant snapshots) forces slow physical copies and duplicates disk usage. | Automated OS installer installs and verifies subvolume layout on bare-metal test drives. |
| **ASM-DP-002** | Deployment | Operating system updates are distributed as atomic, signed container images via OCI registries (`bootc`). | Traditional package-by-package updates (`dnf`) risk dependency corruption and partial upgrade failures. | Simulate sudden power-loss during `bootc update` in lab test rig; verify zero system corruption. |
| **ASM-DP-003** | Deployment | Systems have intermittent broadband internet access for image updates, compatibility DB syncs, and winetricks. | Fully offline systems cannot fetch dynamic winetricks dependencies without pre-bundled offline media. | Test offline deployment mode with pre-cached dependency packages on USB installation media. |
| **ASM-DP-004** | Deployment | Dual-root bootc deployment enables instantaneous, non-destructive GRUB rollback to the previous OS state. | Failed OS updates leave user machines unbootable without manual rescue media. | Automated boot-failure injection test triggering automatic fallback reboot to previous deployment. |
| **ASM-DP-005** | Deployment | User application data resides in persistent subvolumes (`/var` and `/home`), surviving OS image replacements. | Operating system image updates must never wipe user documents, prefix data, or application settings. | Execute OS image update from Version A to Version B; verify intact user files and Wine prefixes. |
| **ASM-DP-006** | Deployment | Compatibility profiles can be updated out-of-band via signed SQLite delta sync without requiring a full OS reboot. | Users must wait for monthly OS updates just to receive an application recipe fix. | Verify D-Bus triggered SQLite profile update and dynamic ingestion without session restart. |

---

### 2.6 Performance Budgets & Resource Assumptions

| ID | Category | Assumption Statement | Impact if Wrong | Validation Plan |
|---|---|---|---|---|
| **ASM-PF-001** | Performance | Combined base operating system idle RAM usage (kernel + systemd + compositor + shell) is $\le 800\text{ MB}$. | Exceeding 800MB idle leaves insufficient headroom for Windows applications on 4GB hardware. | Automated RAM profiling script measuring `MemAvailable` and PSS across all system daemons at cold boot. |
| **ASM-PF-002** | Performance | Cold application launch latency for certified software on SATA SSDs is $\le 2.5\text{ seconds}$. | Sluggish application startup creates a perceived slow, non-native desktop experience. | Automated high-speed camera and timestamp benchmarking measuring click-to-first-frame render. |
| **ASM-PF-003** | Performance | Warm application launch latency (via pre-warmed runtime cache) is $\le 800\text{ milliseconds}$. | Lack of warm caching makes relaunching closed applications feel sluggish. | Benchmark launch latency of second run of Word/Excel with active warm runtime pool. |
| **ASM-PF-004** | Performance | NebuCompositor maintains steady 60 FPS presentation without frame drops under normal desktop interaction. | UI stutter, jerky window dragging, or input lag severely damages perceived system quality. | Continuous frame pacing analysis using Wayland presentation-time protocol and KMS vblank timers. |
| **ASM-PF-005** | Performance | ZRAM with `zstd` compression provides $1.5\times\text{--}2.0\times$ virtual memory expansion on 4GB systems with minimal CPU penalty. | Without ZRAM, memory-intensive CAD applications crash immediately upon exceeding physical RAM. | Run AutoCAD stress test loading complex DWG files while monitoring ZRAM swap throughput and CPU load. |
| **ASM-PF-006** | Performance | All background system daemons adhere to the zero-polling invariant, consuming $<1\%$ CPU combined at idle. | Continuous timer wakeups drain laptop battery and degrade single-thread application responsiveness. | Profile CPU wakeups using `powertop` and `perf`; verify $\le 20\text{ wakeups/sec}$ at idle. |

---

## 3. Assumptions Management & Escalation Lifecycle

1. **Continuous Empirical Verification:** Every assumption marked with an automated test in the Validation Plan is integrated into the Compatibility Lab nightly regression suite.
2. **Invalidation Response Procedure:** If an assumption is invalidated by empirical test data:
   - A high-priority architecture defect is filed.
   - The Systems Architect convenes a review within 48 hours to evaluate alternative designs.
   - The corresponding ADR is updated, and mitigations in [RISK_REGISTER.md](file:///root/NebuOS/docs/RISK_REGISTER.md) are activated.
3. **Periodic Re-Assessment:** All assumptions are formally audited prior to each major milestone exit gate (P0, P5, P9, P12).

---

## 4. Related Documents
- [README.md](file:///root/NebuOS/docs/README.md) — Master documentation blueprint
- [INDEX.md](file:///root/NebuOS/docs/INDEX.md) — Complete documentation catalog and reading paths
- [OPEN_QUESTIONS.md](file:///root/NebuOS/docs/OPEN_QUESTIONS.md) — Open architectural trade-offs and decision log
- [RISK_REGISTER.md](file:///root/NebuOS/docs/RISK_REGISTER.md) — Quantitative systems risk register and mitigations
- [TRACEABILITY.md](file:///root/NebuOS/docs/TRACEABILITY.md) — Requirements traceability matrix mapping PRD sections 1–103
- [performance/00-performance-goals.md](file:///root/NebuOS/docs/performance/00-performance-goals.md) — Performance goals and latency budgets
