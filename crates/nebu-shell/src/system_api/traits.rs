//! System API subsystem trait contracts (per NEBU-SPEC-INT-008).
#![deny(unsafe_code)]

use std::fmt;

// --- Network Trait Contracts ---

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NetworkState {
    Disconnected,
    Connecting,
    ConnectedLocal,
    ConnectedGlobal,
    PortalDetected,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AccessPoint {
    pub ssid: String,
    pub bssid: String,
    pub signal_strength: u8, // 0 - 100%
    pub is_secure: bool,
    pub is_active: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum NetworkError {
    ServiceUnavailable(String),
    InvalidCredentials,
    ScanThrottled,
    DeviceNotFound(String),
}

impl fmt::Display for NetworkError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ServiceUnavailable(s) => write!(f, "Network service unavailable: {s}"),
            Self::InvalidCredentials => write!(f, "Invalid credentials"),
            Self::ScanThrottled => write!(f, "Scan request throttled"),
            Self::DeviceNotFound(s) => write!(f, "Device not found: {s}"),
        }
    }
}

impl std::error::Error for NetworkError {}

pub trait NetworkProvider: Send + Sync {
    fn get_state(&self) -> NetworkState;
    fn is_wifi_enabled(&self) -> bool;
    fn set_wifi_enabled(&mut self, enabled: bool) -> Result<(), NetworkError>;
    fn scan_access_points(&mut self) -> Result<Vec<AccessPoint>, NetworkError>;
    fn connect_wifi(&mut self, ssid: &str, passphrase: Option<&str>) -> Result<(), NetworkError>;
    fn disconnect(&mut self) -> Result<(), NetworkError>;
}

// --- Power Trait Contracts ---

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BatteryState {
    Unknown,
    Charging,
    Discharging,
    Empty,
    FullyCharged,
    NotPresent,
}

#[derive(Debug, Clone, PartialEq)]
pub struct PowerStatus {
    pub has_battery: bool,
    pub on_battery: bool,
    pub percentage: f32, // 0.0 to 100.0
    pub state: BatteryState,
    pub time_remaining_secs: Option<u64>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PowerError {
    UPowerUnavailable(String),
    LogindError(String),
    Inhibited(String),
}

impl fmt::Display for PowerError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::UPowerUnavailable(s) => write!(f, "UPower unavailable: {s}"),
            Self::LogindError(s) => write!(f, "logind error: {s}"),
            Self::Inhibited(s) => write!(f, "Operation inhibited: {s}"),
        }
    }
}

impl std::error::Error for PowerError {}

pub trait PowerProvider: Send + Sync {
    fn get_power_status(&self) -> PowerStatus;
    fn request_suspend(&mut self) -> Result<(), PowerError>;
    fn request_reboot(&mut self) -> Result<(), PowerError>;
    fn request_poweroff(&mut self) -> Result<(), PowerError>;
}

// --- Bluetooth Trait Contracts ---

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BluetoothDevice {
    pub mac_address: String,
    pub name: String,
    pub is_connected: bool,
    pub is_paired: bool,
    pub battery_percentage: Option<u8>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BluetoothError {
    ServiceUnavailable(String),
    NoAdapter,
    ConnectionFailed(String),
}

impl fmt::Display for BluetoothError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ServiceUnavailable(s) => write!(f, "BlueZ unavailable: {s}"),
            Self::NoAdapter => write!(f, "No Bluetooth adapter"),
            Self::ConnectionFailed(s) => write!(f, "Connection failed: {s}"),
        }
    }
}

impl std::error::Error for BluetoothError {}

pub trait BluetoothProvider: Send + Sync {
    fn is_powered(&self) -> bool;
    fn set_powered(&mut self, powered: bool) -> Result<(), BluetoothError>;
    fn start_discovery(&mut self) -> Result<(), BluetoothError>;
    fn stop_discovery(&mut self) -> Result<(), BluetoothError>;
    fn list_devices(&self) -> Vec<BluetoothDevice>;
    fn connect_device(&mut self, mac: &str) -> Result<(), BluetoothError>;
    fn disconnect_device(&mut self, mac: &str) -> Result<(), BluetoothError>;
}

// --- Audio Trait Contracts ---

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AudioEndpoint {
    pub id: u32,
    pub name: String,
    pub description: String,
    pub is_default: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AudioError {
    ConnectionLost(String),
    InvalidParameter(String),
}

impl fmt::Display for AudioError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ConnectionLost(s) => write!(f, "Audio server connection lost: {s}"),
            Self::InvalidParameter(s) => write!(f, "Invalid audio parameter: {s}"),
        }
    }
}

impl std::error::Error for AudioError {}

pub trait AudioProvider: Send + Sync {
    fn get_volume(&self) -> f32; // 0.0 to 1.0
    fn set_volume(&mut self, volume: f32) -> Result<(), AudioError>;
    fn is_muted(&self) -> bool;
    fn set_muted(&mut self, muted: bool) -> Result<(), AudioError>;
    fn list_sinks(&self) -> Vec<AudioEndpoint>;
    fn set_default_sink(&mut self, sink_id: u32) -> Result<(), AudioError>;
}
