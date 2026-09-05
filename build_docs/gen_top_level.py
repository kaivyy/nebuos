#!/usr/bin/env python3
"""
Generate Top-Level Documentation for NebuOS:
- docs/README.md
- docs/OPEN_QUESTIONS.md
- docs/ASSUMPTIONS.md
- docs/RISK_REGISTER.md
- docs/REQUIREMENT_TRACEABILITY.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_file(rel_path, content):
    path = os.path.join(DOCS_DIR, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: {rel_path} ({len(content.splitlines())} lines)")

# 1. docs/README.md
readme_content = """# NebuOS Technical Documentation & Engineering Blueprint

**Status:** APPROVED  
**Target Architecture:** x86_64 (Future: ARM64)  
**Primary Implementation Language:** Rust  
**Foundation:** Fedora Atomic (bootc / ostree) + Linux Kernel + Wayland + Mesa + Wine/Proton  
**Compatibility Model:** Process-level Translation & Prefix Isolation (NO VIRTUAL MACHINE)

---

## 1. Documentation Purpose & Scope

This documentation repository serves as the definitive engineering-level specification and architectural blueprint for **NebuOS**. While the [NebuOS PRD](../PRD.md) specifies high-level product goals and requirements, these technical documents define the exact software architecture, subsystem boundaries, data models, IPC protocols, lifecycle state machines, hardware validation procedures, and testing frameworks needed to execute implementation.

Any systems engineer, kernel hacker, Rust developer, or QA specialist reading this blueprint should understand:
1. What components must be built from scratch in Rust (e.g., NebuCompositor, NebuShell, NebuRuntime, NebuPatcher).
2. What components must be strictly reused from upstream Linux ecosystems (Linux kernel, systemd, Wayland protocols, Mesa, PipeWire, Wine, Proton, DXVK, VKD3D).
3. The exact boundaries and IPC protocols between all system and user daemons.
4. The database schemas, prefix layouts, and graphics translation paths.
5. The strict prohibition of Virtual Machines as a compatibility fallback.

---

## 2. Recommended Reading Order

To understand NebuOS systematically, follow this curated reading path:

```mermaid
flowchart TD
    PRD["1. PRD (Master Requirements)"] --> ARCH_00["2. Architecture Overview (docs/architecture/00-overview.md)"]
    ARCH_00 --> SYS_ARCH["3. System Architecture (docs/architecture/01-system-architecture.md)"]
    SYS_ARCH --> RUNTIME["4. Runtime & Lifecycle (docs/runtime/)"]
    SYS_ARCH --> COMPOSITOR["5. Desktop & Compositor (docs/desktop/)"]
    RUNTIME --> COMPAT["6. Compatibility & Database (docs/compatibility/)"]
    RUNTIME --> GRAPHICS["7. Graphics Pipeline (docs/graphics/)"]
    SYS_ARCH --> UPDATES["8. Atomic Updates & Rollback (docs/updates/)"]
    COMPAT --> TESTING["9. Compatibility Lab & QA (docs/testing/)"]
    SYS_ARCH --> PERF["10. Performance & Low-End Mode (docs/performance/)"]
    SYS_ARCH --> ROADMAP["11. Engineering Roadmap P0-P12 (docs/roadmap/)"]
    ROADMAP --> ADR["12. Architectural Decision Records (docs/decisions/)"]
```

1. **Master PRD:** [../PRD.md](../PRD.md)
2. **System Architecture Overview:** [architecture/00-overview.md](architecture/00-overview.md)
3. **Core Subsystems:**
   - [architecture/01-system-architecture.md](architecture/01-system-architecture.md)
   - [architecture/02-boot-and-init.md](architecture/02-boot-and-init.md)
   - [architecture/03-process-and-ipc.md](architecture/03-process-and-ipc.md)
   - [architecture/04-filesystem.md](architecture/04-filesystem.md)
   - [architecture/05-security.md](architecture/05-security.md)
