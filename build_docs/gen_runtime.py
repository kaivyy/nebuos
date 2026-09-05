#!/usr/bin/env python3
"""
Generate Runtime Documentation for NebuOS (docs/runtime/):
- 00-runtime-overview.md
- 01-application-lifecycle.md
- 02-windows-runtime.md
- 03-prefix-management.md
- 04-wine-integration.md
- 05-proton-integration.md
- 06-dependencies.md
- 07-error-handling.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs/runtime"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_file(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: runtime/{filename} ({len(content.splitlines())} lines)")

# 00-runtime-overview.md
write_file("00-runtime-overview.md", """# Runtime Architecture Overview — NebuOS

**Status:** REVIEW  
**Purpose:** Establish the technical foundation of NebuRuntime, the primary engine executing Windows PE executables natively on Linux without a hypervisor.

---

## 1. Scope & Execution Philosophy
NebuRuntime transforms Windows PE32/PE32+ binaries into first-class managed entities on Linux. Rather than forcing users to manually configure Wine prefixes, environment variables, and DLL overrides, NebuRuntime automates executable analysis, compatibility database lookup, sandbox instantiation, prefix lifecycle management, and graphics stack selection.

## 2. Prohibition of Virtualization
Under no circumstances does NebuRuntime invoke a virtual machine (KVM, QEMU, VirtualBox, VMware) to execute Windows workloads. Applications requiring Windows kernel-mode drivers (`.sys`), unsupported anti-cheat, or proprietary hardware ring-0 interfaces are explicitly marked **UNSUPPORTED** and safely rejected.

## 3. Subsystem Component Map

```mermaid
graph TD
    subgraph INGESTION [Binary Ingestion]
        EXE[User Double-Click / CLI: app.exe]
        MIME[xdg-open / binfmt_misc]
    end

    subgraph RUNTIME_CORE [NebuRuntime Core - Rust]
        PE_SCAN[PE Header Analyzer & Hasher]
        COMPAT_LOOKUP[Compat DB Query Engine]
        PROFILE_ENG[Profile Applicator]
        PREFIX_MGR[Prefix Manager & Btrfs Snapper]
        SANDBOX_WRAP[Bubblewrap Sandbox Wrapper]
    end

    subgraph EXECUTION [Execution Engines]
        WINE_ENV[Wine Runtime Engine: Office / CAD / Tools]
        PROTON_ENV[Proton Runtime Engine: Games / DXVK / VKD3D]
    end

    subgraph OS_LAYER [Linux Host Foundation]
        WAYLAND[NebuCompositor Socket]
        PIPEWIRE[PipeWire Socket]
        GPU_DEV[Mesa / DRM Render Nodes]
    end

    EXE --> MIME
    MIME --> PE_SCAN
    PE_SCAN --> COMPAT_LOOKUP
    COMPAT_LOOKUP --> PROFILE_ENG
    PROFILE_ENG --> PREFIX_MGR
    PREFIX_MGR --> SANDBOX_WRAP
    SANDBOX_WRAP -->|Desktop App| WINE_ENV
    SANDBOX_WRAP -->|Game Binary| PROTON_ENV
    WINE_ENV --> OS_LAYER
    PROTON_ENV --> OS_LAYER
```

## 4. Architectural Invariants
1. **Per-Application Prefix Isolation:** Every certified Windows application resides in an isolated prefix directory (`~/.nebu/apps/<app_id>/`). A crash or configuration change in AutoCAD never affects Microsoft Office or Photoshop.
2. **Deterministic Startup:** Prefix creation happens once during initial installation. Routine launches reuse cached state, launching within 1.5 to 3 seconds.
3. **Crash Isolation:** A crashing Wine process terminates within its sandbox. `NebuShell`, `NebuCompositor`, and other running applications remain entirely unaffected.

## 5. Related Documents
- [01-application-lifecycle.md](01-application-lifecycle.md)
- [02-windows-runtime.md](02-windows-runtime.md)
- [03-prefix-management.md](03-prefix-management.md)
""")

# 01-application-lifecycle.md
write_file("01-application-lifecycle.md", """# Application Lifecycle Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Formulate the end-to-end lifecycle state machine of an application in NebuOS from detection through installation, execution, repair, and termination.

---

