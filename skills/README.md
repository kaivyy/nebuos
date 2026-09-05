# NebuOS Modular Agent Skills Catalog

**Catalog Authority:** Operational Workflow Guides for Engineering Agents  
**Status:** ACTIVE  

---

## 1. Purpose of Skills in NebuOS

Skills are specialized operational guides that teach human developers and AI coding agents **HOW TO WORK** within specific domains of the NebuOS project.
- **Skills are NOT sources of truth:** Architectural decisions come from `docs/decisions/` (ADRs), requirements come from `PRD.md`, and technical schemas come from `docs/specification/`.
- **Skills explain workflow and constraints:** They define domain boundaries, allowed/forbidden changes, mandatory verification procedures, common failure modes, and handoff expectations.
- **Read on Demand:** Agents should **ONLY** read skills directly relevant to their active task. Do not exhaust context by ingesting all skills indiscriminately.

---

## 2. Skill Discovery Catalog

| Domain Directory | Skill Name | Target Milestones | Primary Scope & Focus |
|---|---|---|---|
| [`architecture/`](architecture/SKILL.md) | Architecture Governance | All (P0–P8) | System layering, milestone boundaries, ADR rules, conflict protocol, traceability |
| [`rust/`](rust/SKILL.md) | Rust Systems Engineering | P1, P2, P3, P4 | Idiomatic Rust, error propagation, minimal unsafe, clippy, cargo policies |
| [`system/`](system/SKILL.md) | Base OS & System Services | P0, P8 | Fedora 44 Atomic / bootc, Btrfs subvolumes, systemd, dracut (no Plymouth), GRUB/BLS, silent boot cmdline, TTY |
| [`compositor/`](compositor/SKILL.md) | Wayland Compositor | P1 | Smithay 0.3+, DRM/KMS, BGRT scanout plane inheritance, atomic handover, libinput, Mesa, pure Wayland |
| [`shell/`](shell/SKILL.md) | Desktop Shell & UI | P2 | NebuShell, Slint, Design System tokens, NebuIcon, boot splash/cross-fade, Theme vs Layout vs Behavior |
| [`runtime/`](runtime/SKILL.md) | Windows App Runtime | P3 | Wine 9.x, Proton, per-app prefix isolation, Btrfs reflink, bwrap sandbox |
| [`compatibility/`](compatibility/SKILL.md) | Compatibility Platform | P4, P7 | SQLite compat DB, PE fingerprinting, patch engine DSL, certification tiers |
| [`graphics/`](graphics/SKILL.md) | 3D Graphics & Drivers | P5 | Mesa, Vulkan, OpenGL, DXVK, VKD3D-Proton, PRIME hybrid GPU, shader cache |
| [`application/`](application/SKILL.md) | Application Platform & Store | P6, P8 | Flatpak, Flathub, Nebu App Manager, Marketplace, permission model, security |
| [`security/`](security/SKILL.md) | Security & Containment | All (P0–P8) | SELinux (permissive->enforcing), Bubblewrap, seccomp BPF, capabilities, namespaces |
| [`testing/`](testing/SKILL.md) | Verification & Testing | All (P0–P8) | Test pyramid, boot testing, compatibility lab, Tested vs Verified vs Accepted |
| [`performance/`](performance/SKILL.md) | Performance Engineering | All (P0–P8) | Benchmarking methodology, latency budgets, idle memory limits, regression gates |
| [`documentation/`](documentation/SKILL.md) | Documentation Sync | All (P0–P8) | Doc synchronization, drift detection, traceability, ADR authoring |
| [`release/`](release/SKILL.md) | Release & Updates | P0, P8 | bootc image build, ostree deployment, signing, automatic rollback, recovery boot mode |
| [`p0-build-test/`](p0-build-test/SKILL.md) | P0 Build & Boot Verification | P0 | End-to-end P0 lifecycle: build, container validate, disk image generation, QEMU boot, health gate, evidence logs |

---

## 3. Mandatory Structure of Every SKILL.md

Every skill file adheres strictly to a 10-section schema:
1. **Purpose:** Why this skill exists and what problems it solves.
2. **Scope:** Target milestone and subsystems covered.
3. **Relevant Documentation:** Authoritative specifications and ADRs governing this domain.
4. **Allowed Changes:** Exact files and components permitted to be modified.
5. **Forbidden Changes:** Explicitly prohibited edits, anti-scope, and destructive actions.
6. **Architecture Constraints:** Invariants, protocols, and technical dependencies.
7. **Implementation Guidance:** Best practices, coding conventions, and design patterns.
8. **Verification:** Concrete commands, test scenarios, and evidence collection.
9. **Common Failure Modes:** Recurring pitfalls, subtle bugs, and how to avoid them.
10. **Handoff Requirements:** Mandatory reporting fields before yielding to the next agent.
