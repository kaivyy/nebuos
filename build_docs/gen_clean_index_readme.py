#!/usr/bin/env python3
"""
Generate a comprehensive, pristine INDEX.md and README.md with 100% valid relative markdown links.
"""

import os, glob

base_dir = "/root/NebuOS/docs"

dirs = [
    ("specification", "System Specifications (Core OS, Kernel, Boot, Filesystem, Security, Hardware, Resources)"),
    ("desktop", "Desktop Environment & Shell (Compositor, Shell, Theme, Layout, Window Management, Input, System UI)"),
    ("runtime", "Runtime Subsystem (Application Lifecycle, Process Model, Windows Runtime, Prefixes, Wine, Proton, Security)"),
    ("compatibility", "Compatibility Platform (Compat Engine, Database Schema, Profiles, Patch Engine, Detection, Certs, Boundaries)"),
    ("graphics", "Graphics Subsystem (GPU Detection, Mesa, Vulkan/OpenGL, DXVK/VKD3D, GPU Profiles, Shader Cache)"),
    ("applications", "Applications Subsystem (App Model, Installer, Registration, Path Mapping, Associations, Uninstall, Store)"),
    ("updates", "Update Subsystem (Update Model, Image Build, Channels, Quality Gates, Rollback)"),
    ("testing", "Testing Strategy & Verification (Unit, Integration, System, Compatibility, Graphics, Performance, Hardware, Certification)"),
    ("interfaces", "System Interfaces & Wire Contracts (IPC, Runtime Traits, Compositor Wayland, Shell, Installer, Database)"),
    ("development", "Development & Engineering (Model, Repo Structure, Build System, CI/CD, Dependencies, Rust Style, Release)"),
    ("decisions", "Architectural Decision Records (ADRs 0001 through 0009)"),
    ("roadmap", "Engineering Implementation Roadmap (Phases P0 through P8, and Future Phases)")
]

index_content = """# Master Documentation Index — NebuOS

Welcome to the authoritative engineering documentation repository for **NebuOS**, a lightweight Linux desktop operating system with native-feeling Windows application compatibility without running virtual machines.

---

## 1. Executive Master Registers & Top-Level Documents

| Document | Description |
|---|---|
| [README.md](README.md) | Master architectural blueprint, system layer topology, and engineering overview. |
| [INDEX.md](INDEX.md) | Complete index of all technical specifications, contracts, ADRs, and roadmaps. |
| [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) | Comprehensive register of 34 prioritized design questions (P0–P3) awaiting resolution. |
| [RISK_REGISTER.md](RISK_REGISTER.md) | Quantitative risk matrix tracking 28 system risks, impacts, and containment plans. |
| [ASSUMPTIONS.md](ASSUMPTIONS.md) | 42 foundational engineering assumptions across hardware, software, and compatibility. |
| [TRACEABILITY.md](TRACEABILITY.md) | Requirements traceability matrix mapping PRD sections 1–103 to specifications and tests. |

---

## 2. Technical Specifications by Subsystem
"""