4. **Desktop Environment & UI:**
   - [desktop/00-desktop-overview.md](desktop/00-desktop-overview.md)
   - [desktop/01-compositor.md](desktop/01-compositor.md)
   - [desktop/02-shell.md](desktop/02-shell.md)
5. **Windows Execution Engine:**
   - [runtime/00-runtime-overview.md](runtime/00-runtime-overview.md)
   - [runtime/01-application-lifecycle.md](runtime/01-application-lifecycle.md)
   - [runtime/03-prefix-management.md](runtime/03-prefix-management.md)
   - [runtime/04-wine-integration.md](runtime/04-wine-integration.md)
6. **Compatibility & Patching:**
   - [compatibility/00-compatibility-overview.md](compatibility/00-compatibility-overview.md)
   - [compatibility/01-database-schema.md](compatibility/01-database-schema.md)
   - [compatibility/03-patching.md](compatibility/03-patching.md)
7. **Graphics Subsystem:**
   - [graphics/00-graphics-overview.md](graphics/00-graphics-overview.md)
   - [graphics/03-dxvk-vkd3d.md](graphics/03-dxvk-vkd3d.md)
8. **Engineering Roadmap & ADRs:**
   - [roadmap/00-engineering-roadmap.md](roadmap/00-engineering-roadmap.md)
   - [decisions/](decisions/)

---

## 3. Directory Structure & Documentation Map

```text
docs/
├── README.md                          # Master documentation index and reading guide
├── OPEN_QUESTIONS.md                  # Unresolved architectural dilemmas with trade-offs
├── ASSUMPTIONS.md                     # Foundational engineering assumptions
├── RISK_REGISTER.md                   # Systematic risk matrix and mitigation strategies
├── REQUIREMENT_TRACEABILITY.md        # Mapping of PRD requirements to architecture and tests
│
├── architecture/                      # System topology, boot flow, IPC, security & hardware
├── desktop/                           # NebuCompositor, NebuShell, windowing & input
├── runtime/                           # Process execution engine, prefix isolation & Wine/Proton
├── compatibility/                     # SQLite schema, application profiles & patch engine
├── graphics/                          # GPU detection, Mesa, Vulkan, DXVK & VKD3D
├── applications/                      # App manager, filesystem mapping, associations & store
├── updates/                           # OSTree/bootc atomic image lifecycle & rollback
├── testing/                           # Compatibility Lab, automation, QA tiers & matrices
├── performance/                       # Boot benchmarks, memory targets & Low-End Mode (4GB)
├── development/                       # Repository layout, Rust toolchains & CI/CD
├── decisions/                         # Architectural Decision Records (ADR-0001 to ADR-0015)
└── roadmap/                           # Phased milestones (P0 through P12) with Definition of Done
```

---

## 4. Document Status Lifecycle

All technical documents in this repository are managed with strict lifecycle tags:
- **DRAFT:** Work in progress, open for structural feedback.
- **REVIEW:** Complete specification undergoing technical review by systems and compatibility leads.
- **APPROVED:** Accepted baseline for engineering implementation. Changes require an ADR update.
- **SUPERSEDED:** Deprecated in favor of an updated architecture document.
"""

write_file("README.md", readme_content)

# 2. docs/OPEN_QUESTIONS.md
open_q_content = """# NebuOS Open Architectural Questions

**Status:** REVIEW  
**Purpose:** Formal tracking of unresolved engineering questions, architectural trade-offs, and empirical decision criteria.

---

## 1. Summary Matrix

