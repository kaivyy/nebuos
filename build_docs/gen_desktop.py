#!/usr/bin/env python3
"""
Generate Desktop Documentation for NebuOS (docs/desktop/):
- 00-desktop-overview.md
- 01-compositor.md
- 02-shell.md
- 03-window-management.md
- 04-input.md
- 05-display.md
- 06-system-integration.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs/desktop"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_file(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: desktop/{filename} ({len(content.splitlines())} lines)")

# 00-desktop-overview.md
write_file("00-desktop-overview.md", """# Desktop Overview — NebuOS

**Status:** REVIEW  
**Purpose:** Establish the architectural foundation, component partitioning, UI design principles, and technology stack of the NebuOS Desktop environment.

---

## 1. Scope & Desktop Philosophy
NebuOS provides a modern, distraction-free, highly responsive desktop experience engineered in native Rust. The desktop prioritizes immediate response times, low memory overhead (< 150 MB combined RAM for Compositor and Shell), and seamless integration between native Linux surfaces and Windows application windows.

## 2. Non-Goals
- Embedding Chromium, Electron, or web-view runtimes into core desktop shells or panels.
- Complex 3D visual effects, physics-based window wobbles, or heavy blur shaders that compromise responsiveness on 4 GB RAM hardware.
- Emulating the exact visual aesthetics of Windows 11; rather, providing intuitive, familiar desktop ergonomics (taskbar, launcher, system tray, quick settings).

## 3. Strict Separation of Concerns

```mermaid
graph LR
    subgraph COMPOSITOR [nebu-compositor - Wayland Server]
        DRM_KMS[DRM/KMS Rendering]
        LIBINPUT[libinput Event Handling]
        FRAME_SCHED[Frame Scheduler & Sync]
        SURF_MGR[Surface & Buffer Manager]
    end

    subgraph SHELL [nebu-shell - Wayland Client]
        PANEL[Taskbar & Panel]
        LAUNCHER[App Launcher & Search]
        TRAY[System Tray Host]
        NOTIF[Notification Popups]
    end

    subgraph SERVICES [Session & System Services]
        PIPEWIRE[PipeWire Audio Daemon]
        NET_MGR[NetworkManager]
        RUNTIME_D[nebu-runtime-daemon]
        DBUS[D-Bus Broker]
    end

    COMPOSITOR <-->|Wayland Protocols: wlr-layer-shell, xdg-shell| SHELL
    SHELL <-->|D-Bus Session Bus| SERVICES
    COMPOSITOR <-->|D-Bus Control Interface| SERVICES
```

### Responsibility Matrix

| Subsystem | Responsibilities | Technologies | Strict Boundaries |
|---|---|---|---|
| **`nebu-compositor`** | Direct GPU display scanout, window geometry, surface commit handling, input device reading, multi-monitor configuration. | Rust, Smithay, DRM/KMS, EGL/Vulkan, libinput | Does NOT draw taskbar buttons, menus, notifications, or launcher UI. |
| **`nebu-shell`** | UI presentation, taskbar icon rendering, application launching, quick settings toggles, notification popups. | Rust, Slint / Iced, Wayland Client Protocols | Does NOT access raw `/dev/dri/cardX` or manage hardware framebuffers directly. |
| **Session Services** | Background business logic (audio volume, WiFi scanning, package updates, prefix lifecycle). | Rust, systemd, PipeWire, D-Bus | Headless services communicating strictly via IPC contracts. |

## 4. Related Documents
- [01-compositor.md](01-compositor.md)
- [02-shell.md](02-shell.md)
- [06-system-integration.md](06-system-integration.md)
""")

# 01-compositor.md
write_file("01-compositor.md", """# NebuCompositor Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define the software architecture, rendering pipeline, Wayland protocol support, buffer exchange mechanisms, and frame scheduling for `nebu-compositor`.

---

## 1. Architectural Foundation & Core Technologies
- **Implementation Language:** Rust (100% safe Rust where possible, isolated `unsafe` blocks for FFI).
- **Compositor Framework:** Built upon `smithay` (modular Rust Wayland compositor primitives).
- **Backend Display Interface:** Linux Direct Rendering Manager / Kernel Mode Setting (`DRM/KMS`) via `gbm` (Generic Buffer Management) and `libdrm`.
- **Input Engine:** `libinput` with custom event dispatch loops.
- **Hardware Acceleration:** OpenGL ES 3.2 / Vulkan via Mesa with explicit synchronization (`linux-drm-syncobj-v1`).

## 2. Rendering Pipeline & Frame Scheduling

