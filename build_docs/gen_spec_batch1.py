#!/usr/bin/env python3
"""
Generator for Batch 1:
- runtime/06-proton-integration.md
- desktop/00-desktop-specification.md
- desktop/01-nebucompositor-specification.md
- desktop/02-nebushell-specification.md
- desktop/05-window-management.md
- desktop/06-input-display.md
"""

import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {path} ({len(content.splitlines())} lines)")

# 1. runtime/06-proton-integration.md
p1 = r"""# Proton Integration Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Define the architectural integration, runtime selection, prefix configuration, gaming runtime environment, and container execution model for Valve Proton within NebuOS.

---

## 1. Status
DRAFT — Architectural specification awaiting lab validation against Valve Proton 8.0/9.0 and Proton-GE release builds.

## 2. Purpose
NebuOS provides first-class support for Windows games without requiring a virtual machine or a complete Steam client installation. This specification defines how NebuOS integrates Proton as a specialized compatibility runtime alongside upstream Wine, orchestrating DXVK, VKD3D-Proton, Esync/Fsync, OpenVR stubs, and media foundation decoders.

## 3. Scope
- Packaging and version management of Proton runtimes in `/usr/lib/nebu/runtimes/proton/`.
- Detection of gaming vs. productivity executables and automatic runtime routing.
- Environment variables and prefix specialization for Proton prefixes.
- Integration of `proton-ge-custom` and official Valve Proton releases.
- Audio and gamepad mapping (PipeWire, evdev, SDL2 gamepad database).
- Fsync (`futex_waitv`) kernel interface utilization.

## 4. Non-goals
- Recompiling or maintaining an out-of-tree Proton fork.
- Emulating the Steam store, Steam Cloud, or proprietary Steamworks DRM.
- Bypassing kernel-level anti-cheat systems (Vanguard, Easy Anti-Cheat kernel mode).
- Bundling copyrighted Windows system DLLs or proprietary video codecs.

## 5. Requirements
1. **R-PRT-01:** Support automated deployment of Proton releases into isolated read-only runtime directories.
2. **R-PRT-02:** Provision gaming prefixes at `~/.nebu/apps/<app_id>/` with Proton-specific directory structures and registry layouts.
3. **R-PRT-03:** Enable Linux `fsync` (`futex_waitv`) by default on Linux kernel 6.6+; gracefully fall back to `esync` (eventfd) or standard Wine server IPC.
4. **R-PRT-04:** Enforce strict Bubblewrap sandboxing while granting direct access to `/dev/dri/renderD128` (Vulkan) and `/dev/input/` (gamepads).
5. **R-PRT-05:** Map Windows D3D9/10/11/12 API calls to Vulkan via DXVK and VKD3D-Proton bundles packaged with Proton.

## 6. Architecture
NebuOS treats Proton as an autonomous, self-contained runtime bundle containing its own customized Wine build, DXVK/VKD3D libraries, OpenAL audio, and GStreamer plugins.

```mermaid
graph TD
    subgraph Host[NebuOS Host Environment]
        LAUNCH[nebu-launch CLI / D-Bus] --> ROUTER[NebuRuntime Router]
        ROUTER -->|Type: Game| PROTON_SEL[Proton Version Selector]
        PROTON_SEL --> BWRAP[Bubblewrap Sandbox Engine]
        FSYNC_CHK[futex_waitv kernel probe] --> BWRAP
    end

    subgraph Sandbox[Bubblewrap Unprivileged Container]
        BWRAP --> PROTON_WRAP[proton wrapper script]
        PROTON_WRAP --> WINESVR[Proton wineserver]
        PROTON_WRAP --> WINE64[wine64-preloader]
        WINE64 --> APP_PE[Game Executable]
        APP_PE --> DXVK[DXVK / VKD3D-Proton]
        APP_PE --> WIN_MEDIA[GStreamer Media Foundation]
    end

    subgraph Hardware[Hardware Acceleration]
        DXVK --> VULKAN[Vulkan Loader & Mesa Drivers]
        VULKAN --> GPU_HW[AMD / Intel / NVIDIA GPU]
    end
```

## 7. Components
1. **Proton Runtime Store (`/usr/lib/nebu/runtimes/proton/`):** Immutable directories containing Proton releases (e.g. `proton-9.0-2`, `proton-ge-custom`).
2. **NebuRuntime Router:** Evaluates executable metadata, Compatibility Database tags, and user overrides to select between Wine and Proton.
3. **Fsync Manager:** Probes `/sys/kernel/debug/` or syscall availability for `__NR_futex_waitv` (syscall 449 on x86_64) and injects `PROTON_NO_FSYNC=0` or `1`.
4. **Gamepad Subsystem Bridge:** Ensures `/dev/input/js*` and `/dev/input/event*` devices are exposed inside the container with proper permissions.
5. **Media Foundation Bridge:** Configures Proton's bundled GStreamer plugins for in-game video playback (WMV, MP4, Bink).

## 8. Data Flow
1. User or application launcher initiates execution of a game executable `game.exe`.
2. `neburuntimed` inspects `compat.db` and identifies game classification (`is_game = 1`).
3. Profile specifies Proton target (e.g., `proton-9.0`).
4. Runtime copies/reflinks gaming prefix template from `/usr/share/nebu/prefix-template-proton/`.
5. Environment variables generated:
   ```bash
   STEAM_COMPAT_DATA_PATH="~/.nebu/apps/<app_id>"
   STEAM_COMPAT_CLIENT_INSTALL_PATH="/usr/lib/nebu/runtimes/proton/stubs"
   PROTON_USE_SECCOMP=1
   PROTON_ENABLE_NVAPI=1
   DXVK_ENABLE_NVAPI=1
   WINEFSYNC=1
   ```
6. Bubblewrap isolates the execution namespace, mounting only necessary host paths and DRM devices.
7. Game process spawns; graphics frames route through Vulkan directly to Wayland surfaces via DMA-BUF.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Shell as NebuShell
    participant Daemon as neburuntimed
    participant DB as compat.db
    participant Bwrap as Bubblewrap
    participant Proton as Proton Runtime

    User->>Shell: Launch game executable
    Shell->>Daemon: LaunchExecutable(path, flags)
    Daemon->>DB: QueryProfile(hash)
    DB-->>Daemon: Profile(runtime="proton-9.0", fsync=true)
    Daemon->>Daemon: PreparePrefix(app_id)
    Daemon->>Bwrap: Execute(bwrap_args, proton_run_cmd)
    Bwrap->>Proton: run game.exe
    Proton->>Proton: Start wineserver & init DXVK
    Proton-->>Shell: Wayland surface created
    Shell-->>User: Display Game Window
```

## 10. Interfaces
- **Filesystem Paths:**
  - Runtime Root: `/usr/lib/nebu/runtimes/proton/<version>/`
  - User Custom Runtimes: `~/.local/share/nebu/runtimes/proton/<version>/`
  - Per-App Prefix: `~/.nebu/apps/<app_id>/pfx/`
- **D-Bus Interface Integration:** Methods on `org.nebu.Runtime1` accept `runtime_override: "proton-latest"` in property maps.
- **Environment Invariants:** Standardizes `WINEPREFIX`, `WINEDEBUG=-all`, `DXVK_LOG_LEVEL=none`, `WINEFSYNC=1`.

## 11. Dependencies
- Upstream Valve Proton releases or Proton-GE binaries.
- Linux Kernel >= 6.6 with `CONFIG_FUTEX=y` and `CONFIG_FUTEX2=y`.
- Mesa Drivers >= 24.0 with Vulkan 1.3 support.
- Bubblewrap (`bwrap`) >= 0.8.0.
- PipeWire >= 1.0 for low-latency audio.

## 12. Security
- Proton binaries execute exclusively within unprivileged user namespaces (`bwrap`).
- Host network is disabled by default unless game profile explicitly specifies multiplayer networking (`network_allowed = true`).
- Access to root filesystems (`/etc`, `/usr`) is mounted strictly read-only (`--ro-bind`).
- Access to user personal files is strictly confined to `drive_c/users/nebu/` and whitelisted folders.
- Ptrace and dangerous syscalls are blocked via seccomp filters.

## 13. Resource Requirements
- **Disk Footprint:** ~1.8 GB per Proton runtime version in `/usr/lib/nebu/runtimes/`. Shared across all gaming prefixes.
- **Prefix Storage:** ~150 MB initial reflink footprint per gaming prefix on Btrfs.
- **RAM Overhead:** Proton wineserver: 18–35 MB RSS; game memory determined by target title.
- **CPU Scheduling:** `SCHED_OTHER` with `nice=-2` or `SCHED_BATCH` based on priority mode.

## 14. Failure Modes
1. **Fsync Kernel Incompatibility:** Kernel lacks `futex_waitv` support.
2. **Vulkan 1.3 Missing:** Host GPU driver lacks mandatory Vulkan extensions (e.g. dynamic state 3).
3. **Prefix Version Collision:** Prefix initialized with Proton 8 attempted to run under Proton 9 with conflicting registry structures.
4. **Media Foundation Missing Codec:** Video cutscenes hang on proprietary H.264/AAC streams.

## 15. Recovery Behavior
- When `fsync` fails initialization, runtime immediately logs warning and sets `WINEFSYNC=0 WINEESYNC=1` before retrying.
- In version collision, runtime takes an automated Btrfs snapshot (`snap-pre-upgrade`), runs `proton run wineboot -u`, and if failure occurs, restores the snapshot within 400ms.
- If Vulkan 1.3 is missing, runtime alerts user via notification that GPU acceleration requires Mesa 24+ and blocks launch gracefully instead of hard crashing.

## 16. Testing Requirements
- Test suite verifying `futex_waitv` detection on 6.6 LTS and 6.10+ kernels.
- Automated headless launch test using `dxvk-cube` and VKD3D test binaries.
- Gamepad input polling test using simulated evdev devices.
- Prefix reflink provisioning latency verification (< 250ms).

## 17. Performance Requirements
- Proton launch overhead from click to process execution: <= 600ms (warm cache).
- Game framerate overhead vs. native Windows: <= 7% on Vulkan/D3D11 workloads, <= 10% on D3D12 workloads.
- Input latency overhead added by Proton layer: <= 1.5ms.

## 18. Compatibility Considerations
- Certain legacy games require 32-bit Proton runtime components (`wine` 32-bit loader). NebuOS packages multiarch sysroot layers to support WoW64.
- Games demanding Steamworks DRM stubs must use mock DLLs (`steam_api.dll` stubs) to prevent instant exit.
- Games bundling invasive anti-cheat must be detected and rejected at launch with informative error dialogs.

## 19. Open Questions
- **OQ-PRT-01:** Should NebuOS bundle Proton-GE by default or strictly stick to Valve's official Proton releases for stability?
- **OQ-PRT-02:** What is the optimal automated prune policy for unused Proton runtime versions on storage-constrained devices?

## 20. Related Documents
- [00-runtime-specification.md](00-runtime-specification.md)
- [04-prefix-management.md](04-prefix-management.md)
- [05-wine-integration.md](05-wine-integration.md)
- [07-runtime-security.md](07-runtime-security.md)
- [../graphics/04-dxvk-vkd3d.md](../graphics/04-dxvk-vkd3d.md)
"""

