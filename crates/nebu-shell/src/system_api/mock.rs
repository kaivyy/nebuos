//! Deterministic mock implementations of System API interfaces for testing and headless verification.
#![deny(unsafe_code)]

use crate::system_api::traits::*;

/// Headless/testing mock network provider.
#[derive(Debug, Clone)]
pub struct MockNetworkProvider {
    state: NetworkState,
    wifi_enabled: bool,
    access_points: Vec<AccessPoint>,
}

impl Default for MockNetworkProvider {
    fn default() -> Self {
        Self {
            state: NetworkState::ConnectedGlobal,
            wifi_enabled: true,
            access_points: vec![
                AccessPoint {
                    ssid: "NebuOS-Secure".into(),
                    bssid: "00:11:22:33:44:55".into(),
                    signal_strength: 95,
                    is_secure: true,
                    is_active: true,
                },
                AccessPoint {
                    ssid: "Guest-Wi-Fi".into(),
                    bssid: "AA:BB:CC:DD:EE:FF".into(),
                    signal_strength: 65,
                    is_secure: false,
                    is_active: false,
                },
            ],
        }
    }
}

impl NetworkProvider for MockNetworkProvider {
    fn get_state(&self) -> NetworkState {
        self.state
    }

    fn is_wifi_enabled(&self) -> bool {
        self.wifi_enabled
    }

    fn set_wifi_enabled(&mut self, enabled: bool) -> Result<(), NetworkError> {
        self.wifi_enabled = enabled;
        if !enabled {
            self.state = NetworkState::Disconnected;
        } else {
            self.state = NetworkState::ConnectedGlobal;
        }
        Ok(())
    }

    fn scan_access_points(&mut self) -> Result<Vec<AccessPoint>, NetworkError> {
        if !self.wifi_enabled {
            return Err(NetworkError::DeviceNotFound("Wi-Fi disabled".into()));
        }
        Ok(self.access_points.clone())
    }

    fn connect_wifi(&mut self, ssid: &str, _passphrase: Option<&str>) -> Result<(), NetworkError> {
        if let Some(ap) = self.access_points.iter_mut().find(|a| a.ssid == ssid) {
            ap.is_active = true;
            self.state = NetworkState::ConnectedGlobal;
            Ok(())
        } else {
            Err(NetworkError::DeviceNotFound(ssid.to_string()))
        }
    }

    fn disconnect(&mut self) -> Result<(), NetworkError> {
        for ap in &mut self.access_points {
            ap.is_active = false;
        }
        self.state = NetworkState::Disconnected;
        Ok(())
    }
}

/// Headless/testing mock power provider.
#[derive(Debug, Clone)]
pub struct MockPowerProvider {
    pub status: PowerStatus,
}

impl Default for MockPowerProvider {
    fn default() -> Self {
        Self {
            status: PowerStatus {
                has_battery: true,
                on_battery: false,
                percentage: 98.5,
                state: BatteryState::FullyCharged,
                time_remaining_secs: None,
            },
        }
    }
}

impl PowerProvider for MockPowerProvider {
    fn get_power_status(&self) -> PowerStatus {
        self.status.clone()
    }

    fn request_suspend(&mut self) -> Result<(), PowerError> {
        Ok(())
    }

    fn request_reboot(&mut self) -> Result<(), PowerError> {
        Ok(())
    }

    fn request_poweroff(&mut self) -> Result<(), PowerError> {
        Ok(())
    }
}

/// Headless/testing mock Bluetooth provider.
#[derive(Debug, Clone)]
pub struct MockBluetoothProvider {
    powered: bool,
    devices: Vec<BluetoothDevice>,
}

impl Default for MockBluetoothProvider {
    fn default() -> Self {
        Self {
            powered: true,
            devices: vec![BluetoothDevice {
                mac_address: "12:34:56:78:9A:BC".into(),
                name: "Nebu Wireless Mouse".into(),
                is_connected: true,
                is_paired: true,
                battery_percentage: Some(85),
            }],
        }
    }
}

impl BluetoothProvider for MockBluetoothProvider {
    fn is_powered(&self) -> bool {
        self.powered
    }

    fn set_powered(&mut self, powered: bool) -> Result<(), BluetoothError> {
        self.powered = powered;
        Ok(())
    }

    fn start_discovery(&mut self) -> Result<(), BluetoothError> {
        if !self.powered {
            return Err(BluetoothError::NoAdapter);
        }
        Ok(())
    }

    fn stop_discovery(&mut self) -> Result<(), BluetoothError> {
        Ok(())
    }

    fn list_devices(&self) -> Vec<BluetoothDevice> {
        self.devices.clone()
    }

    fn connect_device(&mut self, mac: &str) -> Result<(), BluetoothError> {
        if let Some(dev) = self.devices.iter_mut().find(|d| d.mac_address == mac) {
            dev.is_connected = true;
            Ok(())
        } else {
            Err(BluetoothError::ConnectionFailed(mac.into()))
        }
    }

