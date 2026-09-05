#!/usr/bin/env python3
"""
Generate Architecture Documentation for NebuOS (docs/architecture/):
- 00-overview.md
- 01-system-architecture.md
- 02-boot-and-init.md
- 03-process-and-ipc.md
- 04-filesystem.md
- 05-security.md
- 06-hardware.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs/architecture"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_file(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: architecture/{filename} ({len(content.splitlines())} lines)")

# 00-overview.md
write_file("00-overview.md", """# Architecture Overview — NebuOS

**Status:** REVIEW  
**Purpose:** Provide the top-level architectural framework, core principles, system boundary definitions, and design invariants governing NebuOS.

---

## 1. Scope & System Purpose
NebuOS is an immutable, desktop-focused Linux operating system engineered to execute both native Linux applications and Windows PE binaries with seamless, native-feeling responsiveness. NebuOS eliminates the operational complexity of Wine prefix tuning, Winetricks scripts, and graphics backend configuration through a system-level compatibility layer while strictly prohibiting virtualization (VMs).

## 2. Non-Goals
- Designing or maintaining a custom kernel from scratch.
- Replacing mature Linux graphics stacks (Mesa, DRM/KMS, Vulkan, Wayland).
- Providing hypervisor-based compatibility (QEMU, KVM, VirtualBox).
- Developing a 100% clone of the Windows NT userland.

## 3. Core Architectural Principles
1. **Upstream Foundation First:** Reuse the Linux kernel, systemd, udev, Mesa, PipeWire, NetworkManager, and upstream Wine. Custom code is written exclusively where systemic integration gaps exist.
2. **Strict Component Isolation:** Userland desktop elements (NebuCompositor, NebuShell) run as unprivileged user processes. Windows applications execute in sandboxed, per-application isolated prefixes.
3. **Rust as System Implementation Language:** All Nebu-original components (`nebu-compositor`, `nebu-shell`, `nebu-runtime`, `nebu-compat`, `nebu-patcher`) are authored in memory-safe Rust.
4. **Predictable Low-End Performance:** Architecture guarantees fluent desktop operation on 4 GB RAM dual-core x86_64 machines (< 800 MB idle memory).

## 4. High-Level Subsystem Map

```mermaid
graph TD
    subgraph HW [Hardware Infrastructure]
        CPU[x86_64 CPU]
        GPU[Intel / AMD / NVIDIA GPU]
        STOR[NVMe / SATA SSD]
    end

    subgraph KERNEL [Kernel & Drivers]
        K[Linux Kernel 6.x]
        DRM[DRM / KMS Driver]
        KVM_NO[No VM Allowed]
    end

    subgraph BASE [Base OS - Fedora Atomic]
        SYSTEMD[systemd Init & Services]
        MESA[Mesa 24+ / Vulkan / OpenGL]
        PIPE[PipeWire Audio]
        NET[NetworkManager]
    end

    subgraph DESKTOP [Nebu Desktop Layer - Rust]
        COMP[NebuCompositor - Wayland]
        SHELL[NebuShell - Native UI]
    end

    subgraph RUNTIME [Nebu Application Platform]
        APP_MGR[Nebu App Manager]
        RUNTIME_D[Nebu Runtime Daemon]
        COMPAT_DB[(SQLite Compatibility DB)]
        PATCH_ENG[Nebu Patch Engine]
    end

    subgraph COMPAT_LAYER [Execution Engines]
        WINE[Wine Upstream / Patched]
        PROTON[Proton + DXVK + VKD3D]
    end

    subgraph APPS [Workloads]
        LINUX_APP[Native Linux Apps / Flatpak]
        WIN_APP[Windows Apps: Office, AutoCAD, etc.]
        GAME[Windows Games]
    end

    HW --> KERNEL
    KERNEL --> BASE
    BASE --> DESKTOP
    DESKTOP --> RUNTIME
    RUNTIME --> LINUX_APP
    RUNTIME --> COMPAT_LAYER
    COMPAT_LAYER --> WIN_APP
    COMPAT_LAYER --> GAME
```

## 5. Subsystem Summary Table