write_file("/root/NebuOS/docs/runtime/06-proton-integration.md", p1)

# 2. desktop/00-desktop-specification.md
p2 = r"""# Desktop Subsystem Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Define the master architecture, process topology, Wayland protocol contracts, system services, and resource budgets for the NebuOS Desktop Environment.

---

## 1. Status
DRAFT — Master specification for the desktop subsystem, unifying NebuCompositor, NebuShell, theme engine, layout engine, and system UI components.

## 2. Purpose
The NebuOS Desktop Subsystem delivers a lightweight, modern, responsive Wayland user experience tailored for mixed Linux and Windows application execution. It coordinates surface rendering, frame presentation, input dispatch, dynamic layout switching, and system notifications without bloat, webviews, or multi-process Electron overhead.

## 3. Scope
- Master architecture and process boundaries of the desktop subsystem.
- Communication mechanisms between `nebu-compositor` and `nebu-shell`.
- Display server lifecycle and integration with `systemd --user` session targets.
- Coordinated resource limits (Compositor + Shell <= 120 MB combined idle RSS).
- Session startup, locking, idle management, and logout flows.

## 4. Non-goals
- X11 display server support as primary compositor (X11 supported solely via rootless Xwayland).
- Implementation of multiple desktop environments (GNOME, KDE, XFCE). NebuOS provides a single native Rust desktop.
- Web-based shell UI (no Electron, CEF, or Node.js).
- Heavy 3D window physics or resource-draining visual gimmicks.

## 5. Requirements
1. **R-DSK-01:** Provide native Wayland display management implemented in Rust using Smithay primitives.
2. **R-DSK-02:** Execute desktop shell as a separate unprivileged process using `wlr-layer-shell-unstable-v1`.
3. **R-DSK-03:** Maintain steady-state idle memory footprint of <= 35 MB RSS for Compositor and <= 45 MB RSS for Shell.
4. **R-DSK-04:** Support live switching between Nebu Default, Windows-like, and macOS-like desktop paradigms in <= 150ms without process restart (ADR-0009).
5. **R-DSK-05:** Present frames at native display refresh rates (60Hz–240Hz) with tearing-free atomic KMS commits and zero-copy direct scanout for fullscreen applications.

## 6. Architecture
The desktop subsystem consists of two core cooperating daemons and external FreeDesktop/systemd services:

```mermaid
graph TD
    subgraph DisplayServer[Display & Compositing Layer]
        COMP[nebu-compositor]
        KMS[Linux DRM/KMS Driver]
        LIBINPUT[libinput]
        XWAYLAND[Rootless Xwayland]
    end

    subgraph ShellLayer[Desktop Shell Layer]
        SHELL[nebu-shell]
        PANEL[Panel & Taskbar]
        DOCK[Floating Dock]
        LAUNCHER[App Launcher]
        SYSTEM_UI[Lock / OSD / Greeter]
    end

    subgraph SystemBridges[System Daemons]
        DBUS[D-Bus Session Bus]
        LOGIN[systemd-logind]
        PIPEWIRE[PipeWire Audio]
        RUNTIME_D[nebu-runtime-daemon]
    end

    LIBINPUT -->|Evdev events| COMP
    COMP -->|DRM atomic commit| KMS
    COMP <-->|Wayland / Layer Shell| SHELL
    COMP <-->|Wayland Socket| XWAYLAND
    SHELL --> PANEL
    SHELL --> DOCK
    SHELL --> LAUNCHER
    SHELL --> SYSTEM_UI
    SHELL <-->|org.nebu.Shell1| DBUS
    SHELL <-->|Volume / Media| PIPEWIRE
    SHELL <-->|Session Control| LOGIN
    LAUNCHER <-->|Launch Requests| RUNTIME_D
```

## 7. Components
1. **`nebu-compositor`:** Standalone Wayland compositor handling DRM/KMS output, input event routing, window stacking, and surface presentation.
2. **`nebu-shell`:** Unified desktop UI process containing the panel, launcher, notification center, quick settings, and dock.
3. **`nebu-greeter`:** Display manager login screen compliant with `greetd` protocol.
4. **Theme Subsystem:** Rust-native token engine styling UI elements with zero CSS overhead.
5. **Layout Subsystem:** Geometry solver dynamically placing panels, docks, and controls.

## 8. Data Flow
1. Hardware input event generated (keyboard/mouse/touch).
2. Kernel evdev subsystem forwards event to `libinput` inside `nebu-compositor`.
3. Compositor tests hit regions:
   - If event targets a shell layer surface (e.g. start button click), event routes to `nebu-shell` via `wl_pointer`/`wl_keyboard`.
   - If event targets a client surface (e.g. Wine application window), event routes to client Wayland socket.
4. Client updates internal buffer, attaches new DMA-BUF, and issues `wl_surface.commit`.
5. Compositor collects damage rects, schedules composite pass or direct scanout, and executes `drmModeAtomicCommit` at VSync.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant Session as systemd --user
    participant Comp as nebu-compositor
    participant Shell as nebu-shell
    participant Client as Application Window

    Session->>Comp: Start graphical-session.target
    Comp->>Comp: Init DRM/KMS, EGL, and libinput
    Comp->>Session: Notify READY=1 via sd_notify
    Session->>Shell: Start nebu-shell.service
    Shell->>Comp: Connect wayland-0
    Shell->>Comp: zwlr_layer_shell_v1.get_layer_surface (Panel/Dock)
    Comp-->>Shell: Surface configured & mapped
    Shell-->>Comp: Commit initial frame
    Client->>Comp: Map xdg_toplevel window
    Comp->>Shell: Window state changed (taskbar update)
    Shell->>Comp: Commit updated taskbar surface
```

## 10. Interfaces
- **Wayland Socket:** `$XDG_RUNTIME_DIR/wayland-0`
- **Session Control D-Bus:** `org.nebu.Shell1` (`SwitchParadigm`, `GetActiveParadigm`)
- **Compositor Query D-Bus:** `org.nebu.Compositor1` (`ListOutputs`, `GetWindowTree`)
- **System Notification Protocol:** `org.freedesktop.Notifications` v1.2

## 11. Dependencies
- `smithay` 0.3+ (Rust compositor building blocks).
- `libinput` >= 1.25.
- `libdrm` >= 2.4.120.
- `mesa` >= 24.0 (EGL, GBM, Wayland platform).
- Slint / Iced native Rust UI toolkits (no webview/Chromium).

## 12. Security
- Wayland security model enforces strict client isolation: clients cannot snoop keystrokes or capture screen content without explicit privileged portal APIs (`xdg-desktop-portal`).
- Compositor and shell execute under unprivileged user UID (1000).
- Session lock screen utilizes `ext-session-lock-v1` guaranteeing that untrusted clients cannot bypass authentication.
- IPC sockets permissioned `0700` inside user runtime directory.

## 13. Resource Requirements
- **Compositor Memory:** Budgeted <= 35 MB RSS on idle (with 1 display output).
- **Shell Memory:** Budgeted <= 45 MB RSS on idle.
- **CPU Idle:** Combined desktop CPU consumption < 0.3% on modern x86_64 cores.
- **GPU VRAM:** Framebuffers allocated based on screen resolution (e.g. double-buffered 4K: ~64 MB).

## 14. Failure Modes
1. **GPU Hang / Driver Reset:** DRM driver encounters kernel timeout and resets GPU context.
2. **Compositor Crash:** Fatal panic or assertion inside `nebu-compositor`.
3. **Shell Process Crash:** Unexpected termination of `nebu-shell`.
4. **Wayland Socket Exhaustion:** File descriptor leak in client connection handling.

## 15. Recovery Behavior
- When GPU resets, compositor catches `EGL_CONTEXT_LOST`, drops invalid GBM textures, rebuilds render pipelines, and prompts clients to re-commit surfaces without terminating session.
- If `nebu-shell` crashes, systemd user supervisor immediately restarts it (`Restart=always`, `RestartSec=200ms`). Layer-shell surfaces re-anchor seamlessly; client applications remain running.
- If `nebu-compositor` crashes, systemd restarts `graphical-session.target`.

## 16. Testing Requirements
- Headless compositor test harness verifying Wayland protocol compliance.
- Virtual input injection test verifying mouse hover, click, drag, and window focus transitions.
- Multi-monitor hotplug simulation (display connect/disconnect events).
- Paradigm switch latency benchmark (< 150ms ceiling).

## 17. Performance Requirements
- Input latency (mouse movement to screen scanout): <= 16ms at 60Hz, <= 6ms at 165Hz.
- Application launcher invocation latency: <= 80ms from Super key release to first rendered frame.
- Zero dropped frames during window moving, resizing, and panel animations.

## 18. Compatibility Considerations
- Legacy X11 applications and games run through rootless Xwayland with automatic clipboard synchronization (`wl_data_device` <-> X11 CLIPBOARD).
- Fractional scaling handled via `wp_fractional_scale_v1` to prevent blur in Win32 HiDPI applications.
- Windows non-client decorations (custom titlebars, borderless windows) mapped accurately to xdg-toplevel states.

## 19. Open Questions
- **OQ-DSK-01:** Should Xwayland run on-demand (socket activated) or continuously as a standard session daemon?
- **OQ-DSK-02:** What is the preferred mechanism for custom shader effects on low-end Intel Gen9 iGPUs?

## 20. Related Documents
- [01-nebucompositor-specification.md](01-nebucompositor-specification.md)
- [02-nebushell-specification.md](02-nebushell-specification.md)
- [03-ui-theme-system.md](03-ui-theme-system.md)
- [04-layout-system.md](04-layout-system.md)
- [05-window-management.md](05-window-management.md)
- [06-input-display.md](06-input-display.md)
- [07-system-ui.md](07-system-ui.md)
"""