    fn disconnect_device(&mut self, mac: &str) -> Result<(), BluetoothError> {
        if let Some(dev) = self.devices.iter_mut().find(|d| d.mac_address == mac) {
            dev.is_connected = false;
            Ok(())
        } else {
            Err(BluetoothError::ConnectionFailed(mac.into()))
        }
    }
}

/// Headless/testing mock Audio provider.
#[derive(Debug, Clone)]
pub struct MockAudioProvider {
    volume: f32,
    muted: bool,
    sinks: Vec<AudioEndpoint>,
}

impl Default for MockAudioProvider {
    fn default() -> Self {
        Self {
            volume: 0.65,
            muted: false,
            sinks: vec![
                AudioEndpoint {
                    id: 1,
                    name: "alsa_output.pci-0000_00_1f.3.analog-stereo".into(),
                    description: "Built-in Audio Analog Stereo".into(),
                    is_default: true,
                },
                AudioEndpoint {
                    id: 2,
                    name: "bluez_output.12_34_56_78_9A_BC.1".into(),
                    description: "Wireless Headphones".into(),
                    is_default: false,
                },
            ],
        }
    }
}

impl AudioProvider for MockAudioProvider {
    fn get_volume(&self) -> f32 {
        self.volume
    }

    fn set_volume(&mut self, volume: f32) -> Result<(), AudioError> {
        if !(0.0..=1.5).contains(&volume) {
            return Err(AudioError::InvalidParameter(
                "Volume must be 0.0..=1.5".into(),
            ));
        }
        self.volume = volume;
        Ok(())
    }

    fn is_muted(&self) -> bool {
        self.muted
    }

    fn set_muted(&mut self, muted: bool) -> Result<(), AudioError> {
        self.muted = muted;
        Ok(())
    }

    fn list_sinks(&self) -> Vec<AudioEndpoint> {
        self.sinks.clone()
    }

    fn set_default_sink(&mut self, sink_id: u32) -> Result<(), AudioError> {
        if let Some(s) = self.sinks.iter_mut().find(|s| s.id == sink_id) {
            s.is_default = true;
            for other in &mut self.sinks {
                if other.id != sink_id {
                    other.is_default = false;
                }
            }
            Ok(())
        } else {
            Err(AudioError::InvalidParameter(format!(
                "Sink ID {sink_id} not found"
            )))
        }
    }
}

/// Unified mock system hub combining all mock providers.
#[derive(Debug, Default)]
pub struct MockSystemApiHub {
    pub network: MockNetworkProvider,
    pub power: MockPowerProvider,
    pub bluetooth: MockBluetoothProvider,
    pub audio: MockAudioProvider,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mock_network_provider() {
        let mut net = MockNetworkProvider::default();
        assert_eq!(net.get_state(), NetworkState::ConnectedGlobal);
        assert!(net.is_wifi_enabled());

        let aps = net.scan_access_points().unwrap();
        assert_eq!(aps.len(), 2);
        assert_eq!(aps[0].ssid, "NebuOS-Secure");

        net.disconnect().unwrap();
        assert_eq!(net.get_state(), NetworkState::Disconnected);

        net.connect_wifi("NebuOS-Secure", None).unwrap();
        assert_eq!(net.get_state(), NetworkState::ConnectedGlobal);

        net.set_wifi_enabled(false).unwrap();
        assert!(!net.is_wifi_enabled());
        assert!(net.scan_access_points().is_err());
    }

    #[test]
    fn test_mock_power_provider() {
        let mut power = MockPowerProvider::default();
        let status = power.get_power_status();
        assert!(status.has_battery);
        assert_eq!(status.state, BatteryState::FullyCharged);
        assert!(power.request_suspend().is_ok());
        assert!(power.request_reboot().is_ok());
        assert!(power.request_poweroff().is_ok());
    }

    #[test]
    fn test_mock_bluetooth_provider() {
        let mut bt = MockBluetoothProvider::default();
        assert!(bt.is_powered());
        let devs = bt.list_devices();
        assert_eq!(devs.len(), 1);
        assert_eq!(devs[0].name, "Nebu Wireless Mouse");

        assert!(bt.start_discovery().is_ok());
        assert!(bt.stop_discovery().is_ok());
        assert!(bt.disconnect_device("12:34:56:78:9A:BC").is_ok());
        assert!(bt.connect_device("12:34:56:78:9A:BC").is_ok());
    }

    #[test]
    fn test_mock_audio_provider() {
        let mut audio = MockAudioProvider::default();
        assert_eq!(audio.get_volume(), 0.65);
        assert!(!audio.is_muted());

        audio.set_volume(0.80).unwrap();
        assert_eq!(audio.get_volume(), 0.80);

        audio.set_muted(true).unwrap();
        assert!(audio.is_muted());

        let sinks = audio.list_sinks();
        assert_eq!(sinks.len(), 2);
        assert!(audio.set_default_sink(2).is_ok());
        assert!(audio.set_volume(2.0).is_err());
    }
}
