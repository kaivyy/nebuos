# Master Documentation Index — NebuOS

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
| [audit/DOCUMENTATION_AUDIT_REPORT.md](audit/DOCUMENTATION_AUDIT_REPORT.md) | Master documentation audit and forensic verification report (27 sections, P0 readiness assessment). |
| [audit/P0_READY_GATE.md](audit/P0_READY_GATE.md) | Formal P0 Ready Gate Verification Report (37 audit steps, architectural boundaries, acceptance matrix). |
| [audit/AGENT_GOVERNANCE_AUDIT.md](audit/AGENT_GOVERNANCE_AUDIT.md) | Forensic audit report of repository agent governance architecture (16 dimensions, multi-agent safety). |
| [audit/HARDWARE_COMPATIBILITY_ENHANCEMENT_AUDIT.md](audit/HARDWARE_COMPATIBILITY_ENHANCEMENT_AUDIT.md) | Comprehensive audit report of hardware compatibility, laptop validation, and power management architecture. |
| [audit/HARDWARE_COMPATIBILITY_TECHNICAL_HARDENING_AUDIT.md](audit/HARDWARE_COMPATIBILITY_TECHNICAL_HARDENING_AUDIT.md) | Second-Pass Technical Hardening Audit Report (requirements taxonomy, power feasibility, GPU reality, P0 independence). |
| [audit/OS_UPDATE_ARCHITECTURE_ENHANCEMENT_AUDIT.md](audit/OS_UPDATE_ARCHITECTURE_ENHANCEMENT_AUDIT.md) | Comprehensive OS Update Architecture & bootc Integration Audit Report (transactional mechanics, release engineering, rollback). |
| [audit/FEDORA_44_BASELINE_AUDIT.md](audit/FEDORA_44_BASELINE_AUDIT.md) | Comprehensive Fedora 44 Baseline Foundation Audit Report (P0 baseline alignment, bootc, kernel 6.14+, systemd 256+, immutability). |
| [audit/AGENTS_SKILLS_ALIGNMENT_AUDIT.md](audit/AGENTS_SKILLS_ALIGNMENT_AUDIT.md) | Comprehensive Agents & Skills Alignment Audit Report (AGENTS.md, 13 skills, agent configurations, Fedora 44, digest pinning, minimal change principle). |
| [audit/APPLICATION_PLATFORM_MARKETPLACE_ENHANCEMENT_AUDIT.md](audit/APPLICATION_PLATFORM_MARKETPLACE_ENHANCEMENT_AUDIT.md) | Comprehensive Application Platform & Nebu Marketplace Phase Enhancement Audit Report (Flatpak, Flathub, App Manager, security, P6 subphases). |
| [audit/UI_DESIGN_AND_ICON_ARCHITECTURE_AUDIT.md](audit/UI_DESIGN_AND_ICON_ARCHITECTURE_AUDIT.md) | Comprehensive UI/UX, Design System, Iconography & Phase Ownership Enhancement Audit Report (ADR-0013, design tokens, NebuIcon, tripartite shell, Slint native). |
| [audit/BOOT_EXPERIENCE_ARCHITECTURE_AUDIT.md](audit/BOOT_EXPERIENCE_ARCHITECTURE_AUDIT.md) | Comprehensive Boot Experience Architecture, Lifecycle & Graphical Handoff Audit Report (ADR-0014, 10-stage lifecycle, 3 boot modes, BGRT handover, silent cmdline, P0 headless boundary). |
| [audit/P1_FINAL_VALIDATION_AUDIT.md](audit/P1_FINAL_VALIDATION_AUDIT.md) | Milestone P1.8: Final Compositor Stack Validation, Security Audit & P1 Baseline Lock Report. |

### Phase P1 Milestone Empirical Proof Reports (`docs/p1/`)

