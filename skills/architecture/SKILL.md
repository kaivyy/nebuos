# Architecture Governance Skill — NebuOS

## 1. Purpose
This skill governs how architects and agents maintain architectural integrity, enforce milestone boundaries, handle technical conflicts, and record architectural decisions (ADRs) across the NebuOS project.

## 2. Scope
Applies to all milestones (P0 through P8) and all top-level architectural documentation (`PRD.md`, `ARCHITECTURE.md`, `docs/decisions/`, `docs/roadmap/`).

## 3. Relevant Documentation
- `PRD.md`: Master Product Requirements and non-negotiable invariants.
- `ARCHITECTURE.md`: Conceptual layer topology and system navigation.
- `docs/decisions/ADR-0001` through `ADR-0013`: Approved architectural decisions.
- `docs/roadmap/00-implementation-roadmap.md`: Milestone dependency DAG.
- `docs/design/00-design-system.md` through `05-external-assets-and-licensing.md`: UI design specifications.

## 4. Allowed Changes
- Drafting new Architecture Decision Records (ADRs) in `docs/decisions/`.
- Updating `ARCHITECTURE.md` navigation links and layer diagrams.
- Maintaining requirements traceability in `docs/TRACEABILITY.md`.

## 5. Forbidden Changes
- **NO SILENT ARCHITECTURE CHANGES:** Never replace chosen components (e.g., swapping Smithay for wlroots, bootc for raw ostree, Slint for GTK) without an approved ADR.
- **NO VIRTUAL MACHINES:** Never introduce KVM/QEMU guest hypervisors for Windows compatibility.
- **NO PREMATURE IMPLEMENTATION:** Never implement future milestone features in early milestones.
- **NO SPECULATIVE ABSTRACTIONS:** Never introduce complex architectural layers, frameworks, or dependencies that are not strictly needed by the immediate task.

## 6. Architecture Constraints
- Maintain the strict layer hierarchy: Linux Kernel (6.14+) -> Fedora 44 bootc (`quay.io/fedora/fedora-bootc:44`) -> System Services -> Wayland -> Smithay -> NebuShell -> NebuRuntime -> Wine/Proton -> Windows Apps.
- Enforce strict milestone entry and exit criteria.
- **Milestone Isolation:** Scope is strictly partitioned across milestones (P0 through P8). Work on milestone P0 must remain purely headless foundation; future components (Wayland, Smithay, NebuShell, Wine, Proton, Marketplace) are strictly forbidden until their designated milestones.
- **Minimal Change Principle:** Prefer the smallest correct change. Reuse existing components, utilities, and standard conventions before adding abstractions or dependencies.
- **UI/UX & Design System Architecture (P2):** Governed by ADR-0013 and `docs/design/`. P0 remains strictly headless; P1 is Wayland compositor; P2 owns desktop UI design system, token engine, and icon abstraction (`NebuIcon`). Webviews and Electron are prohibited; Slint is the native UI standard.
- **Application Platform & Packaging Architecture (P6):** Rely on Flatpak and Flathub as the primary desktop application foundation. Do not create custom package managers or bespoke package formats without an approved ADR. Nebu App Manager serves as an abstraction layer; Marketplace UI never invokes package backends directly.
- **Update Lifecycle Separation:** OS updates (`bootc`), application updates (Flatpak), compatibility DB updates, and firmware (`fwupd`) operate on strictly independent lifecycles.

## 7. Implementation Guidance
- When resolving contradictions between docs: follow the Source of Truth Hierarchy (`PRD` > `ADRs` > `Specifications` > `Roadmap` > `Implementation`).
- Use the 9-step Conflict Protocol defined in `AGENTS.md` §5.
- Base image pinning: Production releases must pin immutable base image digests (`@sha256:...`); unversioned tags or `:latest` are prohibited.

## 8. Verification
- Validate cross-references across specifications with static link checkers.
- Confirm that every PRD requirement maps cleanly to at least one specification in `docs/TRACEABILITY.md`.

## 9. Common Failure Modes
- "Architectural Drift": Code implements an unapproved pattern because it was "easier" or "more modern".
- "Bypassing ADRs": Deciding to add a large dependency without documenting the trade-off.

## 10. Handoff Requirements
- Document any identified architectural discrepancies under `Known Issues` in `HANDOFF.md`.
- Report ADR status changes (Proposed, Accepted, Superseded).