| ID | Topic | Impact Area | Current Recommendation | Decision Deadline |
|---|---|---|---|---|
| OQ-001 | Wayland Compositor Foundation: Smithay vs Custom wlroots Binding | NebuCompositor | Smithay (Pure Rust) | Milestone P0 Exit |
| OQ-002 | Sandboxing Technology for Windows Prefixes: Bubblewrap vs Landlock+seccomp | NebuRuntime / Security | Bubblewrap (Initial) -> Landlock (P6) | Milestone P1 Exit |
| OQ-003 | Btrfs vs Ext4 as Default Root Filesystem in Atomic Image Deployments | Storage / Update | Btrfs with Subvolumes (`@`, `@home`, `@nebu`) | Milestone P0 Exit |
| OQ-004 | Wine Upstream Tracking: Stable (Annual) vs Staging (Bi-weekly) | Wine Integration | Dual-track: Staging for Beta, Stable for LTS | Milestone P5 Exit |
| OQ-005 | .NET Framework Bridge: Mono vs Upstream Wine-Mono vs Dotnet Core Shim | Windows Apps (CAD/Office) | Wine-Mono baseline + Native CoreCLR injection | Milestone P6 Exit |

---

## 2. Detailed Questions & Trade-Off Analyses

### OQ-001: Wayland Compositor Foundation (Smithay vs wlroots)
- **Question:** Should `NebuCompositor` be implemented using pure Rust via the `smithay` framework, or using C-bindings to `wlroots`?
- **Context:** NebuOS requires a lightweight, memory-efficient compositor with low latency (< 100MB idle RAM).
- **Options:**
  1. *Smithay:* Pure Rust, memory-safe, native async handling, zero C FFI overhead in compositor logic. Active maintenance in modern Rust ecosystem.
  2. *wlroots (C / Bindings):* Highly mature, battle-tested in Sway/Hyprland, but introduces unsafe C boundaries, complex lifetime bindings, and upstream API churn.
- **Current Recommendation:** Smithay. It aligns with the mandate for native Rust components, prevents memory safety vulnerabilities in input/display handling, and provides total control over frame scheduling and damage tracking.
- **Evidence Required:** Benchmark idle RAM and frame latency of a minimal Smithay compositor vs wlroots under DRM/KMS on an Intel N4020 (low-end test harness).
- **Decision Deadline:** P0 Exit.

### OQ-002: Sandboxing Technology for Windows Applications
- **Question:** How should NebuRuntime enforce isolation on Windows prefixes without performance degradation?
- **Context:** Untrusted Windows executables and setup routines must not inspect arbitrary paths in `/home/$USER` or system directories.
- **Options:**
  1. *Bubblewrap (`bwrap`):* Battle-tested in Flatpak, unprivileged user namespaces, robust mount namespace filtering. Overhead is ~5ms process startup.
  2. *Landlock LSM + seccomp:* In-kernel unprivileged access control, zero mount overhead, but requires kernel >= 5.13 and has limited support for complex path rewriting.
- **Current Recommendation:** Bubblewrap for P1-P5 to guarantee robust filesystem isolation, transitioning to Landlock for internal process restriction in P6.
- **Decision Deadline:** P1 Exit.

### OQ-003: Default Filesystem Strategy (Btrfs vs Ext4)
- **Question:** Should the installation image mandate Btrfs formatted partitions or maintain Ext4 compatibility?
- **Context:** Instant snapshotting and subvolume rollbacks are critical for prefix repair and system update rollback. However, Ext4 is simpler on low-end flash storage.
- **Current Recommendation:** Default to Btrfs with subvolume layout (`@` for OSTree root, `@home` for user data, `@nebu_apps` with `nodatacow` for Wine prefixes to avoid fragmentation). Allow Ext4 fallback for older hardware.
- **Decision Deadline:** P0 Exit.

### OQ-004: Wine Upstream Cadence Tracking
- **Question:** Which upstream Wine branch should NebuOS package and certify?
- **Context:** Upstream Wine releases bi-weekly Staging builds and annual Stable releases. Wine-Staging contains essential patches for commercial CAD and Adobe products, but risks regressions.
- **Current Recommendation:** Maintain two tiers in Nebu Compatibility Engine:
  - Stable Tier: Built on Wine-Stable + curated Nebu patches (for Certified Enterprise applications).
  - Fast Tier: Built on Wine-Staging (for games and general desktop applications).
