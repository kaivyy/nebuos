# System API Subsystem Interfaces Specification — NebuOS

**Document ID:** NEBU-SPEC-INT-008  
**Status:** DRAFT (Approved for P2.0 Architecture Lock)  
**Authority Level:** Master Subsystem Interface Specification  
**Governing ADRs:** [ADR-0004](../decisions/ADR-0004-rust.md), [ADR-0009](../decisions/ADR-0009-nebushell-ui-architecture.md), [ADR-0019](../decisions/ADR-0019-slint-toolkit-adoption.md)  
**Consulted:** PRD §12, §13, §14, §96  

---

## 1. Status

DRAFT — Technical implementation specification defining the abstraction boundary between `nebu-shell` and underlying system daemons (NetworkManager, UPower, systemd-logind, BlueZ, PipeWire/WirePlumber, and Notification services).

---

## 2. Purpose

This specification establishes the authoritative, type-safe Rust abstraction layer through which `nebu-shell` queries system telemetry and issues control actions. NebuShell operates strictly as an unprivileged user-space process (`UID 1000`). It is fundamentally prohibited from opening raw kernel device nodes, executing ioctl calls, issuing ACPI operations, or directly parsing raw sysfs trees. All hardware interaction flows through standardized D-Bus services and IPC interfaces governed by this document.

---

## 3. Scope

- Architecture and security boundaries between `nebu-shell` and system services.
- Typed Rust traits, data structures, and error models for:
  - Network Management (`trait NetworkProvider` -> `NetworkManager`)
  - Power & Battery Management (`trait PowerProvider` -> `UPower` & `systemd-logind`)
  - Bluetooth Connectivity (`trait BluetoothProvider` -> `BlueZ 5.x`)
  - Audio Routing & Volume (`trait AudioProvider` -> `PipeWire` & `WirePlumber`)
  - Desktop Notifications (`trait NotificationServer` -> `org.freedesktop.Notifications`)
  - Session & Authentication (`trait SessionManager` -> `systemd-logind`)
- D-Bus service bindings, object paths, method signatures, properties, and signals.
- Decoupled mock harnesses (`MockNetworkProvider`, `MockPowerProvider`, etc.) for headless unit testing and continuous integration.

---

## 4. Non-goals

- Implementing low-level Linux kernel device drivers or ALSA kernel modules.
- Re-implementing networking state machines or DHCP engines inside NebuShell.
- Exposing raw root or administrative D-Bus methods directly to unverified UI components.

---

## 5. Architectural Invariant & System Hierarchy

```
+-------------------------------------------------------------------------------+
|                        Hardware Devices (Wi-Fi, Battery, Audio, BT)           |
+-------------------------------------------------------------------------------+
                                        | Kernel Drivers / sysfs
+-------------------------------------------------------------------------------+
|                       Linux Kernel Subsystems (evdev, DRM, ALSA, cfg80211)    |
+-------------------------------------------------------------------------------+
                                        | System D-Bus & UNIX Sockets
+-------------------------------------------------------------------------------+
|                       System Services & Daemons (Root / Service Users)        |
|  [NetworkManager]    [UPower]    [systemd-logind]    [BlueZ]    [PipeWire]    |
+-------------------------------------------------------------------------------+
                                        | Unprivileged D-Bus / SPA Protocols
+-------------------------------------------------------------------------------+
|                  Nebu System API Abstraction Layer (crates/nebu-shell)        |
|  trait NetworkProvider | trait PowerProvider | trait BluetoothProvider         |
|  trait AudioProvider   | trait SessionManager| trait NotificationServer       |
+-------------------------------------------------------------------------------+
                                        | Rust Method Calls & State Observables
+-------------------------------------------------------------------------------+
|                         NebuShell UI Engine (Slint 1.7+)                      |
|  [Taskbar Tray]    [Quick Settings Flyout]    [Volume/Brightness OSD]         |
+-------------------------------------------------------------------------------+
```

---

## 6. Network API Specification (`NetworkManager`)

### 6.1 Subsystem Identity & Ownership
- **Upstream Service:** `NetworkManager` (`/usr/sbin/NetworkManager`)
- **D-Bus Bus:** System Bus (`dbus-broker`)
- **Well-Known Name:** `org.freedesktop.NetworkManager`
- **Object Path:** `/org/freedesktop/NetworkManager`
- **Client Ownership:** `nebu-shell::system_api::network`