write_file("/root/NebuOS/docs/desktop/00-desktop-specification.md", p2)

# 3. desktop/01-nebucompositor-specification.md
p3 = r"""# NebuCompositor Technical Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Provide the detailed engineering specification for `nebu-compositor`, the native Rust Wayland display server, render pipeline, and frame presentation scheduler.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P1.

## 2. Purpose
`nebu-compositor` is the core display server for NebuOS. Written in Rust using Smithay, it manages display hardware via DRM/KMS, receives input events via libinput, coordinates buffer exchange with client applications, and schedules atomic page flips with deterministic frame pacing and minimal latency.

## 3. Scope
- DRM/KMS device enumeration, atomic modesetting, and page-flip lifecycle.
- GBM (Generic Buffer Management) buffer allocation and EGL/GLES2 rendering backend.
- Wayland protocol extension implementations (`xdg_shell`, `wlr_layer_shell`, `linux_dmabuf_v1`, `wp_fractional_scale_v1`).
- Direct scanout engine for uncomposited fullscreen gaming and video.
- Window stacking, geometry calculation, damage tracking, and dirty-rect composite passes.

## 4. Non-goals
- Embedding shell widgets or UI controls inside the compositor process.
- Software rasterization fallback for primary desktop rendering (GPU acceleration required).
- Supporting legacy proprietary display drivers incompatible with standard DRM/KMS GBM.

## 5. Requirements
1. **R-CMP-01:** Implement 100% safe Rust architecture for core event dispatch and window management logic, isolating unsafe FFI to graphics and ioctl bindings.
2. **R-CMP-02:** Expose standard Wayland core and extension protocols with strict protocol adherence.
3. **R-CMP-03:** Provide zero-copy direct scanout for eligible fullscreen surfaces bypassing the compositing shader.
4. **R-CMP-04:** Enforce memory usage budget <= 35 MB RSS during steady-state single-monitor operation.
5. **R-CMP-05:** Implement explicit GPU synchronization (`linux-drm-syncobj-v1`) to prevent frame tearing and pipeline bubbles.

## 6. Architecture
`nebu-compositor` is architected as an event-driven state machine centered around the `smithay` event loop and DRM backend:

```mermaid
graph TD
    subgraph Drivers[Kernel & Hardware]
        KMS[DRM/KMS /dev/dri/cardX]
        EVDEV[Kernel evdev /dev/input/*]
    end

    subgraph CompositorCore[nebu-compositor Process]
        LOOP[Calloop Event Loop]
        INPUT_MOD[Input Manager: libinput backend]
        DRM_BACKEND[DRM/KMS Atomic Modesetting Backend]
        RENDERER[GLES2 / Glow Framebuffer Renderer]
        SPACE[Smithay Space: Window Stacking & Geometry]
        WAYLAND_SRV[Wayland Protocol Server]
    end

    subgraph Clients[Wayland Clients]
        SHELL[nebu-shell surfaces]
        WIN_APP[Wine / Proton Windows App]
        NATIVE_APP[Native Linux App]
    end

    EVDEV --> INPUT_MOD
    INPUT_MOD --> LOOP
    KMS <--> DRM_BACKEND
    LOOP --> DRM_BACKEND
    DRM_BACKEND --> RENDERER
    WAYLAND_SRV <--> Clients
    WAYLAND_SRV --> SPACE
    SPACE --> RENDERER
```

## 7. Components
1. **DRM Node Manager:** Discovers primary GPU (`/dev/dri/card0`), enumerates connectors (CRTCs, encoders, planes), and binds atomic modesetting states.
2. **Buffer Importer (`linux-dmabuf`):** Imports client DMA-BUF textures into GBM and EGL without CPU copies.
3. **Damage Tracker:** Aggregates surface dirty rectangles to restrict rendering strictly to damaged screen regions.
4. **Direct Scanout Arbiter:** Evaluates if a fullscreen window covers the entire CRTC; if pixel formats match, flips the client DMA-BUF directly to the hardware primary plane.
5. **Layer Shell Coordinator:** Maps and arranges `wlr-layer-shell` surfaces (panels, background wallpapers, docks, notifications) into dedicated visual tiers.

## 8. Data Flow
1. Client draws into a Vulkan/OpenGL framebuffer and issues `wl_surface.commit` with an attached DMA-BUF handle.
2. Compositor receives `commit` event via Wayland UNIX socket.
3. Damage tracker records bounding boxes of modified regions.
4. Render tick triggered by DRM `PAGE_FLIP_EVENT`:
   - If direct scanout applies: assigns client buffer directly to DRM plane property `FB_ID`.
   - If compositing required: binds screen framebuffer, sets scissor rect to damage union, renders background, windows, and overlays via GLES2 shaders.
5. Issues non-blocking `drmModeAtomicCommit` with presentation timeline syncobj.
6. Hardware scans out buffer at next VSync; compositor dispatches `wl_surface.frame` callbacks to clients.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant Client as Client Application
    participant Comp as nebu-compositor
    participant DRM as Linux DRM/KMS
    participant Screen as Physical Display

    Client->>Comp: wl_surface.commit(buffer, damage)
    Comp->>Comp: Validate buffer & queue damage
    DRM-->>Comp: Page Flip Event (VSync ready)
    Comp->>Comp: Evaluate Direct Scanout eligibility
    alt Direct Scanout Active
        Comp->>DRM: drmModeAtomicCommit(client_fb, flags=ATOMIC_NONBLOCK)
    else Composite Pass Required
        Comp->>Comp: Render damaged rects to GLES2 backbuffer
        Comp->>DRM: drmModeAtomicCommit(compositor_fb, flags=ATOMIC_NONBLOCK)
    end
    DRM->>Screen: Scan out pixels
    Comp->>Client: wl_surface.frame(timestamp)
```

## 10. Interfaces
- **Exported Wayland Protocols:**
  - `wl_compositor` (v6), `wl_subcompositor` (v1)
  - `wl_seat` (v8), `wl_output` (v4), `wl_shm` (v1)
  - `xdg_wm_base` (v4), `wlr-layer-shell-unstable-v1` (v4)
  - `linux_dmabuf_v1` (v4), `wp_fractional_scale_v1` (v1), `wp_viewporter` (v1)
  - `ext-session-lock-v1` (v1), `linux-drm-syncobj-v1` (v1)
- **Private IPC:**
  - Custom protocol `nebu_window_grouping_v1` for Windows multi-window taskbar grouping.
  - Session D-Bus `org.nebu.Compositor1`.

## 11. Dependencies
- `smithay` = "0.3"
- `calloop` = "0.13"
- `nix` = "0.28"
- `drm-rs` = "0.11"
- `gbm` = "0.15"

## 12. Security
- Complete isolation of client surfaces: applications cannot read pixels of other windows.
- Clipboard data transfer governed strictly by user interaction (paste events).
- Privileged protocols (`wlr-layer-shell`, `screencopy`) restricted to authorized binaries (`nebu-shell`, `nebu-screenshot`) via Unix domain socket UID/credential checks.
- Virtual input injection restricted to authorized tools.

## 13. Resource Requirements
- **Idle Memory:** <= 35 MB RSS.
- **Active Memory (4K desktop with 10 windows):** <= 65 MB RSS.
- **CPU Utilization:** < 0.2% CPU when desktop is idle; < 2% during continuous 60 FPS window dragging.
- **File Descriptors:** Capped at 1024 open descriptors.

## 14. Failure Modes
1. **DRM Atomic Commit Failure (`EINVAL` / `EBUSY`):** Invalid hardware plane configuration.
2. **GPU Driver Hang (`EIO` / `ENODEV`):** Driver reset during execution.
3. **Out of Memory during Buffer Allocation:** GBM buffer allocation fails.
4. **Wayland Client Protocol Violation:** Client sends malformed arguments.

## 15. Recovery Behavior
- When atomic commit returns `EINVAL` (unsupported multi-plane layout), direct scanout arbiter drops to safe single-plane composited mode immediately and retries.
- Client protocol violations trigger `wl_client_post_implementation_error`, terminating solely the offending client without destabilizing compositor.
- Under memory pressure, unused cached surface textures and scratch framebuffers are evicted immediately.

## 16. Testing Requirements
- Virtual KMS test runner executing in CI via `vkms` (Virtual Kernel Modesetting).
- Protocol conformance test suite asserting valid state transitions across all exposed Wayland interfaces.
- Direct scanout verification test verifying 0 shader draw calls when fullscreen video/game active.

## 17. Performance Requirements
- Frame scheduling precision: standard deviation of frame delivery time <= 0.5ms at 60Hz.
- Compositor internal latency (commit received to atomic commit ioctl dispatched): <= 2.5ms.
- Zero copy overhead for fullscreen DMA-BUF scanout.

## 18. Compatibility Considerations
- Wine applications requiring non-standard window border behavior are governed through xdg-toplevel rules.
- Legacy full-screen resolutions (e.g. 800x600, 1024x768) scaled seamlessly using `wp_viewporter` without altering physical monitor resolution.
- Xwayland rootless windows receive seamless window stacking and focus transitions.

## 19. Open Questions
- **OQ-CMP-01:** Should Variable Refresh Rate (VRR / Adaptive Sync) be enabled globally or toggled strictly per-window for detected gaming surfaces?
- **OQ-CMP-02:** What is the optimal threshold for switching from DRM double-buffering to triple-buffering during heavy GPU load?

## 20. Related Documents
- [00-desktop-specification.md](00-desktop-specification.md)
- [02-nebushell-specification.md](02-nebushell-specification.md)
- [05-window-management.md](05-window-management.md)
- [06-input-display.md](06-input-display.md)
- [../decisions/ADR-0005-nebu-compositor.md](../decisions/ADR-0005-nebu-compositor.md)
"""

