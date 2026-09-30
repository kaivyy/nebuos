//! NebuShell configuration structures and desktop paradigms.
#![deny(unsafe_code)]

use crate::error::{ShellError, ShellResult};
use std::str::FromStr;

/// Desktop paradigm as specified in ADR-0009 and PRD.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum DesktopParadigm {
    /// Traditional desktop: bottom taskbar, start menu, tray.
    Traditional,
    /// Modern desktop: top bar, floating bottom dock.
    #[default]
    Modern,
    /// Minimal desktop: clean status panel, minimal widgets.
    Minimal,
}

impl FromStr for DesktopParadigm {
    type Err = ShellError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "traditional" => Ok(Self::Traditional),
            "modern" => Ok(Self::Modern),
            "minimal" => Ok(Self::Minimal),
            _ => Err(ShellError::ConfigError(format!(
                "Unknown desktop paradigm '{s}'. Expected traditional, modern, or minimal."
            ))),
        }
    }
}

/// Panel anchoring position.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum PanelPosition {
    #[default]
    Top,
    Bottom,
    Left,
    Right,
}

/// Surface geometry and layer shell constraints.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SurfaceGeometry {
    pub width: u32,
    pub height: u32,
    pub exclusive_zone: i32,
    pub margin_top: i32,
    pub margin_right: i32,
    pub margin_bottom: i32,
    pub margin_left: i32,
}

impl Default for SurfaceGeometry {
    fn default() -> Self {
        Self {
            width: 0,
            height: 32,
            exclusive_zone: 32,
            margin_top: 0,
            margin_right: 0,
            margin_bottom: 0,
            margin_left: 0,
        }
    }
}

/// Configuration for desktop background surface.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BackgroundConfig {
    /// Solid background RGBA color (default: #0f172a, slate-900).
    pub color_rgba: (u8, u8, u8, u8),
    /// Optional wallpaper path.
    pub wallpaper_path: Option<String>,
}

impl Default for BackgroundConfig {
    fn default() -> Self {
        Self {
            color_rgba: (15, 23, 42, 255),
            wallpaper_path: None,
        }
    }
}

/// Configuration for desktop panel surface.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PanelConfig {
    pub position: PanelPosition,
    pub height: u32,
    pub exclusive_zone: i32,
    pub title: String,
    pub show_clock: bool,
}

impl Default for PanelConfig {
    fn default() -> Self {
        Self {
            position: PanelPosition::Top,
            height: 32,
            exclusive_zone: 32,
            title: "NebuOS Desktop".to_string(),
            show_clock: true,
        }
    }
}

/// Master configuration for NebuShell.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct ShellConfig {
    pub paradigm: DesktopParadigm,
    pub background: BackgroundConfig,
    pub panel: PanelConfig,
    pub socket_override: Option<String>,
}

impl ShellConfig {
    pub fn validate(&self) -> ShellResult<()> {
        if self.panel.height < 16 || self.panel.height > 120 {
            return Err(ShellError::ConfigError(format!(
                "Panel height {} is out of valid bounds (16-120)",
                self.panel.height
            )));
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_paradigm_parsing() {
        assert_eq!(
            "modern".parse::<DesktopParadigm>().unwrap(),
            DesktopParadigm::Modern
        );
        assert_eq!(
            "traditional".parse::<DesktopParadigm>().unwrap(),
            DesktopParadigm::Traditional
        );
        assert_eq!(
            "minimal".parse::<DesktopParadigm>().unwrap(),
            DesktopParadigm::Minimal
        );
        assert!("invalid".parse::<DesktopParadigm>().is_err());
    }

    #[test]
    fn test_config_validation() {
        let mut cfg = ShellConfig::default();
        assert!(cfg.validate().is_ok());
        cfg.panel.height = 5;
        assert!(cfg.validate().is_err());
    }
}