| Subsystem | Upstream Technology | Nebu In-House Technology | Primary Responsibility |
|---|---|---|---|
| Core Kernel & Drivers | Linux Kernel, DRM/KMS, Mesa | HW Tuning Profiles | Hardware control, direct scanout, GPU buffer allocation. |
| OS Base & Immutability | Fedora Atomic, ostree, bootc | Staged Update Agent | Read-only rootfs (`/usr`), atomic deployments, A/B rollback. |
| Display & Windowing | Wayland Protocol, libinput | `nebu-compositor` (Rust) | Buffer composition, frame scheduling, multi-monitor, HiDPI. |
| Desktop Shell | FreeDesktop specs | `nebu-shell` (Rust) | Taskbar, launcher, quick settings, workspace manager. |
| Runtime & Compatibility | Wine, Proton, DXVK, VKD3D | `nebu-runtime`, `nebu-patcher` | PE binary detection, prefix lifecycle, DLL overrides, sandboxing. |
| Metadata & Intelligence | SQLite 3 | `nebu-compat-db` | Application profiles, certified configurations, hardware limits. |

## 6. Failure Modes & Degradation
- **Compositor Crash:** Monitored by systemd user session watchdog. Upon unexpected crash, state is serialized to IPC shm, restarting the compositor without terminating client processes.
- **Prefix Corruption:** NebuRuntime captures crash loops, automatically offering snapshot rollback to the last known working state.

## 7. Related Documents
- [01-system-architecture.md](01-system-architecture.md)
- [02-boot-and-init.md](02-boot-and-init.md)
- [../runtime/00-runtime-overview.md](../runtime/00-runtime-overview.md)
""")

# 01-system-architecture.md
write_file("01-system-architecture.md", """# System Architecture Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define the complete vertical stack of NebuOS, component interactions, interface boundaries, and operational invariants.

---

## 1. System Topology & Layers
NebuOS is structured into seven distinct architectural layers, ensuring strict encapsulation and unidirectional dependencies.

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Shell as NebuShell
    participant Runtime as NebuRuntime
    participant DB as CompatDB
    participant Prefix as App Prefix (~/.nebu/apps)
    participant Wine as Wine/Proton Server
    participant Mesa as Mesa/DRM
    participant Comp as NebuCompositor

    User->>Shell: Double-click setup.exe or app.exe
    Shell->>Runtime: LaunchRequest(exe_path, args) via D-Bus
    Runtime->>DB: QueryAppProfile(hash, pe_header)
    DB-->>Runtime: Return Profile(Wine-ver, DLL_overrides, GfxProfile)
    Runtime->>Prefix: EnsurePrefixExists(app_id)
    Runtime->>Prefix: ApplyPatchesAndRegistry(profile)
    Runtime->>Wine: Spawn wine64 with LD_PRELOAD & Env
    Wine->>Mesa: Vulkan/OpenGL Rendering Call
    Mesa->>Comp: Wayland Surface Commit (dmabuf)
    Comp->>User: Display Composited Frame on Screen
