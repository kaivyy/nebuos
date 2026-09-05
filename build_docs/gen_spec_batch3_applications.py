#!/usr/bin/env python3
"""
Generator for Batch 3: Applications subsystem specifications:
- applications/00-application-specification.md
- applications/01-installer.md
- applications/02-application-registration.md
- applications/03-filesystem-mapping.md
- applications/04-file-associations.md
- applications/05-uninstallation.md
- applications/06-software-center.md
"""

import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {path} ({len(content.splitlines())} lines)")

# 00-application-specification.md
a0 = r"""# Application Subsystem Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Define the unified application model, package classification, execution topology, and integration standards for native Linux and Windows applications in NebuOS.

---

## 1. Status
DRAFT — Master implementation specification for the NebuOS application ecosystem.

## 2. Purpose
NebuOS provides a unified application experience where the user does not need to know or care whether an application was originally compiled for Linux or Windows. This specification establishes the core abstractions, metadata manifests, isolation boundaries, and lifecycle management governing all applications installed on NebuOS.

## 3. Scope
- Unified application taxonomy: Native Linux packages, Flatpaks, and Sandboxed Windows Executables.
- Canonical application identifier format (`app_id`).
- Application state model (Installed, Running, Suspended, Updating, Uninstalled).
- Metadata persistence in local SQLite registry (`~/.local/share/nebu/apps.db`).
- Desktop integration standards (FreeDesktop specifications compliance).

## 4. Non-goals
- Running Windows Store / UWP / MSIX applications requiring modern Windows AppX virtualization.
- Allowing unconfined root privileges to Windows or Flatpak applications.
- Running multiple concurrent graphical sessions for different users on one desktop seat.

## 5. Requirements
1. **R-APP-01:** Support unified application representation across native Linux binaries, Flatpaks, and Wine-sandboxed Windows PE binaries.
2. **R-APP-02:** Enforce unique reverse-DNS naming for all applications (`com.vendor.appname`).
3. **R-APP-03:** Store application state, launch arguments, prefix paths, and statistics in SQLite.
4. **R-APP-04:** Provide standard FreeDesktop `.desktop` entry generation and `.rsrc` icon extraction for all installed Windows applications.
5. **R-APP-05:** Isolate Windows applications in dedicated per-application prefixes with Btrfs reflink snapshots.

## 6. Architecture
The application subsystem coordinates between the user desktop shell, the installer engine, and the runtime daemon:

```mermaid
graph TD
    subgraph UI[User Interface Layer]
        LAUNCHER[NebuShell Launcher]
        STORE[Nebu Software Center]
        INSTALLER_WIZ[Nebu Installer Wizard]
    end

    subgraph Management[Application Management Layer]
        APP_MGR[Application Manager Service]
        REGISTRY[SQLite App Registry: apps.db]
        ICON_CACHE[Icon & Desktop Generator]
    end

    subgraph Runtime[Execution Layer]
        RUNTIME_D[nebu-runtime-daemon]
        FLATPAK[Flatpak Runtime]
        NATIVE[Host Linux Process]
    end

    STORE --> APP_MGR
    INSTALLER_WIZ --> APP_MGR
    APP_MGR <--> REGISTRY
    APP_MGR --> ICON_CACHE
    ICON_CACHE --> LAUNCHER
    LAUNCHER -->|Launch App| APP_MGR
    APP_MGR -->|Windows PE| RUNTIME_D
    APP_MGR -->|Flatpak ID| FLATPAK
    APP_MGR -->|Host Binary| NATIVE
```

## 7. Components
1. **Application Manager Service:** Coordinates installation, updates, queries, and uninstallation.
2. **App Registry (`apps.db`):** SQLite database recording installed applications, versions, and execution profiles.
3. **Desktop Entry Generator:** Emits compliant FreeDesktop `.desktop` files into `~/.local/share/applications/`.
4. **PE Icon Extractor:** Decodes `.rsrc` section of Windows PE binaries and exports 256x256 PNG icons.
5. **MIME Association Broker:** Maps Windows file extensions (`.docx`, `.dwg`, `.psd`) to registered applications.

## 8. Data Flow
1. Software Center or user initiates installation of an application.
2. Application Manager creates registry record in `apps.db`.
3. If Windows executable:
   - Evaluates PE headers and matches profile in `compat.db`.
   - Provisions prefix at `~/.nebu/apps/<app_id>/`.
   - Runs installer wizard inside Bubblewrap jail.
   - Discovers installed target executable (`.exe`).
   - Extracts embedded icon to `~/.local/share/icons/hicolor/256x256/apps/<app_id>.png`.
   - Emits `.desktop` launcher entry.
4. Shell immediately displays application icon in launcher search index (< 100ms).

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Shell as NebuShell
    participant Mgr as Application Manager
    participant Runtime as nebu-runtime-daemon
    participant Bwrap as Bubblewrap Sandbox

    User->>Shell: Click app icon in launcher
    Shell->>Mgr: LaunchApplication(app_id)
    Mgr->>Mgr: Look up app_id in apps.db
    Mgr->>Runtime: LaunchRequest(path, prefix, profile)
    Runtime->>Bwrap: Execute Wine process in sandbox
    Bwrap-->>Shell: Wayland window emerges
```

## 10. Interfaces
- **D-Bus Interface:** `org.nebu.ApplicationManager1`
  - `ListInstalledApplications() -> Array<AppMetadata>`
  - `GetApplicationDetails(String app_id) -> AppDetails`
  - `UninstallApplication(String app_id, Boolean purge_data) -> Boolean`
- **Application Metadata Schema (JSON):**
  ```json
  {
    "app_id": "com.adobe.photoshop2024",
    "name": "Adobe Photoshop 2024",
    "kind": "windows_pe",
    "executable": "drive_c/Program Files/Adobe/Photoshop.exe",
    "prefix_path": "~/.nebu/apps/com.adobe.photoshop2024",
    "installed_at": 1725440000,
    "size_bytes": 4294967296
  }
  ```

## 11. Dependencies
- SQLite 3.42+ with WAL mode enabled.
- `icoutils` / `wrestool` / native Rust PE resource parser (`pelite`).
- FreeDesktop Desktop Entry and MIME info specifications.

## 12. Security
- Every Windows application is isolated in its own Bubblewrap container.
- Shared documents (`~/Documents`, `~/Downloads`) accessible only via explicit whitelist.
- Application cannot access another application's prefix or configuration.
- System binaries in `/usr` mounted strictly read-only.

## 13. Resource Requirements
- Application manager daemon idle memory: <= 12 MB RSS.
- Metadata query latency: <= 0.5ms per application.
- Desktop entry emission: <= 15ms.

## 14. Failure Modes
1. **Corrupted Desktop Entry:** Malformed syntax causes launcher to hide application.
2. **Missing Executable:** Application uninstalled internally by Windows uninstaller without notifying NebuOS.
3. **Icon Extraction Failure:** PE contains 16-color or non-standard compressed icon format.

## 15. Recovery Behavior
- Desktop entry syntax validated via `desktop-file-validate` before writing to disk.
- Missing executable detected on launch; user prompted to repair or remove stale shortcut.
- Fallback icon assigned if PE icon extraction fails.

## 16. Testing Requirements
- Unit tests validating FreeDesktop `.desktop` file generation.
- Icon extraction test suite across 100 diverse Windows executables (MFC, .NET, Delphi, Electron PE).
- Registry integrity tests under simulated process crashes.

## 17. Performance Requirements
- Application launch dispatch overhead: <= 40ms.
- Application list query of 1,000 apps: <= 15ms.
- Full uninstallation and disk reclaim: <= 500ms.

## 18. Compatibility Considerations
- Supports standard Windows installation conventions (`Program Files`, `AppData`, `Common Files`).
- Handles spaces and Unicode in Windows paths transparently.

## 19. Open Questions
- **OQ-APP-01:** Should NebuOS support sandboxed portable executables (single `.exe` without installation) in a dedicated transient prefix?
- **OQ-APP-02:** Should native Linux Flatpak updates be triggered automatically alongside OS image updates?

## 20. Related Documents
- [01-installer.md](01-installer.md)
- [02-application-registration.md](02-application-registration.md)
- [03-filesystem-mapping.md](03-filesystem-mapping.md)
- [04-file-associations.md](04-file-associations.md)
- [05-uninstallation.md](05-uninstallation.md)
- [06-software-center.md](06-software-center.md)
"""

