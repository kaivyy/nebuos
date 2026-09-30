//! Wayland client connection handling and socket resolution.
#![deny(unsafe_code)]

use crate::error::{ShellError, ShellResult};
use std::os::unix::net::UnixStream;
use std::path::{Path, PathBuf};
use wayland_client::Connection;

/// Resolve the Wayland socket path based on configuration, environment, and standard fallbacks.
pub fn resolve_socket_path(override_path: Option<&str>) -> ShellResult<PathBuf> {
    if let Some(p) = override_path {
        let pb = PathBuf::from(p);
        if pb.is_absolute() {
            return Ok(pb);
        }
        if let Ok(runtime_dir) = std::env::var("XDG_RUNTIME_DIR") {
            return Ok(Path::new(&runtime_dir).join(pb));
        }
        return Ok(pb);
    }

    if let Ok(display) = std::env::var("WAYLAND_DISPLAY") {
        let pb = PathBuf::from(&display);
        if pb.is_absolute() {
            return Ok(pb);
        }
        if let Ok(runtime_dir) = std::env::var("XDG_RUNTIME_DIR") {
            return Ok(Path::new(&runtime_dir).join(pb));
        }
        return Ok(pb);
    }

    if let Ok(runtime_dir) = std::env::var("XDG_RUNTIME_DIR") {
        let standard = Path::new(&runtime_dir).join("wayland-0");
        if standard.exists() {
            return Ok(standard);
        }
    }

    let uid = rustix::process::getuid().as_raw();
    let run_user = PathBuf::from(format!("/run/user/{uid}/wayland-0"));
    if run_user.exists() {
        return Ok(run_user);
    }

    let tmp = PathBuf::from("/tmp/wayland-0");
    if tmp.exists() {
        return Ok(tmp);
    }

    // Default fallback
    if let Ok(runtime_dir) = std::env::var("XDG_RUNTIME_DIR") {
        Ok(Path::new(&runtime_dir).join("wayland-0"))
    } else {
        Ok(PathBuf::from("/run/user/1000/wayland-0"))
    }
}

/// Connect to the Wayland compositor socket.
pub fn connect_to_wayland(override_path: Option<&str>) -> ShellResult<(Connection, PathBuf)> {
    let socket_path = resolve_socket_path(override_path)?;
    tracing::info!(socket = %socket_path.display(), "Connecting to Wayland compositor");

    let stream = UnixStream::connect(&socket_path).map_err(|err| {
        ShellError::WaylandConnection(format!(
            "Failed to connect to Wayland UNIX socket at {}: {err}",
            socket_path.display()
        ))
    })?;

    let conn = Connection::from_socket(stream).map_err(|err| {
        ShellError::WaylandConnection(format!(
            "Failed to initialize Wayland connection from socket {}: {err}",
            socket_path.display()
        ))
    })?;

    Ok((conn, socket_path))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolve_explicit_socket() {
        let path = resolve_socket_path(Some("/tmp/custom-wayland.sock")).unwrap();
        assert_eq!(path, PathBuf::from("/tmp/custom-wayland.sock"));
    }
}