```

## 2. Detailed Layer Specifications

### Layer 1: Hardware & Kernel Foundation
- **Linux Kernel:** Standard LTS Linux kernel (6.6+ or 6.10+ as supplied by Fedora Atomic base).
- **Core Drivers:** In-tree DRM drivers (`i915`/`xe`, `amdgpu`, `nouveau`), proprietary NVIDIA via pre-compiled OSTree kmods.
- **Kernel Tunables:** `vm.max_map_count=2147483642` (mandatory for high-end Windows games and CAD runtime), `fs.file-max=2097152`, `split_lock_mitigate=0` for uninhibited Wine performance.

### Layer 2: Base Operating System (Fedora Atomic)
- **Deployment Model:** OCI container-based image deployments (`bootc` / `rpm-ostree`).
- **Filesystem Security:** `/usr` mounted read-only; `/etc` writable state managed via 3-way merge; `/var` persistent state.
- **Core Services:** `systemd` (init, cgroups v2, user sessions), `udev` (dynamic device enumeration), `NetworkManager`, `PipeWire` + `wireplumber` (audio/video pipeline).

### Layer 3: Display & Compositing Engine (`nebu-compositor`)
- **Protocol:** Wayland Core Protocol + `xdg_shell`, `linux_dmabuf_v1`, `viewporter`, `fractional_scale_v1`.
- **Backend:** DRM/KMS backend using Direct Render Nodes (`/dev/dri/cardX`, `/dev/dri/renderD128`).
- **Memory Footprint:** Budgeted <= 75 MB RSS on idle.

### Layer 4: Desktop Shell (`nebu-shell`)
- **Architecture:** Standalone Wayland client communicating via `wlr-layer-shell-unstable-v1` and custom IPC.
- **Rendering:** GPU-accelerated via Slint or Iced toolkit utilizing Vulkan/OpenGL. Strict prohibition against Chromium/Electron.
- **Components:** System Panel, Application Launcher, Quick Settings, System Tray (StatusNotifierWatcher), Lock Screen.

### Layer 5: Nebu Application Platform & Runtime
- **Daemon:** `neburuntimed` running as a `systemd --user` service.
- **Responsibilities:** PE header inspection, SHA-256 fingerprinting, prefix provisioning, environment sanitization, sandbox invocation (`bwrap`).

### Layer 6: Windows Compatibility Infrastructure
- **Wine Foundation:** Reused upstream Wine binaries (Stable & Staging trees) decoupled from base OS.
- **Proton Infrastructure:** Valve Proton runtime bundles deployed in `/usr/lib/nebu/runtimes/proton/` for gaming applications.
- **Translation Stacks:** DXVK (Direct3D 9/10/11 -> Vulkan), VKD3D-Proton (Direct3D 12 -> Vulkan).

### Layer 7: Applications & Storage
- Native Linux applications (packaged via Flatpak or system packages).
- Managed Windows applications residing within isolated directories: `~/.nebu/apps/<app-id>/`.

## 3. Data Interfaces & Contracts
1. **Shell-to-Runtime IPC:** D-Bus service `org.nebu.Runtime1` on the Session Bus.
2. **Runtime-to-Database:** In-process SQLite3 binding via `rusqlite` with WAL mode enabled.
3. **Compositor-to-Clients:** Standard Wayland UNIX domain socket (`$XDG_RUNTIME_DIR/wayland-0`).

## 4. Security & Privilege Boundaries
- NebuCompositor and NebuShell execute under the standard unprivileged user session UID (1000).
- Windows PE binaries are jailed using unprivileged user namespaces (`bwrap`):
  - Read-only bind mount of base system: `/usr`, `/lib64`.
  - Isolated temporary directory: isolated `/tmp`.
  - Filtered `/home`: Only `~/.nebu/apps/<app-id>/drive_c` and explicitly whitelisted user folders (`~/Documents`, `~/Downloads`) are exposed.

## 5. Performance Invariants
- Zero polling threads in system daemons; 100% epoll/eventfd event-driven loops.
- Idle CPU consumption across all Nebu background daemons < 0.5% total CPU utilization.

## 6. Related Documents
- [02-boot-and-init.md](02-boot-and-init.md)
- [03-process-and-ipc.md](03-process-and-ipc.md)
- [05-security.md](05-security.md)
""")

# 02-boot-and-init.md
write_file("02-boot-and-init.md", """# Boot and Initialization Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify the end-to-end boot sequence, initramfs design, systemd service dependency graph, graphical target transitions, and rollback triggers.

---

## 1. Boot Stages Sequence

```mermaid
stateDiagram-v2
    [*] --> UEFI_BIOS: Hardware Power-On
    UEFI_BIOS --> GRUB2: Load EFI Bootloader (/EFI/nebu/grubx64.efi)
    GRUB2 --> OstreeBLS: Select Bootloader Spec (Deployment A / B)
    OstreeBLS --> KernelInit: Load vmlinuz & initramfs
    KernelInit --> Dracut: Mount Read-Only Root (ostree sysroot)
    Dracut --> SystemdInit: Switch Root to /sysroot (PID 1)
    SystemdInit --> BaseTargets: multi-user.target (udev, Network, PipeWire)
    BaseTargets --> DisplayManager: graphical.target / nebu-greet
    DisplayManager --> UserSession: systemd --user (NebuCompositor)
    UserSession --> DesktopReady: NebuShell active, launcher indexed
