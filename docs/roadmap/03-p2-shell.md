# Phase P2: NebuShell Specification — NebuOS

**Status:** APPROVED  
**Phase:** P2  
**Target Duration:** Sprint 6–8  
**Prerequisite:** Phase P1  

---

## 1. Objective
Implement `nebu-shell`, the unified native Rust desktop shell implementing ADR-0009. P2 delivers the taskbar, application launcher, status tray (SNI), quick settings flyout, lock screen (`ext-session-lock-v1`), and the dynamic theme/layout engine supporting runtime switching between Nebu, Windows-like, and macOS-like paradigms in <= 150ms without process restart.

## 2. Scope (What's IN)
- Rust Crate: `crates/nebu-shell` (lean single crate with `core`, `layout`, `theme`, `system_api`, `ui` modules).
- Native GUI rendering via Slint 1.7+ toolkit ([ADR-0019](../decisions/ADR-0019-slint-toolkit-adoption.md)).
- Wayland layer-shell surfaces (`zwlr_layer_surface_v1`): Panel, Dock, Launcher, Quick Settings, OSD.
- Dynamic layout engine: runtime switching between Nebu Default, Windows-like, and macOS-like paradigms.
- Fast application launcher with sub-millisecond in-memory SQLite indexing.
- System tray host compliant with `org.kde.StatusNotifierWatcher`.
- PipeWire volume control and NetworkManager Wi-Fi/Ethernet flyout widgets.
- Memory budget <= 45 MB RSS idle.

## 3. Anti-Scope (What's NOT IN)
- NO Electron, CEF, Node.js, or HTML/CSS runtime components.
- NO arbitrary untrusted JavaScript applet plugins.
- NO software center store GUI (governed by P6).
- NO Windows EXE execution logic (governed by P3).

## 4. Dependencies
- Phase P1 NebuCompositor.
- GUI Toolkit: `slint` = "1.6" or `iced` = "0.12".
- `zbus` = "4.0", `rusqlite` = "0.31".
- PipeWire client libraries (`libpipewire-0.3`).

## 5. Deliverables
- Binaries: `/usr/bin/nebu-shell`, `/usr/bin/nebu-greeter`, `/usr/bin/nebu-screenshot`.
- Built-in Themes: `/usr/share/nebu/themes/{nebu-default,nebu-dark,windows-like,macos-like}.toml`.
- Systemd Unit: `/usr/lib/systemd/user/nebu-shell.service`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P2-01 (Launcher Responsiveness):** Pressing Super key renders application launcher UI in <= 80ms.
2. **EC-P2-02 (Live Paradigm Switch):** Invoking `nebu-shell-ctl switch macos-like` re-anchors layer surfaces in <= 150ms without dropping client windows.
3. **EC-P2-03 (Tray Compatibility):** Background application registering via SNI displays clickable tray icon with functional context menu.
4. **EC-P2-04 (Combined Memory Budget):** Combined Compositor + Shell idle memory <= 80 MB RSS.
5. **EC-P2-05 (Lock Screen Security):** Lock screen activates via `ext-session-lock-v1` and unlocks cleanly with valid PAM password authentication.

## 7. Known Risks & Mitigations
- **Risk:** Geometry calculation glitches on ultra-wide or rotated displays during paradigm switch.
  - *Mitigation:* Constraint solver enforces strict bounds clamp ($[32, 64]$ px) and tests layout across 10 display aspect ratios in CI.
