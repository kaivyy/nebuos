//! Session and Seat Management Module
//!
//! Provides unprivileged device acquisition via `libseat` (connecting to
//! `systemd-logind`), allowing the compositor to obtain DRM device file descriptors
//! without requiring root privileges.

use std::os::unix::io::OwnedFd;
use std::path::{Path, PathBuf};

use smithay::backend::session::{
    libseat::{LibSeatSession, LibSeatSessionNotifier},
    Session,
};
use smithay::reexports::rustix::fs::OFlags;

/// Represents the active session manager implementation.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SessionManagerType {
    /// systemd-logind via libseat (Production path)
    SystemdLogind,
    /// Direct device access (Fallback for standalone headless diagnostics)
    Direct,
}

impl std::fmt::Display for SessionManagerType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::SystemdLogind => write!(f, "systemd-logind"),
            Self::Direct => write!(f, "direct"),
        }
    }
}

/// Handle to an active session capable of opening DRM and input devices.
pub struct SessionHandle {
    libseat: Option<LibSeatSession>,
    notifier: Option<LibSeatSessionNotifier>,
    /// Manager type
    pub manager: SessionManagerType,
    /// Seat name
    pub seat_name: String,
    /// Session active flag
    pub active: bool,
}

/// Errors occurring during session creation or device acquisition.
#[derive(Debug)]
pub enum SessionError {
    /// Failed to initialize production session via libseat / systemd-logind.
    ProductionSessionUnavailable(String),
    /// Failed to open a device file descriptor.
    DeviceOpenFailed(PathBuf, String),
}

impl std::fmt::Display for SessionError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::ProductionSessionUnavailable(msg) => {
                write!(
                    f,
                    "production session unavailable (libseat/logind required): {msg}"
                )
            }
            Self::DeviceOpenFailed(p, msg) => {
                write!(f, "failed to open device '{}': {msg}", p.display())
            }
        }
    }
}

impl std::error::Error for SessionError {}

impl SessionHandle {
    /// Initializes production session access using unprivileged `libseat` interfacing with `systemd-logind`.
    /// Fails immediately if logind/libseat session is not active (will never silently fall back to direct root access).
    pub fn new_production() -> Result<Self, SessionError> {
        match LibSeatSession::new() {
            Ok((session, notifier)) => {
                let seat_name = session.seat();
                Ok(Self {
                    libseat: Some(session),
                    notifier: Some(notifier),
                    manager: SessionManagerType::SystemdLogind,
                    seat_name,
                    active: true,
                })
            }
            Err(e) => Err(SessionError::ProductionSessionUnavailable(e.to_string())),
        }
    }

    /// Initializes diagnostic session access. Attempts `libseat/systemd-logind` first,
    /// but permits a direct descriptor fallback when running in standalone diagnostic contexts.
    pub fn new_diagnostic() -> Result<Self, SessionError> {
        if let Ok((session, notifier)) = LibSeatSession::new() {
            let seat_name = session.seat();
            Ok(Self {
                libseat: Some(session),
                notifier: Some(notifier),
                manager: SessionManagerType::SystemdLogind,
                seat_name,
                active: true,
            })
        } else {
            // Direct access fallback for standalone/diagnostic environments only
            Ok(Self {
                libseat: None,
                notifier: None,
                manager: SessionManagerType::Direct,
                seat_name: "seat0".to_string(),
                active: true,
            })
        }
    }

    /// Default constructor (diagnostic mode for CLI probes).
    pub fn new() -> Result<Self, SessionError> {
        Self::new_diagnostic()
    }

    /// Takes the session notifier if running on the production libseat path.
    /// This allows registering the notifier with the compositor's calloop event loop
    /// for handling session pause/resume and VT switching events.
    pub fn take_notifier(&mut self) -> Option<LibSeatSessionNotifier> {
        self.notifier.take()
    }

    /// Returns whether this session is operating on the approved unprivileged production path.
    pub fn is_production(&self) -> bool {
        self.manager == SessionManagerType::SystemdLogind
    }

    /// Opens a device through the active session.
    pub fn open_device(&mut self, path: &Path) -> Result<OwnedFd, SessionError> {
        self.open_device_with_flags(path, (OFlags::RDWR | OFlags::CLOEXEC).bits() as i32)
    }

    /// Opens a device with explicit open flags through the active session.
    pub fn open_device_with_flags(
        &mut self,
        path: &Path,
        flags: i32,
    ) -> Result<OwnedFd, SessionError> {
        let oflags = OFlags::from_bits_truncate(flags as u32) | OFlags::CLOEXEC | OFlags::NONBLOCK;
        if let Some(ref mut session) = self.libseat {
            session
                .open(path, oflags)
                .map_err(|e| SessionError::DeviceOpenFailed(path.to_path_buf(), e.to_string()))
        } else {
            use std::os::unix::fs::OpenOptionsExt;
            std::fs::OpenOptions::new()
                .read(true)
                .write(true)
                .custom_flags(oflags.bits() as i32)
                .open(path)
                .map(std::convert::Into::into)
                .map_err(|e| SessionError::DeviceOpenFailed(path.to_path_buf(), e.to_string()))
        }
    }

    /// Closes a device previously opened through this session.
    pub fn close_device(&mut self, fd: OwnedFd) -> Result<(), SessionError> {
        if let Some(ref mut session) = self.libseat {
            session
                .close(fd)
                .map_err(|e| SessionError::DeviceOpenFailed(PathBuf::from("<fd>"), e.to_string()))
        } else {
            drop(fd);
            Ok(())
        }
    }
}