write_file("/root/NebuOS/docs/applications/00-application-specification.md", a0)

# 01-installer.md
a1 = r"""# Installer Subsystem Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the Windows setup and installer execution workflow, wizard UI, silent installation automation, and post-install discovery in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P6 installer subsystem.

## 2. Purpose
Installing Windows applications on Linux is historically confusing and failure-prone. This specification defines the automated, guided installation workflow of NebuOS. It intercepts `.exe` and `.msi` setup binaries, provisions isolated environments, guides the user through a clean native wizard, and discovers the resulting main application executable automatically.

## 3. Scope
- Installer binary inspection (MSI, Inno Setup, NSIS, InstallShield, Wise, WiX).
- Automated silent install flag injection when available.
- Interactive GUI installer wizard (`nebu-installer-ui`).
- Filesystem delta tracking to identify newly created executables.
- Registry analysis to determine installed display names and version numbers.

## 4. Non-goals
- Modifying proprietary installer binaries on disk.
- Reverse engineering encrypted or password-protected setup packages.
- Installing device drivers (.sys files) packaged inside Windows installers.

## 5. Requirements
1. **R-INS-01:** Intercept double-clicked `.exe` and `.msi` files from file manager or browser downloads.
2. **R-INS-02:** Determine whether executable is an installer vs. standalone portable application.
3. **R-INS-03:** Present a clean native installation dialog showing app name, icon, estimated disk space, and sandbox security level.
4. **R-INS-04:** Execute installation inside a transient staging sandbox before committing prefix.
5. **R-INS-05:** Automatically identify the primary installed executable and generate desktop launcher.

## 6. Architecture
The installer engine coordinates between detection heuristics, prefix management, and user interaction:

```mermaid
graph TD
    subgraph Input[User Action]
        EXE[User double-clicks setup.exe / installer.msi]
    end

    subgraph Engine[NebuOS Installer Engine]
        DETECTOR[PE & Installer Classifier]
        WIZARD[nebu-installer-ui Wizard]
        PROVISIONER[Prefix Provisioner: Btrfs Reflink]
        MONITOR[Filesystem & Registry Watcher]
    end

    subgraph Sandbox[Execution]
        BWRAP[Bubblewrap Sandbox]
        WINE_SETUP[Wine Setup Process]
    end

    EXE --> DETECTOR
    DETECTOR -->|Installer Detected| WIZARD
    WIZARD -->|User Confirms| PROVISIONER
    PROVISIONER --> MONITOR
    MONITOR --> BWRAP
    BWRAP --> WINE_SETUP
    WINE_SETUP -->|Writes Files| MONITOR
    MONITOR -->|Detects Installed EXE| WIZARD
```

## 7. Components
1. **Installer Classifier:** Reads PE headers and string tables to identify installer engine (NSIS, Inno, MSI).
2. **Setup Wizard (`nebu-installer-ui`):** Slint-based native dialog presenting install progress, license agreements, and target drive options.
3. **Delta Monitor:** Snapshots prefix filesystem before setup runs and compares after termination to isolate installed files.
4. **Target Selector:** Heuristic algorithm scoring newly created `.exe` files to select the main application binary (rejecting `unins000.exe`, `update.exe`, `crashpad.exe`).

## 8. Data Flow
1. User launches `setup.exe`.
2. Classifier detects Inno Setup installer.
3. Wizard displays: *"Install Microsoft Office 2024?"* with estimated footprint (2.4 GB).
4. User clicks "Install".
5. Runtime reflinks clean template prefix at `~/.nebu/apps/com.microsoft.office2024/`.
6. Setup executes within Bubblewrap jail.
7. Setup completes; Delta Monitor identifies:
   - `drive_c/Program Files/Microsoft Office/root/Office16/WINWORD.EXE`
   - `drive_c/Program Files/Microsoft Office/root/Office16/EXCEL.EXE`
   - `drive_c/Program Files/Microsoft Office/root/Office16/POWERPNT.EXE`
8. Wizard creates separate desktop entries for Word, Excel, and PowerPoint.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Wiz as nebu-installer-ui
    participant Daemon as neburuntimed
    participant Sandbox as Bubblewrap
    participant Watcher as Delta Watcher

    User->>Wiz: Launch installer
    Wiz->>Daemon: ProvisionStagingPrefix()
    Daemon-->>Wiz: Prefix Ready: /tmp/nebu_stage_1000
    Wiz->>Watcher: SnapshotPreInstall()
    Wiz->>Sandbox: Execute setup.exe in sandbox
    Sandbox-->>Wiz: Setup process exited (code 0)
    Wiz->>Watcher: SnapshotPostInstall()
    Watcher-->>Wiz: Identified Targets: [WINWORD.EXE, EXCEL.EXE]
    Wiz->>Daemon: CommitPrefix(staging_id, app_id)
    Wiz->>User: "Installation Complete!"
```

## 10. Interfaces
- **D-Bus Interface:** `org.nebu.Installer1`
  - `InspectInstaller(String path) -> InstallerInfo`
  - `StartInstallation(String path, InstallOptions options) -> String job_id`
  - Signals: `InstallProgress(String job_id, Double percent, String status)`
- **Installer Heuristic Signatures:**
  - Inno Setup: String `"Inno Setup Setup Data"` in `.data` section.
  - NSIS: Nullsoft signature `0xDEADBEEF` at offset 0x80.
  - MSI: OLE compound document magic `D0 CF 11 E0 A1 B1 1A E1`.

## 11. Dependencies
- `bwrap` >= 0.8.0.
- `msitools` (for headless MSI inspection).
- Btrfs filesystem with snapshot capabilities.

## 12. Security
- Installers run with network disabled by default unless user checks "Allow internet access during install".
- Installers cannot write to real user home directory or Linux system root.
- Post-install analysis validates that no malicious auto-start registry keys escape into host system.

## 13. Resource Requirements
- Installer wizard idle RAM: <= 20 MB RSS.
- Staging prefix creation time: <= 250ms (Btrfs reflink).
- Post-install delta scanning time: <= 500ms on SSD.

## 14. Failure Modes
1. **Installer Hangs:** Setup process deadlocks waiting for unsupported Windows driver installation.
2. **Silent Failure:** Installer exits with non-zero error code.
3. **No Target Found:** Setup finishes but no valid executable files were written.

## 15. Recovery Behavior
- User provided with an explicit "Cancel & Clean Up" button; terminates sandbox and purges staging prefix immediately.
- If installer crashes, wizard displays error log excerpt and checks `compat.db` for known missing DLL workarounds.
- Staging prefixes automatically cleaned up after 24 hours if installation abandoned.

## 16. Testing Requirements
- Automated test installing 20 representative open-source Windows installers (Notepad++, 7-Zip, VLC Windows build, Blender).
- Delta detection accuracy test asserting correct target executable selection.
- Sandbox escape prevention tests during setup execution.

## 17. Performance Requirements
- Total wizard startup latency: <= 150ms.
- Staging prefix allocation: <= 300ms.
- Target discovery and desktop entry generation: <= 1.0s after setup exits.

## 18. Compatibility Considerations
- Handles multi-disk / multi-part installers seamlessly via mounted ISO or folder binds.
- Injects `WINEARCH=win64` or `win32` dynamically based on installer architecture.

## 19. Open Questions
- **OQ-INS-01:** Should NebuOS support an "Express Install" mode that bypasses all wizard prompts for known certified applications?
- **OQ-INS-02:** How should installer reboot prompts ("You must restart your computer now") be handled cleanly?

## 20. Related Documents
- [00-application-specification.md](00-application-specification.md)
- [02-application-registration.md](02-application-registration.md)
- [03-filesystem-mapping.md](03-filesystem-mapping.md)
- [05-uninstallation.md](05-uninstallation.md)
"""