```mermaid
sequenceDiagram
    autonumber
    participant App as Client (Wine / Linux App)
    participant Comp as NebuCompositor
    participant GPU as GPU / DRM KMS
    participant Mon as Display Monitor

    App->>Comp: wl_surface.commit(buffer: dmabuf)
    Comp->>Comp: Damage Tracking (Compute dirty rects)
    Comp->>Comp: Determine Direct Scanout eligibility
    alt Direct Scanout (Fullscreen App / Game)
        Comp->>GPU: drmModePageFlip(buffer: dmabuf) - Zero Copy
    else Composited Mode (Windowed Desktop)
        Comp->>GPU: Render dirty rects into composite framebuffer
        Comp->>GPU: drmModeAtomicCommit(presentation_time)
    end
    GPU->>Mon: VSync Refresh (Hardware Scanout)
    Comp->>App: wl_surface.frame(callback)
```

## 3. Wayland Protocol Support Matrix

### Core Protocols
- `wl_compositor` (v6), `wl_subcompositor` (v1)
- `wl_shm` (v1), `linux_dmabuf_v1` (v4)
- `wl_seat` (v8), `wl_output` (v4)
- `xdg_wm_base` (v4)

### Desktop Shell & Window Management Extensions
- `wlr-layer-shell-unstable-v1` (for dock, panel, launcher, notification surfaces)
- `xdg-output-unstable-v1` (accurate physical display coordinates and HiDPI mapping)
- `viewporter` (v1) and `wp_fractional_scale_v1` (clean fractional scaling without blur)
- `ext-session-lock-v1` (secure screen locking architecture)
- `linux-drm-syncobj-v1` (explicit GPU synchronization for stutter-free frame delivery)

## 4. Window & Surface Buffering Rules
1. **Direct Scanout:** Fullscreen Windows games and CAD viewports bypass compositing shaders and scan out directly from their DMA buffer, yielding near-zero latency (< 1ms compositor overhead).
2. **Tearing Policy:** Default is strict VSync (`DRM_MODE_PAGE_FLIP_EVENT`). A per-window override protocol allows tearing for high-FPS competitive games when requested.

## 5. Failure Recovery & Watchdog Integration
- `nebu-compositor` runs as a systemd user service with `WatchdogSec=5s`.
- In the event of a compositor crash, client buffer references are released cleanly, and session state is preserved in shared memory to allow client re-attach where supported by protocols.

## 6. Related Documents
- [00-desktop-overview.md](00-desktop-overview.md)
- [03-window-management.md](03-window-management.md)
- [05-display.md](05-display.md)
""")

# 02-shell.md
write_file("02-shell.md", """# NebuShell Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify the user-facing desktop shell, panel, application launcher, workspace switcher, and quick settings interface.

---

## 1. Architecture & Design Principles
- **Implementation Language:** Rust.
- **GUI Toolkit:** Native declarative Rust GUI framework (Slint or Iced) rendering directly via OpenGL/Vulkan.
- **Protocol:** Connects to `nebu-compositor` as a Wayland client using `wlr-layer-shell-unstable-v1`.
- **Latency Target:** Application launcher response < 100ms from keypress to UI render.
- **Strict Prohibition:** Absolutely no Electron, Chromium, CEF, or Node.js runtime in any desktop UI component.

## 2. Shell Subsystems Topology

```mermaid
graph TD
    subgraph NEBUSHELL [nebu-shell Process Architecture]
        CORE[Shell Core Coordinator]
        PANEL[Taskbar & Panel Surface]
        LAUNCHER[Application Launcher]
        SETTINGS[Quick Settings Modal]
        NOTIF_SURF[Notification Banner Surface]
        LOCK[Lock Screen Surface]
    end

    subgraph DAEMONS [External Session Daemons]
        RUNTIME_D[nebu-runtime-daemon]
        PIPEWIRE[PipeWire Audio]
        NM[NetworkManager]
        POWER[systemd-logind]
    end

    CORE --> PANEL
    CORE --> LAUNCHER
    CORE --> SETTINGS
    CORE --> NOTIF_SURF
    CORE --> LOCK

    PANEL <-->|D-Bus: StatusNotifierWatcher| DAEMONS
    LAUNCHER <-->|D-Bus: org.nebu.Runtime1| RUNTIME_D
    SETTINGS <-->|D-Bus: Network & Audio APIs| NM
    SETTINGS <-->|D-Bus: Session Control| POWER
```

## 3. UI Component Specifications