## 1. Application Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> Ingested: User opens .exe / .desktop
    Ingested --> Identifying: Compute SHA-256 & Inspect PE
    
    state Identifying {
        [*] --> QueryDB
        QueryDB --> ProfileFound: Match in CompatDB
        QueryDB --> GenericFallback: Unknown Executable
    }

    Identifying --> Provisioning: Check Prefix Status
    
    state Provisioning {
        [*] --> CheckPrefix
        CheckPrefix --> CreatePrefix: Prefix Missing
        CreatePrefix --> ApplyPatches: Seed Template
        CheckPrefix --> VerifyHealth: Prefix Exists
        VerifyHealth --> ApplyPatches: Config Update
    }

    Provisioning --> Launching: Configure Sandbox & Env
    Launching --> Running: wineserver Active & Process Forked
    
    state Running {
        [*] --> Monitoring
        Monitoring --> HealthyRunning: Active Render Loops
        Monitoring --> Degraded: High Fault Rate
    }

    Running --> Terminated: Clean Application Exit (0)
    Running --> Crashed: Non-zero Exit / SEGV / DLL Fault
    
    Crashed --> DiagnosticUI: Prompt User (Repair / View Logs)
    DiagnosticUI --> Provisioning: Rollback / Rebuild Cache
    
    Terminated --> [*]: Session Cleaned
```

## 2. Lifecycle Stages in Detail

### Stage 1: Ingestion & Fingerprinting
- **Input:** Target file path (`/path/to/target.exe`).
- **Inspection:** Inspect PE header for subsystem (`IMAGE_SUBSYSTEM_WINDOWS_GUI` vs `IMAGE_SUBSYSTEM_WINDOWS_CUI`), target architecture (x86 vs x86_64), imports table (Direct3D, Vulkan, .NET, COM dependencies), and compute SHA-256 hash.

### Stage 2: Compatibility Lookup
- NebuRuntime queries local SQLite database `~/.local/share/nebu/compat.db`.
- Matches known application profile (e.g. `autodesk.autocad.2024`). If no match is found, assigns default fallback profile `generic.desktop.x86_64`.

### Stage 3: Prefix Provisioning & Verification
- Validates prefix at `~/.nebu/apps/<app-id>/`. If absent, provisions a fresh prefix using Btrfs `reflink` from `/usr/share/nebu/prefix-template/`.
- Applies declarative registry changes, DLL overrides, and patch files specified in the profile.

### Stage 4: Sandboxed Execution
- Spawns Bubblewrap container with scoped bind-mounts.
- Injects environment variables (`WINEPREFIX`, `WINEDLLOVERRIDES`, `DXVK_STATE_CACHE_PATH`, `DRI_PRIME`).
- Launches `wine64` and starts the application process.

### Stage 5: Process Monitoring & Telemetry
- NebuRuntime monitors process group via cgroups v2 (`/sys/fs/cgroup/user.slice/user-1000.slice/app-nebu-<app-id>.scope`).
- Collects stderr/stdout to rotating log file: `~/.nebu/apps/<app-id>/logs/runtime.log`.

## 3. Related Documents
- [02-windows-runtime.md](02-windows-runtime.md)
- [03-prefix-management.md](03-prefix-management.md)
- [07-error-handling.md](07-error-handling.md)
""")

# 02-windows-runtime.md
write_file("02-windows-runtime.md", """# Windows Runtime Daemon Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Detail the implementation architecture of `nebu-runtime-daemon` and the `nebu` CLI tool.

---

## 1. Daemon Architecture (`neburuntimed`)
- **Service Name:** `nebu-runtime.service` (systemd user unit).
- **Language:** Rust (Tokio async runtime).
- **IPC Interface:** D-Bus service `org.nebu.Runtime1`.

```mermaid
graph TD
    CLI[nebu CLI] -->|D-Bus| DAEMON[nebu-runtime-daemon]
    SHELL[NebuShell] -->|D-Bus| DAEMON
    FILE_MGR[File Manager] -->|D-Bus| DAEMON
    
    subgraph DAEMON_INTERNALS [nebu-runtime-daemon Architecture]
        REQ_HANDLER[Async Request Dispatcher]
        PE_PARSER[PE32+ Binary Header Parser]
        DB_CLIENT[SQLite3 Connection Pool]
        CGROUP_MGR[cgroups v2 Resource Allocator]
        BWRAP_EXEC[Process Launcher & Sandbox Engine]
    end

    DAEMON --> REQ_HANDLER
    REQ_HANDLER --> PE_PARSER
    REQ_HANDLER --> DB_CLIENT
    REQ_HANDLER --> CGROUP_MGR
    REQ_HANDLER --> BWRAP_EXEC
