//! DRM/KMS Display Subsystem Module
//!
//! Provides dynamic DRM device discovery, connector enumeration, CRTC enumeration,
//! plane enumeration, atomic modesetting capability testing, and page-flip detection.

use std::fs;
use std::path::{Path, PathBuf};

use smithay::backend::drm::{DrmDevice, DrmDeviceFd};
use smithay::reexports::drm::{
    control::{connector::State as ConnectorState, plane, Device as ControlDevice, ModeTypeFlags},
    Device as DrmDeviceTrait, DriverCapability,
};

use crate::session::{SessionError, SessionHandle, SessionManagerType};

/// Summary report of the DRM/KMS probe.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DrmProbeReport {
    /// Session backend label
    pub session_backend: &'static str,
    /// Detected or active session manager
    pub session_manager: SessionManagerType,
    /// Session access status
    pub session_access: bool,
    /// Discovered DRM card path
    pub card_path: PathBuf,
    /// Discovered DRM render node path (if available)
    pub render_path: Option<PathBuf>,
    /// Driver identifier
    pub driver_name: String,
    /// Driver description string
    pub driver_desc: String,
    /// Total connector count
    pub connectors_count: usize,
    /// Active connected connector count
    pub connected_count: usize,
    /// Available CRTC count
    pub crtcs_count: usize,
    /// Available hardware plane count
    pub planes_count: usize,
    /// Primary plane count
    pub primary_planes_count: usize,
    /// Cursor plane count
    pub cursor_planes_count: usize,
    /// Overlay plane count
    pub overlay_planes_count: usize,
    /// Available display modes count across connected connectors
    pub modes_count: usize,
    /// Preferred display mode if reported
    pub preferred_mode: Option<String>,
    /// Whether atomic modesetting is supported
    pub atomic_modesetting: bool,
    /// Whether page-flip capability is available
    pub page_flip_capability: bool,
    /// Overall proof determination
    pub probe_success: bool,
}

/// Errors occurring during the DRM/KMS hardware probe.
#[derive(Debug)]
pub enum DrmProbeError {
    /// No DRM card nodes discovered in `/dev/dri/`.
    NoDrmDeviceFound,
    /// Session initialization or device opening failed.
    SessionError(SessionError),
    /// DRM resource query failure.
    DrmQueryFailed(String),
}

impl std::fmt::Display for DrmProbeError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::NoDrmDeviceFound => write!(f, "no DRM card device found under /dev/dri/"),
            Self::SessionError(err) => write!(f, "session error: {err}"),
            Self::DrmQueryFailed(msg) => write!(f, "DRM query failed: {msg}"),
        }
    }
}

impl std::error::Error for DrmProbeError {}

impl From<SessionError> for DrmProbeError {
    fn from(err: SessionError) -> Self {
        Self::SessionError(err)
    }
}

/// Discovers available DRM card and render nodes under a specified directory (typically `/dev/dri`).
pub fn discover_drm_devices_in(dir: &Path) -> (Option<PathBuf>, Option<PathBuf>) {
    let mut card_path = None;
    let mut render_path = None;

    if let Ok(entries) = fs::read_dir(dir) {
        let mut cards = Vec::new();
        let mut renders = Vec::new();

        for entry in entries.flatten() {
            let p = entry.path();
            if let Some(file_name) = p.file_name().and_then(|n| n.to_str()) {
                if file_name.starts_with("card") {
                    cards.push(p.clone());
                } else if file_name.starts_with("renderD") {
                    renders.push(p.clone());
                }
            }
        }

        cards.sort();
        renders.sort();

        card_path = cards.into_iter().next();
        render_path = renders.into_iter().next();
    }

    (card_path, render_path)
}

/// Discovers available DRM card and render nodes in default `/dev/dri`.
pub fn discover_drm_devices() -> (Option<PathBuf>, Option<PathBuf>) {
    discover_drm_devices_in(Path::new("/dev/dri"))
}

fn classify_plane<D: ControlDevice>(dev: &D, handle: plane::Handle) -> &'static str {
    if let Ok(props) = dev.get_properties(handle) {
        let (handles, values) = props.as_props_and_values();
        for (h, val) in handles.iter().zip(values.iter()) {
            if let Ok(info) = dev.get_property(*h) {
                if info.name().to_string_lossy() == "type" {
                    return match *val {
                        1 => "Primary",
                        2 => "Cursor",
                        0 => "Overlay",
                        _ => "Unknown",
                    };
                }
            }
        }
    }
    "Unknown"
}