### 6.2 D-Bus Interface Surface
- **Primary Interface:** `org.freedesktop.NetworkManager`
- **Properties:**
  - `State` (`u`): Overall connection state (e.g., `NM_STATE_CONNECTED_GLOBAL = 70`).
  - `WirelessEnabled` (`b`): Wi-Fi radio power state.
  - `PrimaryConnection` (`o`): Object path of active default route.
- **Methods:**
  - `GetDevices() -> (ao)`: Returns paths of all network interfaces.
  - `ActivateConnection(o: connection, o: device, o: specific_object) -> (o: active_connection)`
  - `DeactivateConnection(o: active_connection) -> ()`
- **Signals:**
  - `StateChanged(u: state)`
  - `DeviceAdded(o: device_path)`
  - `DeviceRemoved(o: device_path)`
- **Wireless Interface:** `org.freedesktop.NetworkManager.Device.Wireless`
  - `RequestScan(a{sv}: options) -> ()`
  - `GetAccessPoints() -> (ao: access_points)`
  - `PropertiesChanged(a{sv}: properties)`

### 6.3 Rust Trait Contract
```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum NetworkState {
    Disconnected,
    Connecting,
    ConnectedLocal,
    ConnectedGlobal,
    PortalDetected,
}

#[derive(Debug, Clone)]
pub struct AccessPoint {
    pub ssid: String,
    pub bssid: String,
    pub signal_strength: u8, // 0 - 100%
    pub is_secure: bool,
    pub is_active: bool,
}

#[derive(Debug, thiserror::Error)]
pub enum NetworkError {
    #[error("NetworkManager D-Bus service unavailable: {0}")]
    ServiceUnavailable(String),
    #[error("Authentication failed: invalid passphrase")]
    InvalidCredentials,
    #[error("Scan request throttled")]
    ScanThrottled,
    #[error("Device not found: {0}")]
    DeviceNotFound(String),
}

pub trait NetworkProvider: Send + Sync {
    fn get_state(&self) -> NetworkState;
    fn is_wifi_enabled(&self) -> bool;
    fn set_wifi_enabled(&mut self, enabled: bool) -> Result<(), NetworkError>;
    fn scan_access_points(&mut self) -> Result<Vec<AccessPoint>, NetworkError>;
    fn connect_wifi(&mut self, ssid: &str, passphrase: Option<&str>) -> Result<(), NetworkError>;
    fn disconnect(&mut self) -> Result<(), NetworkError>;
}
```

### 6.4 Security & Mock Strategy
- **Authorization:** Querying state is unprivileged. Connecting to new Wi-Fi networks triggers Polkit authorization (`org.freedesktop.NetworkManager.settings.modify.system`).
- **Mock Implementation:** `MockNetworkProvider` returns deterministic synthetic Wi-Fi access points and transitions connection states on timer ticks without invoking D-Bus.

---

## 7. Power & Battery API Specification (`UPower` & `systemd-logind`)

### 7.1 Subsystem Identity & Ownership
- **Upstream Services:** 
  - `UPower` (`/usr/libexec/upowerd`) on System Bus (`org.freedesktop.UPower`)
  - `systemd-logind` (`/usr/lib/systemd/systemd-logind`) on System Bus (`org.freedesktop.login1`)
- **Client Ownership:** `nebu-shell::system_api::power`

### 7.2 D-Bus Interface Surface
- **UPower Daemon:** `/org/freedesktop/UPower` (`org.freedesktop.UPower`)
  - `OnBattery` (`b`): System operating on DC battery power.
  - `EnumerateDevices() -> (ao: devices)`
- **UPower Device:** `/org/freedesktop/UPower/devices/battery_BAT0` (`org.freedesktop.UPower.Device`)
  - `State` (`u`): `1 = Charging`, `2 = Discharging`, `3 = Empty`, `4 = Fully Charged`.
  - `Percentage` (`d`): Battery charge percentage ($0.0 \dots 100.0\%$).
  - `TimeToEmpty` (`x`): Seconds remaining until empty.
  - `TimeToFull` (`x`): Seconds remaining until fully charged.
  - `EnergyRate` (`d`): Current discharge rate in Watts.