```

## 2. CLI Tooling Specification (`nebu`)
The `nebu` command-line utility provides administrative and developer access to the runtime:

```bash
# Launch a Windows application directly
nebu run /path/to/setup.exe

# Launch in diagnostic / verbose debug mode
nebu run --debug autodesk.autocad.2024

# Manage application prefixes
nebu prefix list
nebu prefix repair autodesk.autocad.2024
nebu prefix snapshot create autodesk.autocad.2024 --tag "pre-update"
nebu prefix snapshot rollback autodesk.autocad.2024 --tag "pre-update"
nebu prefix reset autodesk.autocad.2024

# Query application compatibility
nebu compat query "AutoCAD 2024"
nebu compat info autodesk.autocad.2024
```

## 3. Related Documents
- [01-application-lifecycle.md](01-application-lifecycle.md)
- [03-prefix-management.md](03-prefix-management.md)
- [../compatibility/01-database-schema.md](../compatibility/01-database-schema.md)
""")

# 03-prefix-management.md
write_file("03-prefix-management.md", """# Prefix Management Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define the filesystem layout, provisioning algorithms, snapshot mechanisms, and repair routines for isolated Wine application prefixes.

---

## 1. Prefix Directory Layout
Every managed Windows application receives a dedicated prefix root at `~/.nebu/apps/<app-id>/`:

```text
~/.nebu/apps/autodesk.autocad.2024/
├── metadata.json          # Application configuration, profile ID, runtime version
├── system.reg             # Wine system registry hive
├── user.reg               # Wine user registry hive
├── userdef.reg            # Default user registry
├── dosdevices/            # Drive letter mappings
│   ├── c: -> ../drive_c
│   └── z: -> /home/user/Documents (Restricted)
├── drive_c/
│   ├── Program Files/
│   ├── Program Files (x86)/
│   ├── ProgramData/
│   ├── users/
│   │   └── nebu/
│   │       ├── AppData/
│   │       │   ├── Local/
│   │       │   └── Roaming/
│   │       └── Documents/ -> /home/user/Documents
│   └── windows/
│       ├── system32/
│       └── syswow64/
├── logs/                  # Rotating runtime and Wine crash logs
└── snapshots/             # Read-only Btrfs snapshot points
```

## 2. Instant Provisioning via Btrfs `reflink`
Creating a full 64-bit Wine prefix normally takes 10 to 30 seconds via `wineboot`. NebuOS achieves prefix provisioning in **< 150 ms**:
1. Base template prefix is pre-generated at OS build time: `/usr/share/nebu/prefix-template/`.
2. Upon new app installation, `nebu-runtime` executes a Btrfs reflink copy:
   `cp -r --reflink=always /usr/share/nebu/prefix-template ~/.nebu/apps/<app_id>`
3. Allocates zero additional disk blocks initially; blocks are duplicated copy-on-write only when modified.

## 3. Snapshot & Rollback Architecture
- **Automatic Pre-Patch Snapshot:** Prior to applying any profile update, patch, or redistributable installer, NebuRuntime generates a snapshot: `snapshots/auto-snapshot-<timestamp>`.
- **Instant Rollback:** If the application fails to initialize within 3 attempts following an update, NebuRuntime prompts the user to restore the snapshot, executing in < 50 ms.

## 4. Related Documents
- [02-windows-runtime.md](02-windows-runtime.md)
- [04-wine-integration.md](04-wine-integration.md)
- [../architecture/04-filesystem.md](../architecture/04-filesystem.md)
""")

# 04-wine-integration.md
write_file("04-wine-integration.md", """# Wine Integration Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify how NebuOS integrates upstream Wine, manages multiple Wine runtime trees, injects DLL overrides, and orchestrates `wineserver`.

---

## 1. Upstream Wine Tracking Policy
NebuOS strictly avoids maintaining a monolithic, permanently out-of-tree Wine fork. 
- **Upstream Re-Use:** Packages upstream Wine releases into modular runtimes placed under `/usr/lib/nebu/runtimes/wine/`:
  - `wine-stable-9.x`: Hardened, enterprise-grade compatibility.
  - `wine-staging-9.x`: Incorporates experimental userland patches, essential for cutting-edge CAD and Office functionality.
- **Nebu Patch Policy:** Custom Wine patches are maintained as discrete, rebasable `.patch` sets against upstream tags, submitted upstream to `wine-devel` wherever accepted.

## 2. DLL Overrides & Architecture

```mermaid
graph TD
    APP_EXE[Windows PE: acad.exe] --> LOADER[Wine DLL Dynamic Linker]
    LOADER --> CONFIG{Override Check in WINEDLLOVERRIDES}
    
    CONFIG -->|native,builtin| NATIVE[Native Windows DLL in drive_c/windows/system32]
    CONFIG -->|builtin,native| BUILTIN[Wine Builtin DLL /so Library]
    
    NATIVE -->|Fallback if Missing| BUILTIN