write_file("/root/NebuOS/docs/applications/01-installer.md", a1)

# 02-application-registration.md
a2 = r"""# Application Registration Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the application registration workflow, FreeDesktop `.desktop` entry generation, icon decoding and caching, and MIME association persistence in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P6 application registration.

## 2. Purpose
When a Windows application is installed, it must integrate seamlessly into the Linux desktop environment. This specification defines how NebuOS extracts application metadata, registers records in the local SQLite database, extracts high-resolution embedded icons from Windows PE binaries, generates standard `.desktop` files, and updates desktop launcher caches.

## 3. Scope
- Extraction of metadata from Windows PE headers and `VS_VERSIONINFO` resource blocks.
- Decoding multi-resolution Windows `.ico` formats and converting to standard PNG.
- Generating FreeDesktop Desktop Entry Specification 1.5 `.desktop` files.
- Managing localized desktop entries (English, Indonesian, etc.).
- Registering application state in `~/.local/share/nebu/apps.db`.

## 4. Non-goals
- Modifying host system `/usr/share/applications` (all user apps reside in user space).
- Supporting legacy Windows 3.1 16-bit icon structures.
- Inventing proprietary desktop entry formats incompatible with Linux standards.

## 5. Requirements
1. **R-REG-01:** Automatically register every installed application in `~/.local/share/nebu/apps.db`.
2. **R-REG-02:** Extract highest resolution embedded icon (up to 256x256 PNG) from target PE binary.
3. **R-REG-03:** Emit compliant `.desktop` files in `~/.local/share/applications/` referencing `nebu-launch`.
4. **R-REG-04:** Register standard categories (`Office`, `Graphics`, `Development`, `Game`) derived from application profile.
5. **R-REG-05:** Trigger immediate notification to desktop shell launcher to refresh search indexes.

## 6. Architecture
Application registration bridges the Windows binary structure with the Linux FreeDesktop desktop specification:

```mermaid
graph TD
    subgraph TargetBinary[Installed Windows PE Binary]
        PE[Executable / DLL]
        RSRC[PE .rsrc Section: Icons & Version Info]
    end

    subgraph RegistrationPipeline[Registration Engine]
        PARSER[PE Resource Parser]
        ICON_CONV[ICO to PNG Converter]
        DESKTOP_GEN[.desktop File Generator]
        DB_WRITER[SQLite Registry Writer]
    end

    subgraph DesktopEnvironment[NebuOS Desktop]
        ICON_DIR[~/.local/share/icons/hicolor/256x256/apps/]
        APP_DIR[~/.local/share/applications/]
        DB[~/.local/share/nebu/apps.db]
        SHELL[NebuShell Launcher Index]
    end

    PE --> RSRC
    RSRC --> PARSER
    PARSER --> ICON_CONV
    PARSER --> DESKTOP_GEN
    PARSER --> DB_WRITER
    ICON_CONV --> ICON_DIR
    DESKTOP_GEN --> APP_DIR
    DB_WRITER --> DB
    APP_DIR --> SHELL
```

## 7. Components
1. **PE Metadata Extractor:** Reads `VS_FIXEDFILEINFO` and `StringFileInfo` (ProductName, FileDescription, ProductVersion, CompanyName).
2. **Icon Pipeline:** Parses `RT_GROUP_ICON` and `RT_ICON` structures, extracts largest icon bitmap/PNG, and saves to icon cache.
3. **Desktop Entry Synthesizer:** Formats desktop entry string with proper `Exec`, `Icon`, `Categories`, and `StartupWMClass`.
4. **Launcher Index Notifier:** Dispatches D-Bus signal notifying `nebu-shell` that application catalog updated.

## 8. Data Flow
1. Target binary identified: `~/.nebu/apps/com.adobe.photoshop2024/pfx/drive_c/Photoshop.exe`.
2. Parser extracts `ProductName`: "Adobe Photoshop 2024".
3. Icon pipeline extracts 256x256 PNG icon and writes to `~/.local/share/icons/hicolor/256x256/apps/nebu-com.adobe.photoshop2024.png`.
4. Synthesizer generates `.desktop` entry:
   ```ini
   [Desktop Entry]
   Version=1.5
   Type=Application
   Name=Adobe Photoshop 2024
   GenericName=Graphics Editor
   Comment=Professional photo editing and digital art
   Exec=/usr/bin/nebu-launch com.adobe.photoshop2024 %F
   Icon=nebu-com.adobe.photoshop2024
   Terminal=false
   Categories=Graphics;Photography;2DGraphics;RasterGraphics;
   MimeType=image/vnd.adobe.photoshop;image/x-psd;
   StartupWMClass=photoshop.exe
   X-Nebu-AppID=com.adobe.photoshop2024
   X-Nebu-Runtime=wine-stable
   ```
5. Writes file to `~/.local/share/applications/nebu-com.adobe.photoshop2024.desktop`.
6. Updates desktop database via `update-desktop-database ~/.local/share/applications`.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant Installer as Installer Engine
    participant Reg as Registration Service
    participant Disk as Local Filesystem
    participant DB as apps.db
    participant Shell as NebuShell

    Installer->>Reg: RegisterApplication(app_id, exe_path)
    Reg->>Disk: Extract icons to ~/.local/share/icons/
    Reg->>Disk: Write .desktop file to ~/.local/share/applications/
    Reg->>DB: INSERT INTO installed_apps (...)
    Reg->>Disk: update-desktop-database
    Reg->>Shell: D-Bus: ApplicationCatalogChanged(app_id)
    Shell->>Shell: Invalidate and reload in-memory search index
```

## 10. Interfaces
- **Database Schema Table:**
  ```sql
  CREATE TABLE installed_apps (
      app_id TEXT PRIMARY KEY,
      display_name TEXT NOT NULL,
      version TEXT,
      publisher TEXT,
      kind TEXT NOT NULL, -- 'windows_pe', 'flatpak', 'native'
      prefix_path TEXT,
      exe_path TEXT NOT NULL,
      desktop_file TEXT NOT NULL,
      icon_path TEXT NOT NULL,
      installed_at INTEGER NOT NULL
  );
  ```
- **Registration Command:** `nebu app register --app-id <id> --exe <path>`

## 11. Dependencies
- Rust crate `pelite` (zero-copy PE parsing).
- `image` crate (for PNG resizing and format conversion).
- `update-desktop-database` (FreeDesktop tools).

## 12. Security
- Desktop entry `Exec` line strictly formatted to call `/usr/bin/nebu-launch` with validated `app_id` argument; never invokes raw shell strings or unescaped paths.
- Extracted icons validated to ensure valid image dimensions and prevent decompression bomb attacks.

## 13. Resource Requirements
- Complete registration process execution time: <= 120ms per application.
- Peak memory during icon conversion: <= 15 MB RSS.
- Disk footprint of generated assets: <= 150 KB per application.

## 14. Failure Modes
1. **PE Binary Lacks Embedded Icon:** Minimalist console or utility executable contains no `.rsrc` icon group.
2. **Malformed Version String:** Windows executable contains non-UTF-8 or corrupt version info table.
3. **MIME Association Conflict:** Windows app attempts to hijack critical system MIME types (e.g. `inode/directory`).

## 15. Recovery Behavior
- When embedded icon is missing, registration service assigns standard themed category icon (e.g. `application-x-executable`).
- Non-UTF8 strings sanitized via lossless replacement characters (`U+FFFD`).
- Blacklisted system MIME types automatically stripped from generated `.desktop` file.

## 16. Testing Requirements
- Unit tests parsing PE resources across 50 real-world Windows applications.
- Icon extraction tests verifying proper handling of ICO format variations (BMP vs PNG sub-streams).
- Conformance test running `desktop-file-validate` on all generated `.desktop` entries.

## 17. Performance Requirements
- PE resource inspection latency: <= 20ms.
- Icon decoding and PNG export: <= 40ms.
- Shell search index update latency: <= 50ms from file commit.

## 18. Compatibility Considerations
- Handles multi-language string tables in Windows executables, selecting current system locale if available, falling back to English (US).

## 19. Open Questions
- **OQ-REG-01:** Should application registration generate Windows Start Menu folder hierarchies as sub-menus or flatten them into standard categories?
- **OQ-REG-02:** Should actions / jump-lists (e.g. "New Document", "Open Project") be supported via Desktop Actions specification?

## 20. Related Documents
- [00-application-specification.md](00-application-specification.md)
- [01-installer.md](01-installer.md)
- [03-filesystem-mapping.md](03-filesystem-mapping.md)
- [04-file-associations.md](04-file-associations.md)
- [05-uninstallation.md](05-uninstallation.md)
"""

