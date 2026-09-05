#!/usr/bin/env python3
"""
Generate Applications Documentation for NebuOS (docs/applications/):
- 00-application-model.md
- 01-installation.md
- 02-filesystem-mapping.md
- 03-file-associations.md
- 04-uninstallation.md
- 05-software-center.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs/applications"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_file(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: applications/{filename} ({len(content.splitlines())} lines)")

# 00-application-model.md
write_file("00-application-model.md", """# Unified Application Model Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define the unified data model representing both native Linux and sandboxed Windows applications as first-class desktop entities.

---

## 1. Unified Application Entity Schema
NebuOS abstracts the underlying binary execution model so that the desktop environment, taskbar, search indexer, and package manager interact with a single, uniform application abstraction:

```json
{
  "$schema": "https://nebuos.org/schemas/app-model-v1.json",
  "app_id": "autodesk.autocad.2024",
  "name": "Autodesk AutoCAD 2024",
  "version": "2024.1.2",
  "vendor": "Autodesk, Inc.",
  "categories": ["Graphics", "Engineering", "CAD"],
  "architecture": "x86_64",
  "runtime": {
    "type": "wine",
    "version": "wine-staging-9.2",
    "prefix_path": "~/.nebu/apps/autodesk.autocad.2024"
  },
  "profiles": {
    "compatibility": "autodesk.autocad.2024",
    "graphics": "discrete_forced",
    "patches": ["patch.autodesk.license_stub.v1"]
  },
  "entry_point": {
    "binary_path": "C:\\\\Program Files\\\\Autodesk\\\\AutoCAD 2024\\\\acad.exe",
    "working_directory": "C:\\\\Program Files\\\\Autodesk\\\\AutoCAD 2024",
    "arguments": []
  },
  "integration": {
    "desktop_file": "~/.local/share/applications/autodesk.autocad.2024.desktop",
    "icon_path": "~/.local/share/icons/hicolor/256x256/apps/autodesk.autocad.2024.png",
    "mime_associations": ["application/dwg", "application/dxf"]
  },
  "status": "INSTALLED"
}
```

## 2. Related Documents
- [01-installation.md](01-installation.md)
- [03-file-associations.md](03-file-associations.md)
- [../runtime/00-runtime-overview.md](../runtime/00-runtime-overview.md)
""")

# 01-installation.md
write_file("01-installation.md", """# Application Installation Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Detail the workflow for intercepting Windows `.exe` / `.msi` installers, provisioning prefixes, and registering launchers.

---

## 1. Installation Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Shell as NebuShell
    participant Daemon as nebu-runtime-daemon
    participant DB as CompatDB
    participant Pfx as Prefix Manager
    participant Wine as Wine Installer Engine

    User->>Shell: Double-click setup.exe / installer.msi
    Shell->>Daemon: InspectBinary(path)
    Daemon->>Daemon: Identify Installer Type (Inno, NSIS, InstallShield, MSI)
    Daemon->>DB: QueryAppProfile(pe_hash)
    DB-->>Daemon: Return Profile (Dependencies, DLL Overrides, Patches)
    Daemon->>User: Display Guided Installation Dialog
    User->>Daemon: Click "Install"
    Daemon->>Pfx: ProvisionPrefix(app_id)
    Daemon->>Pfx: InstallDependencies(vcrun, dotnet, fonts)
    Daemon->>Wine: Run Installer in Sandbox
    User->>Wine: Complete Windows Setup Wizard
    Wine-->>Daemon: Installer Process Finished (Exit 0)
    Daemon->>Daemon: Scan prefix drive_c for new .exe entrypoints
    Daemon->>Daemon: Extract Embedded PE Icons to PNG
    Daemon->>Shell: Register .desktop file & MIME types
    Shell->>User: Display Notification: "AutoCAD 2024 Ready to Launch"
