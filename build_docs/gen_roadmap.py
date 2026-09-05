#!/usr/bin/env python3
"""
Generate Engineering Roadmap Documentation for NebuOS (docs/roadmap/):
- 00-engineering-roadmap.md
- 01-p0.md through 13-p12.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs/roadmap"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_roadmap_file(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: roadmap/{filename} ({len(content.splitlines())} lines)")

# 00-engineering-roadmap.md
write_roadmap_file("00-engineering-roadmap.md", r"""# Engineering Roadmap Master Overview — NebuOS

**Status:** APPROVED  
**Purpose:** Establish the sequential development milestones, dependency graph, and critical path from initial research through production 1.0 release.

---

## 1. Master Milestone Progression & Critical Path

```mermaid
graph TD
    P0[P0: Research & Specification] --> P1[P1: Base OS Foundation]
    P1 --> P2[P2: NebuCompositor - Wayland]
    P2 --> P3[P3: NebuShell - Desktop UI]
    P3 --> P4[P4: Native Desktop Applications]
    P1 --> P5[P5: Nebu Runtime Core]
    P5 --> P6[P6: Windows Wine/Proton Integration]
    P6 --> P7[P7: Compatibility Database - SQLite]
    P7 --> P8[P8: Nebu Patch Engine]
    P6 --> P9[P9: Adaptive Graphics Subsystem]
    P8 --> P10[P10: Professional Apps: Office & CAD]
    P9 --> P10
    P4 --> P11[P11: OS Installer & Atomic Updates]
    P10 --> P12[P12: Performance & Production Validation]
    P11 --> P12
    P12 --> V1[NebuOS 1.0 Production Release]
```

## 2. Milestone Summary Matrix

| Milestone | Code | Primary Objective | Key Deliverable | Exit Gate |
|---|---|---|---|---|
| **Phase 0** | P0 | Research, Architectural Specs, Toolchains | Full Blueprint & ADRs | 100% Architecture Approved |
| **Phase 1** | P1 | Bootable Fedora Atomic Base OS | Bootable OSTree Image | Boots to Terminal on Baremetal |
| **Phase 2** | P2 | NebuCompositor (Wayland Server in Rust) | Smithay-based DRM Compositor | Renders Wayland clients @ 60 FPS |
| **Phase 3** | P3 | NebuShell (Native Desktop Shell in Rust) | Taskbar, Launcher, Quick Settings | Launcher response < 100ms |
| **Phase 4** | P4 | Native System Apps | File Manager, Terminal, Settings | Basic desktop usable without terminal |
| **Phase 5** | P5 | Nebu Runtime Core & Sandbox | `neburuntimed` & `bwrap` sandbox | Double-click runs simple PE binary |
| **Phase 6** | P6 | Windows Wine Integration | Prefix Manager & Runtime Trees | Isolated prefix launches 7-Zip & Notepad++ |
| **Phase 7** | P7 | Compatibility Database Engine | SQLite schema & profile indexer | Sub-2ms profile resolution |
| **Phase 8** | P8 | Nebu Patch Engine | 9-tier declarative patch engine | Reversible DLL/registry patching |
| **Phase 9** | P9 | Adaptive Graphics Subsystem | DXVK / VKD3D / Hybrid GPU offload | Hardware-accelerated 3D viewport |
| **Phase 10** | P10 | Professional Application Certification | Microsoft Office & AutoCAD profiles | Office & AutoCAD certified in Lab |
| **Phase 11** | P11 | Graphical Installer & Atomic Updates | Live USB Installer & `bootc` updater | Transactional update & rollback |
| **Phase 12** | P12 | Performance & Production Hardening | 4GB RAM Low-End Mode & Security Audit | Production 1.0 Sign-off |

## 3. Related Documents
- [01-p0.md](01-p0.md) through [13-p12.md](13-p12.md)
""")

def create_milestone_doc(filename, num, name, objective, deps, inputs, outputs, components, tasks, tests, perf_gates, sec_gates, dod, risks, exit_crit):
    content = f"""# Milestone {num}: {name} — NebuOS