```

### Critical Overrides for Target Applications
- **Microsoft Office (2019/2021/2024):**
  `WINEDLLOVERRIDES="mso40i=native,builtin;riched20=native,builtin;ole32=native,builtin"`
- **Autodesk AutoCAD 2024:**
  `WINEDLLOVERRIDES="d3d11=native,builtin;dxgi=native,builtin;d3dcompiler_47=native"`

## 3. Wineserver Management & IPC
- **Ephemeral Process Group:** `wineserver` is launched within the application's dedicated Bubblewrap sandbox.
- **Socket Isolation:** Each prefix creates its isolated wineserver socket at `/run/user/1000/nebu/<app_id>/wineserver.sock`. Two running applications never share a wineserver instance.

## 4. Related Documents
- [00-runtime-overview.md](00-runtime-overview.md)
- [05-proton-integration.md](05-proton-integration.md)
- [06-dependencies.md](06-dependencies.md)
""")

# 05-proton-integration.md
write_file("05-proton-integration.md", """# Proton Integration Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Detail the specialized integration of Valve's Proton runtime, DXVK, and VKD3D for Windows gaming workloads on NebuOS.

---

## 1. Runtime Selection Heuristic: Wine vs Proton
NebuRuntime automatically selects between standard Wine and Proton:

```mermaid
flowchart TD
    START[Executable Ingested] --> DB_CHECK{Known Game in CompatDB?}
    DB_CHECK -->|Yes| SELECT_PROTON[Select Proton Runtime]
    DB_CHECK -->|No| STEAM_CHECK{Launched via Steam / Game Manifest?}
    STEAM_CHECK -->|Yes| SELECT_PROTON
    STEAM_CHECK -->|No| GFX_CHECK{Requires DX12 / DirectInput Gamepad?}
    GFX_CHECK -->|Yes| SELECT_PROTON
    GFX_CHECK -->|No| SELECT_WINE[Select Standard Wine Runtime]
```

## 2. Proton Components & Graphics Translation
- **DXVK:** Translates DirectX 9, 10, and 11 calls into Vulkan API calls.
- **VKD3D-Proton:** Translates modern DirectX 12 calls into low-overhead Vulkan command buffers.
- **FS Hack / Wayland Fullscreen:** Enables borderless Wayland fullscreen mode and integer scaling for classic retro games.
- **Game Controller Forwarding:** Direct integration with `libevdev` and `hidraw`, passing Xbox, DualShock, DualSense, and Nintendo Switch controller inputs directly into `xinput1_3.dll`.

## 3. Related Documents
- [04-wine-integration.md](04-wine-integration.md)
- [../graphics/03-dxvk-vkd3d.md](../graphics/03-dxvk-vkd3d.md)
""")

# 06-dependencies.md
write_file("06-dependencies.md", """# Windows Dependencies Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define automated installation, caching, and management of Windows redistributable dependencies (Visual C++, .NET, DirectX, Core Fonts).

---

## 1. Dependency Engine Architecture
NebuRuntime contains a declarative dependency resolution engine. When an application profile specifies a dependency, NebuRuntime installs it into the private prefix without requiring manual winetricks interaction.

```mermaid
graph LR
    DEP_SPEC[Profile: autodesk.autocad.2024] -->|Requires: vcredist2019, dotnet48, corefonts| RESOLVER[Nebu Dependency Resolver]
    RESOLVER --> CACHE_CHECK{Cached in /var/cache/nebu/redist?}
    CACHE_CHECK -->|Yes| SHA_VERIFY[Verify SHA-256 Checksum]
    CACHE_CHECK -->|No| DOWNLOAD[Download from Official CDN]
    DOWNLOAD --> SHA_VERIFY
    SHA_VERIFY --> INJECT[Silent Unattended Install into Prefix]