- **Decision Deadline:** P5 Exit.

### OQ-005: .NET Framework Implementation for Heavy CAD Applications
- **Question:** How should NebuOS satisfy hard dependencies on .NET Framework 3.5 / 4.8 in AutoCAD and 3ds Max?
- **Context:** Wine-Mono does not fully implement Windows Presentation Foundation (WPF) or deep WCF remoting required by Autodesk licensing engines.
- **Current Recommendation:** Wine-Mono as default. For certified profiles requiring proprietary .NET, automated profile scripts install native Microsoft .NET redistributables into the application prefix via winetricks automation routines embedded in NebuRuntime.
- **Decision Deadline:** P6 Exit.
"""

write_file("OPEN_QUESTIONS.md", open_q_content)

# 3. docs/ASSUMPTIONS.md
assumptions_content = """# NebuOS Engineering Assumptions Register

**Status:** APPROVED  
**Purpose:** Formal record of foundational assumptions governing systems architecture, hardware targets, external dependencies, and technical boundaries.

---

## 1. Foundational Architecture Assumptions

| ID | Assumption Statement | Rationale | Impact if Invalidated |
|---|---|---|---|
| ASM-001 | x86_64 architecture is the exclusive initial target; ARM64 is deferred to post-1.0. | Wine x86_64 execution on x86_64 CPU requires zero instruction emulation. Translating x86_64 Windows PE to ARM64 Linux requires FEX/Box64, introducing high complexity and overhead. | Would require integrating CPU binary translation layer (FEX-Emu / Rosetta alternative). |
| ASM-002 | Fedora Atomic (ostree / bootc) provides sufficient immutability and package stability. | Proven image deployment model, SELinux enforcement, atomic rollbacks, and first-class Flatpak integration. | Would require building a custom image builder (Yocto/Debian Live) with high maintenance cost. |
| ASM-003 | Wayland display protocol has matured sufficiently to replace X11 entirely. | X11 is deprecated upstream; Wayland provides proper security isolation between surfaces, HiDPI scaling, and modern GPU buffer management. | Fallback to Xwayland is required for legacy Linux/Wine windows, but base compositor remains pure Wayland. |
| ASM-004 | Native Windows applications can run without Windows VM or hypervisor. | Wine, Proton, DXVK, and VKD3D cover >85% of standard user32/gdi32/kernel32 and DirectX calls. | Applications requiring Windows ring-0 drivers (anti-cheat, raw hardware dongles) will be marked UNSUPPORTED. |
| ASM-005 | SQLite is optimal for local compatibility databases and application metadata. | Zero-configuration, serverless, atomic ACID transactions, sub-millisecond query performance, and compact storage. | If concurrent multi-daemon write contention arises, daemonized IPC service or LMDB would be evaluated. |
| ASM-006 | Btrfs subvolumes allow instant prefix snapshots without duplicating disk space. | Copy-on-Write (CoW) enables `reflink` copies of 5GB application prefixes in under 50ms. | File copies would take minutes on SATA SSDs and consume gigabytes of storage. |
| ASM-007 | PipeWire replaces both ALSA directly and PulseAudio for audio routing. | Unified low-latency audio/video routing engine, native JACK compatibility, and per-client volume controls. | Complex audio routing and Bluetooth profiles would require legacy pulseaudio hacks. |
| ASM-008 | Rust provides memory safety and zero-cost abstractions needed for system components. | Memory safety prevents use-after-free, buffer overflows, and race conditions in compositor and privileged runtimes. | C/C++ components would require extensive Valgrind/ASan testing and risk CVE vulnerabilities. |

---

## 2. Hardware Environment Assumptions