```

## 2. Stage Breakdown & Responsibilities

### Stage 1: Firmware & Bootloader
- **Firmware:** UEFI 64-bit (Legacy CSM supported where present, but not validated).
- **Bootloader:** GRUB2 with Boot Loader Specification (BLS) integration.
- **A/B Deployment Choice:** GRUB reads `/boot/loader/entries/` populated by `bootc` / `ostree`. Default deployment is index 0; prior deployment is index 1.
- **Rollback Hook:** If boot fails 3 consecutive times (`boot_counter > 3`), GRUB automatically falls back to index 1.

### Stage 2: Initramfs (Dracut)
- **Components:** Minimal dracut profile containing storage drivers (NVMe, AHCI), Btrfs filesystem driver, and OSTree sysroot pivot tools.
- **Tasks:**
  1. Initialize storage and unlock encrypted LUKS volumes (if configured).
  2. Locate root filesystem UUID and mount Btrfs `@` subvolume.
  3. Prepare OSTree deployment mount at `/sysroot`.
  4. Perform `switch_root` to `/sysroot`.

### Stage 3: Systemd Initialization (PID 1)
- **Core Units Active:**
  - `systemd-journald.service`: High-performance binary logging.
  - `systemd-udevd.service`: Accelerated device node creation.
  - `systemd-oomd.service`: Out-of-memory killer monitoring memory pressure.
  - `dbus-broker.service`: High-throughput, low-latency D-Bus message broker.
- **Target Reach:** `basic.target` -> `sysinit.target` -> `multi-user.target` -> `graphical.target`.

### Stage 4: Session Startup & Graphical Target
- **Display Manager:** Lightweight native greeter (`nebu-greet`) or auto-login service for single-user desktop configurations.
- **Compositor Startup:** Launch `nebu-compositor.service` within `systemd --user` session.
- **Shell Startup:** `nebu-shell.service` starts after `wayland-session.target` is reached.

## 3. Boot Failure Behavior & Automated Recovery

| Boot Stage | Failure Symptom | Detection Mechanism | Automated Recovery Action |
|---|---|---|---|
| Kernel / Initramfs | Kernel Panic / Mount Failure | Watchdog timer (60s hardware watchdog) | Reboot into prior OSTree image deployment. |
| Systemd Base | Hang before `multi-user.target` | `systemd-boot-check-no-failures` | Enter emergency rescue shell; log diagnostic dump. |
| GPU Driver Init | Black screen, DRM fail | `nebu-greet` exit status != 0 | Fallback to `simpledrm` / `llvmpipe` software rasterizer. |
| Compositor Crash | Immediate exit or crash loop | systemd restart throttle (5 restarts in 10s) | Display Fallback Diagnostic Dialog with rollback option. |

## 4. Boot Performance Budget

| Milestone | SATA SSD Target | NVMe Gen3/4 Target |
|---|---|---|
| UEFI to Kernel Hand-off | 2.5 s | 1.8 s |
| Kernel + Initramfs | 1.8 s | 1.0 s |
| Userspace systemd to Graphical Target | 2.2 s | 1.2 s |
| Compositor + Shell Render | 0.8 s | 0.4 s |
| **Total Boot to Interactive Desktop** | **< 7.3 s** | **< 4.4 s** |

## 5. Related Documents
- [01-system-architecture.md](01-system-architecture.md)
- [../updates/04-rollback.md](../updates/04-rollback.md)
- [../performance/03-boot.md](../performance/03-boot.md)
""")

# 03-process-and-ipc.md
write_file("03-process-and-ipc.md", """# Process and IPC Architecture Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define process isolation boundaries, privilege hierarchies, IPC protocols, and session communication contracts.

---

## 1. Process Hierarchy & Privilege Model

```mermaid
graph TD
    subgraph ROOT [Privileged Space - UID 0]
        PID1[systemd PID 1]
        UDEV[systemd-udevd]
        NET_D[NetworkManager]
        UPDATE_D[nebu-update-daemon]
    end

    subgraph USER [User Session - UID 1000]
        USER_INIT[systemd --user]
        COMP[nebu-compositor]
        SHELL[nebu-shell]
        RUNTIME[nebu-runtime-daemon]
        DBUS[dbus-broker]
        PIPEWIRE[PipeWire / WirePlumber]
    end

    subgraph SANDBOX [Application Sandboxes - Isolated Namespaces]
        LINUX_APP[Flatpak App Process]
        WIN_SERVER[wineserver]
        WIN_PE[Wine Process: acad.exe / winword.exe]
    end

    PID1 --> UDEV
    PID1 --> NET_D
    PID1 --> UPDATE_D
    PID1 --> USER_INIT

    USER_INIT --> DBUS
    USER_INIT --> COMP
    USER_INIT --> SHELL
    USER_INIT --> RUNTIME
    USER_INIT --> PIPEWIRE

    RUNTIME -.->|bwrap spawn| WIN_SERVER
    WIN_SERVER --> WIN_PE
    COMP -.->|Wayland Socket| WIN_PE
    COMP -.->|Wayland Socket| LINUX_APP
