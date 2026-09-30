//! Desktop background surface management.
#![deny(unsafe_code)]

use crate::config::BackgroundConfig;
use crate::error::ShellResult;
use crate::wayland::{
    layer_surface::{LayerSurfaceConfig, ManagedLayerSurface},
    protocols::{ShellWaylandState, SURFACE_ID_BACKGROUND},
    shm::ShmBuffer,
};
use wayland_client::protocol::{wl_compositor::WlCompositor, wl_shm::WlShm};
use wayland_client::QueueHandle;
use wayland_protocols_wlr::layer_shell::v1::client::{
    zwlr_layer_shell_v1::{Layer, ZwlrLayerShellV1},
    zwlr_layer_surface_v1::{Anchor, KeyboardInteractivity},
};

/// Managed desktop background layer surface.
pub struct BackgroundSurface {
    pub managed: ManagedLayerSurface,
    pub config: BackgroundConfig,
    pub current_buffer: Option<ShmBuffer>,
}

impl BackgroundSurface {
    /// Instantiate a background layer surface spanning the entire display.
    pub fn new(
        compositor: &WlCompositor,
        layer_shell: &ZwlrLayerShellV1,
        qh: &QueueHandle<ShellWaylandState>,
        config: BackgroundConfig,
    ) -> ShellResult<Self> {
        let surface = compositor.create_surface(qh, ());
        let surface_cfg = LayerSurfaceConfig {
            surface_id: SURFACE_ID_BACKGROUND,
            namespace: "nebu-background".to_string(),
            layer: Layer::Background,
            anchor: Anchor::Top | Anchor::Bottom | Anchor::Left | Anchor::Right,
            width: 0,  // Requests output width
            height: 0, // Requests output height
            exclusive_zone: 0,
            margin: (0, 0, 0, 0),
            keyboard_interactivity: KeyboardInteractivity::None,
        };

        let managed = ManagedLayerSurface::new(layer_shell, surface, surface_cfg, qh)?;

        Ok(Self {
            managed,
            config,
            current_buffer: None,
        })
    }

    /// Render and commit the background surface with configured color.
    pub fn render_and_commit(
        &mut self,
        shm: &WlShm,
        qh: &QueueHandle<ShellWaylandState>,
        width: u32,
        height: u32,
    ) -> ShellResult<()> {
        let (r, g, b, a) = self.config.color_rgba;
        let mut pixels = Vec::with_capacity((width * height * 4) as usize);

        // Fill with ARGB8888 bytes (B, G, R, A in little-endian byte ordering)
        for _ in 0..(width * height) {
            pixels.push(b);
            pixels.push(g);
            pixels.push(r);
            pixels.push(a);
        }

        let mut buffer = ShmBuffer::allocate(shm, qh, width, height)?;
        buffer.write_pixels(&pixels)?;

        self.managed.attach_and_commit(&buffer);

        if let Some(old) = self.current_buffer.take() {
            old.destroy();
        }
        self.current_buffer = Some(buffer);

        Ok(())
    }

    /// Destroy resources.
    pub fn destroy(mut self) {
        if let Some(buf) = self.current_buffer.take() {
            buf.destroy();
        }
        self.managed.destroy();
    }
}
