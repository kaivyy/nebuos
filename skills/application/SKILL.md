# Application Platform & Marketplace Skill — NebuOS

## 1. Purpose
Governs the architecture, source abstractions, lifecycle management, sandboxing, and user experience for application distribution in NebuOS, encompassing Flatpak packaging, Flathub discovery, Fedora repository separation, Nebu App Manager abstraction, and the native Nebu Marketplace.

## 2. Scope
Applies strictly to Milestone P6 (Application Platform & Nebu Marketplace, subphases P6.0–P6.4) and Phase P8 (Production Readiness).

## 3. Relevant Documentation
- `docs/decisions/ADR-0012-application-distribution-and-marketplace.md`: Master architectural decision.
- `docs/decisions/ADR-0013-ui-design-system-and-icon-architecture.md`: UI design system and iconography architecture.
- `docs/design/00-design-system.md`: Design tokens and semantic color rules.
- `docs/design/01-iconography.md`: Untrusted application icon pipeline and sandboxed caching.
- `docs/design/03-components.md`: MarketplaceCard, PermissionMatrixCard, and InstallerWizardStep specs.
- `docs/roadmap/00-implementation-roadmap.md`: Subphases P6.0–P6.4 and Phase P8 deliverables.
- `docs/applications/00-application-specification.md`: Master application platform model.
- `docs/applications/06-software-center.md`: Nebu Marketplace specification.
- `docs/applications/07-app-manager-specification.md`: Nebu App Manager daemon and D-Bus interfaces.
- `docs/applications/08-developer-platform-and-security.md`: Application security, trust tiers, and developer platform.

## 4. Allowed Changes
- Authoring App Manager daemon source code under `crates/nebu-app-manager-daemon/`.
- Developing native Marketplace UI components in `crates/nebu-marketplace-ui/` using Slint.
- Authoring Windows installer wizard in `crates/nebu-installer-ui/`.
- Defining D-Bus interfaces in `packaging/dbus-1/interfaces/org.nebu.AppManager1.xml`.
- Managing systemd user service `packaging/systemd/user/nebu-app-manager.service`.

## 5. Forbidden Changes
- **DO NOT WORK IN P0, P1, P2, P3, P4, OR P5:** Locked until earlier milestones are complete.
- **NO CUSTOM PACKAGE MANAGER:** Never create a custom packaging format (e.g. `.nebu`) without an approved ADR.
- **NO FORKING FLATHUB:** Never fork Flathub or host private mirrors in initial phases.
- **NO DIRECT PACKAGE MANAGER SPAWNING FROM UI:** The Marketplace UI must never execute `flatpak`, `dnf`, or `wine` directly; all actions must route through `org.nebu.AppManager1`.
- **NO ELECTRON OR WEBVIEWS:** All marketplace and installer UI components must use native Rust toolkits (Slint).
- **NO UNSANITIZED APP ICONS:** Never render third-party SVGs or extracted PE icons directly in UI without passing through `nebu-icon-sandbox` (`docs/design/01-iconography.md`).
- **NO CONFLATING OS AND APP UPDATES:** Application updates must never trigger or depend on OS `bootc` reboots.
- **NO PACKAGING WINDOWS APPS AS FLATPAKS:** Windows applications must remain in the Nebu Compatibility Engine with isolated Btrfs prefixes.

## 6. Architecture Constraints
- **Layering:** UI (Slint) -> D-Bus (`org.nebu.AppManager1`) -> `nebu-app-manager-daemon` -> Adapters (`libflatpak`, `nebu-runtime-daemon`) -> Storage (`~/.local/share/flatpak`, `~/.nebu/apps/`).
- **Visual Design:** Marketplace UI must bind strictly to `nebu-design-tokens` and request UI glyphs via `nebu-icon` (ADR-0013).
- **Permission Model:** All applications must declare permissions; pre-installation consent card is mandatory.
- **Application Identity:** Stable reverse-DNS format (`app_id`); versioning decoupled from OS and Wine releases.
- **Memory Budgets:** App Manager idle RSS <= 18 MB; Marketplace UI idle RSS <= 35 MB.

## 7. Implementation Guidance
- Implement the `ApplicationSource` trait to normalize metadata across Flathub, Fedora, and Windows recipes.
- Cache remote AppStream metadata in local SQLite database `marketplace.db` to enable instant offline search.
- Enforce the 10-state lifecycle: `Discover -> Inspect -> Verify -> Install -> Register -> Launch -> Update -> Disable -> Repair -> Uninstall`.
- Support HTTP range requests for resumable downloads and perform disk space checks prior to staging.

## 8. Verification
- Validate search query response times (< 40ms) using SQLite FTS5 index.
- Verify unprivileged Flatpak user-space installation without root elevation.
- Verify clean uninstallation: zero lingering prefixes, icons, or desktop files.
- Verify update separation: Flatpak app updates live without OS reboot.

## 9. Common Failure Modes
- Marketplace UI freezing because metadata queries run synchronously on the UI thread (must use async D-Bus).
- Redundant Flatpak runtime accumulation exhausting user storage (requires automatic pruning prompts).
- Conflating Wine prefix state with user application configurations.

## 10. Handoff Requirements
- Document active D-Bus interface versions, Flathub API compatibility, and memory measurements in `HANDOFF.md`.
