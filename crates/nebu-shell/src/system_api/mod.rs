//! System API abstraction layer for NebuShell (per NEBU-SPEC-INT-008).
#![deny(unsafe_code)]

pub mod mock;
pub mod traits;

pub use mock::*;
pub use traits::*;