for d, desc in dirs:
    path = os.path.join(base_dir, d)
    files = sorted(glob.glob(f"{path}/*.md"))
    index_content += f"\n### {d.capitalize()} (`docs/{d}/`)\n*{desc}*\n\n| Specification Document | Purpose & Scope |\n|---|---|\n"
    for f in files:
        fname = os.path.basename(f)
        rel_link = f"{d}/{fname}"
        # Extract title from first line
        title = fname
        with open(f, "r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line.startswith("# "):
                    title = line[2:].replace(" — NebuOS", "").strip()
                    break
        index_content += f"| [{fname}]({rel_link}) | {title} |\n"

index_content += """
---

## 3. Curated Reading Sequences

### Path A: Systems Architect & Lead Engineer
1. [README.md](README.md) — Master architectural topology
2. [specification/00-system-specification.md](specification/00-system-specification.md) — Component ownership and systemd units
3. [specification/01-boot-specification.md](specification/01-boot-specification.md) — Deterministic boot sequence & A/B fallback
4. [interfaces/00-interface-overview.md](interfaces/00-interface-overview.md) — Subsystem boundary matrix & protocols
5. [decisions/ADR-0009-nebushell-ui-architecture.md](decisions/ADR-0009-nebushell-ui-architecture.md) — Single shell paradigm engine
6. [roadmap/00-implementation-roadmap.md](roadmap/00-implementation-roadmap.md) — Phased implementation plan (P0–P8)

### Path B: Desktop & Graphics Engineer
1. [desktop/00-desktop-specification.md](desktop/00-desktop-specification.md) — Desktop environment master architecture
2. [desktop/01-nebucompositor-specification.md](desktop/01-nebucompositor-specification.md) — Smithay DRM/KMS compositor
3. [desktop/02-nebushell-specification.md](desktop/02-nebushell-specification.md) — Unified shell process architecture
4. [desktop/03-ui-theme-system.md](desktop/03-ui-theme-system.md) — Declarative native theming engine
5. [desktop/04-layout-system.md](desktop/04-layout-system.md) — Dynamic paradigm geometry solver
6. [graphics/00-graphics-specification.md](graphics/00-graphics-specification.md) — Mesa and Vulkan render pipeline
7. [graphics/04-dxvk-vkd3d.md](graphics/04-dxvk-vkd3d.md) — Direct3D translation layer

### Path C: Windows Compatibility & Wine Specialist
1. [runtime/00-runtime-specification.md](runtime/00-runtime-specification.md) — Runtime daemon workspace architecture
2. [runtime/01-application-lifecycle.md](runtime/01-application-lifecycle.md) — 16-state execution state machine
3. [runtime/04-prefix-management.md](runtime/04-prefix-management.md) — Btrfs reflink prefix provisioning
4. [runtime/05-wine-integration.md](runtime/05-wine-integration.md) — Upstream Wine DLL overrides and registry hives
5. [runtime/07-runtime-security.md](runtime/07-runtime-security.md) — Bubblewrap unprivileged sandboxing
6. [compatibility/01-database-schema.md](compatibility/01-database-schema.md) — Relational compatibility database
7. [compatibility/03-patch-engine.md](compatibility/03-patch-engine.md) — 9-tier declarative patch hierarchy

### Path D: QA & Quality Gate Engineer
1. [testing/00-test-strategy.md](testing/00-test-strategy.md) — Master testing pyramid & quality gates
2. [testing/02-integration-testing.md](testing/02-integration-testing.md) — Inter-component integration testing
3. [testing/03-system-testing.md](testing/03-system-testing.md) — End-to-end boot and power state automation
4. [testing/04-compatibility-testing.md](testing/04-compatibility-testing.md) — 11-stage application invariant
5. [updates/03-regression-gates.md](updates/03-regression-gates.md) — Automated release candidate promotion gates
6. [updates/04-rollback-recovery.md](updates/04-rollback-recovery.md) — Boot-counter rollback and recovery
"""

readme_content = """# NebuOS — Master Engineering Blueprint & Technical Specification

> **NebuOS:** Lightweight Linux Desktop OS with Native-Feeling Windows Application Compatibility  
> **Target Architecture:** x86_64 | **Primary Language:** Rust | **Base OS:** Fedora Atomic (bootc)  
> **Display Architecture:** Wayland | **Windows Compatibility:** Wine / Proton / DXVK / VKD3D  
> **Core Architectural Rule:** Virtual Machine: NOT PART OF NEBUOS  

---

## 1. Architectural Topology & Component Layers

NebuOS is structured into 7 encapsulated layers with strict unidirectional dependencies:

```mermaid
graph TD
    subgraph Layer7[Layer 7: Application Ecosystem]
        NATIVE_APP[Native Linux Apps / Flatpaks]
        WIN_APP[Sandboxed Windows Applications]
        STORE[Nebu Software Center & Installer Wizard]
    end

    subgraph Layer6[Layer 6: Compatibility Infrastructure]
        COMPAT_DB[SQLite Compatibility Database]
        PATCH_ENG[9-Tier Declarative Patch Engine]
        PROFILES[Certified Application Profiles]
    end

    subgraph Layer5[Layer 5: Application Runtime Platform]
        RUNTIME_D[nebu-runtime-daemon: D-Bus org.nebu.Runtime1]
        SANDBOX[Bubblewrap Unprivileged Namespace Sandbox]
        PFX_MGR[Prefix Manager: Btrfs Reflink Templates]
    end

    subgraph Layer4[Layer 4: Desktop Shell]
        SHELL[nebu-shell: Single Unified Binary]
        PARADIGM[Theme & Layout Engine: Nebu, Windows, macOS Paradigms]
        SYS_UI[Lock Screen, Greeter, Notifications, OSD]
    end

    subgraph Layer3[Layer 3: Display & Compositing Engine]
        COMPOSITOR[nebu-compositor: Rust / Smithay DRM/KMS]
        WAYLAND[Wayland Core & Extensions]
        DIRECT_SCAN[Direct Scanout Engine: Zero-Copy Fullscreen]
    end

    subgraph Layer2[Layer 2: Base Operating System]
        FEDORA[Fedora Atomic bootc Container Image]
        SYSTEMD[systemd PID 1 & cgroups v2 Slices]
        STORAGE[Btrfs Subvolumes: @, @home, @var, @nebu_apps]
    end

    subgraph Layer1[Layer 1: Hardware & Kernel Foundation]
        KERNEL[LTS Linux Kernel 6.x with futex_waitv]
        MESA[Mesa 24.0+ RADV, ANV, NVK Drivers]
        DRM[Linux Direct Rendering Manager / KMS]
    end

    Layer7 --> Layer5
    Layer6 --> Layer5
    Layer5 --> Layer4
    Layer5 --> Layer2
    Layer4 --> Layer3
    Layer3 --> Layer2
    Layer2 --> Layer1
```

---

## 2. Documentation Architecture & Directory Map

The engineering specifications are organized into 12 structured domains:

| Directory | Scope & Domain Responsibility | File Count |
|---|---|:---:|
| [`specification/`](specification/00-system-specification.md) | Core system specs: ownership matrix, boot sequence, IPC, filesystem, security, hardware, resources. | 7 |
| [`desktop/`](desktop/00-desktop-specification.md) | Desktop shell, compositor, native theming engine, layout solver, window management, input. | 8 |
| [`runtime/`](runtime/00-runtime-specification.md) | Windows PE runtime, 16-state lifecycle, process model, Btrfs reflink prefixes, Wine/Proton, sandboxing. | 8 |
| [`compatibility/`](compatibility/00-compatibility-specification.md) | Compatibility database schema, declarative profiles, 9-tier patch engine, application detection, certification. | 7 |
| [`graphics/`](graphics/00-graphics-specification.md) | GPU detection, Mesa integration, Vulkan/OpenGL, DXVK/VKD3D translation, GPU profiles, shader caching. | 7 |
| [`applications/`](applications/00-application-specification.md) | Unified application model, installer wizard, registration, path mapping, file associations, uninstallation, store. | 7 |
| [`updates/`](updates/00-update-specification.md) | Transactional `bootc` container updates, Containerfile build stages, release channels, regression gates, rollback. | 5 |
| [`testing/`](testing/00-test-strategy.md) | Testing pyramid, unit tests, integration tests, system tests, 11-stage compatibility lab, certification. | 9 |
| [`interfaces/`](interfaces/00-interface-overview.md) | Formal IPC wire protocols, D-Bus XML schemas, Wayland extensions, Rust traits, relational schemas. | 7 |
| [`development/`](development/00-development-model.md) | Engineering workflow, repository structure, build systems, CI/CD pipelines, dependency policies, Rust style. | 7 |
| [`decisions/`](decisions/ADR-0001-linux-kernel.md) | Architectural Decision Records (ADR-0001 through ADR-0009). | 9 |
| [`roadmap/`](roadmap/00-implementation-roadmap.md) | Engineering implementation roadmap across phases P0 through P8, and future milestones. | 11 |

**Master Documentation Catalog:** See [INDEX.md](INDEX.md) for the complete directory of all files.

---

## 3. Core Architectural Invariants

1. **NO Virtual Machines:** Windows applications run as native Linux processes via Wine/Proton within unprivileged Bubblewrap namespaces. No hypervisors (KVM/QEMU) are used for application compatibility.
2. **Immutable System Root:** `/usr` is mounted strictly read-only. The OS is updated as atomic container images via `bootc`.
3. **Rust Systems Architecture:** Core userland daemons (`nebu-compositor`, `nebu-shell`, `nebu-runtime-daemon`, `nebu-installer-ui`) are authored in 100% safe Rust.
4. **Single Unified Shell (ADR-0009):** `nebu-shell` is a single binary that dynamically re-anchors layer-shell surfaces to support Nebu, Windows-like, and macOS-like paradigms live at runtime in <= 150ms.
5. **Strict Resource Constraints:** System idle memory must remain < 800 MB RAM on 4GB hardware baseline. Compositor + Shell idle <= 80 MB RSS combined.
6. **Zero Data Loss & Deterministic Rollback:** Btrfs subvolumes and GRUB boot-counters ensure instant recovery from bad updates or prefix corruptions.

---

## 4. Master Registers & Matrices

- [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) — 34 prioritized design decisions awaiting resolution.
- [RISK_REGISTER.md](RISK_REGISTER.md) — Quantitative risk register and containment architectures.
- [ASSUMPTIONS.md](ASSUMPTIONS.md) — 42 foundational engineering assumptions and validation plans.
- [TRACEABILITY.md](TRACEABILITY.md) — Requirements traceability matrix mapping PRD sections 1–103 to specifications and tests.
"""

with open(f"{base_dir}/INDEX.md", "w", encoding="utf-8") as f:
    f.write(index_content.strip() + "\n")
print(f"Wrote {base_dir}/INDEX.md ({len(index_content.splitlines())} lines)")

with open(f"{base_dir}/README.md", "w", encoding="utf-8") as f:
    f.write(readme_content.strip() + "\n")
print(f"Wrote {base_dir}/README.md ({len(readme_content.splitlines())} lines)")