| Verification Report | Milestone & Purpose |
|---|---|
| [p1/P1_1_IMPLEMENTATION_NOTE.md](p1/P1_1_IMPLEMENTATION_NOTE.md) | Milestone P1.1: Minimal Rust Workspace & NebuCompositor Skeleton Implementation Note. |
| [p1/P1_2_DRM_KMS_PROOF.md](p1/P1_2_DRM_KMS_PROOF.md) | Milestone P1.2: DRM/KMS Device Management & Atomic Modesetting Verification Report. |
| [p1/P1_3_RENDERER_INITIALIZATION_PROOF.md](p1/P1_3_RENDERER_INITIALIZATION_PROOF.md) | Milestone P1.3: GBM, EGL & OpenGL ES Renderer Initialization Verification Report. |
| [p1/P1_4_OUTPUT_PRESENTATION_EVENT_LOOP_PROOF.md](p1/P1_4_OUTPUT_PRESENTATION_EVENT_LOOP_PROOF.md) | Milestone P1.4: Output Presentation & Calloop Event Loop Reactor Verification Report. |
| [p1/P1_5_INPUT_SUBSYSTEM_INTEGRATION_PROOF.md](p1/P1_5_INPUT_SUBSYSTEM_INTEGRATION_PROOF.md) | Milestone P1.5: Input Subsystem, Device Discovery & Key Translation Verification Report. |
| [p1/P1_6_WAYLAND_CORE_SURFACE_LIFECYCLE_PROOF.md](p1/P1_6_WAYLAND_CORE_SURFACE_LIFECYCLE_PROOF.md) | Milestone P1.6: Wayland Core Display Server & Surface Lifecycle Verification Report. |
| [p1/P1_7_SURFACE_PRESENTATION_SCENE_RENDERING_PROOF.md](p1/P1_7_SURFACE_PRESENTATION_SCENE_RENDERING_PROOF.md) | Milestone P1.7: Surface Presentation, Scene Rendering & Safe Framebuffer Readback Verification Report. |

---

## 2. Technical Specifications by Subsystem

### Specification (`docs/specification/`)
*System Specifications (Core OS, Kernel, Boot, Filesystem, Security, Hardware, Resources)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-system-specification.md](specification/00-system-specification.md) | System Specification |
| [01-boot-specification.md](specification/01-boot-specification.md) | Boot Specification |
| [02-process-ipc-specification.md](specification/02-process-ipc-specification.md) | Process and IPC Specification |
| [03-filesystem-specification.md](specification/03-filesystem-specification.md) | Filesystem Specification |
| [04-security-specification.md](specification/04-security-specification.md) | Security Specification |
| [05-hardware-specification.md](specification/05-hardware-specification.md) | Hardware Specification |
| [06-resource-management.md](specification/06-resource-management.md) | Resource Management Specification |

### Desktop (`docs/desktop/`)
*Desktop Environment & Shell (Compositor, Shell, Theme, Layout, Window Management, Input, System UI)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-desktop-specification.md](desktop/00-desktop-specification.md) | Desktop Subsystem Specification |
| [01-nebucompositor-specification.md](desktop/01-nebucompositor-specification.md) | NebuCompositor Technical Specification |
| [02-nebushell-specification.md](desktop/02-nebushell-specification.md) | NebuShell Technical Specification |
| [03-ui-theme-system.md](desktop/03-ui-theme-system.md) | UI Theme System Specification |
| [04-layout-system.md](desktop/04-layout-system.md) | Layout System Specification |
| [05-window-management.md](desktop/05-window-management.md) | Window Management Specification |
| [06-input-display.md](desktop/06-input-display.md) | Input and Display Management Specification |
| [07-system-ui.md](desktop/07-system-ui.md) | System UI Components Specification |

### Design & Iconography (`docs/design/`)
*UI/UX Design System, Design Tokens, Iconography, Tripartite Architecture, Components, Accessibility, and Asset Licensing*

| Specification Document | Purpose & Scope |
|---|---|
| [README.md](design/README.md) | Master Design Subsystem Overview and Reading Paths |
| [00-design-system.md](design/00-design-system.md) | Master Design System & Design Tokens Specification |
| [01-iconography.md](design/01-iconography.md) | Iconography Architecture & Asset Pipeline Specification |
| [02-theming-layout-behavior.md](design/02-theming-layout-behavior.md) | Tripartite Desktop Architecture Specification (Theme, Layout, Behavior) |
| [03-components.md](design/03-components.md) | Component Taxonomy & UI Architecture Specification |
| [04-accessibility-and-performance.md](design/04-accessibility-and-performance.md) | Accessibility & Performance Engineering Specification |
| [05-external-assets-and-licensing.md](design/05-external-assets-and-licensing.md) | External Asset Governance & Licensing Policy Specification |