### 3.1 Taskbar & Panel (`nebu-panel`)
- **Position:** Anchored to bottom of primary monitor by default (configurable: top, left, right).
- **Height:** 44px on standard 1080p display (auto-scales with HiDPI).
- **Elements:**
  - *Start Button:* Triggers Application Launcher.
  - *Taskbar Items:* Running application icons with live running indicator dots and multi-window grouping.
  - *System Tray:* StatusNotifierItem (SNI) implementation for background apps.
  - *Quick Status:* Clock, battery status, volume slider trigger, network state.

### 3.2 Application Launcher (`nebu-launcher`)
- **Trigger:** Super (Windows) key or Start button click.
- **Search Engine:** In-memory indexed SQLite database of desktop entries and compatibility profiles.
- **Categorization:** Pinned Favorites, All Applications (A-Z), Recent Documents.
- **Performance Rule:** Never scans the filesystem during launch. Read-only query from local SQLite index.

### 3.3 Quick Settings (`nebu-settings-tray`)
- **Slide-out Flyout:** Displayed upon clicking the status area.
- **Controls:**
  - Volume slider and audio output selector (PipeWire).
  - WiFi network picker and toggle (NetworkManager).
  - Bluetooth device list and pairing toggle (BlueZ).
  - Performance Mode selector: [Lite | Balanced | High Performance].
  - Display brightness and Night Light toggle.

## 4. Memory and Performance Budget
- Idle Memory (RSS): <= 45 MB.
- Active Memory during launcher search: <= 70 MB.
- Frame Rate: Smooth 60 FPS / 120 FPS animations utilizing hardware GPU rendering.

## 5. Related Documents
- [00-desktop-overview.md](00-desktop-overview.md)
- [01-compositor.md](01-compositor.md)
- [06-system-integration.md](06-system-integration.md)
""")

# 03-window-management.md
write_file("03-window-management.md", """# Window Management Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify window states, window rules, floating vs tiling behaviors, focus policies, and grouping mechanisms for complex multi-window Windows applications.

---

## 1. Window Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> Unmapped: Client creates wl_surface
    Unmapped --> InitialConfig: xdg_toplevel.configure
    InitialConfig --> Floating: First Buffer Commit (Default Window)
    Floating --> Maximized: Window maximize action / snap to top
    Maximized --> Floating: Restore geometry
    Floating --> Fullscreen: Fullscreen toggle / F11
    Fullscreen --> Floating: Exit fullscreen
    Floating --> Minimized: Minimize action
    Minimized --> Floating: Taskbar restore
    Floating --> [*]: wl_surface.destroy
```

## 2. Window Geometry & Snapping
- **Window Snapping:** Edge-drag to screen borders triggers half-screen split (left/right) or quarter-screen quadrants (corners).
- **Floating Controls:** Titlebar with Close, Maximize/Restore, and Minimize controls; double-click titlebar toggles maximize.
- **Multi-Monitor Window Placement:** Windows restore to their last known output and geometry coordinates indexed by application ID.

## 3. Windows Application Window Grouping Rules
Windows applications (especially CAD tools like AutoCAD, Maya, 3ds Max, Photoshop) spawn numerous child surfaces: tool palettes, floating toolbars, modal dialogs, and splash screens.
1. **Transient Parent Binding:** Child surfaces (`WS_POPUP`, `WS_CHILD`) are strictly linked to the main application window using `xdg_toplevel.set_parent`.
2. **Taskbar Aggregation:** All child windows belonging to an application prefix (e.g. `autodesk.autocad.2024`) are grouped under a single taskbar icon.
3. **Modal Dialog Focus Trap:** Modal Windows dialogs (e.g., File Open, Options) capture focus and keep the parent window locked until dismissed.

## 4. Related Documents
- [01-compositor.md](01-compositor.md)
- [02-shell.md](02-shell.md)
- [../runtime/02-windows-runtime.md](../runtime/02-windows-runtime.md)
""")

# 04-input.md
write_file("04-input.md", """# Input Subsystem Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Detail input device handling, event dispatch, keyboard mapping, touchpad gestures, stylus/tablet input for CAD, and gaming controllers.

---

## 1. Input Architecture Stack
- **Device Enumeration:** Kernel `evdev` events -> `libinput` -> `nebu-compositor` -> Wayland Input Events (`wl_keyboard`, `wl_pointer`, `wl_touch`, `zwp_tablet_v2`).
- **Focus Management:** Click-to-focus with configurable focus-follows-mouse option.

## 2. Input Subsystem Flow

```mermaid
graph LR
    HW[Hardware: Keyboard / Mouse / Touchpad / Stylus / Gamepad] --> KERNEL[Kernel evdev / uinput]
    KERNEL --> LIBINPUT[libinput Library]
    LIBINPUT --> COMP[nebu-compositor Event Dispatcher]
    COMP -->|Wayland wl_pointer / wl_keyboard| NATIVE[Native Linux Client]
    COMP -->|Wayland wl_seat| WINE[Wine Xwayland / Native Wayland Driver]
    WINE --> WIN_APP[Windows App / CAD / Game]
