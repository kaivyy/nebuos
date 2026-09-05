# Desktop Shell & UI Engineering Skill — NebuOS

## 1. Purpose
Governs the development of `nebu-shell`, the unified, pluggable desktop shell environment providing panels, docks, application launchers, system tray, and notifications.

## 2. Scope
Applies strictly to Milestone P2 (NebuShell).

## 3. Relevant Documentation
- `docs/roadmap/03-p2-nebushell.md`: Milestone P2 roadmap.
- `docs/desktop/02-nebushell-specification.md`: Shell architecture specification.
- `docs/decisions/ADR-0009-nebushell-ui-architecture.md`: Single shell pluggable architecture.
- `docs/decisions/ADR-0013-ui-design-system-and-icon-architecture.md`: Master UI design system and iconography ADR.
- `docs/design/00-design-system.md`: Design tokens, colors, typography, spatial scales.
- `docs/design/01-iconography.md`: Abstract `NebuIcon` architecture and icon pipeline.
- `docs/design/02-theming-layout-behavior.md`: Tripartite architecture specification.
- `docs/design/03-components.md`: Five-tier component taxonomy and Slint widgets.
- [docs/design/04-accessibility-and-performance.md](04-accessibility-and-performance.md): Accessibility and performance requirements.
- [docs/design/05-external-assets-and-licensing.md](05-external-assets-and-licensing.md): External asset licensing and governance.
- [docs/decisions/ADR-0014-boot-experience-and-graphical-handoff.md](../decisions/ADR-0014-boot-experience-and-graphical-handoff.md): Boot experience and graphical handoff.

## 4. Allowed Changes
- Authoring shell source code under `crates/nebu-shell/`.
- Authoring token and iconography crates under `crates/nebu-design-tokens/` and `crates/nebu-icon/`.
- Developing Slint UI markup files (`.slint`) adhering to `docs/design/03-components.md`.
- Defining built-in theme and layout presets in declarative TOML manifests.
- Authoring Milestone P2 boot splash branding and post-rollback notification card UI components.

## 5. Forbidden Changes
- **DO NOT WORK IN P0 OR P1:** Locked until P0 and P1 exit criteria are fully satisfied. P0 is strictly headless; P1 is compositor only.
- **NO SEPARATE SHELL BINARIES:** Never build separate binaries for Windows-like vs macOS-like layouts. Use a single binary with runtime layout switching (ADR-0009).
- **NO DIRECT ICON FILE BINDING:** Never hardcode external SVG paths or library glyph names; all icons must route through `NebuIcon` (`docs/design/01-iconography.md`).
- **THEME != LAYOUT != BEHAVIOR:** Do not conflate styling (Theme), panel geometry (Layout), and window management logic (Behavior).
- **NO EMBEDDING MARKETPLACE IN SHELL CORE:** The Nebu Marketplace is an independent application (`crates/nebu-marketplace-ui/`); NebuShell must never embed store discovery or package manager logic. Shell provides launcher, search provider, and notifications integration only.
- **NO ELECTRON OR WEBVIEWS:** All UI must be written in native Rust with Slint.
- **NO SEPARATE BOOT DESIGN SYSTEM:** Early boot visual elements (splash, rollback notification) must strictly consume master tokens from `nebu-design-tokens` (ADR-0014).

## 6. Architecture Constraints
- UI Toolkit: **Slint** (ADR-0009, ADR-0013).
- Integration Protocol: `wlr-layer-shell` for anchoring panels and overlays.
- Boot Transition (ADR-0014): Stage 9 to 10 cross-fade transition from boot splash into interactive desktop must complete in <= 200ms using `Motion.EasingEmphasized`.
- Shell Memory Budget: Steady-state idle RAM strictly <= 45 MB RSS.
- Icon Cache Budget: In-memory icon texture pool strictly <= 8.0 MB.
- Application Integration: Query installed applications via `org.nebu.AppManager1` over D-Bus; do not parse package databases directly.

## 7. Implementation Guidance
- Keep Slint UI definitions clean, declarative, and decoupled from business logic.
- Connect to `nebu-compositor` via layer-shell protocol and `org.nebu.Compositor1` D-Bus.
- Implement Freedesktop specifications: Notification Daemon (`org.freedesktop.Notifications`) and StatusNotifierItem system tray.

## 8. Verification
- Validate layout switching dynamically without restarting the shell process.
- Benchmark idle RAM footprint (`free -m` / `smem`) asserting shell RSS < 25 MB.

## 9. Common Failure Modes
- Slint UI thread blocking on synchronous D-Bus or disk I/O.
- Memory bloat caused by uncompressed icon caches.

## 10. Handoff Requirements
- Document active UI toolkit version, layout switching test results, and RAM measurements in `HANDOFF.md`.