write_file("/root/NebuOS/docs/desktop/01-nebucompositor-specification.md", p3)

# 4. desktop/02-nebushell-specification.md
p4 = r"""# NebuShell Technical Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Provide the detailed engineering specification for `nebu-shell`, the unified native Rust desktop shell implementing configurable themes, layouts, panels, and system widgets.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P2.

## 2. Purpose
`nebu-shell` is the sole user-facing desktop shell process for NebuOS. In accordance with ADR-0009, NebuShell avoids maintaining fragmented, separate shell binaries. Instead, it provides a single, high-performance Rust process equipped with a declarative theme and layout engine capable of rendering Nebu-default, Windows-like, and macOS-like paradigms live at runtime.

## 3. Scope
- Unified shell process architecture and sub-module topology.
- Taskbar/panel surface rendering and layer-shell integration.
- Application launcher with in-memory indexed search.
- Quick settings modal, system tray (StatusNotifierItem), and OSD overlays.
- Dynamic layout reconfiguration without process restart or user logout.
- Memory budget enforcement (<= 45 MB idle RSS).

## 4. Non-goals
- Multi-process shell architectures where every widget runs as a separate binary.
- Web-based frontends (Electron, React, HTML/CSS).
- Arbitrary untrusted JavaScript plugin ecosystems.
- Window compositor responsibilities (rendering done via Wayland client surfaces).

## 5. Requirements
1. **R-SHL-01:** Implement NebuShell as a single native Rust binary utilizing Slint or Iced GUI framework.
2. **R-SHL-02:** Anchor all UI surfaces via `wlr-layer-shell-unstable-v1` into designated Wayland layers (`Bottom`, `Top`, `Overlay`).
3. **R-SHL-03:** Support instant paradigm switching (Nebu, Windows-like, macOS-like) in <= 150ms over D-Bus without killing running applications.
4. **R-SHL-04:** Ensure application launcher response time is <= 80ms from Super key press to visible UI.
5. **R-SHL-05:** Implement StatusNotifierWatcher and StatusNotifierItem (SNI) specifications for background application tray icons.

## 6. Architecture
NebuShell is structured into decoupled functional crates within the NebuOS workspace:

```mermaid
graph TD
    subgraph NebuShellProcess[nebu-shell Binary]
        CORE[nebu-shell-core: Event Loop & State Hub]
        LAYOUT_ENG[nebu-shell-layout: Geometry & Layer Solver]
        THEME_ENG[nebu-shell-theme: Token Engine & Palette]
        PANEL_WIDGET[Panel / Taskbar Surface]
        DOCK_WIDGET[Floating Dock Surface]
        LAUNCHER_WIDGET[Launcher Surface]
        SETTINGS_WIDGET[Quick Settings Surface]
        TRAY_MGR[SNI Tray Manager]
    end

    subgraph ExternalInterfaces[Compositor & Session]
        COMP[nebu-compositor via Wayland]
        DBUS[D-Bus Session Bus]
        LOGIND[systemd-logind]
        RUNTIME[nebu-runtime-daemon]
    end

    CORE --> LAYOUT_ENG
    CORE --> THEME_ENG
    CORE --> PANEL_WIDGET
    CORE --> DOCK_WIDGET
    CORE --> LAUNCHER_WIDGET
    CORE --> SETTINGS_WIDGET
    CORE --> TRAY_MGR

    LAYOUT_ENG <-->|wlr_layer_shell| COMP
    TRAY_MGR <-->|StatusNotifierWatcher| DBUS
    LAUNCHER_WIDGET <-->|org.nebu.Runtime1| RUNTIME
    SETTINGS_WIDGET <-->|Session power / locks| LOGIND
```

## 7. Components
1. **Shell State Hub:** Centralized reactive state store managing running windows, active layout, theme tokens, and network/audio status.
2. **Layout Solver:** Computes monitor boundaries, calculates exclusive zones, anchors layer surfaces, and dynamically reconfigures anchors during paradigm switches.
3. **Taskbar & Window Switcher:** Displays active windows with live running indicators, thumbnails, and multi-window grouping for Wine/Linux apps.
4. **Fast Launcher:** Queries in-memory SQLite application index with fuzzy search matching (sub-millisecond query latency).
5. **System Tray Host:** Implements `org.kde.StatusNotifierWatcher` providing native tray icon hosting for Wine background apps and Linux utilities.

## 8. Data Flow
1. Window mapped or state changed in `nebu-compositor`.
2. Compositor broadcasts window event over Wayland protocol extension.
3. `nebu-shell` receives event; State Hub updates window list.
4. Taskbar widget invalidates local rect and triggers minimal repaint.
5. Slint/Iced renderer draws updated panel UI to DMA-BUF and issues `wl_surface.commit`.
6. Total time from compositor event to committed shell frame: < 8ms.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Shell as nebu-shell
    participant Layout as Layout Engine
    participant Comp as nebu-compositor
    participant DB as compat.db

    User->>Shell: D-Bus call: SwitchParadigm("macos-like")
    Shell->>Layout: ApplyParadigm(MacOS)
    Layout->>Layout: Calculate new geometries (Top Bar: 32px, Bottom Dock: 52px)
    Layout->>Comp: zwlr_layer_surface_v1.set_anchor(Top) for Bar
    Layout->>Comp: zwlr_layer_surface_v1.set_anchor(Bottom) for Dock
    Layout->>Comp: zwlr_layer_surface_v1.set_exclusive_zone(32)
    Comp-->>Layout: configure(serial)
    Layout->>Layout: Rearrange widgets (App Menu to Top, Icons to Dock)
    Shell-->>Comp: Commit updated layer surfaces
    Comp-->>User: Screen updates instantly (< 150ms)
```

## 10. Interfaces
- **D-Bus Session Interface:** `org.nebu.Shell1`
  - Methods: `SwitchParadigm(String name)`, `GetActiveParadigm() -> String`, `ListAvailableParadigms() -> Array<String>`, `ToggleLauncher()`, `ToggleQuickSettings()`.
- **System Tray Protocol:** `org.kde.StatusNotifierWatcher` / `org.kde.StatusNotifierItem`.
- **Layer Shell Wayland Protocol:** `zwlr_layer_shell_v1` surfaces.

## 11. Dependencies
- Native Rust GUI toolkit (`slint` or `iced`).
- `wayland-client` = "0.31".
- `zbus` = "4.0" (asynchronous D-Bus).
- `rusqlite` = "0.31" (read-only in-memory search index).

## 12. Security
- Executes exclusively as unprivileged user session process (UID 1000).
- Password inputs (lock screen / authentication prompts) wrapped in memory-safe `zeroize::Zeroizing` buffers.
- D-Bus methods restricted to session owner.
- Shell does not execute arbitrary shell scripts; all application launches routed through `nebu-runtime-daemon` validation.

## 13. Resource Requirements
- **Idle Memory:** <= 45 MB RSS.
- **Peak Search Memory:** <= 70 MB RSS.
- **CPU Idle:** 0.0% CPU when no animations active; event-driven rendering only.
- **Binary Footprint:** Stripped executable <= 18 MB on disk.

## 14. Failure Modes
1. **D-Bus Daemon Disconnection:** Session bus restarts or drops socket.
2. **Layer Shell Surface Collision:** Exclusive zone conflicts with display edge.
3. **Tray App Malformed Icon:** Background application provides invalid PNG/ARGB data.
4. **Rapid Paradigm Toggling:** User triggers repeated paradigm changes within milliseconds.

## 15. Recovery Behavior
- In D-Bus disconnection, `nebu-shell` maintains local rendering and enters a reconnection loop with exponential backoff (100ms to 2s).
- Malformed SNI icons are caught by parser and replaced with standard fallback asset without crashing tray thread.
- Paradigm switch requests are debounced by 200ms in the event loop, preventing race conditions or layout instability.

## 16. Testing Requirements
- Unit tests for layout constraint solver verifying all display aspect ratios (16:9, 16:10, 21:9, 32:9).
- Integration test benchmarking launcher search query latency with 5,000 indexed application entries.
- Automated paradigm switch stress test verifying 100 consecutive switches without memory leaks or UI artifacts.

## 17. Performance Requirements
- Cold start launch to visible panel: <= 200ms.
- Launcher search keystroke to filtered results render: <= 12ms.
- Paradigm switch execution: <= 150ms.
- Frame delivery during dock magnification / panel animation: locked 60/120 FPS.

## 18. Compatibility Considerations
- Windows applications minimizing to system tray map directly to SNI icons with right-click context menu forwarding.
- Start menu search integrates Wine application shortcuts (`.desktop` files) transparently alongside native Linux tools.
- Multi-monitor environments allow panel replication or primary-monitor-only configurations.

## 19. Open Questions
- **OQ-SHL-01:** Should application launcher include integrated web search suggestions or remain strictly local-only? (PRD leans local-only for privacy and speed).
- **OQ-SHL-02:** Should panel widgets support user drag-and-drop rearrangement in P2 or be deferred to P4?

## 20. Related Documents
- [00-desktop-specification.md](00-desktop-specification.md)
- [01-nebucompositor-specification.md](01-nebucompositor-specification.md)
- [03-ui-theme-system.md](03-ui-theme-system.md)
- [04-layout-system.md](04-layout-system.md)
- [07-system-ui.md](07-system-ui.md)
- [../decisions/ADR-0009-nebushell-ui-architecture.md](../decisions/ADR-0009-nebushell-ui-architecture.md)
"""