- **Logind Manager:** `/org/freedesktop/login1` (`org.freedesktop.login1.Manager`)
  - `Suspend(b: interactive) -> ()`
  - `PowerOff(b: interactive) -> ()`
  - `Reboot(b: interactive) -> ()`
  - `Inhibit(s: what, s: who, s: why, s: mode) -> (h: fd)`

### 7.3 Rust Trait Contract
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BatteryState {
    Unknown,
    Charging,
    Discharging,
    Empty,
    FullyCharged,
    NotPresent,
}

#[derive(Debug, Clone)]
pub struct PowerStatus {
    pub has_battery: bool,
    pub on_battery: bool,
    pub percentage: f32, // 0.0 to 100.0
    pub state: BatteryState,
    pub time_remaining_secs: Option<u64>,
}

#[derive(Debug, thiserror::Error)]
pub enum PowerError {
    #[error("UPower daemon unavailable: {0}")]
    UPowerUnavailable(String),
    #[error("systemd-logind rejected action: {0}")]
    LogindError(String),
    #[error("Operation inhibited by active process: {0}")]
    Inhibited(String),
}

pub trait PowerProvider: Send + Sync {
    fn get_power_status(&self) -> PowerStatus;
    fn request_suspend(&mut self) -> Result<(), PowerError>;
    fn request_reboot(&mut self) -> Result<(), PowerError>;
    fn request_poweroff(&mut self) -> Result<(), PowerError>;
}
```

---

## 8. Bluetooth API Specification (`BlueZ`)

### 8.1 Subsystem Identity & Ownership
- **Upstream Service:** `bluetoothd` (`/usr/libexec/bluetooth/bluetoothd`)
- **D-Bus Bus:** System Bus (`org.bluez`)
- **Client Ownership:** `nebu-shell::system_api::bluetooth`

### 8.2 D-Bus Interface Surface
- **Adapter Interface:** `/org/bluez/hci0` (`org.bluez.Adapter1`)
  - `Powered` (`b`): Radio active state.
  - `Discovering` (`b`): Active scan state.
  - `StartDiscovery() -> ()`
  - `StopDiscovery() -> ()`
- **Device Interface:** `/org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX` (`org.bluez.Device1`)
  - `Address` (`s`), `Name` (`s`), `Alias` (`s`), `Icon` (`s`).
  - `Paired` (`b`), `Connected` (`b`), `Trusted` (`b`).
  - `Connect() -> ()`
  - `Disconnect() -> ()`
  - `Pair() -> ()`
- **Battery Interface:** `org.bluez.Battery1`
  - `Percentage` (`y`): Peripheral battery percentage ($0 \dots 100\%$).

### 8.3 Rust Trait Contract
```rust
#[derive(Debug, Clone)]
pub struct BluetoothDevice {
    pub mac_address: String,
    pub name: String,
    pub is_connected: bool,
    pub is_paired: bool,
    pub battery_percentage: Option<u8>,
}

#[derive(Debug, thiserror::Error)]
pub enum BluetoothError {
    #[error("BlueZ daemon unavailable: {0}")]
    ServiceUnavailable(String),
    #[error("No Bluetooth adapter found")]
    NoAdapter,
    #[error("Device connection failed: {0}")]
    ConnectionFailed(String),
}

pub trait BluetoothProvider: Send + Sync {
    fn is_powered(&self) -> bool;
    fn set_powered(&mut self, powered: bool) -> Result<(), BluetoothError>;
    fn start_discovery(&mut self) -> Result<(), BluetoothError>;
    fn stop_discovery(&mut self) -> Result<(), BluetoothError>;
    fn list_devices(&self) -> Vec<BluetoothDevice>;
    fn connect_device(&mut self, mac: &str) -> Result<(), BluetoothError>;
    fn disconnect_device(&mut self, mac: &str) -> Result<(), BluetoothError>;
}
```

---

## 9. Audio API Specification (`PipeWire` & `WirePlumber`)

### 9.1 Subsystem Identity & Ownership
- **Upstream Services:** `pipewire` & `wireplumber` running inside user session (`user@1000.service`).
- **Communication:** PipeWire native SPA socket (`$XDG_RUNTIME_DIR/pipewire-0`) and WirePlumber D-Bus interface.
- **Client Ownership:** `nebu-shell::system_api::audio`

### 9.2 Interface Surface & Capabilities
- **Master Volume:** Range $0.0$ to $1.5$ (clamped to $1.0$ standard, $1.5$ with over-amplification).
- **Mute Toggle:** Boolean state.
- **Default Endpoints:** Output sink (Speakers / Headphones / HDMI) and input source (Microphone).
- **Node Monitoring:** Real-time event notifications when audio streams appear, route, or terminate.

### 9.3 Rust Trait Contract
```rust
#[derive(Debug, Clone)]
pub struct AudioEndpoint {
    pub id: u32,
    pub name: String,
    pub description: String,
    pub is_default: bool,
}

