//! NebuShell Core Architecture & Layer Shell Scaffolding (Milestone P2.1)
#![deny(unsafe_code)]

pub const VERSION: &str = env!("CARGO_PKG_VERSION");

slint::include_modules!();

pub mod config;
pub mod error;
pub mod lifecycle;
pub mod surfaces;
pub mod system_api;
pub mod ui;
pub mod wayland;

pub mod session;
pub use session::*;