write_file("/root/NebuOS/docs/desktop/02-nebushell-specification.md", p4)

# 5. desktop/05-window-management.md
p5 = r"""# Window Management Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the window lifecycle, stacking order, tiling and floating policies, window decoration models, and snapping mechanisms in NebuOS.

---

## 1. Status
DRAFT — Technical specification for window management behaviors within `nebu-compositor` and `nebu-shell`.

## 2. Purpose
This document defines how windows are managed in NebuOS. It bridges the behavior of native Wayland Linux clients and sandboxed Windows PE applications running under Wine/Proton, providing consistent decorations, predictable window state transitions, intuitive keyboard shortcuts, and responsive snapping.

## 3. Scope
- Window states: Minimized, Maximized, Fullscreen, Tiled, Floating.
- Server-Side Decorations (SSD) vs. Client-Side Decorations (CSD) policy.
- Multi-window application grouping and taskbar synchronization.
- Edge snapping, split-screen tiling, and virtual workspace transitions.
- Multi-monitor window movement and focus policies.

## 4. Non-goals
- Full manual tiling window manager mechanics (e.g. i3/sway complex tree manipulation).
- Multi-user multi-seat desktop multiplexing.
- 3D spatial window flipping or desktop cube effects.

## 5. Requirements
1. **R-WIN-01:** Provide Server-Side Decorations (SSD) for all applications that do not explicitly negotiate CSD, ensuring uniform titlebars for Win32 apps.
2. **R-WIN-02:** Support dynamic edge snapping: dragging window to top edge maximizes; dragging to left/right halves splits 50/50.
3. **R-WIN-03:** Maintain strict window stacking order: Fullscreen (topmost) > Modal Dialogs > Normal Floating > Tiled > Desktop Background.
4. **R-WIN-04:** Synchronize window controls ordering (Close/Min/Max) with the active desktop layout paradigm (right-side for Nebu/Windows, left-side for macOS).
5. **R-WIN-05:** Track transient parent-child relationships for Windows modal dialogs, preventing parent interaction while modal is active.

## 6. Architecture
Window management logic is embedded within `nebu-compositor`'s space management module and synchronized with `nebu-shell`:

```mermaid
graph TD
    subgraph ClientWindow[Application Window Surface]
        XDG_TOPLEVEL[xdg_toplevel / xwayland_surface]
        SURFACE_COMMIT[Surface Commit: Buffers & Damage]
    end

    subgraph WindowManager[nebu-compositor Window Manager]
        STACK[Window Stacking Tree]
        GEOM[Geometry & Layout Solver]
        DECORATOR[SSD Titlebar Renderer]
        SNAPPING[Edge & Corner Snapping Engine]
    end

    subgraph ShellSync[nebu-shell Taskbar]
        TASKBAR[Taskbar Window List]
        GROUPING[Multi-Window Grouping Manager]
    end

    XDG_TOPLEVEL --> STACK
    SURFACE_COMMIT --> GEOM
    GEOM --> DECORATOR
    GEOM --> SNAPPING
    STACK <-->|nebu_window_grouping_v1| GROUPING
    GROUPING --> TASKBAR
```

## 7. Components
1. **Stacking Manager:** Maintains the Z-order hierarchy of mapped windows.
2. **Decoration Engine:** Renders native titlebars, window titles, close/minimize/maximize buttons, and drop shadows for SSD clients.
3. **Snapping Controller:** Detects cursor proximity to display edges during interactive drag moves (threshold: 16px) and displays visual snap preview overlays.
4. **Focus Arbiter:** Implements click-to-focus policy with automatic elevation of clicked windows to the top of their stacking layer.
5. **Workspace Manager:** Organizes windows across virtual workspaces with smooth slide transitions.

## 8. Data Flow
1. User clicks and drags window titlebar.
2. Compositor initiates interactive move grab.
3. As cursor approaches screen boundary, Snapping Controller computes half-tile geometry.
4. Compositor renders translucent snap preview rectangle on overlay layer.
5. User releases mouse button:
   - If released near edge: window state transitions to Tiled (Left/Right) and size updates via `xdg_toplevel.configure`.
   - If released in free space: window remains Floating at new coordinates.
6. Compositor informs shell of updated window position; shell taskbar updates active monitor indicator.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Comp as nebu-compositor
    participant Client as Application
    participant Shell as nebu-shell

    User->>Comp: Click Maximize button (or drag to top)
    Comp->>Comp: Calculate maximized geometry (Monitor rect minus Panel exclusive zone)
    Comp->>Client: xdg_toplevel.configure(width, height, states=[MAXIMIZED])
    Client->>Client: Re-render internal layout to new size
    Client->>Comp: wl_surface.attach(new_buffer) + commit
    Comp->>Comp: Update window state to MAXIMIZED (hide shadows, disable rounded corners)
    Comp->>Shell: Broadcast window_state_changed(app_id, MAXIMIZED)
    Shell->>Shell: Highlight taskbar item as maximized
```

## 10. Interfaces
- **Wayland Extensions:**
  - `xdg-shell` (`xdg_wm_base`, `xdg_toplevel`, `xdg_popup`)
  - `zxdg_decoration_manager_v1` (negotiates SSD vs CSD)
  - `nebu_window_grouping_v1` (custom protocol syncing multi-window Win32 process groups to taskbar)
- **Keybindings:**
  - `Super + Up`: Maximize window
  - `Super + Down`: Restore / Minimize window
  - `Super + Left / Right`: Tile window to left / right half
  - `Alt + Tab`: Fast window switcher popup

## 11. Dependencies
- `smithay` space and desktop abstractions.
- `tiny-skia` or GLES2 for rendering crisp window decorations and vector button glyphs.

## 12. Security
- Windows cannot disguise themselves as system UI panels (layer shell reserved for authenticated shell).
- Sandboxed Windows applications cannot capture global keybindings (`Super`, `Alt+Tab` intercepted by compositor).
- Modal dialogs cannot escape their application sandbox boundary.

## 13. Resource Requirements
- Window management state memory: <= 50 KB per active window.
- Decoration rendering: Cached textures shared across identical window button states; < 2 MB VRAM total.
- Snapping computation: < 0.1ms per pointer motion event.

## 14. Failure Modes
1. **Client Refuses Resize:** Win32 application with fixed-size dialog ignores resize configure events.
2. **Modal Lockout:** Modal window hidden behind unmapped parent.
3. **Infinite Resize Loop:** Application resizes recursively based on decoration size.

## 15. Recovery Behavior
- Fixed-size windows are identified via `min_size == max_size` hints; maximize button is disabled and tile snapping ignored.
- Modals without parent mappings are promoted to normal floating windows.
- Resize loops are broken by rate-limiting configure events to display refresh rate (VSync throttle).

## 16. Testing Requirements
- Unit tests for edge snapping geometry calculation.
- Automated tests verifying Alt+Tab cycling order across multiple workspaces.
- Multi-window Wine process grouping verification test.

## 17. Performance Requirements
- Interactive window dragging: 100% VSync locked (zero stutter or lag).
- Resize configure dispatch: <= 2ms.
- Alt+Tab switcher activation latency: <= 16ms.

## 18. Compatibility Considerations
- Win32 tool windows and floating toolbars mapped to `xdg_popup` or child toplevels without taskbar clutter.
- Wine borderless fullscreen windows granted direct scanout with zero decoration overhead.

## 19. Open Questions
- **OQ-WIN-01:** Should NebuOS support quarter-screen corner snapping (top-left, top-right, etc.) in Phase P2 or P3?
- **OQ-WIN-02:** What is the optimal policy for handling multi-window Win32 MDI (Multiple Document Interface) applications?

## 20. Related Documents
- [00-desktop-specification.md](00-desktop-specification.md)
- [01-nebucompositor-specification.md](01-nebucompositor-specification.md)
- [02-nebushell-specification.md](02-nebushell-specification.md)
- [04-layout-system.md](04-layout-system.md)
"""