### Runtime (`docs/runtime/`)
*Runtime Subsystem (Application Lifecycle, Process Model, Windows Runtime, Prefixes, Wine, Proton, Security)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-runtime-specification.md](runtime/00-runtime-specification.md) | Runtime Master Specification |
| [01-application-lifecycle.md](runtime/01-application-lifecycle.md) | Application Lifecycle Specification |
| [02-process-model.md](runtime/02-process-model.md) | Process Supervision and Cgroups Model |
| [03-windows-runtime.md](runtime/03-windows-runtime.md) | Windows Runtime Execution Specification |
| [04-prefix-management.md](runtime/04-prefix-management.md) | Prefix Management and Reflink Snapshot Specification |
| [05-wine-integration.md](runtime/05-wine-integration.md) | Wine and Proton Integration Specification |
| [06-proton-integration.md](runtime/06-proton-integration.md) | Proton Integration Specification |
| [07-runtime-security.md](runtime/07-runtime-security.md) | Runtime Sandboxing and Security Specification |
| [08-nebuwine-specification.md](runtime/08-nebuwine-specification.md) | NebuWine Downstream Distribution & Upstream Lifecycle Specification |

### Compatibility (`docs/compatibility/`)
*Compatibility Platform (Compat Engine, Database Schema, Profiles, Patch Engine, Detection, Certs, Boundaries)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-compatibility-specification.md](compatibility/00-compatibility-specification.md) | Compatibility Platform Master Specification |
| [01-database-schema.md](compatibility/01-database-schema.md) | Compatibility Database Schema Specification |
| [02-compatibility-profile.md](compatibility/02-compatibility-profile.md) | Compatibility Profile Specification |
| [03-patch-engine.md](compatibility/03-patch-engine.md) | Patch Engine Specification (Domain B: Prefix Remediation) |
| [04-application-detection.md](compatibility/04-application-detection.md) | Application Detection Specification |
| [05-certification-model.md](compatibility/05-certification-model.md) | Compatibility Certification Model Specification |
| [06-known-limitations.md](compatibility/06-known-limitations.md) | Known Limitations & Non-Compatibility Boundaries Specification |
| [07-wine-patch-governance.md](compatibility/07-wine-patch-governance.md) | Wine Source Patch Governance & Upstream Equivalence Specification (Domain A) |

### Graphics (`docs/graphics/`)
*Graphics Subsystem (GPU Detection, Mesa, Vulkan/OpenGL, DXVK/VKD3D, GPU Profiles, Shader Cache)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-graphics-specification.md](graphics/00-graphics-specification.md) | Master Graphics Specification |
| [01-gpu-detection.md](graphics/01-gpu-detection.md) | GPU Detection Specification |
| [02-mesa-integration.md](graphics/02-mesa-integration.md) | Mesa Driver Integration Specification |
| [03-vulkan-opengl.md](graphics/03-vulkan-opengl.md) | Vulkan and OpenGL Architecture Specification |
| [04-dxvk-vkd3d.md](graphics/04-dxvk-vkd3d.md) | DXVK and VKD3D-Proton Translation Layer Specification |
| [05-gpu-profiles.md](graphics/05-gpu-profiles.md) | GPU Profiles Specification |
| [06-shader-cache.md](graphics/06-shader-cache.md) | Shader Cache Specification |

### Applications (`docs/applications/`)
*Applications Subsystem (App Model, Installer, Registration, Path Mapping, Associations, Uninstall, Store)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-application-specification.md](applications/00-application-specification.md) | Master Application Platform Specification |
| [01-installer.md](applications/01-installer.md) | Installer Subsystem Specification |
| [02-application-registration.md](applications/02-application-registration.md) | Application Registration Specification |
| [03-filesystem-mapping.md](applications/03-filesystem-mapping.md) | Filesystem Mapping Specification |
| [04-file-associations.md](applications/04-file-associations.md) | File Associations Specification |
| [05-uninstallation.md](applications/05-uninstallation.md) | Application Uninstallation Specification |
| [06-software-center.md](applications/06-software-center.md) | Nebu Marketplace Specification |
| [07-app-manager-specification.md](applications/07-app-manager-specification.md) | Nebu App Manager Daemon Specification |
| [08-developer-platform-and-security.md](applications/08-developer-platform-and-security.md) | Developer Platform & Application Security Specification |

### Updates (`docs/updates/`)
*Update Subsystem (Update Model, Image Build, Channels, Quality Gates, Rollback)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-update-specification.md](updates/00-update-specification.md) | Update Subsystem Specification |
| [01-image-build.md](updates/01-image-build.md) | Image Build Specification |
| [02-release-channels.md](updates/02-release-channels.md) | Release Channels Specification |
| [03-regression-gates.md](updates/03-regression-gates.md) | Regression Gates Specification |
| [04-rollback-recovery.md](updates/04-rollback-recovery.md) | Rollback and Recovery Specification |

