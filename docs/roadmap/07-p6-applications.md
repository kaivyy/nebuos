# Phase P6: Applications Subsystem Specification — NebuOS

**Status:** APPROVED  
**Phase:** P6  
**Target Duration:** Sprint 18–20  
**Prerequisite:** Phase P2, P3, P4, P5  

---

## 1. Objective
Implement the user-facing application installer wizard, desktop registration engine, FreeDesktop MIME associations, 100% clean uninstallation agent, and the Nebu Software Center dual-catalog store. P6 ensures end-users can discover, install, manage, and remove both native Linux and Windows applications effortlessly.

## 2. Scope (What's IN)
- Native installer wizard GUI `crates/nebu-installer-ui`.
- Software Center dual-catalog store `crates/nebu-software-center` (Flatpak + Windows Recipes).
- Application registration: PE `.rsrc` icon extraction (PNG), FreeDesktop `.desktop` entry generation.
- Filesystem mapping: bidirectional path translation (`nebu-path`), `C:` drive mapping, sanitized `Z:` drive.
- Shared MIME database management (`update-mime-database`, `mimeapps.list`).
- Deterministic 100% clean uninstallation agent.

## 3. Anti-Scope (What's NOT IN)
- NO webview / Electron store UI.
- NO hosting proprietary Windows binaries on NebuOS servers (uses declarative recipes).
- NO payment processing inside the software store.

## 4. Dependencies
- Slint / Iced GUI frameworks.
- `libflatpak` >= 1.14.
- `pelite`, `image` Rust crates.

## 5. Deliverables
- GUI Binaries: `/usr/bin/nebu-installer-ui`, `/usr/bin/nebu-software-center`.
- App Registry DB: `~/.local/share/nebu/apps.db`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P6-01 (Installer Interception):** Double-clicking `setup.exe` opens `nebu-installer-ui` wizard; completed setup generates desktop shortcut with high-resolution icon in <= 2.0s.
2. **EC-P6-02 (MIME Association):** Double-clicking `.docx` or `.dwg` file launches associated application with translated POSIX path argument.
3. **EC-P6-03 (Clean Uninstall):** Clicking Uninstall in Software Center purges prefix, removes `.desktop` file, unregisters MIME types, and frees disk space in <= 500ms.
4. **EC-P6-04 (Store Responsiveness):** Software Center starts up in <= 350ms and searches 5,000 catalog applications in <= 10ms.
5. **EC-P6-05 (Recipe Installation):** Automated Windows recipe installs target application unattended using silent flags (`/S`).

## 7. Known Risks & Mitigations
- **Risk:** Multi-part installers fail to discover secondary disk files inside sandbox.
  - *Mitigation:* Installer wizard automatically binds parent download directory as read-only volume.
