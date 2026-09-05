# Wayland Compositor Engineering Skill — NebuOS

## 1. Purpose
Governs the design, implementation, and maintenance of `nebu-compositor`, the pure-Rust Wayland display compositor built upon the Smithay framework.

## 2. Scope
Applies strictly to Milestone P1 (NebuCompositor) and its subsequent integration points.

## 3. Relevant Documentation
- `docs/roadmap/02-p1-nebucompositor.md`: Milestone P1 execution blueprint.
- `docs/desktop/01-compositor.md`: Compositor architectural overview.
- `docs/desktop/01-nebucompositor-specification.md`: Implementation specification for compositor.
- `docs/interfaces/03-compositor-interfaces.md`: Wayland protocol definitions.
- `docs/decisions/ADR-0003-smithay-wayland-compositor.md`: Smithay architecture decision.
- `docs/decisions/ADR-0014-boot-experience-and-graphical-handoff.md`: Boot experience and graphical handoff.

## 4. Allowed Changes
- Implementing compositor source code under `crates/nebu-compositor/`.
- Authoring Wayland protocol extension XML and generated bindings.
- Configuring DRM/KMS backend pipelines and libinput event loops.

## 5. Forbidden Changes
- **DO NOT WORK IN P0:** This skill is **LOCKED** until Milestone P0 passes all exit gates.
- **NO SHELL WIDGETS IN COMPOSITOR:** The compositor handles display surfaces and window trees; desktop UI (taskbars, docks, launchers) belongs strictly in `nebu-shell`.
- **NO IN-PROCESS WINE EXECUTION:** The compositor does not launch or supervise Windows applications directly.

## 6. Architecture Constraints
- Framework: Smithay 0.3+ in pure Rust.
- Core Protocols: `xdg-shell`, `wlr-layer-shell-unstable-v1`, `linux-dmabuf-v1`, `viewporter`, `fractional-scale-v1`.
- Display Target: Direct DRM/KMS takeover (seatd / logind).
- Graphical Handoff (ADR-0014): Inherit active EFI framebuffer scanout plane from SimpleDRM (guided by BGRT metadata) without VT toggling or display power cycling; stage initial frame and commit atomically under the scanout preservation principle (avoiding unnecessary modeset when compatible, while permitting clean atomic modeset if hardware requires link retraining) for flicker-free boot transition.
- Legacy Apps: Rootless Xwayland spawned exclusively on-demand.

## 7. Implementation Guidance
- Implement strict damage tracking to eliminate unnecessary frame repaints and preserve CPU/GPU power.
- Expose window management state to the shell via D-Bus interface `org.nebu.Compositor1`.
- Keep memory footprint strictly under 60 MB RSS.

## 8. Verification
- Headless compositor test running under `Winit` or virtual DRM backend.
- Wayland client compliance verification using `weston-simple-shm` and `weston-terminal`.
- Frame timing verification: 60 FPS presentation without frame drops.

## 9. Common Failure Modes
- Zombie Xwayland processes lingering after legacy client termination.
- Deadlocks in event loops when waiting on D-Bus synchronous calls.

## 10. Handoff Requirements
- Record verified Wayland protocol versions and client test execution results in `HANDOFF.md`.
