//! High-level abstraction for wlr-layer-shell surfaces.
#![deny(unsafe_code)]

use crate::error::ShellResult;
use crate::wayland::protocols::ShellWaylandState;
use crate::wayland::shm::ShmBuffer;
use wayland_client::protocol::wl_surface::WlSurface;
use wayland_client::QueueHandle;
use wayland_protocols_wlr::layer_shell::v1::client::{
    zwlr_layer_shell_v1::{Layer, ZwlrLayerShellV1},
    zwlr_layer_surface_v1::{Anchor, KeyboardInteractivity, ZwlrLayerSurfaceV1},
};

/// Layer surface configuration parameters.
#[derive(Debug, Clone)]
pub struct LayerSurfaceConfig {
    pub surface_id: u32,
    pub namespace: String,
    pub layer: Layer,
    pub anchor: Anchor,
    pub width: u32,
    pub height: u32,
    pub exclusive_zone: i32,
    pub margin: (i32, i32, i32, i32),
    pub keyboard_interactivity: KeyboardInteractivity,
}

/// Managed layer shell surface.
#[derive(Debug)]
pub struct ManagedLayerSurface {
    pub surface: WlSurface,
    pub layer_surface: ZwlrLayerSurfaceV1,
    pub config: LayerSurfaceConfig,
    pub configured: bool,
    pub configured_width: u32,
    pub configured_height: u32,
    pub last_serial: u32,
}

impl ManagedLayerSurface {
    /// Create a new layer surface via ZwlrLayerShellV1.
    pub fn new(
        layer_shell: &ZwlrLayerShellV1,
        surface: WlSurface,
        config: LayerSurfaceConfig,
        qh: &QueueHandle<ShellWaylandState>,
    ) -> ShellResult<Self> {
        let surface_id = config.surface_id;
        let layer_surface = layer_shell.get_layer_surface(
            &surface,
            None, // Default to primary output
            config.layer,
            config.namespace.clone(),
            qh,
            surface_id,
        );

        layer_surface.set_size(config.width, config.height);
        layer_surface.set_anchor(config.anchor);
        layer_surface.set_exclusive_zone(config.exclusive_zone);
        layer_surface.set_margin(
            config.margin.0,
            config.margin.1,
            config.margin.2,
            config.margin.3,
        );
        layer_surface.set_keyboard_interactivity(config.keyboard_interactivity);

        // Initial commit to request configure event from compositor
        surface.commit();

        Ok(Self {
            surface,
            layer_surface,
            config,
            configured: false,
            configured_width: 0,
            configured_height: 0,
            last_serial: 0,
        })
    }

    /// Handle configure event received from the compositor.
    pub fn handle_configure(&mut self, serial: u32, width: u32, height: u32) {
        self.last_serial = serial;
        self.configured = true;
        self.configured_width = if width > 0 { width } else { self.config.width };
        self.configured_height = if height > 0 {
            height
        } else {
            self.config.height
        };

        self.layer_surface.ack_configure(serial);
    }

    /// Attach a SHM buffer, damage full rect, and commit.
    pub fn attach_and_commit(&self, shm_buffer: &ShmBuffer) {
        self.surface.attach(Some(&shm_buffer.buffer), 0, 0);
        self.surface.damage_buffer(
            0,
            0,
            self.configured_width as i32,
            self.configured_height as i32,
        );
        self.surface.commit();
    }

    /// Destroy surface resources.
    pub fn destroy(self) {
        self.layer_surface.destroy();
        self.surface.destroy();
    }
}