```

## 2. IPC Protocol Selection Rationale

1. **D-Bus (`dbus-broker`):**
   - *Use Case:* High-level system state changes, application launch requests, hardware notifications, and update orchestration.
   - *Rationale:* Standard Linux IPC mechanism. Reusing `dbus-broker` eliminates custom IPC bugs, provides strict polkit authorization, and exposes introspectable interfaces.
2. **Wayland UNIX Domain Sockets:**
   - *Use Case:* Surface buffer exchange, input events, window state negotiation between clients and `nebu-compositor`.
   - *Rationale:* Native display protocol standard with zero-copy `dmabuf` buffer sharing.
3. **Shared Memory (`memfd_create` + POSIX shm):**
   - *Use Case:* High-bandwidth telemetry, frame buffer passing, and crash state serialization between compositor and shell.

## 3. Core D-Bus Service Contracts

### Interface: `org.nebu.Runtime1`
- **Bus:** Session Bus (`dbus-broker`)
- **Object Path:** `/org/nebu/Runtime1`
- **Methods:**
  - `LaunchExecutable(String path, Array[String] args, Dict options) -> ObjectPath app_instance`
  - `IdentifyExecutable(String path) -> Struct(String app_id, String app_name, Int32 cert_status)`
  - `RepairPrefix(String app_id, Int32 repair_mode) -> Boolean success`
  - `TerminateApplication(String app_id) -> Boolean success`
- **Signals:**
  - `ApplicationStarted(String app_id, Int32 pid)`
  - `ApplicationTerminated(String app_id, Int32 exit_code)`
  - `ApplicationCrashed(String app_id, String error_report_path)`

### Interface: `org.nebu.Compositor1`
- **Bus:** Session Bus
- **Object Path:** `/org/nebu/Compositor1`
- **Methods:**
  - `GetWindowList() -> Array[Struct(UInt32 window_id, String title, String app_id, Rect geometry)]`
  - `ActivateWindow(UInt32 window_id) -> Void`
  - `SetWindowGeometry(UInt32 window_id, Rect geometry) -> Void`
  - `SetWorkspace(UInt32 workspace_index) -> Void`
- **Signals:**
  - `WindowCreated(UInt32 window_id, String app_id)`
  - `WindowDestroyed(UInt32 window_id)`
  - `ActiveWindowChanged(UInt32 window_id)`

## 4. Authentication & Authorization
- **Privileged Actions:** Admin actions (applying OS image, rollback, raw disk ops) require PolicyKit (`polkit`) authorization via `org.nebu.update.policy`.
- **Desktop Actions:** All desktop, runtime, and prefix management operations execute unprivileged as UID 1000 without requiring `sudo` or root privileges.

## 5. Related Documents
- [01-system-architecture.md](01-system-architecture.md)
- [05-security.md](05-security.md)
- [../runtime/02-windows-runtime.md](../runtime/02-windows-runtime.md)
""")

# 04-filesystem.md
write_file("04-filesystem.md", """# Filesystem Architecture Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define system mount topologies, Btrfs subvolume layout, immutable root partitions, user data isolation, and Windows prefix filesystem virtualization.

---

## 1. Storage Layout & Partition Scheme

```mermaid
graph TD
    subgraph DISK [Physical Storage: NVMe / SSD / HDD]
        P1[Partition 1: EFI System Partition - 512 MB - vfat]
        P2[Partition 2: Boot Partition - 1024 MB - ext4]
        P3[Partition 3: Nebu System & Data - Remainder - Btrfs]
    end

    subgraph BTRFS_SUBVOLS [Btrfs Subvolumes]
        ROOT_SUB["@ (OSTree Sysroot - Read-Only)"]
        VAR_SUB["@var (Persistent System State - Writable)"]
        HOME_SUB["@home (User Profiles & Documents - Writable)"]
        APPS_SUB["@nebu_apps (Prefix Storage - CoW Disabled)"]
    end

    P3 --> ROOT_SUB
    P3 --> VAR_SUB
    P3 --> HOME_SUB
    P3 --> APPS_SUB