```

## 3. Specialized Input Device Support
- **Touchpad Gestures:** 3-finger swipe up (workspace overview), 3-finger swipe left/right (switch workspace), pinch-to-zoom (emits `wl_pointer` gesture events).
- **Graphics Tablets & Stylus:** Direct support for Wacom and Huion drawing tablets via `zwp_tablet_v2`, forwarding pressure sensitivity, tilt, and button events to AutoCAD, Photoshop, and Maya.
- **Game Controllers:** Gamepad events are handled via Linux `joydev`/`evdev` and exposed directly to Wine/Proton `xinput1_3.dll` translation layer.

## 4. Related Documents
- [01-compositor.md](01-compositor.md)
- [../runtime/05-proton-integration.md](../runtime/05-proton-integration.md)
""")

# 05-display.md
write_file("05-display.md", """# Display Subsystem Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify multi-monitor topology, mixed-DPI scaling, fractional scaling algorithms, Variable Refresh Rate (VRR), and display hotplugging.

---

## 1. Multi-Monitor Architecture
- **Display Topology:** Arbitrary 2D virtual coordinate space supporting mixed orientations (horizontal, vertical) and mixed refresh rates (e.g. 60 Hz laptop screen + 144 Hz gaming monitor).
- **Hotplug Detection:** Handled asynchronously via udev DRM connector events (`HOTPLUG=1`), adapting layout without terminating running applications.

## 2. Scaling Architecture & HiDPI

```mermaid
graph TD
    MON_4K[4K Monitor - 200% Scale] -->|Scale Factor: 2.0| COMP[NebuCompositor]
    MON_1080P[1080p Monitor - 100% Scale] -->|Scale Factor: 1.0| COMP
    
    COMP -->|wp_fractional_scale_v1| WAYLAND_CLIENT[Wayland Native App: Crisp Vector Scale]
    COMP -->|Xwayland Scaling Hook| WINE_CLIENT[Wine Windows App: DPI Virtualization]
```

- **Fractional Scaling:** Implements `wp_fractional_scale_v1` and `wp_viewporter`, allowing scaling increments of 125%, 150%, 175% without the blur associated with full-screen raster scaling.
- **Wine DPI Emulation:** NebuRuntime writes appropriate `LogPixels` (e.g. 96 for 100%, 144 for 150%, 192 for 200%) into the prefix registry (`HKEY_CURRENT_USER\\Control Panel\\Desktop`), ensuring Windows CAD and Office text renders sharply.

## 3. Related Documents
- [01-compositor.md](01-compositor.md)
- [03-window-management.md](03-window-management.md)
""")

# 06-system-integration.md
write_file("06-system-integration.md", """# System Integration Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define integration between NebuShell and system daemons including PipeWire audio, NetworkManager, Power/Battery management, and notification delivery.

---

## 1. Subsystem Integration Diagram

```mermaid
graph TD
    SHELL[nebu-shell] -->|libpipewire IPC| PIPEWIRE[PipeWire Audio Server]
    SHELL -->|D-Bus: org.freedesktop.NetworkManager| NM[NetworkManager Daemon]
    SHELL -->|D-Bus: org.freedesktop.login1| LOGIND[systemd-logind]
    SHELL -->|D-Bus: org.freedesktop.UPower| UPOWER[UPower Daemon]
    SHELL -->|D-Bus: org.freedesktop.Notifications| NOTIF_SRV[Internal Notification Manager]
    
    WINE_APP[Windows App] -->|Wine Audio Driver| PIPEWIRE
```

## 2. Core Service Contracts & Integration Points
- **Audio Control:** Shell binds to PipeWire's native API via `libpipewire-sys` Rust bindings, providing real-time volume meters, output device hot-swapping, and per-application volume controls (including isolating loud Windows processes).
- **Network Management:** Asynchronous D-Bus client connecting to NetworkManager for WiFi SSID scanning, WPA2/WPA3 enterprise credential submission, and VPN activation.
- **Power Management:** Listens to `UPower` battery discharge rates; triggers low-battery warnings and automatically transitions the desktop into **Nebu Lite Mode** when battery reaches critical threshold (< 15%).

## 3. Related Documents
- [00-desktop-overview.md](00-desktop-overview.md)
- [02-shell.md](02-shell.md)
- [../performance/00-performance-goals.md](../performance/00-performance-goals.md)
""")

print("Desktop documentation generated successfully.")
