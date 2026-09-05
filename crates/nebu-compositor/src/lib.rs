//! NebuCompositor Core Library — NebuOS Milestone P1
//!
//! Provides the architectural scaffolding and entrypoint for the
//! native Wayland display server built upon Smithay primitives.

#![forbid(unsafe_code)]

pub mod backend;
pub mod input;
pub mod render;
pub mod session;
pub mod state;
pub mod wayland;

use std::fmt;

/// Error type representing initialization or runtime failures in NebuCompositor.
#[derive(Debug, PartialEq, Eq)]
pub enum CompositorError {
    /// Failure during initialization of a specific subsystem.
    InitializationFailed(&'static str),
}

impl fmt::Display for CompositorError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InitializationFailed(subsystem) => {
                write!(
                    f,
                    "compositor initialization failed at subsystem: {subsystem}"
                )
            }
        }
    }
}

impl std::error::Error for CompositorError {}

/// Executes the NebuCompositor entrypoint sequence.
///
/// In Milestone P1.1, this initializes the crate skeleton, validates
/// dependency resolution, reports version and subsystem status, and returns cleanly.
pub fn run() -> Result<(), CompositorError> {
    println!(
        "NebuCompositor v{} (Milestone P1.1 Skeleton)",
        env!("CARGO_PKG_VERSION")
    );
    println!("  Architecture: Wayland display server substrate (Smithay-based)");
    println!("  Status: Workspace initialized, dependency graph resolved");
    println!("  Next Milestone: P1.2 DRM/KMS Proof");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compositor_skeleton_run() {
        assert!(run().is_ok());
    }

    #[test]
    fn test_error_display() {
        let err = CompositorError::InitializationFailed("backend");
        assert_eq!(
            err.to_string(),
            "compositor initialization failed at subsystem: backend"
        );
    }
}