```

## 2. Core Supported Dependency Registry

| Dependency ID | Windows Package Name | Primary Target Applications | Installation Method |
|---|---|---|---|
| `vcrun2015_2022` | Microsoft Visual C++ 2015-2022 Redistributable (x64) | AutoCAD, Maya, Office 2024, Modern Games | Silent MSI / EXE install (`/quiet /norestart`) |
| `dotnet48` | Microsoft .NET Framework 4.8 | CAD Add-ins, Engineering Tools | Silent Wine install with staging patches |
| `wine-mono` | Open-source .NET implementation | General Windows utilities | Direct unpack into prefix |
| `corefonts` | Microsoft TrueType Core Fonts (Arial, Times, Calibri) | Microsoft Office, General Document Viewers | Extracted directly into `drive_c/windows/fonts` |
| `d3dcompiler_47`| Direct3D Shader Compiler 47 | 3D Viewports, CAD Renderers | Copied to `system32` with native DLL override |

## 3. Integrity Verification & Licensing
All downloaded redistributable packages are validated against hardcoded SHA-256 digests in the Nebu database. Proprietary packages are downloaded on-demand from vendor CDNs directly onto the user's machine; NebuOS does not host or redistribute proprietary binaries.

## 4. Related Documents
- [03-prefix-management.md](03-prefix-management.md)
- [../compatibility/02-profiles.md](../compatibility/02-profiles.md)
""")

# 07-error-handling.md
write_file("07-error-handling.md", """# Runtime Error Handling Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Establish failure detection, crash classification, prefix corruption recovery, and user-facing diagnostic workflows.

---

## 1. Crash Detection & Recovery Flow

```mermaid
sequenceDiagram
    autonumber
    participant App as Wine App Process
    participant Sand as Bubblewrap Sandbox
    participant Daemon as nebu-runtime-daemon
    participant UI as Diagnostic Modal UI
    participant Pfx as Prefix Manager

    App->>Sand: SIGSEGV / Unhandled Exception (c0000005)
    Sand->>Daemon: Process Exit Status != 0
    Daemon->>Daemon: Inspect rotating log (runtime.log)
    Daemon->>Daemon: Match Known Crash Signature
    Daemon->>UI: Emit org.nebu.Runtime1.ApplicationCrashed
    UI->>User: Display Crash Dialog with Actionable Options
    User->>UI: Select "Restore Previous Working Snapshot"
    UI->>Pfx: Rollback Prefix to pre-crash snapshot
    Pfx-->>UI: Rollback Succeeded
    UI->>User: Notify Ready to Relaunch
```

## 2. Crash Classification Taxonomy

| Error Code | Classification | Root Cause | Automated Recovery Strategy |
|---|---|---|---|
| `0xC0000005` | Access Violation | Missing DLL override, invalid memory pointer, or page fault. | Verify DLL overrides against profile; trigger registry verification. |
| `0xC0000135` | DLL Not Found | Application failed to locate dependency DLL in search path. | Check dependency manifest; automatically prompt to reinstall missing VC++ / .NET runtime. |
| `0x80004005` | COM Unspecified Error | OLE/COM interface not registered in prefix registry. | Re-run `regsvr32` on registered COM modules in profile. |
| `0xDEADBEEF` | Wine Staging Assertion | Incompatible graphics call or unhandled NT kernel ioctl. | Offer toggle: Fallback from DXVK to Mesa wined3d OpenGL. |

## 3. User Diagnostic Dialog Options
When an application terminates unexpectedly, the user is never left with an empty silence or cryptic terminal error. The graphical diagnostic modal presents:
1. **[Relaunch Application]** (with clean temporary state).
2. **[Repair Prefix]** (re-registers DLLs and restores default registry hives).
3. **[Rollback Snapshot]** (reverts to last known working state).
4. **[View Diagnostic Logs]** (opens clean graphical log viewer).
5. **[Submit Anonymous Report]** (sanitized crash report sent to Nebu Compatibility Lab).

## 4. Related Documents
- [01-application-lifecycle.md](01-application-lifecycle.md)
- [03-prefix-management.md](03-prefix-management.md)
- [../compatibility/06-known-limitations.md](../compatibility/06-known-limitations.md)
""")

print("Runtime documentation generated successfully.")