```

## 2. Icon Extraction Pipeline
Windows PE binaries embed high-resolution icons within their `.rsrc` section. During installation registration, `nebu-runtime` parses the PE resource directory table, extracts ICO resource group 0, and converts the 256x256 PNG sub-image into standard FreeDesktop icon paths (`~/.local/share/icons/hicolor/256x256/apps/<app_id>.png`).

## 3. Related Documents
- [00-application-model.md](00-application-model.md)
- [03-file-associations.md](03-file-associations.md)
- [04-uninstallation.md](04-uninstallation.md)
""")

# 02-filesystem-mapping.md
write_file("02-filesystem-mapping.md", r"""# Filesystem Mapping Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify the path translation algorithms between Windows backslash notation (`C:\...`) and POSIX filepaths (`/...`).

---

## 1. Path Virtualization Topology

```text
Windows Application View                 Host Linux Filesystem
------------------------                 ---------------------
C:\Program Files                         ~/.nebu/apps/<app_id>/drive_c/Program Files
C:\ProgramData                           ~/.nebu/apps/<app_id>/drive_c/ProgramData
C:\Windows\System32                      ~/.nebu/apps/<app_id>/drive_c/windows/system32
C:\Users\nebu\Documents                  /home/user/Documents (Bind Mounted)
C:\Users\nebu\AppData\Roaming            ~/.nebu/apps/<app_id>/drive_c/users/nebu/AppData/Roaming
Z:\Documents                             /home/user/Documents (Controlled)
Z:\Downloads                             /home/user/Downloads (Controlled)
```

## 2. Path Translation Heuristics in `nebu-runtime`
When a user launches a file from the host Linux desktop (e.g. double-clicking `/home/user/Documents/blueprint.dwg`):
1. NebuRuntime maps the host path to the corresponding Windows virtual path:
   `/home/user/Documents/blueprint.dwg` -> `C:\users\nebu\Documents\blueprint.dwg`
2. Translates path arguments and invokes Wine:
   `wine64 "C:\Program Files\Autodesk\AutoCAD 2024\acad.exe" "C:\users\nebu\Documents\blueprint.dwg"`
3. Handles case-sensitivity differences transparently via Wine's internal case-folding hash table.

## 3. Related Documents
- [00-application-model.md](00-application-model.md)
- [../architecture/04-filesystem.md](../architecture/04-filesystem.md)
""")

# 03-file-associations.md
write_file("03-file-associations.md", """# File Associations Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define MIME type bindings, FreeDesktop desktop entries, and protocol handler registrations for Windows applications.

---

## 1. Desktop Entry Specification (`.desktop`)
For every installed Windows application, NebuOS generates a standard XDG `.desktop` file at `~/.local/share/applications/<app_id>.desktop`:

```ini
[Desktop Entry]
Type=Application
Version=1.4
Name=Autodesk AutoCAD 2024
GenericName=CAD Software
Comment=2D and 3D CAD Design and Drafting
Exec=nebu run autodesk.autocad.2024 %F
Icon=autodesk.autocad.2024
Terminal=false
Categories=Graphics;Engineering;
MimeType=application/dwg;application/dxf;
StartupNotify=true
StartupWMClass=acad.exe
X-Nebu-Application-ID=autodesk.autocad.2024
X-Nebu-Runtime=wine
```

## 2. MIME Association Registry
MIME registrations link Windows extensions directly to NebuRuntime execution wrappers:
- `.docx`, `.doc` -> `microsoft.office.word.2024.desktop`
- `.xlsx`, `.xls` -> `microsoft.office.excel.2024.desktop`
- `.dwg`, `.dxf` -> `autodesk.autocad.2024.desktop`
- `.exe`, `.msi` -> `org.nebu.installer.desktop`

## 3. Related Documents
- [00-application-model.md](00-application-model.md)
- [01-installation.md](01-installation.md)
""")

# 04-uninstallation.md
write_file("04-uninstallation.md", """# Application Uninstallation Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define clean, atomic application removal, prefix deletion, and user data preservation policies.

---

## 1. Atomic Uninstallation Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Shell as Nebu Software Center / UI
    participant Daemon as nebu-runtime-daemon
    participant Pfx as Prefix Manager

    User->>Shell: Click "Uninstall AutoCAD 2024"
    Shell->>User: Prompt: "Keep user project files in Documents? [Yes / No]"
    User->>Shell: Confirm (Yes)
    Shell->>Daemon: UninstallApplication(app_id, keep_documents=true)
    Daemon->>Daemon: Kill active wineserver & processes for app_id
    Daemon->>Daemon: Remove .desktop entry & MIME bindings
    Daemon->>Daemon: Purge ~/.nebu/cache/shaders/<app_id>
    Daemon->>Pfx: Delete subvolume ~/.nebu/apps/<app_id>
    Daemon->>Daemon: Remove entry from SQLite applications table
    Daemon-->>Shell: Uninstallation Complete
    Shell->>User: Notification: "AutoCAD 2024 Successfully Removed"
```

## 2. Clean State Invariant
Unlike standard Windows where uninstallation leaves orphan registry keys and files in `%APPDATA%`, NebuOS removes the entire prefix subvolume. The system is left in an identical state to before the application was ever installed.

## 3. Related Documents
- [00-application-model.md](00-application-model.md)
- [01-installation.md](01-installation.md)
- [05-software-center.md](05-software-center.md)
""")

# 05-software-center.md
write_file("05-software-center.md", """# Nebu Software Center Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Detail the graphical software store, catalog browsing, Flatpak integration, and certified Windows profile recipes.

---

## 1. Dual-Catalog Architecture
Nebu Software Center manages two complementary software ecosystems:
1. **Native Linux Applications:** Curated Flatpak repository integration (Flathub verified).
2. **Certified Windows Profiles:** A catalog of pre-tested, certified compatibility recipes for popular Windows applications (Office, AutoCAD, Adobe Creative Cloud, Steam).

## 2. Zero-Piracy / Legal Policy
- **Strict Prohibition:** NebuOS never distributes, caches, or redistributes proprietary Windows binaries.
- **Recipe Workflow:** The Software Center provides the certified recipe (Wine settings, registry templates, dependency requirements). When the user clicks "Install", the software center prompts:
  `"Please select your official installer executable (.exe / .msi) or insert installation media."`

## 3. Related Documents
- [00-application-model.md](00-application-model.md)
- [01-installation.md](01-installation.md)
- [../compatibility/04-certification.md](../compatibility/04-certification.md)
""")

print("Applications documentation generated successfully.")