1. **Memory Baseline (4 GB RAM):** The operating system must operate reliably on 4 GB physical RAM. This assumes base OS services, compositor, and shell consume no more than 800 MB combined at idle.
2. **GPU & Driver Support:** The system assumes hardware Vulkan 1.2+ support is available for modern gaming and DXVK. For legacy GPUs (Intel Gen 7/8, Ivy Bridge), Mesa OpenGL fallbacks (wined3d) are assumed to function for non-Vulkan workloads.
3. **Storage Speed:** While SATA SSD is the minimum recommended drive, HDD support is maintained for installation but explicitly excluded from performance metrics.
"""

write_file("ASSUMPTIONS.md", assumptions_content)

# 4. docs/RISK_REGISTER.md
risk_content = """# NebuOS Systems Risk Register

**Status:** APPROVED  
**Purpose:** Formal identification, scoring, mitigation, and contingency planning for all critical engineering, operational, and architectural risks.

---

## 1. Risk Scoring Methodology

- **Probability (P):** 1 (Rare) to 5 (Almost Certain)
- **Impact (I):** 1 (Insignificant) to 5 (Catastrophic / Project Blocker)
- **Risk Score (R):** P × I (1 to 25)
  - **Critical (16-25):** Immediate mitigation plan required; daily monitoring.
  - **High (10-15):** Subsystem architectural safeguard required.
  - **Medium (5-9):** Managed via testing and operational gates.
  - **Low (1-4):** Acceptable residual risk.

---

## 2. Comprehensive Risk Matrix

| Risk ID | Category | Risk Description | P | I | R | Mitigation Strategy | Detection Mechanism | Fallback / Recovery | Owner |
|---|---|---|---|---|---|---|---|---|---|
| RSK-001 | Compatibility | Windows Kernel Driver Dependency (Anti-cheat, DRM, CAD dongles) | 5 | 4 | **20** | Explicit Non-Goal. Do not pretend compatibility. Auto-detect driver requirements and report UNSUPPORTED immediately. | NebuRuntime PE scanner detects `.sys` drivers and known anti-cheat signatures (EasyAntiCheat, BattlEye, Denuvo). | Display user-facing notification explaining architectural restriction. NO VM fallback. | Compatibility Lead |
| RSK-002 | Compatibility | COM/OLE / ActiveX Deep Coupling in Microsoft Office & CAD | 4 | 4 | **16** | Curate custom Wine DLL overrides (`ole32`, `oleaut32`, `rpcrt4`). Pre-register OLE servers in isolated prefix registry. | Automated COM test suite in Compatibility Lab (Word macro execution, Excel OLE link test). | Auto-apply targeted Nebu patch for specific Office version. | Compatibility Lead |
| RSK-003 | Performance | Memory Exhaustion on 4GB Low-End Devices | 4 | 4 | **16** | Implement Nebu Lite Mode: compositor disables blur/shadows, aggressively evicts unused prefix caches, limits background daemons. | systemd-oomd pressure stall information (PSI) monitoring; proactive daemon memory trimming. | Drop runtime warm-cache; trigger zram swap compaction. | Systems Architect |
| RSK-004 | Updates | System Image Regression Breaks GPU Acceleration or Wine | 3 | 5 | **15** | Strict Quality Gates: Build -> OSTree staging -> Automated Tier 0-2 tests -> Canary channel -> Stable promotion. | Pre-boot health check and systemd rollback-target. | Dual-staged OSTree root allows one-click GRUB rollback to prior working deployment. | Release Engineer |
| RSK-005 | Graphics | Proprietary NVIDIA Driver Instability on Wayland | 4 | 3 | **12** | Support explicit sync (`linux-drm-syncobj-v1`), package tested proprietary driver versions via Akmods/OSTree layers. | Compositor DRM format negotiation check; fallback to EGLStreams/GBM workarounds. | Graceful fallback to software rendering mode or conservative driver profile. | Graphics Engineer |
| RSK-006 | Security | Malicious Windows PE Binary Exploiting Linux User Space | 3 | 4 | **12** | Bubblewrap sandbox per prefix: isolate `/home/$USER`, restrict `Z:` drive to selected folders, drop network capability if not requested. | Landlock LSM audit logs and seccomp violation monitoring. | Immediate process termination and prefix isolation quarantine. | Security Engineer |
| RSK-007 | Compatibility | Autodesk / Adobe Proprietary Licensing Daemon Failures | 4 | 3 | **12** | Stub or emulate Autodesk Access Service / Adobe Genuine Service via Wine background service wrappers. | Licensing daemon heartbeat verification during launch test. | NebuPatch profile configures mock licensing endpoint or manual activation mode. | Compatibility Lead |
| RSK-008 | Storage | Prefix Disk Bloat from Multiple Isolated Wine Environments | 4 | 3 | **12** | Use Btrfs `reflink` deduplication for base `drive_c` templates; share read-only common runtimes (`winetricks` cache). | NebuStorage daemon tracks prefix disk usage; auto-suggests deduplication. | Deduplicate common DLLs and system runtimes across prefixes. | Storage Lead |
| RSK-009 | Legal | Accidental Redistribution of Proprietary Microsoft/Adobe DLLs | 2 | 5 | **10** | Zero binary redistribution. NebuOS only distributes open-source code and recipe profiles. Users supply their own installers. | Automated CI license scanner; sha256 checksums verify clean repository. | Immediate removal of offending script; legal review gate. | Lead Architect |
| RSK-010 | Stability | Wayland Compositor Crash Terminates User Applications | 2 | 5 | **10** | Strict separation of NebuCompositor and NebuShell; handle client buffer disconnects gracefully; recover surface state. | systemd cgroup monitoring; compositor watchdog timer. | Automatic compositor respawn with session lock screen preservation. | Desktop Engineer |
"""

write_file("RISK_REGISTER.md", risk_content)

# 5. docs/REQUIREMENT_TRACEABILITY.md
trace_content = """# NebuOS Requirements Traceability Matrix