**Status:** APPROVED  
**Purpose:** Define the precise engineering specification, deliverables, tasks, and exit criteria for Phase {num}.

---

## 1. Objective
{objective}

## 2. Dependencies & Invariants
- **Upstream Dependencies:** {deps}
- **Required Inputs:** {inputs}

## 3. Components & Outputs
- **Software Components Built:** {components}
- **Key Artifacts / Outputs:** {outputs}

## 4. Engineering Tasks
{tasks}

## 5. Verification & Testing
{tests}

## 6. Performance & Security Gates
- **Performance Gate:** {perf_gates}
- **Security Gate:** {sec_gates}

## 7. Definition of Done (DoD) & Exit Criteria
- **Definition of Done:** {dod}
- **Exit Criteria:** {exit_crit}

## 8. Known Risks & Mitigations
{risks}
"""
    write_roadmap_file(filename, content)

# 01-p0.md
create_milestone_doc(
    "01-p0.md", "P0", "Research and Specification",
    "Establish master architecture, hardware matrix, dependency audit, licensing validation, and engineering blueprints.",
    "PRD Master Specification.",
    "PRD 1.0, upstream kernel docs, Wayland protocol specs, Wine architecture.",
    "Cargo monorepo setup, dev environment scripts.",
    "Full Technical Blueprint (docs/), 15 ADRs, Risk Register, Assumptions.",
    "1. Author system architecture and subsystem documents.\n2. Formulate relational SQLite schema.\n3. Conduct license audit of external dependencies.\n4. Design Compatibility Lab hardware topology.",
    "Linting and cross-reference audit across all documentation files.",
    "N/A (Documentation phase).",
    "No proprietary code committed; licensing compliance verified.",
    "All 100 technical documents and ADRs reviewed and approved.",
    "Formal sign-off by Principal Systems Architect.",
    "Underestimating complexity of COM/OLE or Wayland direct scanout. Mitigation: Addressed in ADR-0005 and ADR-0007."
)

# 02-p1.md
create_milestone_doc(
    "02-p1.md", "P1", "Base OS Foundation",
    "Build a minimal, bootable Fedora Atomic image with kernel, systemd, networking, and graphics infrastructure.",
    "P0 Architecture approval.",
    "Fedora Atomic bootc base container, kernel 6.x, dracut.",
    "systemd config, dracut config, kernel tunables.",
    "Bootable NebuOS raw disk image & ISO.",
    "1. Configure Containerfile for base bootc image.\n2. Configure Btrfs subvolumes (@, @var, @home).\n3. Enable DRM drivers, PipeWire, and NetworkManager.\n4. Verify boot to serial/virtual console.",
    "Tier 0 System Boot Test on QEMU and Baremetal Rig 1.",
    "Boot to console in < 4.0s on SATA SSD.",
    "SELinux in Enforcing mode; read-only rootfs mounted.",
    "Base image boots cleanly on Intel, AMD, and NVIDIA silicon without errors.",
    "Console login operational, networking functional, sound output verified.",
    "Dracut driver omissions causing boot panic. Mitigation: Automate driver inclusion in bootc manifest."
)

# 03-p2.md
create_milestone_doc(
    "03-p2.md", "P2", "NebuCompositor",
    "Implement the core Wayland compositor in Rust using Smithay, supporting DRM/KMS, direct scanout, and input routing.",
    "P1 Base OS Foundation.",
    "Smithay crate, libinput, libdrm, Mesa GBM.",
    "crates/nebu-compositor.",
    "Functional Wayland compositor binary.",
    "1. Initialize Smithay DRM/KMS backend.\n2. Implement `wl_compositor`, `xdg_shell`, `linux_dmabuf_v1`.\n3. Add direct scanout logic for fullscreen surfaces.\n4. Integrate libinput event loop.",
    "Run Wayland Protocol Conformance Test Suite; test tearing and damage tracking.",
    "Compositor idle memory <= 75 MB RSS; zero dropped frames on 60 Hz display.",
    "Wayland surface isolation verified; unprivileged client cannot read external buffers.",
    "Compositor launches from systemd user session and displays native Wayland test clients.",
    "Stable 60/120 FPS rendering on Intel, AMD, and NVIDIA GPUs.",
    "NVIDIA EGLStreams/GBM synchronization quirks. Mitigation: Adopt `linux-drm-syncobj-v1` explicit sync."
)

# 04-p3.md
create_milestone_doc(
    "04-p3.md", "P3", "NebuShell",
    "Develop the native Rust desktop shell providing the taskbar, launcher, quick settings, and notification system.",
    "P2 NebuCompositor.",
    "NebuCompositor layer-shell support, Slint/Iced GUI toolkit.",
    "crates/nebu-shell.",
    "Functional desktop shell surface and panel.",
    "1. Implement taskbar with running app indicators.\n2. Build fast indexed application launcher.\n3. Implement Quick Settings flyout (audio slider, WiFi list).\n4. Implement notification daemon listener.",
    "Launcher response latency benchmark; UI memory profile check.",
    "Launcher opens in < 100ms from keypress; Shell idle RAM <= 45 MB.",
    "Shell runs unprivileged as UID 1000; D-Bus policy restricts system actions.",
    "Desktop panel, launcher, and system tray interact smoothly without flickering.",
    "Desktop shell responsive on 4GB low-end hardware.",
    "Memory bloat in UI layout tree. Mitigation: Strictly avoid WebViews/Chromium; use lightweight Rust vector UI."
)

# 05-p4.md
create_milestone_doc(
    "05-p4.md", "P4", "Native Desktop Applications",
    "Provide core native system applications: file manager, settings, terminal, and task manager.",
    "P3 NebuShell.",
    "Wayland protocols, systemd-logind, PipeWire APIs.",
    "crates/nebu-file-manager, crates/nebu-terminal, crates/nebu-task-manager.",
    "Core desktop productivity apps.",
    "1. Implement tabbed file manager supporting prefix hiding.\n2. Implement GPU-accelerated terminal emulator.\n3. Implement system task manager grouping Wine processes under app headers.\n4. Implement system settings panel.",
    "File transfer stress test; terminal rendering throughput test.",
    "Task Manager CPU overhead < 1% during active process polling.",
    "File manager honors Linux permission bits and restricts sandbox browsing.",
    "All 4 system apps operational without terminal requirement for standard usage.",
    "Complete graphical desktop user experience ready for end users.",
    "File manager lag on large directories. Mitigation: Implement virtualized scrolling list and async stat caching."
)

# 06-p5.md
create_milestone_doc(
    "06-p5.md", "P5", "Nebu Runtime Core",
    "Implement the background daemon and execution engine managing Windows PE binaries and sandbox containers.",
    "P1 Base OS.",
    "Bubblewrap (`bwrap`), Linux namespaces, cgroups v2.",
    "crates/nebu-runtime-daemon, crates/nebu-runtime-core.",
    "`neburuntimed` systemd service and `nebu` CLI.",
    "1. Build PE32/PE32+ binary parser in Rust.\n2. Implement Bubblewrap container generator.\n3. Build D-Bus service `org.nebu.Runtime1`.\n4. Implement cgroup process monitoring and log collector.",
    "Sandbox security escape test; PE parsing fuzzing suite.",
    "Runtime daemon idle RAM < 15 MB; sandbox launch overhead < 10ms.",
    "Sandboxed process cannot read `~/.ssh` or write to root `/usr`.",
    "`nebu run app.exe` successfully spawns sandboxed environment.",
    "Clean process termination and crash signal interception.",
    "Sandbox mount leaks. Mitigation: Enforce `--unshare-all` and `--die-with-parent` flags."
)

# 07-p6.md
create_milestone_doc(
    "07-p6.md", "P6", "Windows Wine Integration",
    "Integrate upstream Wine runtimes, prefix templates, and Btrfs reflink provisioning.",
    "P5 Nebu Runtime Core.",
    "Upstream Wine binaries (Stable & Staging), Btrfs filesystem.",
    "crates/nebu-prefix-manager, `/usr/share/nebu/prefix-template`.",
    "Prefix provisioning engine and Wine runner.",
    "1. Package modular Wine 9.x runtime bundles.\n2. Generate golden prefix template during OS image build.\n3. Implement 150ms Btrfs reflink prefix cloning.\n4. Implement wineserver socket isolation.",
    "Test automated installation of 7-Zip and Notepad++.",
    "Prefix creation duration < 200 ms on SATA SSD.",
    "Prefix mounted with `nosuid,nodev`.",
    "7-Zip and Notepad++ install and launch cleanly from GUI.",
    "Prefixes remain completely isolated; uninstalling 7-Zip leaves zero residue.",
    "Wine prefix initialization race conditions. Mitigation: Use file locking on prefix template."
)

# 08-p7.md
create_milestone_doc(
    "08-p7.md", "P7", "Compatibility Database",
    "Implement the embedded SQLite database engine and profile resolution algorithm.",
    "P5 Nebu Runtime Core.",
    "SQLite 3, `rusqlite` crate.",
    "crates/nebu-compat-db, `/usr/share/nebu/compat.db`.",
    "Compatibility query client and profile catalog.",
    "1. Implement SQLite schema with WAL mode.\n2. Build profile resolution engine matching PE hashes.\n3. Implement JSON profile importer/exporter.\n4. Expose query methods over D-Bus.",
    "Benchmark 10,000 profile queries; test database migration scripts.",
    "Query latency < 2 ms for indexed lookup.",
    "Database file permissions read-only for normal applications; writable only by update daemon.",
    "NebuRuntime queries database to configure DLL overrides and Wine versions automatically.",
    "Zero filesystem scanning required during application lookup.",
    "Database corruption on power loss. Mitigation: WAL mode with `PRAGMA synchronous = NORMAL`."
)

# 09-p8.md
create_milestone_doc(
    "09-p8.md", "P8", "Patch Engine",
    "Implement `nebu-patcher` to manage declarative, reversible application compatibility patches.",
    "P7 Compatibility Database.",
    "Nebu prefix manager, SQLite database.",
    "crates/nebu-patcher.",
    "Transactional patching tool and library.",
    "1. Implement 9-tier patch hierarchy parser.\n2. Build registry patch injector (editing `.reg` files safely).\n3. Implement DLL shim and override applicator.\n4. Implement transactional patch rollback.",
    "Apply and rollback complex registry patch; verify byte-for-byte registry integrity.",
    "Patch execution duration < 50 ms per application launch.",
    "Patches strictly declarative; no arbitrary shell script execution permitted.",
    "NebuPatcher successfully applies and cleanly reverts target patches.",
    "Rollback leaves zero modified keys in prefix.",
    "Corrupted registry syntax breaking Wine. Mitigation: Validate `.reg` grammar prior to committing changes."
)

# 10-p9.md
create_milestone_doc(
    "10-p9.md", "P9", "Adaptive Graphics Subsystem",
    "Integrate DXVK, VKD3D-Proton, GPU detection, and hybrid GPU offloading.",
    "P6 Windows Wine Integration.",
    "Vulkan Loader, Mesa drivers, DXVK binaries, VKD3D binaries.",
    "crates/nebu-gpu-probe, graphics configuration scripts.",
    "GPU offloading engine and shader cache manager.",
    "1. Build `nebu-gpu-probe` using DRM device APIs.\n2. Configure DXVK and VKD3D dynamic injection.\n3. Implement hybrid GPU offload environment rules (`DRI_PRIME`, `__NV_PRIME_RENDER_OFFLOAD`).\n4. Implement persistent Vulkan shader cache directory.",
    "Run 3D benchmark (Unigine Superposition / 3D game) via DXVK; test hybrid switching.",
    "Zero compositor overhead in fullscreen scanout mode.",
    "Direct render nodes accessible unprivileged; card master node protected.",
    "AutoCAD 3D viewport renders smoothly with hardware acceleration.",
    "Shader cache reuses compiled pipelines across app restarts.",
    "GPU driver hang/reset under intense compute. Mitigation: Implement watchdog reset detection."
)

# 11-p10.md
create_milestone_doc(
    "11-p10.md", "P10", "Professional Applications Certification",
    "Certify Microsoft Office (2019/2021/2024), Autodesk AutoCAD 2024, Maya, and 3ds Max.",
    "P8 Patch Engine, P9 Adaptive Graphics.",
    "Commercial application installers (user-provided), Compatibility Lab rigs.",
    "data/profiles/microsoft/, data/profiles/autodesk/.",
    "Certified profiles and automated QA test scripts.",
    "1. Develop and tune Microsoft Office compatibility profile (Word, Excel, PowerPoint).\n2. Develop and tune Autodesk AutoCAD 2024 profile (DWG open/save, GPU viewport).\n3. Resolve COM/OLE and licensing daemon quirks.\n4. Execute 48-hour continuous stress test in Compatibility Lab.",
    "Run full Tier 1 & Tier 2 automated test suites; human exploratory QA validation.",
    "AutoCAD 3D viewport >= 60 FPS; Excel 500k-row calculation within 10% of native Windows speed.",
    "Sandbox boundaries prevent enterprise documents from leaking across prefixes.",
    "Office and AutoCAD awarded CERTIFIED status with passing test reports.",
    "Zero data corruption in saved DWG and DOCX files.",
    "Autodesk licensing service heartbeat failures. Mitigation: Stub licensing daemon via Wine service wrapper."
)

# 12-p11.md
create_milestone_doc(
    "12-p11.md", "P11", "Installer & Atomic Update System",
    "Create the graphical OS installer (Live USB) and transactional image update system.",
    "P4 Native Apps, P1 Base OS.",
    "`bootc`, `ostree`, GRUB2, Btrfs tools.",
    "crates/nebu-installer, `nebu-update-agent`.",
    "Live USB ISO installer and production update daemon.",
    "1. Implement native Rust graphical installer (disk partitioner, Btrfs formatter, bootc deployer).\n2. Implement background atomic update agent.\n3. Integrate GRUB BLS rollback triggers.\n4. Build Software Center update UI.",
    "Install NebuOS on bare metal from USB; trigger simulated power failure during OS update.",
    "Base OS installation duration < 5 minutes on NVMe SSD.",
    "Update images cryptographically verified via Sigstore before deployment.",
    "User can install NebuOS via 4-step wizard without terminal; updates rollback cleanly upon forced crash.",
    "Zero system unbootability after interrupted update.",
    "Partition table corruption on unusual NVMe drives. Mitigation: Extensive dry-run validation in installer."
)

# 13-p12.md
create_milestone_doc(
    "13-p12.md", "P12", "Performance & Production Hardening",
    "Validate low-end 4GB hardware performance, execute security audits, and achieve final production sign-off.",
    "All preceding milestones (P0 through P11).",
    "Compatibility Lab Rigs 1, 2, 3; external security audit tools.",
    "Production NebuOS 1.0 Release Image & Release Notes.",
    "NebuOS 1.0 General Availability (GA) Golden Image.",
    "1. Fine-tune Nebu Lite Mode on 4GB RAM Intel Celeron hardware.\n2. Conduct full penetration testing and sandbox escape audit.\n3. Measure cold/warm launch benchmarks across 50 applications.\n4. Finalize user documentation and release candidate verification.",
    "100% pass rate across Tier 0, Tier 1, and Tier 2 test suites.",
    "Idle RAM < 800 MB on 4GB machine; Boot duration < 5.0s on NVMe; Launcher latency < 100ms.",
    "Zero unresolved high/critical CVEs; SELinux policies active.",
    "All 102 PRD requirements validated with empirical evidence.",
    "NebuOS 1.0 Golden Image signed and published to Stable channel.",
    "Last-minute upstream kernel regression. Mitigation: Pin known-stable LTS kernel tag for 1.0 GA."
)

print("Roadmap documentation generated successfully.")
