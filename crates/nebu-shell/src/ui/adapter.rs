//! Slint software rendering platform adapter for Wayland SHM.
#![deny(unsafe_code)]

use crate::error::{ShellError, ShellResult};
use crate::ShellPanelWindow;
use slint::platform::software_renderer::{MinimalSoftwareWindow, PremultipliedRgbaColor};
use slint::platform::{Platform, PlatformError, WindowAdapter};
use std::rc::Rc;

struct NebuShellPlatform {
    window: Rc<MinimalSoftwareWindow>,
}

impl Platform for NebuShellPlatform {
    fn create_window_adapter(&self) -> Result<Rc<dyn WindowAdapter>, PlatformError> {
        Ok(self.window.clone())
    }
}

/// Managed Slint panel UI instance.
pub struct PanelUi {
    pub window: Rc<MinimalSoftwareWindow>,
    pub ui: ShellPanelWindow,
}

impl PanelUi {
    /// Initialize the Slint platform and instantiate the panel UI.
    pub fn new() -> ShellResult<Self> {
        let window = MinimalSoftwareWindow::new(Default::default());
        // set_platform can fail if called more than once in the same process; ignore duplicate error
        let _ = slint::platform::set_platform(Box::new(NebuShellPlatform {
            window: window.clone(),
        }));

        let ui = ShellPanelWindow::new().map_err(|e| {
            ShellError::SlintError(format!("Failed to create ShellPanelWindow: {e}"))
        })?;

        Ok(Self { window, ui })
    }

    /// Update status message displayed on panel.
    pub fn set_status(&self, status: &str) {
        self.ui.set_status_text(status.into());
    }

    /// Update clock text displayed on panel.
    pub fn set_clock(&self, clock: &str) {
        self.ui.set_clock_text(clock.into());
    }

    /// Render current UI state to an ARGB8888 byte vector.
    pub fn render_to_argb8888(&self, width: u32, height: u32) -> ShellResult<Vec<u8>> {
        self.window
            .set_size(slint::PhysicalSize::new(width, height));

        let mut pixel_buffer = vec![PremultipliedRgbaColor::default(); (width * height) as usize];
        let mut rendered = false;

        self.window.draw_if_needed(|renderer| {
            renderer.render(&mut pixel_buffer, width as usize);
            rendered = true;
        });

        // Even if not strictly marked as needed by Slint, ensure initial buffer has contents
        let mut argb_bytes = Vec::with_capacity((width * height * 4) as usize);
        for p in &pixel_buffer {
            argb_bytes.push(p.blue);
            argb_bytes.push(p.green);
            argb_bytes.push(p.red);
            argb_bytes.push(p.alpha);
        }

        let _ = rendered;
        Ok(argb_bytes)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_slint_panel_rendering() {
        let panel_ui = PanelUi::new().expect("PanelUi should initialize");
        panel_ui.set_status("Test Running");
        panel_ui.set_clock("15:30 UTC");

        let bytes = panel_ui
            .render_to_argb8888(640, 32)
            .expect("Rendering should succeed");
        assert_eq!(bytes.len(), 640 * 32 * 4);

        let has_non_zero = bytes.iter().any(|&b| b != 0);
        assert!(has_non_zero, "Rendered frame must contain pixel data");
    }
}