```

## 2. Partition & Subvolume Table

| Partition / Subvolume | Mount Point | Filesystem | Mount Options | Purpose |
|---|---|---|---|---|
| Partition 1 | `/boot/efi` | vfat | `umask=0077,shortname=winnt` | UEFI bootloaders (`grubx64.efi`). |
| Partition 2 | `/boot` | ext4 | `defaults,ro` | Kernel images (`vmlinuz`) and initramfs. |
| Subvolume `@` | `/` | Btrfs | `compress=zstd:1,ro` | Root filesystem managed by OSTree / bootc. |
| Subvolume `@var` | `/var` | Btrfs | `compress=zstd:1,rw,noatime` | System logs, Flatpak runtimes, libvirt. |
| Subvolume `@home` | `/home` | Btrfs | `compress=zstd:1,rw,noatime` | User configuration and personal files. |
| Subvolume `@nebu_apps` | `/home/$USER/.nebu/apps` | Btrfs | `rw,noatime,nodatacow` | Isolated Wine prefixes and Windows filesystems. |

*Note on `nodatacow`:* Wine prefix databases, registry hives, and high-frequency Direct3D shader caches exhibit fragmentation under copy-on-write. Setting `nodatacow` on `@nebu_apps` prevents SQLite / registry fragmentation while retaining snapshot capabilities at the subvolume level.

## 3. Directory Layout Hierarchy

```text
/
├── usr/                  # Immutable OS binaries, libraries, drivers (Read-Only)
│   ├── lib/nebu/         # Bundled Wine & Proton runtimes
│   └── share/nebu/       # Default compatibility profiles & patches
├── etc/                  # Machine-specific configuration (Writable overlay)
├── var/                  # Variable state (Logs, cache, system DB)
│   └── lib/nebu/db/      # System-wide compatibility database (compat.db)
└── home/
    └── user/
        ├── .config/nebu/ # User shell & desktop preferences
        └── .nebu/
            ├── apps/     # Application prefixes (~/.nebu/apps/<app_id>/)
            │   └── autodesk.autocad.2024/
            │       ├── prefix.json
            │       ├── dosdevices/
            │       │   ├── c: -> ../drive_c
            │       │   └── z: -> /home/user/Documents (Controlled)
            │       ├── drive_c/
            │       │   ├── Program Files/
            │       │   ├── ProgramData/
            │       │   └── windows/
            │       └── snapshots/ # Point-in-time prefix snapshots
            └── cache/    # Vulkan pipeline cache & font cache