write_file("/root/NebuOS/docs/applications/02-application-registration.md", a2)

# 03-filesystem-mapping.md
a3 = r"""# Filesystem Mapping Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the Windows drive letter abstraction (C:, Z:), path translation algorithms, user directory linking, and sandbox isolation in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P6 filesystem mapping.

## 2. Purpose
Windows applications expect DOS/NT drive letters (`C:\`, `D:\`), backslash separators (`\`), and case-insensitive path lookups. This specification defines how NebuOS maps the Linux filesystem hierarchy into standard Windows drive representations, safely presents user document directories, and translates path strings bidirectionally with zero data loss.

## 3. Scope
- Drive letter assignment (`C:`, `Z:`, removable media).
- Symlink topology inside application prefixes (`drive_c`, `dosdevices/`).
- User directory mapping (`~/Documents`, `~/Downloads`, `~/Pictures`, `~/Desktop`).
- Bidirectional path translation algorithm (Linux POSIX path <-> Windows DOS path).
- Security sandboxing restrictions on root filesystem visibility (`Z:\` drive isolation).

## 4. Non-goals
- Emulating raw block-level NTFS file streams or alternate data streams (ADS).
- Case-folding the entire host Linux root filesystem (case-insensitivity enforced inside prefix and Wine).
- Exposing raw unpartitioned host disks to Windows applications.

## 5. Requirements
1. **R-MAP-01:** Map prefix root `drive_c/` to Windows `C:\` drive.
2. **R-MAP-02:** Map user personal folders (`~/Documents`, `~/Downloads`, etc.) into `C:\users\nebu\` using standard symlinks or bind mounts.
3. **R-MAP-03:** Restrict `Z:\` (host root) drive access strictly to read-only whitelisted runtime dependencies; completely hide `/root`, `/etc`, and `/home/<other_users>`.
4. **R-MAP-04:** Provide bi-directional path translation utility via `nebu-path` CLI and Rust library.
5. **R-MAP-05:** Automatically map removable USB drives and optical media to sequential letters (`D:`, `E:`) when mounted.

## 6. Architecture
Filesystem mapping is established at sandbox launch by `nebu-runtime-daemon` and Bubblewrap:

```mermaid
graph TD
    subgraph HostSystem[Linux Host Filesystem]
        PREFIX[~/.nebu/apps/app_id/pfx/drive_c]
        DOCS[~/Documents]
        DLS[~/Downloads]
        SYS_USR[/usr: Runtimes & Libraries - Read Only]
        SECURE[/etc, /root, ~/.ssh - Blocked]
    end

    subgraph Sandbox[Bubblewrap Isolated Mount Namespace]
        BWRAP_ROOT[/]
        DEV_DOS[/dosdevices/]
        WIN_C[C: -> drive_c]
        WIN_Z[Z: -> / (Sandboxed Root)]
        WIN_USERS[C:\users\nebu\]
    end

    PREFIX --> WIN_C
    DOCS --> WIN_USERS
    DLS --> WIN_USERS
    SYS_USR --> WIN_Z
    SECURE -.->|Blocked by bwrap| BWRAP_ROOT
    WIN_C --> DEV_DOS
    WIN_Z --> DEV_DOS
```

## 7. Components
1. **Drive Link Manager:** Creates and maintains symlinks inside prefix `dosdevices/`:
   - `c:` -> `../drive_c`
   - `z:` -> `/`
   - `d:` -> `/media/usb` (dynamic)
2. **User Profile Synthesizer:** Configures `C:\users\nebu\` directories linking to corresponding XDG user directories.
3. **Path Translation Engine (`nebu-path`):** High-speed algorithm converting POSIX paths to Windows paths and vice-versa.
4. **Sandbox Visibility Filter:** Bubblewrap argument builder preventing exposure of sensitive host directories.

## 8. Data Flow
1. User invokes `nebu-launch com.app.cad ~/Documents/project.dwg`.
2. Path Translation Engine detects POSIX path `~/Documents/project.dwg`.
3. Resolves path within sandbox mount namespace:
   - Target translates to `C:\users\nebu\Documents\project.dwg`.
4. Wine command executed with translated argument:
   `wine64 app.exe "C:\users\nebu\Documents\project.dwg"`.
5. Application opens file directly without copy overhead.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as nebu-launch
    participant Trans as Path Translator
    participant Pfx as Prefix Manager
    participant App as Wine Executable

    User->>CLI: nebu-launch app_id "/home/nebu/Downloads/file.pdf"
    CLI->>Trans: PosixToWindows("/home/nebu/Downloads/file.pdf", prefix_path)
    Trans->>Trans: Match against C:\users\nebu\Downloads
    Trans-->>CLI: "C:\\users\\nebu\\Downloads\\file.pdf"
    CLI->>Pfx: EnsureDosDevicesValid(prefix_path)
    CLI->>App: Spawn wine64 app.exe "C:\\users\\nebu\\Downloads\\file.pdf"
```

## 10. Interfaces
- **Rust Translation API:**
  ```rust
  pub fn posix_to_dos_path(prefix: &Path, posix_path: &Path) -> Result<String, PathError>;
  pub fn dos_to_posix_path(prefix: &Path, dos_path: &str) -> Result<PathBuf, PathError>;
  ```
- **CLI Tool:**
  `nebu-path --to-dos --prefix ~/.nebu/apps/app_id /home/nebu/Documents/model.dwg`
  Output: `C:\users\nebu\Documents\model.dwg`

## 11. Dependencies
- Linux Btrfs / Ext4 POSIX filesystem features.
- Bubblewrap namespace isolation.
- XDG User Directories specification (`xdg-user-dirs`).

## 12. Security
- `Z:\` drive does not expose raw host root:
  - `/etc` is a sanitized dummy directory with minimal `/etc/passwd` and `/etc/resolv.conf`.
  - Sensitive user directories (`~/.ssh`, `~/.gnupg`, `~/.bashrc`, `~/.config/nebu`) are completely masked with `empty-dir` mounts.
- Windows applications cannot traverse symlinks out of their container boundary.

## 13. Resource Requirements
- Path translation latency: <= 0.2ms per path.
- In-memory footprint of translator: <= 50 KB RSS.
- Symlink creation on prefix initialization: <= 5ms.

## 14. Failure Modes
1. **Broken Symlink in dosdevices:** External drive unmounted while symlink remains.
2. **Case Sensitivity Collision:** Two files differing only in case (`File.txt` and `file.txt`) exist in same Linux directory.
3. **Path Length Overflow:** Deeply nested Windows path exceeds standard 260-character `MAX_PATH` limit.

## 15. Recovery Behavior
- Broken drive symlinks are pruned during sandbox initialization.
- Case collisions disambiguated by Wine's internal hashing and directory enumeration cache.
- Extended path prefix (`\\?\`) injected transparently for paths exceeding `MAX_PATH`.

## 16. Testing Requirements
- Unit tests verifying bidirectional path translation across 1,000 diverse path strings.
- Traversal attack test attempting to access `/etc/shadow` through `Z:\` drive.
- Removable media mount/unmount simulation test.

## 17. Performance Requirements
- Zero-copy path translation (string allocation only).
- Direct access to `~/Documents` without filesystem translation latency.

## 18. Compatibility Considerations
- Certain legacy Windows software relies on hardcoded `C:\Windows\System32` paths; prefix symlinks ensure complete compatibility.

## 19. Open Questions
- **OQ-MAP-01:** Should `Z:\` drive be disabled entirely for certified high-security application profiles?
- **OQ-MAP-02:** Should cloud storage directories (Nextcloud, Google Drive) be mounted as separate drive letters (e.g. `G:\`)?

## 20. Related Documents
- [00-application-specification.md](00-application-specification.md)
- [01-installer.md](01-installer.md)
- [02-application-registration.md](02-application-registration.md)
- [04-file-associations.md](04-file-associations.md)
"""

