//! NebuShell error definitions.
#![deny(unsafe_code)]

use std::fmt;

/// Result alias for NebuShell operations.
pub type ShellResult<T> = Result<T, ShellError>;

/// Master error type for NebuShell operations.
#[derive(Debug)]
pub enum ShellError {
    /// Wayland connection failure (e.g., socket unreachable, server closed connection).
    WaylandConnection(String),
    /// Required Wayland protocol/global missing from registry.
    ProtocolMissing(String),
    /// Wayland protocol error during interaction.
    ProtocolError(String),
    /// Wayland event loop dispatch failure.
    DispatchError(String),
    /// Shared memory buffer allocation or manipulation failure.
    ShmError(String),
    /// Layer shell surface error.
    SurfaceError(String),
    /// Slint UI initialization or rendering failure.
    SlintError(String),
    /// Configuration validation error.
    ConfigError(String),
    /// Invalid lifecycle state transition.
    LifecycleError(String),
    /// System API integration error.
    SystemApiError(String),
    /// Standard I/O error.
    Io(std::io::Error),
}

impl fmt::Display for ShellError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::WaylandConnection(msg) => write!(f, "Wayland connection failed: {msg}"),
            Self::ProtocolMissing(proto) => write!(f, "Required protocol global missing: {proto}"),
            Self::ProtocolError(msg) => write!(f, "Wayland protocol error: {msg}"),
            Self::DispatchError(msg) => write!(f, "Wayland dispatch error: {msg}"),
            Self::ShmError(msg) => write!(f, "SHM error: {msg}"),
            Self::SurfaceError(msg) => write!(f, "Surface error: {msg}"),
            Self::SlintError(msg) => write!(f, "Slint UI error: {msg}"),
            Self::ConfigError(msg) => write!(f, "Configuration error: {msg}"),
            Self::LifecycleError(msg) => write!(f, "Lifecycle state error: {msg}"),
            Self::SystemApiError(msg) => write!(f, "System API error: {msg}"),
            Self::Io(err) => write!(f, "I/O error: {err}"),
        }
    }
}

impl std::error::Error for ShellError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::Io(err) => Some(err),
            _ => None,
        }
    }
}

impl From<std::io::Error> for ShellError {
    fn from(err: std::io::Error) -> Self {
        Self::Io(err)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let err = ShellError::WaylandConnection("test failure".into());
        assert_eq!(format!("{err}"), "Wayland connection failed: test failure");
    }
}