```

## 4. Windows `C:\` and `Z:\` Drive Virtualization
- **`C:\` Drive:** Sandboxed inside `~/.nebu/apps/<app-id>/drive_c`. Any attempt by the Windows application to access `C:\Windows\System32` routes strictly into its private prefix.
- **`Z:\` Drive (Host Passthrough):** By default, unrestricted access to the root filesystem (`Z:\ -> /`) is **prohibited**. `Z:\` is restricted to mapped directories:
  - `Z:\Documents` -> `/home/$USER/Documents`
  - `Z:\Downloads` -> `/home/$USER/Downloads`
  - Any full-system access must be explicitly authorized by the user via a graphical permission prompt.

## 5. Related Documents
- [01-system-architecture.md](01-system-architecture.md)
- [05-security.md](05-security.md)
- [../runtime/03-prefix-management.md](../runtime/03-prefix-management.md)
""")

# 05-security.md
write_file("05-security.md", """# Security Architecture Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define threat models, isolation boundaries, application sandboxing rules, cryptographic verification mechanisms, and credential protection.

---

## 1. Threat Model & Adversary Capabilities

| Threat Vector | Description | Attacker Objective | NebuOS Countermeasure |
|---|---|---|---|
| Malicious Windows Binary | User downloads untrusted `.exe` infected with ransomware or spyware. | Encrypt `/home/$USER`, exfiltrate SSH keys, inject rootkits. | Bubblewrap sandbox: no access to `~/.ssh`, `~/.gnupg`, or other prefixes. `C:\` is disposable. |
| Compromised Patch / Profile | Attacker supplies malicious patch recipe in community profile store. | Execute arbitrary shell commands during prefix initialization. | Patches are strictly declarative (JSON/Diff); no executable scripts allowed. Cryptographic GPG signing. |
| OS Update Tampering | Man-in-the-middle attack or compromised mirror during OS update. | Inject kernel backdoor or modify system services. | OSTree container images are signed with Sigstore / cosign and verified against embedded public keys. |
| Wine Escape Vulnerability | Exploit in Wine's NT syscall emulation or GDI parser. | Escape Wine process to gain standard Linux shell execution. | Seccomp BPF syscall filtering blocks `ptrace`, `kexec`, `bpf`, and namespace creation within prefix. |

## 2. Sandboxing Architecture (`nebu-sandbox`)

Every Windows application process spawned by `nebu-runtime` runs inside an ephemeral Bubblewrap (`bwrap`) container.

```mermaid
graph TD
    subgraph HOST [Host Linux Environment]
        SEC_FILES["Sensitive Files (~/.ssh, ~/.bashrc, ~/.gnupg)"]
        DOCS["Allowed Files (~/Documents, ~/Downloads)"]
        PULSE["PipeWire Audio Socket"]
        WAYLAND["Wayland Display Socket"]
        DRI["GPU /dev/dri/renderD128"]
    end

    subgraph BWRAP [Bubblewrap Sandbox Boundary]
        subgraph PREFIX [Isolated Prefix Sandbox]
            DRIVE_C["Private drive_c"]
            WINE_PROC["Wine PE Process (AutoCAD / Office)"]
        end
    end

    SEC_FILES -.->|BLOCKED / HIDDEN| BWRAP
    DOCS -->|Read/Write Bind Mount| BWRAP
    PULSE -->|Socket Only| BWRAP
    WAYLAND -->|Filtered Wayland Proxy| BWRAP
    DRI -->|Direct Device Access| BWRAP
```

### Sandbox Launch Arguments Specification
When executing a Windows PE application, `nebu-runtime` constructs the following sandbox boundary:
```text
bwrap \
  --ro-bind /usr /usr \
  --ro-bind /lib64 /lib64 \
  --ro-bind /etc/resolv.conf /etc/resolv.conf \
  --ro-bind /etc/fonts /etc/fonts \
  --proc /proc \
  --dev /dev \
  --dev-bind /dev/dri /dev/dri \
  --bind ~/.nebu/apps/<app_id>/drive_c ~/.nebu/apps/<app_id>/drive_c \
  --bind ~/.nebu/apps/<app_id>/dosdevices ~/.nebu/apps/<app_id>/dosdevices \
  --bind ~/Documents ~/.nebu/apps/<app_id>/drive_c/users/nebu/Documents \
  --ro-bind-try $XDG_RUNTIME_DIR/wayland-0 $XDG_RUNTIME_DIR/wayland-0 \
  --ro-bind-try $XDG_RUNTIME_DIR/pipewire-0 $XDG_RUNTIME_DIR/pipewire-0 \
  --unshare-all \
  --share-net \
  --die-with-parent \
  wine64 <app_binary.exe>
