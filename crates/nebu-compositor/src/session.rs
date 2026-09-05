//! Session and Seat Management Module
//!
//! Provides unprivileged device acquisition via `libseat` (connecting to
//! `systemd-logind`), allowing the compositor to obtain DRM device file descriptors
//! without requiring root privileges.

use std::os::unix::io::OwnedFd;
use std::path::{Path, PathBuf};

use smithay::backend::session::{libseat::LibSeatSession, Session};
use smithay::reexports::rustix::fs::OFlags;

/// Represents the active session manager implementation.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SessionManagerType {
    /// systemd-logind via libseat
    SystemdLogind,
    /// Direct device access (fallback for standalone headless diagnostics)
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

/// Handle to an active session capable of opening DRM devices.
pub struct SessionHandle {
    libseat: Option<LibSeatSession>,
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
    /// Failed to open a device file descriptor.
    DeviceOpenFailed(PathBuf, String),
}

impl std::fmt::Display for SessionError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::DeviceOpenFailed(p, msg) => {
                write!(f, "failed to open device '{}': {msg}", p.display())
            }
        }
    }
}

impl std::error::Error for SessionError {}

impl SessionHandle {
    /// Initializes session access. Attempts libseat/systemd-logind first;
    /// falls back cleanly to direct open if running in a standalone diagnostic context.
    pub fn new() -> Result<Self, SessionError> {
        if let Ok((session, _notifier)) = LibSeatSession::new() {
            let seat_name = session.seat();
            Ok(Self {
                libseat: Some(session),
                manager: SessionManagerType::SystemdLogind,
                seat_name,
                active: true,
            })
        } else {
            // Direct access fallback for standalone/diagnostic environments
            Ok(Self {
                libseat: None,
                manager: SessionManagerType::Direct,
                seat_name: "seat0".to_string(),
                active: true,
            })
        }
    }

    /// Opens a device through the active session.
    pub fn open_device(&mut self, path: &Path) -> Result<OwnedFd, SessionError> {
        if let Some(ref mut session) = self.libseat {
            let flags = OFlags::RDWR | OFlags::CLOEXEC;
            session
                .open(path, flags)
                .map_err(|e| SessionError::DeviceOpenFailed(path.to_path_buf(), e.to_string()))
        } else {
            std::fs::OpenOptions::new()
                .read(true)
                .write(true)
                .open(path)
                .map(std::convert::Into::into)
                .map_err(|e| SessionError::DeviceOpenFailed(path.to_path_buf(), e.to_string()))
        }
    }
}