#[derive(Debug, thiserror::Error)]
pub enum AudioError {
    #[error("WirePlumber / PipeWire service disconnected: {0}")]
    ConnectionLost(String),
    #[error("Invalid volume parameter: {0}")]
    InvalidParameter(String),
}

pub trait AudioProvider: Send + Sync {
    fn get_volume(&self) -> f32; // 0.0 to 1.0
    fn set_volume(&mut self, volume: f32) -> Result<(), AudioError>;
    fn is_muted(&self) -> bool;
    fn set_muted(&mut self, muted: bool) -> Result<(), AudioError>;
    fn list_sinks(&self) -> Vec<AudioEndpoint>;
    fn set_default_sink(&mut self, sink_id: u32) -> Result<(), AudioError>;
}
```

---

## 10. Notification Server Specification (`org.freedesktop.Notifications`)

### 10.1 Subsystem Identity & Ownership
- **Role:** NebuShell provides the authoritative notification server daemon for the user session.
- **D-Bus Bus:** Session Bus (`dbus-broker`)
- **Well-Known Name:** `org.freedesktop.Notifications`
- **Object Path:** `/org/freedesktop/Notifications`
- **Specification Compliance:** Desktop Notification Specification Version 1.2.

### 10.2 Introspection XML Definition
```xml
<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node name="/org/freedesktop/Notifications">
  <interface name="org.freedesktop.Notifications">
    <method name="Notify">
      <arg name="app_name" type="s" direction="in"/>
      <arg name="replaces_id" type="u" direction="in"/>
      <arg name="app_icon" type="s" direction="in"/>
      <arg name="summary" type="s" direction="in"/>
      <arg name="body" type="s" direction="in"/>
      <arg name="actions" type="as" direction="in"/>
      <arg name="hints" type="a{sv}" direction="in"/>
      <arg name="expire_timeout" type="i" direction="in"/>
      <arg name="id" type="u" direction="out"/>
    </method>
    <method name="CloseNotification">
      <arg name="id" type="u" direction="in"/>
    </method>
    <method name="GetCapabilities">
      <arg name="capabilities" type="as" direction="out"/>
    </method>
    <method name="GetServerInformation">
      <arg name="name" type="s" direction="out"/>
      <arg name="vendor" type="s" direction="out"/>
      <arg name="version" type="s" direction="out"/>
      <arg name="spec_version" type="s" direction="out"/>
    </method>
    <signal name="NotificationClosed">
      <arg name="id" type="u"/>
      <arg name="reason" type="u"/>
    </signal>
    <signal name="ActionInvoked">
      <arg name="id" type="u"/>
      <arg name="action_key" type="s"/>
    </signal>
  </interface>
</node>
```

---

## 11. Security and Privilege Model

1. **Zero Raw Device Access:** NebuShell contains `#![forbid(unsafe_code)]` and zero code opening `/dev/*`.
2. **Session Bus Mediation:** All internal shell RPC occurs on the unprivileged user session bus managed by `dbus-broker`.
3. **Polkit Authorization:** Any action modifying system configuration (e.g. Wi-Fi credentials or power off) is gated by Polkit policies defined in `/usr/share/polkit-1/rules.d/50-nebuos-system.rules`.
4. **App Sandbox Containment:** Wine and Linux apps executing in Bubblewrap containers are forbidden from registering or querying private session D-Bus interfaces.

---

## 12. Mock and Headless Testability Strategy

To ensure deterministic testing in continuous integration without real hardware:
- Every provider (`NetworkProvider`, `PowerProvider`, `BluetoothProvider`, `AudioProvider`) is decoupled behind a dynamic or generic trait bound.
- In unit tests and headless GUI verification runs, `MockSystemApiHub` is injected into the Slint UI model, allowing tests to simulate battery drainage, Wi-Fi drops, volume adjustments, and notification bursts with zero external daemon dependencies.