/// Executes the full DRM/KMS probe sequence.
pub fn run_drm_probe() -> Result<DrmProbeReport, DrmProbeError> {
    let mut session = SessionHandle::new()?;
    let (card_opt, render_opt) = discover_drm_devices();

    let card_path = card_opt.ok_or(DrmProbeError::NoDrmDeviceFound)?;
    let dev_fd = session.open_device(&card_path)?;

    let drm_fd = DrmDeviceFd::new(dev_fd.into());
    let (dev, _notifier) = DrmDevice::new(drm_fd, false).map_err(|e| {
        DrmProbeError::DrmQueryFailed(format!("failed to initialize DrmDevice: {e}"))
    })?;

    let driver = dev
        .get_driver()
        .map_err(|e| DrmProbeError::DrmQueryFailed(format!("failed to query driver: {e}")))?;

    let driver_name = driver.name().to_string_lossy().into_owned();
    let driver_desc = driver.description().to_string_lossy().into_owned();

    let resources = dev.resource_handles().map_err(|e| {
        DrmProbeError::DrmQueryFailed(format!("failed to query resource handles: {e}"))
    })?;

    let crtcs_count = resources.crtcs().len();
    let mut connectors_count = 0;
    let mut connected_count = 0;
    let mut modes_count = 0;
    let mut preferred_mode = None;

    for conn_handle in resources.connectors() {
        connectors_count += 1;
        if let Ok(conn_info) = dev.get_connector(*conn_handle, false) {
            if conn_info.state() == ConnectorState::Connected {
                connected_count += 1;
                for mode in conn_info.modes() {
                    modes_count += 1;
                    let (w, h) = mode.size();
                    let refresh = mode.vrefresh();
                    let mode_str = format!("{w}x{h}@{refresh}");
                    if mode.mode_type().contains(ModeTypeFlags::PREFERRED)
                        && preferred_mode.is_none()
                    {
                        preferred_mode = Some(mode_str.clone());
                    }
                }
                if preferred_mode.is_none() && !conn_info.modes().is_empty() {
                    let first = &conn_info.modes()[0];
                    let (w, h) = first.size();
                    let refresh = first.vrefresh();
                    preferred_mode = Some(format!("{w}x{h}@{refresh}"));
                }
            }
        }
    }

    let plane_handles = dev.plane_handles().unwrap_or_default();
    let planes_count = plane_handles.len();
    let mut primary_planes_count = 0;
    let mut cursor_planes_count = 0;
    let mut overlay_planes_count = 0;

    for plane_handle in &plane_handles {
        match classify_plane(&dev, *plane_handle) {
            "Primary" => primary_planes_count += 1,
            "Cursor" => cursor_planes_count += 1,
            "Overlay" => overlay_planes_count += 1,
            _ => {}
        }
    }

    let atomic_modesetting = dev.is_atomic();
    let page_flip_capability = atomic_modesetting
        || dev
            .get_driver_capability(DriverCapability::ASyncPageFlip)
            .unwrap_or(0)
            != 0
        || dev
            .get_driver_capability(DriverCapability::PageFlipTarget)
            .unwrap_or(0)
            != 0;

    let probe_success = !driver_name.is_empty() && crtcs_count > 0;

    let report = DrmProbeReport {
        session_backend: "libseat",
        session_manager: session.manager,
        session_access: session.active,
        card_path,
        render_path: render_opt,
        driver_name,
        driver_desc,
        connectors_count,
        connected_count,
        crtcs_count,
        planes_count,
        primary_planes_count,
        cursor_planes_count,
        overlay_planes_count,
        modes_count,
        preferred_mode,
        atomic_modesetting,
        page_flip_capability,
        probe_success,
    };

    print_probe_report(&report);

    Ok(report)
}

/// Prints the formatted deterministic DRM/KMS proof output.
pub fn print_probe_report(report: &DrmProbeReport) {
    println!("NebuCompositor DRM/KMS Proof");
    println!("=============================");
    println!();
    println!("Session:");
    println!("  Backend: {}", report.session_backend);
    println!("  Manager: {}", report.session_manager);
    println!(
        "  Access: {}",
        if report.session_access {
            "PASS"
        } else {
            "FAIL"
        }
    );
    println!();
    println!("DRM:");
    println!("  Card: {}", report.card_path.display());
    println!(
        "  Render Node: {}",
        report
            .render_path
            .as_ref()
            .map(|p| p.display().to_string())
            .unwrap_or_else(|| "NONE".to_string())
    );
    println!("  Driver: {}", report.driver_name);
    println!("  Description: {}", report.driver_desc);
    println!("  Device discovery: PASS");
    println!();
    println!("Connectors:");
    println!("  Count: {}", report.connectors_count);
    println!("  Connected: {}", report.connected_count);
    println!();
    println!("CRTCs:");
    println!("  Count: {}", report.crtcs_count);
    println!();
    println!("Planes:");
    println!("  Count: {}", report.planes_count);
    println!("  Primary: {}", report.primary_planes_count);
    println!("  Cursor: {}", report.cursor_planes_count);
    println!("  Overlay: {}", report.overlay_planes_count);
    println!();
    println!("Modes:");
    println!("  Available: {}", report.modes_count);
    println!(
        "  Preferred: {}",
        report.preferred_mode.as_deref().unwrap_or("NONE")
    );
    println!();
    println!("Atomic:");
    println!(
        "  {}",
        if report.atomic_modesetting {
            "PASS"
        } else {
            "NOT AVAILABLE"
        }
    );
    println!();
    println!("Page Flip Capability:");
    println!(
        "  {}",
        if report.page_flip_capability {
            "PASS"
        } else {
            "UNKNOWN"
        }
    );
    println!();
    println!("DRM/KMS Proof:");
    println!("  {}", if report.probe_success { "PASS" } else { "FAIL" });
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;

    #[test]
    fn test_device_discovery_empty_dir() {
        let temp_dir = std::env::temp_dir().join("nebu_test_empty_dri");
        let _ = fs::remove_dir_all(&temp_dir);
        fs::create_dir_all(&temp_dir).unwrap();

        let (card, render) = discover_drm_devices_in(&temp_dir);
        assert_eq!(card, None);
        assert_eq!(render, None);

        let _ = fs::remove_dir_all(&temp_dir);
    }

    #[test]
    fn test_device_discovery_with_nodes() {
        let temp_dir = std::env::temp_dir().join("nebu_test_mock_dri");
        let _ = fs::remove_dir_all(&temp_dir);
        fs::create_dir_all(&temp_dir).unwrap();

        File::create(temp_dir.join("card0")).unwrap();
        File::create(temp_dir.join("renderD128")).unwrap();
        File::create(temp_dir.join("controlD64")).unwrap();

        let (card, render) = discover_drm_devices_in(&temp_dir);
        assert_eq!(card, Some(temp_dir.join("card0")));
        assert_eq!(render, Some(temp_dir.join("renderD128")));

        let _ = fs::remove_dir_all(&temp_dir);
    }
}