write_file("/root/NebuOS/docs/applications/03-filesystem-mapping.md", a3)

# 04-file-associations.md
a4 = r"""# File Associations Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify MIME type database integration, default application selection, extension-to-MIME mapping, and conflict resolution between Linux and Windows applications in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P6 file associations.

## 2. Purpose
When a user double-clicks a document (`.docx`, `.xlsx`, `.dwg`, `.psd`), the desktop must launch the correct application predictably. This specification defines how NebuOS manages file associations, registers proprietary Windows file extensions into the shared FreeDesktop MIME database, and resolves conflicts when multiple applications claim the same file format.

## 3. Scope
- Shared MIME database updates via `update-mime-database`.
- Configuration of default applications (`mimeapps.list`).
- Conflict arbitration between native Linux apps and sandboxed Windows apps.
- Double-click open-with context menu integration in file manager.
- Dynamic association registration upon application installation.

## 4. Non-goals
- Allowing Windows applications to silently overwrite user-configured default browser or email client.
- Registering executable extensions (`.exe`, `.msi`, `.bat`) to arbitrary applications (always handled by NebuRuntime).

## 5. Requirements
1. **R-ASC-01:** Integrate Windows application file extensions with standard FreeDesktop Shared MIME-Info Specification 2.4.
2. **R-ASC-02:** Store user default application preferences in `~/.config/mimeapps.list`.
3. **R-ASC-03:** Prompt user with an intuitive dialog when a newly installed app offers to handle already-associated extensions.
4. **R-ASC-04:** Provide CLI and D-Bus interfaces to query and update MIME associations.
5. **R-ASC-05:** Cleanly purge registered associations when an application is uninstalled.

## 6. Architecture
File association management operates through standard FreeDesktop mechanisms integrated with the NebuOS Application Manager:

```mermaid
graph TD
    subgraph AppInstall[Application Installation]
        APP[Windows Application Profile]
        EXTS[Supported Extensions: .docx, .xlsx]
    end

    subgraph AssociationManager[NebuOS Association Broker]
        RESOLVER[MIME Conflict Resolver]
        XML_GEN[MIME XML Generator]
        PREF_WRITER[mimeapps.list Writer]
    end

    subgraph SystemMime[System MIME Subsystem]
        MIME_DB[~/.local/share/mime/packages/]
        MIME_LIST[~/.config/mimeapps.list]
        FILE_MGR[NebuFiles / File Manager]
    end

    APP --> EXTS
    EXTS --> RESOLVER
    RESOLVER --> XML_GEN
    RESOLVER --> PREF_WRITER
    XML_GEN --> MIME_DB
    PREF_WRITER --> MIME_LIST
    MIME_DB --> FILE_MGR
    MIME_LIST --> FILE_MGR
```

## 7. Components
1. **MIME Association Broker:** Coordinates MIME type registration during application install and uninstall.
2. **Conflict Arbiter:** Detects when multiple applications support the same MIME type and applies user preferences.
3. **MIME XML Generator:** Emits standard XML definitions for custom or proprietary Windows file formats.
4. **Preferences Synchronizer:** Atomically updates `~/.config/mimeapps.list`.

## 8. Data Flow
1. User installs Microsoft Word 2024.
2. Installer registers support for `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (`.docx`).
3. Conflict Arbiter checks `mimeapps.list`:
   - If no default set: assigns Microsoft Word 2024 as default.
   - If LibreOffice Writer already set: keeps current default, adds Word to "Open With..." secondary options, and displays non-intrusive toast notification: *"Set Word as default for .docx files? [Yes] [Keep Current]"*.
4. User double-clicks `report.docx` in File Manager; system reads `mimeapps.list` and launches Word.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant FM as File Manager
    participant Broker as Association Broker
    participant Mime as mimeapps.list
    participant Launch as nebu-launch

    User->>FM: Double-click "design.dwg"
    FM->>Broker: ResolveDefaultApp("image/vnd.dwg")
    Broker->>Mime: Query [Default Applications]
    Mime-->>Broker: "nebu-com.autodesk.autocad2024.desktop"
    Broker-->>FM: Return desktop entry
    FM->>Launch: Execute nebu-launch com.autodesk.autocad2024 "design.dwg"
```

## 10. Interfaces
- **CLI Management Command:**
  - `nebu mime get <extension>` (e.g. `nebu mime get .dwg`)
  - `nebu mime set <extension> <app_id>` (e.g. `nebu mime set .dwg com.autodesk.autocad2024`)
  - `nebu mime list <app_id>`
- **D-Bus Interface:** `org.nebu.Mime1`
  - `GetDefaultApplication(String mime_type) -> String desktop_file`
  - `SetDefaultApplication(String mime_type, String desktop_file) -> Boolean`

## 11. Dependencies
- `shared-mime-info` package (`update-mime-database`).
- `xdg-utils` (`xdg-mime`).

## 12. Security
- Windows applications cannot unilaterally hijack default browser (`x-scheme-handler/http`, `https`) or terminal handlers without explicit user confirmation.
- Malicious file associations (e.g. associating `.pdf` with an executable launcher script) are blocked by file type validation.

## 13. Resource Requirements
- MIME lookup latency: <= 1.0ms.
- Database update latency (`update-mime-database`): <= 250ms on background thread.
- Memory footprint: zero daemon overhead (queries read static config files directly).

## 14. Failure Modes
1. **Corrupted mimeapps.list:** Malformed syntax caused by abrupt shutdown.
2. **Missing Desktop File:** Associated application was deleted manually.
3. **MIME Database Lock Contention:** Concurrent updates collide on `mime.cache`.

## 15. Recovery Behavior
- Backups of `mimeapps.list` maintained (`mimeapps.list.bak`); corrupt files restored automatically.
- Dangling associations automatically fallback to generic system viewer or prompt user.
- Atomic file renaming prevents database corruption during concurrent writes.

## 16. Testing Requirements
- Unit tests verifying correct MIME type parsing and conflict resolution.
- Automated tests asserting that Windows uninstall cleanly removes registered MIME types.
- System test validating double-click execution flow from File Manager.

## 17. Performance Requirements
- Association resolution time: <= 1.5ms.
- Background MIME database rebuild: <= 400ms.

## 18. Compatibility Considerations
- Bridges Windows registry file association keys (`HKCR\.ext`, `HKCR\App.Assoc`) to Linux MIME types automatically.

## 19. Open Questions
- **OQ-ASC-01:** Should NebuOS provide a centralized "Default Apps" control panel in System Settings in P2 or P6?
- **OQ-ASC-02:** Should extension-less files be inspected via magic byte sniffing before launch?

## 20. Related Documents
- [00-application-specification.md](00-application-specification.md)
- [02-application-registration.md](02-application-registration.md)
- [03-filesystem-mapping.md](03-filesystem-mapping.md)
- [05-uninstallation.md](05-uninstallation.md)
"""