write_file("/root/NebuOS/docs/desktop/05-window-management.md", p5)

# 6. desktop/06-input-display.md
p6 = r"""# Input and Display Management Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify input device handling (keyboard, pointer, touch, gamepad) and display output management (EDID, modesetting, HiDPI, multi-monitor) in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P1 and P2 display and input subsystems.

## 2. Purpose
This specification governs how hardware displays and user input devices are detected, configured, synchronized, and managed across the display server stack, ensuring precise pointer tracking, crisp fractional scaling, multi-monitor ergonomics, and zero input latency.

## 3. Scope
- DRM/KMS connector management, CRTC allocation, and display hotplugging.
- EDID parsing, mode enumeration, refresh rate selection, and HiDPI scale calculation.
- Fractional scaling protocol (`wp_fractional_scale_v1`) and viewporter integration.
- `libinput` event processing for keyboards, mice, trackpads, and touchscreens.
- Keymap configuration (XKB), repeat rates, acceleration profiles, and gamepad routing.

## 4. Non-goals
- Supporting legacy analog VGA outputs with software bitbanging.
- Complex color-calibration ICC profiling in early phases (deferred to P7).
- Custom proprietary input driver stacks outside standard Linux kernel evdev.

## 5. Requirements
1. **R-IND-01:** Automatically detect display hotplug events via DRM uevents and configure optimal native resolution and refresh rate within 500ms.
2. **R-IND-02:** Support crisp fractional scaling (125%, 150%, 175%, 200%) using `wp_fractional_scale_v1` without blurry nearest-neighbor interpolation.
3. **R-IND-03:** Provide standard libinput pointer acceleration profiles (flat, adaptive) and natural scrolling toggles.
4. **R-IND-04:** Support multi-monitor desktop topologies with arbitrary horizontal, vertical, and mixed-DPI layouts.
5. **R-IND-05:** Map standard multimedia keys (volume, brightness, mute, media playback) directly to desktop shell actions.

## 6. Architecture
Input and display management operate inside `nebu-compositor` via dedicated subsystems:

```mermaid
graph TD
    subgraph HardwareDevices[Physical Hardware]
        MONITORS[Display Monitors via DP / HDMI / eDP]
        INPUTS[Keyboards, Mice, Touchpads via USB / I2C]
    end

    subgraph KernelInterfaces[Linux Kernel]
        DRM_KMS[DRM/KMS Subsystem /dev/dri/card0]
        EVDEV_DEV[evdev Subsystem /dev/input/event*]
        UDEV[systemd-udevd]
    end

    subgraph CompositorInputDisplay[nebu-compositor Engine]
        OUTPUT_MGR[Display Output Manager: DRM Mode & CRTC]
        INPUT_MGR[Input Dispatcher: libinput & XKB]
        SCALE_ENG[Fractional Scaling Engine]
        EVENT_ROUTER[Event Router to Wayland Clients]
    end

    MONITORS --> DRM_KMS
    INPUTS --> EVDEV_DEV
    UDEV -->|Hotplug uevents| OUTPUT_MGR
    UDEV -->|Device uevents| INPUT_MGR
    DRM_KMS <--> OUTPUT_MGR
    EVDEV_DEV <--> INPUT_MGR
    OUTPUT_MGR --> SCALE_ENG
    INPUT_MGR --> EVENT_ROUTER
    SCALE_ENG --> EVENT_ROUTER
```

## 7. Components
1. **Output Manager:** Discovers active connectors via `drmModeGetResources`, reads EDID blocks, and configures CRTC scanout parameters.
2. **Scale Engine:** Computes optimal display scaling factor based on physical screen dimensions and resolution (e.g. 14" 1080p -> 125%, 27" 4K -> 150%).
3. **Input Device Manager:** Wraps `libinput`, applies user configuration (sensitivity, acceleration, tap-to-click), and translates raw events into Wayland events.
4. **XKB Keyboard Processor:** Compiles XKB keymaps (`us`, `de`, `fr`, etc.), manages modifier states (Shift, Ctrl, Alt, Super), and handles key repeats.
5. **Hotplug Monitor:** Listens to netlink uevents on `udev` socket for runtime monitor and peripheral connections.

## 8. Data Flow
1. Hardware monitor plugged into HDMI/DisplayPort.
2. Kernel DRM generates `HOTPLUG=1` uevent.
3. Compositor hotplug listener triggers output probe:
   - Reads EDID string and preferred mode (e.g. 2560x1440 @ 144Hz).
   - Allocates free CRTC and primary plane.
   - Computes layout coordinates (places new display to the right of primary).
4. Compositor registers new `wl_output` global and advertises geometry to connected Wayland clients.
5. Shell dynamically extends taskbar or spawns secondary panel per layout rules.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant Kernel as Linux Kernel
    participant Comp as nebu-compositor
    participant Client as Wayland Client
    participant Shell as nebu-shell

    Kernel->>Comp: libinput event (Pointer Move)
    Comp->>Comp: Apply acceleration curve & update cursor coordinate
    Comp->>Comp: Surface hit-test (determine surface under cursor)
    alt Surface is Shell Widget
        Comp->>Shell: wl_pointer.motion(x, y)
    else Surface is Client Window
        Comp->>Client: wl_pointer.motion(x, y)
    end
    Comp->>Comp: Update hardware cursor plane position (zero-copy DRM cursor move)
```

## 10. Interfaces
- **Wayland Output Protocols:**
  - `wl_output` (v4)
  - `xdg-output-unstable-v1` (v3)
  - `wp_fractional_scale_v1` (v1)
  - `wp_viewporter` (v1)
- **Wayland Input Protocols:**
  - `wl_seat` (v8), `wl_pointer`, `wl_keyboard`, `wl_touch`
  - `zwp_relative_pointer_manager_v1` (for FPS games)
  - `zwp_pointer_constraints_v1` (pointer lock / confine)
- **Configuration Storage:** Stored in `~/.config/nebu/displays.toml` and `~/.config/nebu/input.toml`.

## 11. Dependencies
- `libinput` >= 1.25.
- `xkbcommon` >= 1.6.
- `libdrm` >= 2.4.120.

## 12. Security
- Keystroke snooping strictly prevented: clients only receive keyboard events when their window has focus.
- Pointer position snooping prevented: clients only receive motion events within their own surface bounds.
- Virtual input injection restricted to privileged processes via authentication tokens.

## 13. Resource Requirements
- Input event processing latency: <= 0.8ms from evdev read to Wayland socket write.
- Memory footprint: <= 1.2 MB RSS for all input/display tracking structures.
- CPU utilization: < 0.1% CPU during continuous high-polling mouse movement (1000Hz gaming mice).

## 14. Failure Modes
1. **Invalid EDID Checksum:** Monitor transmits corrupted EDID data.
2. **Unsupported Mode Requested:** User requests mode exceeding display bandwidth limit.
3. **Pointer Lock Abuse:** Malicious client attempts to trap cursor indefinitely.

## 15. Recovery Behavior
- Corrupted EDID triggers safe standard fallback mode (1024x768 @ 60Hz or 1920x1080 @ 60Hz).
- Bandwidth validation tests mode via `DRM_MODE_ATOMIC_TEST_ONLY` before commit; rejects invalid modes cleanly.
- Pointer lock is immediately revoked whenever user presses `Super` key or Alt+Tabs away.

## 16. Testing Requirements
- Automated test validating fractional scaling math across standard resolutions (1080p, 1440p, 4K).
- Hotplug resilience test simulating 50 consecutive monitor disconnect/reconnect cycles.
- High-frequency pointer event stress test (1000Hz polling rate).

## 17. Performance Requirements
- Display hotplug to visible desktop output: <= 400ms.
- Hardware cursor update: 0ms latency (committed directly to DRM cursor plane).
- Display modeswitch time: <= 1.2s.

## 18. Compatibility Considerations
- Windows games requesting full-screen resolution changes are adapted through `wp_viewporter`, maintaining native monitor resolution while scaling the game surface cleanly.
- Pointer locking enables seamless mouselook in first-person Windows games running via Wine/Proton.

## 19. Open Questions
- **OQ-IND-01:** Should custom monitor color profiles (ICC) be supported via colord integration in P2 or deferred to P7?
- **OQ-IND-02:** Should multi-touch trackpad gestures (3-finger swipe for workspace switch) be handled inside compositor or shell?

## 20. Related Documents
- [00-desktop-specification.md](00-desktop-specification.md)
- [01-nebucompositor-specification.md](01-nebucompositor-specification.md)
- [02-nebushell-specification.md](02-nebushell-specification.md)
- [05-window-management.md](05-window-management.md)
"""

write_file("/root/NebuOS/docs/desktop/06-input-display.md", p6)