### Testing (`docs/testing/`)
*Testing Strategy & Verification (Unit, Integration, System, Compatibility, Graphics, Performance, Hardware, Certification)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-test-strategy.md](testing/00-test-strategy.md) | Master Testing Specification |
| [01-unit-testing.md](testing/01-unit-testing.md) | Unit Testing Specification |
| [02-integration-testing.md](testing/02-integration-testing.md) | Integration Testing Specification |
| [03-system-testing.md](testing/03-system-testing.md) | System Testing Specification |
| [04-compatibility-testing.md](testing/04-compatibility-testing.md) | Compatibility Testing Specification |
| [05-graphics-testing.md](testing/05-graphics-testing.md) | Graphics Testing Specification |
| [06-performance-testing.md](testing/06-performance-testing.md) | Performance Testing Specification |
| [07-hardware-testing.md](testing/07-hardware-testing.md) | Hardware Testing Specification |
| [08-release-certification.md](testing/08-release-certification.md) | Release Certification Specification |
| [09-compatibility-lab-specification.md](testing/09-compatibility-lab-specification.md) | Compatibility Lab Architecture & Automated Testing Farm Specification |

### Interfaces (`docs/interfaces/`)
*System Interfaces & Wire Contracts (IPC, Runtime Traits, Compositor Wayland, Shell, Installer, Database)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-interface-overview.md](interfaces/00-interface-overview.md) | Interface Architecture & IPC Overview Specification |
| [01-ipc-interfaces.md](interfaces/01-ipc-interfaces.md) | D-Bus IPC Interface Specification |
| [02-runtime-interfaces.md](interfaces/02-runtime-interfaces.md) | Runtime Engine Trait & Internal API Specification |
| [03-compositor-interfaces.md](interfaces/03-compositor-interfaces.md) | Compositor Wayland & DRM/KMS Interface Specification |
| [04-shell-interfaces.md](interfaces/04-shell-interfaces.md) | Shell Subsystem Interfaces & Protocols Specification |
| [05-installer-interfaces.md](interfaces/05-installer-interfaces.md) | Application Installer & Binary Analysis Interface Specification |
| [06-database-interfaces.md](interfaces/06-database-interfaces.md) | Compatibility Database Relational Schema & Access Interface Specification |
| [07-update-interfaces.md](interfaces/07-update-interfaces.md) | Update Subsystem D-Bus IPC & Service Traits Specification |
| [08-system-api-interfaces.md](interfaces/08-system-api-interfaces.md) | System API Subsystem Interfaces Specification |

### Development (`docs/development/`)
*Development & Engineering (Model, Repo Structure, Build System, CI/CD, Dependencies, Rust Style, Release)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-development-model.md](development/00-development-model.md) | Master Development Specification |
| [01-repository-structure.md](development/01-repository-structure.md) | Repository Structure Specification |
| [02-build-system.md](development/02-build-system.md) | Build System Specification |
| [03-ci-cd.md](development/03-ci-cd.md) | CI/CD Pipeline Specification |
| [04-dependency-policy.md](development/04-dependency-policy.md) | Dependency Policy Specification |
| [05-rust-guidelines.md](development/05-rust-guidelines.md) | Coding Guidelines Specification |
| [06-release-engineering.md](development/06-release-engineering.md) | Release Engineering Specification |

### Decisions (`docs/decisions/`)
*Architectural Decision Records (ADRs 0001 through 0019)*