```

## 3. Privilege Escalation Mitigation
1. **No Setuid Binaries in Prefix:** Prefix directories are mounted with `nosuid,nodev`.
2. **SELinux in Enforcing Mode:** Base Fedora Atomic image runs targeted SELinux policies, preventing userland processes from altering systemd units or kernel tunables.
3. **Hardware Isolation:** Windows applications communicate with the GPU exclusively via unprivileged DRM render nodes (`/dev/dri/renderD128`). Master nodes (`/dev/dri/cardX`) are reserved for `nebu-compositor`.

## 4. Related Documents
- [01-system-architecture.md](01-system-architecture.md)
- [04-filesystem.md](04-filesystem.md)
- [../runtime/02-windows-runtime.md](../runtime/02-windows-runtime.md)
""")

# 06-hardware.md
write_file("06-hardware.md", """# Hardware Architecture Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Establish hardware compatibility tiers, minimum specifications, driver matrix, power management profiles, and hybrid GPU configurations.

---

## 1. Hardware Target Tiers

| Parameter | Tier 1: Minimum (Lite) | Tier 2: Recommended | Tier 3: Professional / Workstation |
|---|---|---|---|
| **CPU Target** | 2 cores / 4 threads, x86_64 (Intel Core 4th Gen / AMD FX) | 4 cores / 8 threads (Intel 8th Gen+ / AMD Ryzen 2000+) | 8+ cores / 16+ threads (Intel 12th Gen+ / AMD Ryzen 5000+) |
| **System Memory (RAM)**| 4 GB DDR3 / DDR4 | 8 GB - 16 GB DDR4 / DDR5 | 32 GB - 64 GB ECC / High-Speed DDR5 |
| **Storage Subsystem** | 64 GB SATA SSD | 256 GB NVMe PCIe 3.0 SSD | 1 TB+ NVMe PCIe 4.0 / 5.0 SSD |
| **GPU Subsystem** | Intel HD Graphics 4400+ / AMD Radeon GCN 1+ | AMD Radeon RX 5000+ / NVIDIA GTX 1660+ / Intel Arc | Dedicated NVIDIA RTX 4000+ / AMD Radeon Pro / RX 7800+ |
| **Display Support** | 1x 1080p @ 60 Hz | 2x 1440p @ 60/144 Hz (Mixed DPI) | 3+ Displays / 4K UltraHD / HDR / Variable Refresh Rate |

## 2. GPU & Driver Matrix

```mermaid
graph TD
    subgraph GPU_DETECTION [Hardware Enumeration at Boot]
        PCI[PCI Device Scan: 0x030000 VGA / 0x030200 3D]
    end

    subgraph DRIVER_SELECTION [Kernel & Userspace Driver Selection]
        INTEL[Intel: xe / i915 kernel driver -> Mesa iris / ANV Vulkan]
        AMD[AMD: amdgpu kernel driver -> Mesa radeonsi / RADV Vulkan]
        NVIDIA_PROPR[NVIDIA Modern: nvidia.ko -> Proprietary Vulkan / NVK Mesa]
        NVIDIA_LEGACY[NVIDIA Legacy: nouveau -> Mesa NVK / Software LLVMpipe]
    end

    PCI -->|Vendor 0x8086| INTEL
    PCI -->|Vendor 0x1002| AMD
    PCI -->|Vendor 0x10de Turing+| NVIDIA_PROPR
    PCI -->|Vendor 0x10de Kepler/Maxwell| NVIDIA_LEGACY
```

## 3. Hybrid GPU (iGPU + dGPU) Management
On laptops equipped with hybrid graphics (e.g., Intel Iris Xe iGPU + NVIDIA RTX dGPU):
- **Desktop & General Apps:** `NebuCompositor`, `NebuShell`, browser, and Microsoft Office execute on the energy-efficient iGPU.
- **CAD & High-Performance Games:** NebuRuntime automatically sets environment variables for discrete GPU offloading based on the application compatibility profile:
  - *AMD dGPU:* `DRI_PRIME=1`
  - *NVIDIA dGPU:* `__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia __VK_LAYER_NV_optimus=NVIDIA_only`

## 4. Power Management & Laptop Optimization
- **Idle Power Optimization:** Suspend idle polling; enable PCIe Active State Power Management (ASPM); enable SATA ALPM (`med_power_with_dipm`).
- **Thermal & Sleep States:** Full support for ACPI S3 (Deep Sleep) and Modern Standby (s2idle). Audio/GPU runtimes cleanly re-initialize upon resume without restarting Wine processes.

## 5. Related Documents
- [01-system-architecture.md](01-system-architecture.md)
- [../graphics/01-gpu-detection.md](../graphics/01-gpu-detection.md)
- [../performance/01-memory.md](../performance/01-memory.md)
""")

print("Architecture documentation generated successfully.")