**Status:** APPROVED  
**Purpose:** End-to-end verification mapping each PRD requirement to architectural design specifications, software components, test cases, and development milestones.

---

## 1. Master Traceability Matrix

| PRD Section | Requirement Description | Technical Architecture Doc | Implementation Component | Verification Test Case | Milestone |
|---|---|---|---|---|---|
| Sec 1 | Linux Kernel & Wayland Display Protocol | `architecture/01-system-architecture.md`, `desktop/01-compositor.md` | Fedora Base, Linux Kernel, NebuCompositor | `TEST-SYS-001` (Wayland Protocol Compliance) | P1, P2 |
| Sec 1 & 92 | NO Virtual Machine Policy for Applications | `decisions/ADR-0009-no-vm.md`, `runtime/00-runtime-overview.md` | NebuRuntime (PE Translator) | `TEST-RUN-002` (Native Process Verification) | P0, P5 |
| Sec 2 & 63 | Low-End 4GB Hardware Responsiveness & <1GB Idle RAM | `performance/01-memory.md`, `performance/00-performance-goals.md` | NebuShell Lite Mode, memory manager | `TEST-PERF-001` (4GB Idle Benchmark) | P3, P12 |
| Sec 9 & 72 | Atomic OS Updates with Instant Rollback | `updates/00-update-overview.md`, `updates/04-rollback.md` | OSTree / bootc deploy engine | `TEST-UPD-001` (Atomic Rollback Test) | P1, P11 |
| Sec 11 | NebuCompositor (Rust Wayland Compositor) | `desktop/01-compositor.md`, `desktop/05-display.md` | `nebu-compositor` (Smithay) | `TEST-COMP-001` (DRM/KMS Buffer Flip) | P2 |
| Sec 12 | NebuShell (Rust Native Desktop Shell, No Electron) | `desktop/02-shell.md`, `desktop/06-system-integration.md` | `nebu-shell` (Iced/Slint/GTK4-rs) | `TEST-SHELL-001` (Shell Memory & IPC Test) | P3 |
| Sec 14 & 16 | Unified App Model & Isolated Per-App Prefix | `applications/00-application-model.md`, `runtime/03-prefix-management.md`| `nebu-runtime`, Prefix Manager | `TEST-PFX-001` (Prefix Isolation Test) | P5, P6 |
| Sec 15 & 55 | Windows Filesystem Emulation (`C:\\` and `Z:\\` Mapping) | `applications/02-filesystem-mapping.md` | Wine Prefix `dosdevices` Manager | `TEST-FS-001` (Path Translation Test) | P6 |
| Sec 17 & 18 | Nebu Runtime & Automatic Installer (.exe detection) | `runtime/02-windows-runtime.md`, `applications/01-installation.md` | `nebu-runtime-daemon`, binfmt_misc | `TEST-RUN-001` (EXE Double-Click Launch) | P5 |
| Sec 20 | SQLite Compatibility Database | `compatibility/01-database-schema.md` | `nebu-compat-db` (SQLite) | `TEST-DB-001` (Schema Query Benchmark) | P7 |
| Sec 22 | Nebu Patch Engine (Layered Compatibility Fixes) | `compatibility/03-patching.md` | `nebu-patcher` | `TEST-PAT-001` (Reversible Patch Verification) | P8 |
| Sec 24 | Proton Strategy for Gaming Workloads | `runtime/05-proton-integration.md` | `nebu-runtime` Game Mode | `TEST-PRO-001` (DXVK/VKD3D Steam Launch) | P6, P9 |
| Sec 25 & 26 | Graphics Compatibility & Hybrid GPU Offloading | `graphics/01-gpu-detection.md`, `graphics/04-gpu-profiles.md` | `nebu-graphics-daemon` | `TEST-GFX-001` (DRI_PRIME / NV_PRIME Test) | P9 |
| Sec 27 | Microsoft Office 2019/2021/2024 Certification | `compatibility/02-profiles.md`, `testing/03-compatibility-testing.md`| Office Compat Profile & Lab | `TEST-APP-OFFICE` (Word/Excel E2E Suite) | P10 |
| Sec 28 | Autodesk AutoCAD DWG/GPU Acceleration Certification | `compatibility/02-profiles.md`, `testing/03-compatibility-testing.md`| AutoCAD Compat Profile & Lab | `TEST-APP-CAD` (DWG 2D/3D Stress Test) | P10 |
| Sec 31 & 32 | Compatibility Lab & Automated Headless Regression | `testing/00-testing-strategy.md`, `testing/03-compatibility-testing.md`| Nebu QA Lab Runner | `TEST-LAB-001` (Automated App Regression) | P0, P7 |
| Sec 41 & 42 | Sandbox Isolation & Unprivileged Windows PE Access | `architecture/05-security.md`, `runtime/02-windows-runtime.md` | Bubblewrap / Landlock Sandbox | `TEST-SEC-001` (Filesystem Jailbreak Test) | P5, P6 |
| Sec 66 | Nebu CLI Tooling (`nebu run`, `nebu repair`, etc.) | `runtime/02-windows-runtime.md`, `applications/04-uninstallation.md`| `nebu-cli` (Rust binary) | `TEST-CLI-001` (Command Execution Suite) | P5, P8 |
| Sec 82 | Clean Repository Structure & Rust Dependency Policy | `development/01-repository-structure.md`, `development/04-dependency-policy.md` | Cargo Workspace Architecture | `TEST-DEV-001` (Cargo Audit & Clippy Clean) | P0 |
"""

write_file("REQUIREMENT_TRACEABILITY.md", trace_content)

print("Top-level documentation generated successfully.")