| Specification Document | Purpose & Scope |
|---|---|
| [ADR-0001-linux-kernel.md](decisions/ADR-0001-linux-kernel.md) | ADR-0001: Standard LTS Linux Kernel as Hardware and Operating System Foundation |
| [ADR-0002-fedora-base.md](decisions/ADR-0002-fedora-base.md) | ADR-0002: Fedora Atomic / Image-Based Base Operating System |
| [ADR-0003-wayland.md](decisions/ADR-0003-wayland.md) | ADR-0003: Pure Wayland Display Architecture and Rejection of X11 |
| [ADR-0004-rust.md](decisions/ADR-0004-rust.md) | ADR-0004: Rust as Primary Implementation Language for Core Components |
| [ADR-0005-wine.md](decisions/ADR-0005-wine.md) | ADR-0005: Upstream Wine as Core Windows Application Compatibility Engine |
| [ADR-0006-proton.md](decisions/ADR-0006-proton.md) | ADR-0006: Proton and DXVK/VKD3D Integration for 3D and Gaming Workloads |
| [ADR-0007-no-vm.md](decisions/ADR-0007-no-vm.md) | ADR-0007: Absolute Prohibition of Virtual Machines for Windows Compatibility |
| [ADR-0008-atomic-updates.md](decisions/ADR-0008-atomic-updates.md) | ADR-0008: Atomic Image Deployments and Btrfs Subvolume Topology |
| [ADR-0009-nebushell-ui-architecture.md](decisions/ADR-0009-nebushell-ui-architecture.md) | ADR-0009: NebuShell UI Architecture — Pluggable Paradigm Engine (Theme, Layout, and Behavior) |
| [ADR-0010-hardware-compatibility-and-power-management.md](decisions/ADR-0010-hardware-compatibility-and-power-management.md) | ADR-0010: Real-World Hardware Compatibility, Laptop-First Platform, and Power Management Architecture |
| [ADR-0011-os-image-updates-and-rollback.md](decisions/ADR-0011-os-image-updates-and-rollback.md) | ADR-0011: Operating System Image Updates, bootc Transactional Deployments, and Automated Rollback Architecture |
| [ADR-0012-application-distribution-and-marketplace.md](decisions/ADR-0012-application-distribution-and-marketplace.md) | ADR-0012: NebuOS Application Distribution and Marketplace Architecture |
| [ADR-0013-ui-design-system-and-icon-architecture.md](decisions/ADR-0013-ui-design-system-and-icon-architecture.md) | ADR-0013: NebuOS UI Design System, Iconography, and Desktop Visual Architecture |
| [ADR-0014-boot-experience-and-graphical-handoff.md](decisions/ADR-0014-boot-experience-and-graphical-handoff.md) | ADR-0014: NebuOS Boot Experience Architecture and Graphical Handoff |
| [ADR-0015-compatibility-lab.md](decisions/ADR-0015-compatibility-lab.md) | ADR-0015: Compatibility Lab Architecture and Automated Testing Farm |
| [ADR-0016-nebuwine-architecture.md](decisions/ADR-0016-nebuwine-architecture.md) | ADR-0016: NebuWine Downstream Distribution Architecture and Upstream-First Lifecycle |
| [ADR-0017-decoupled-runtime-packaging-and-storage.md](decisions/ADR-0017-decoupled-runtime-packaging-and-storage.md) | ADR-0017: Decoupled Compatibility Runtime Packaging and Storage Strategy |
| [ADR-0018-gaming-runtime-architecture.md](decisions/ADR-0018-gaming-runtime-architecture.md) | ADR-0018: NebuWine Gaming Runtime Architecture and Graphics Translation Pipeline |
| [ADR-0019-slint-toolkit-adoption.md](decisions/ADR-0019-slint-toolkit-adoption.md) | ADR-0019: Slint Adoption for NebuShell Desktop Toolkit |

### Roadmap (`docs/roadmap/`)
*Engineering Implementation Roadmap (Phases P0 through P8, and Future Phases)*

| Specification Document | Purpose & Scope |
|---|---|
| [00-implementation-roadmap.md](roadmap/00-implementation-roadmap.md) | Master Implementation Roadmap (P0–P8) |
| [01-p0-foundation.md](roadmap/01-p0-foundation.md) | Phase P0: Foundation Specification |
| [02-p1-compositor.md](roadmap/02-p1-compositor.md) | Phase P1: NebuCompositor Specification |
| [03-p2-shell.md](roadmap/03-p2-shell.md) | Phase P2: NebuShell Specification |
| [04-p3-runtime.md](roadmap/04-p3-runtime.md) | Phase P3: NebuRuntime Specification |
| [05-p4-compatibility.md](roadmap/05-p4-compatibility.md) | Phase P4: Compatibility Subsystem Specification |
| [06-p5-graphics.md](roadmap/06-p5-graphics.md) | Phase P5: Graphics Subsystem Specification |
| [07-p6-applications.md](roadmap/07-p6-applications.md) | Phase P6: Applications Subsystem Specification |
| [08-p7-testing.md](roadmap/08-p7-testing.md) | Phase P7: Testing Subsystem Specification |
| [09-p8-production-validation.md](roadmap/09-p8-production-validation.md) | Phase P8: Production Validation Specification |
| [10-future-phases.md](roadmap/10-future-phases.md) | Future Phases Specification |

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