write_file("/root/NebuOS/docs/applications/04-file-associations.md", a4)

# 05-uninstallation.md
a5 = r"""# Application Uninstallation Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the clean removal workflow, prefix purging, orphan detection, user data retention, and registry cleanup for applications in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P6 uninstallation engine.

## 2. Purpose
Traditional Windows uninstallation leaves behind residual registry entries, temp files, and orphaned directories. In NebuOS, because every application runs in an isolated, per-application prefix, uninstallation can be 100% clean and deterministic. This specification defines the uninstallation workflow, data retention options, and artifact removal.

## 3. Scope
- End-to-end uninstallation workflow for Windows and Linux applications.
- Complete prefix purge vs. document data retention options.
- Desktop entry, icon cache, and MIME association removal.
- Running process termination prior to prefix deletion.
- Orphan prefix and dangling symlink detection.

## 4. Non-goals
- Modifying shared system runtimes in `/usr/lib/nebu/runtimes/`.
- Deleting user personal files outside the application prefix (`~/Documents`, `~/Downloads`).
- Restoring uninstalled applications without user backup snapshots.

## 5. Requirements
1. **R-UNS-01:** Provide single-click complete uninstallation from Software Center and application launcher context menu.
2. **R-UNS-02:** Terminate all running processes associated with target application before uninstallation begins.
3. **R-UNS-03:** Prompt user whether to retain or purge application user data (`drive_c/users/nebu/AppData`).
4. **R-UNS-04:** Atomically remove `.desktop` file, icons, and MIME associations.
5. **R-UNS-05:** Delete prefix directory using asynchronous background unlinking to prevent UI freezing.

## 6. Architecture
The uninstallation engine coordinates cleanup across the application registry, desktop integration files, and storage subvolumes:

```mermaid
graph TD
    subgraph Trigger[User Action]
        UI[Right-click Uninstall / Software Center]
    end

    subgraph UninstallerCore[NebuOS Uninstaller Engine]
        PROC_KILLER[Process Terminator]
        REG_PURGER[Application Registry Purger]
        INT_CLEANER[Desktop & MIME Cleaner]
        STORAGE_PURGER[Btrfs Storage Purger]
    end

    subgraph Targets[Cleaned Targets]
        WINE_PROC[wineserver / app.exe]
        DB[~/.local/share/nebu/apps.db]
        DESKTOP[~/.local/share/applications/]
        ICONS[~/.local/share/icons/]
        PFX_DIR[~/.nebu/apps/<app_id>/]
    end

    UI --> PROC_KILLER
    PROC_KILLER --> WINE_PROC
    PROC_KILLER --> REG_PURGER
    REG_PURGER --> DB
    REG_PURGER --> INT_CLEANER
    INT_CLEANER --> DESKTOP
    INT_CLEANER --> ICONS
    REG_PURGER --> STORAGE_PURGER
    STORAGE_PURGER --> PFX_DIR
```

## 7. Components
1. **Process Terminator:** Identifies active cgroup `app-nebu-<app_id>.scope`, sends SIGTERM, waits 2.0s, and issues SIGKILL.
2. **Integration Cleaner:** Unlinks `.desktop` file and icon files, then invokes `update-desktop-database`.
3. **Prefix Purger:** Moves prefix to ephemeral trash directory (`~/.nebu/trash/`) and asynchronously deletes extents.
4. **Orphan Scanner:** Periodic maintenance tool identifying prefixes on disk that have no matching entry in `apps.db`.

## 8. Data Flow
1. User clicks "Uninstall" for `com.autodesk.autocad2024`.
2. UI displays confirmation modal:
   - *"Uninstall AutoCAD 2024? This will free 4.2 GB of disk space."*
   - Checkbox: *[x] Delete application preferences and templates*.
3. User confirms.
4. Process Terminator halts any active AutoCAD processes.
5. Integration Cleaner deletes:
   - `~/.local/share/applications/nebu-com.autodesk.autocad2024.desktop`
   - `~/.local/share/icons/hicolor/256x256/apps/nebu-com.autodesk.autocad2024.png`
6. Association Broker removes AutoCAD from `mimeapps.list`.
7. Storage Purger unlinks `~/.nebu/apps/com.autodesk.autocad2024/`.
8. UI updates application list immediately (< 300ms).

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Shell as NebuShell
    participant Uninst as Uninstaller Service
    participant Cgroup as systemd cgroups
    participant Disk as Btrfs Storage

    User->>Shell: Right click app -> "Uninstall"
    Shell->>Uninst: UninstallApp(app_id, purge_data=true)
    Uninst->>Cgroup: TerminateScope("app-nebu-<app_id>.scope")
    Cgroup-->>Uninst: Scope Empty
    Uninst->>Disk: Remove .desktop and icon files
    Uninst->>Disk: Rename prefix -> ~/.nebu/trash/<app_id>
    Uninst->>Uninst: Spawn background deletion thread (rm -rf)
    Uninst-->>Shell: Success (App removed)
    Shell-->>User: Visual feedback: app removed from launcher
```

## 10. Interfaces
- **D-Bus Interface:** `org.nebu.ApplicationManager1`
  - `UninstallApplication(String app_id, Boolean purge_data) -> Boolean`
- **CLI Command:** `nebu app uninstall <app_id> [--purge-data]`
- **Orphan Cleanup Command:** `nebu app cleanup-orphans`

## 11. Dependencies
- `systemd` cgroup v2 controller.
- Btrfs subvolume / file management tools.
- `update-desktop-database`.

## 12. Security
- Uninstallation strictly validates `app_id` to prevent directory traversal attacks (e.g. passing `../../` to delete arbitrary user directories).
- Prefix deletion runs under user privileges (UID 1000); cannot damage root filesystem.

## 13. Resource Requirements
- Perceived uninstallation latency (time to UI update): <= 300ms.
- Background directory deletion I/O priority: `IDLE` (ionice class 3) to prevent UI lag.
- Memory overhead: <= 8 MB RSS during cleanup.

## 14. Failure Modes
1. **Locked Files:** Process refuses to terminate, holding open file handles.
2. **Permission Denial:** User manually created files with root ownership inside prefix.
3. **Power Interruption During Deletion:** System loses power mid-unlink.

## 15. Recovery Behavior
- Stubborn processes killed forcefully via cgroup `cgroup.kill` interface.
- Permission errors reported to user with clear resolution instructions.
- Staged trash directory (`~/.nebu/trash/`) purged automatically at next system boot.

## 16. Testing Requirements
- Unit tests verifying complete asset removal across 10 sample applications.
- Concurrency test attempting launch during active uninstallation.
- Orphan scanner validation test.

## 17. Performance Requirements
- Immediate UI removal: <= 300ms.
- Complete disk space reclamation: <= 3.0s for 10 GB prefix on SSD.

## 18. Compatibility Considerations
- Deterministic 100% clean uninstall solves the notorious "Windows registry rot" problem entirely.

## 19. Open Questions
- **OQ-UNS-01:** Should NebuOS retain an automated Btrfs snapshot of uninstalled applications for 7 days before permanent deletion?
- **OQ-UNS-02:** Should the user be warned if other installed applications depend on files in the target prefix?

## 20. Related Documents
- [00-application-specification.md](00-application-specification.md)
- [01-installer.md](01-installer.md)
- [02-application-registration.md](02-application-registration.md)
- [04-file-associations.md](04-file-associations.md)
"""

write_file("/root/NebuOS/docs/applications/05-uninstallation.md", a5)

# 06-software-center.md
a6 = r"""# Software Center Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the dual-catalog application store architecture, Flatpak repository integration, certified Windows recipe ecosystem, and graphical store UI in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P6 Software Center.

## 2. Purpose
The Nebu Software Center provides a curated, unified graphical application store. It bridges two distinct application catalogs: native Linux applications (via Flatpak / Flathub) and certified Windows applications (via declarative installation recipes). The user can browse, search, install, and update software through a clean, native interface without using a terminal.

## 3. Scope
- Dual-catalog architecture (Native Linux Flatpaks + Certified Windows Recipes).
- Store user interface layout (Discover, Categories, Installed, Updates).
- Recipe format specification for automated Windows application deployment.
- Flathub integration and Flatpak transaction handling.
- Review, rating, and compatibility certification tier badges.

## 4. Non-goals
- Re-hosting or distributing proprietary, copyrighted commercial Windows binaries directly.
- Maintaining an independent proprietary Linux package repository.
- Payment processing or commercial software billing inside the store.

## 5. Requirements
1. **R-SWC-01:** Implement a responsive, native Rust GUI store interface without Electron or webviews.
2. **R-SWC-02:** Integrate Flathub as the primary source for native open-source Linux software.
3. **R-SWC-03:** Provide a certified Windows Application Recipe catalog guiding automated installation of popular Windows software.
4. **R-SWC-04:** Display clear compatibility tier badges (Certified, Supported, Limited) on all Windows catalog entries.
5. **R-SWC-05:** Manage centralized software update checks for Flatpaks and compatibility profiles.

## 6. Architecture
The Software Center interacts with package backends through a unified abstraction layer:

```mermaid
graph TD
    subgraph UI[Nebu Software Center GUI]
        DISCOVER[Discover View]
        CATALOG[Browse & Categories]
        INSTALLED[Installed Apps View]
        UPDATES[Updates Manager]
    end

    subgraph Backend[Store Backend Service]
        STORE_SVC[nebu-store-daemon]
        FLATPAK_BE[Flatpak Backend libflatpak]
        RECIPE_BE[Windows Recipe Engine]
        CACHE_MGR[Catalog Cache Manager]
    end

    subgraph Upstream[Application Sources]
        FLATHUB[Flathub Repository]
        COMMUNITY_DB[Nebu Compatibility & Recipe Cloud]
        USER_INSTALLER[User Provided Installer .exe/.msi]
    end

    UI --> STORE_SVC
    STORE_SVC --> FLATPAK_BE
    STORE_SVC --> RECIPE_BE
    STORE_SVC --> CACHE_MGR
    FLATPAK_BE <--> FLATHUB
    RECIPE_BE <--> COMMUNITY_DB
    RECIPE_BE <--> USER_INSTALLER
```

## 7. Components
1. **Store GUI (`nebu-software-center`):** Native Slint/Iced application presenting curated app banners, screenshots, reviews, and search.
2. **Flatpak Engine:** Communicates with `libflatpak` to resolve runtimes, handle downloads, and verify GPG signatures.
3. **Windows Recipe Engine:** Interprets declarative JSON recipes that automate prefix setup, required DLL overrides, and installer execution.
4. **Catalog Indexer:** Maintains local SQLite index of available applications for instant, offline search.

## 8. Data Flow
1. User searches for "Blender" in Software Center.
2. Indexer queries local cache:
   - Returns Native Linux Flatpak (v4.2).
   - Returns Windows Build Recipe (v4.2) tagged with compatibility score.
3. User selects Native Linux Flatpak.
4. Store backend issues Flatpak transaction; progress bar updates in UI.
5. Installation completes; desktop shortcut created automatically.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Store as Software Center GUI
    participant Daemon as nebu-store-daemon
    participant Recipe as Recipe Engine
    participant Installer as nebu-installer-ui

    User->>Store: Click "Install Microsoft Office 2024" (Recipe)
    Store->>Daemon: StartRecipeInstall("com.microsoft.office2024")
    Daemon->>Recipe: FetchRecipeManifest()
    Recipe-->>Store: Prompt: "Please select your Office setup.exe or ISO"
    Store->>User: Display file picker dialog
    User->>Store: Selects "/home/nebu/Downloads/OfficeSetup.exe"
    Store->>Installer: ExecuteRecipeWithInstaller(manifest, file_path)
    Installer-->>Store: Installation Completed Successfully
    Store-->>User: Button changes to "Open"
```

## 10. Interfaces
- **Recipe Format Specification (JSON):**
  ```json
  {
    "$schema": "https://nebuos.org/schemas/recipe-v1.json",
    "app_id": "com.notepadplusplus.npp",
    "name": "Notepad++",
    "version": "8.6.9",
    "category": "Development",
    "certification_tier": "Certified",
    "source": {
      "download_url": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6.9/npp.8.6.9.Installer.x64.exe",
      "sha256": "4b4f3b0e3f5e04e9c748cbb3de4d6c77a94f0f089602e1c9535eb07ee2366b59"
    },
    "profile_id": "prof-npp-default",
    "silent_args": ["/S"]
  }
  ```
- **D-Bus Store Service:** `org.nebu.Store1`

## 11. Dependencies
- `libflatpak` >= 1.14.
- `reqwest` / `tokio` (for async catalog and icon downloading).
- `sqlite3` for fast catalog indexing.

## 12. Security
- All downloaded recipe installers verified against cryptographic SHA-256 hashes before execution.
- Flatpak sandbox permissions clearly displayed to user prior to installation.
- Recipes cannot execute arbitrary host shell scripts; only declarative patch operations allowed.

## 13. Resource Requirements
- Store GUI idle memory: <= 55 MB RSS.
- Active browsing / image caching memory: <= 95 MB RSS.
- Search query latency across 5,000 catalog apps: <= 10ms.

## 14. Failure Modes
1. **Network Disconnection During Download:** Partial Flatpak or installer download.
2. **Hash Mismatch:** Upstream vendor updated installer without updating recipe hash.
3. **Disk Exhaustion During Install:** System runs out of disk space mid-download.

## 15. Recovery Behavior
- Resumable downloads via HTTP range requests; automatic retry with exponential backoff.
- Hash mismatch aborts installation immediately, alerts user to potential security risk, and flags recipe for review.
- Pre-install disk space check validates free space before initiating any download.

## 16. Testing Requirements
- Automated test downloading and executing 10 representative free software recipes.
- Flatpak install/uninstall transaction integration test.
- Offline search indexing performance benchmark.

## 17. Performance Requirements
- Software Center cold startup latency: <= 350ms.
- Catalog page navigation: locked 60 FPS.
- Search query typing response: <= 16ms.

## 18. Compatibility Considerations
- Clear visual badges prevent user confusion between native Linux applications and Windows applications.

## 19. Open Questions
- **OQ-SWC-01:** Should user-submitted application ratings and reviews be stored centrally on NebuOS community servers?
- **OQ-SWC-02:** Should Software Center support installing Steam, Lutris, and Heroic Games Launcher directly from the Discover tab?

## 20. Related Documents
- [00-application-specification.md](00-application-specification.md)
- [01-installer.md](01-installer.md)
- [02-application-registration.md](02-application-registration.md)
- [05-uninstallation.md](05-uninstallation.md)
"""

write_file("/root/NebuOS/docs/applications/06-software-center.md", a6)

