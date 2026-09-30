//! Desktop panel surface management and Slint integration.
#![deny(unsafe_code)]

use crate::config::{PanelConfig, PanelPosition};
use crate::error::ShellResult;
use crate::ui::PanelUi;
use crate::wayland::{
    layer_surface::{LayerSurfaceConfig, ManagedLayerSurface},
    protocols::{ShellWaylandState, SURFACE_ID_PANEL},
    shm::ShmBuffer,
};
use wayland_client::protocol::{wl_compositor::WlCompositor, wl_shm::WlShm};
use wayland_client::QueueHandle;
use wayland_protocols_wlr::layer_shell::v1::client::{
    zwlr_layer_shell_v1::{Layer, ZwlrLayerShellV1},
    zwlr_layer_surface_v1::{Anchor, KeyboardInteractivity},
};

/// Managed desktop top/bottom panel layer surface.
pub struct PanelSurface {
    pub managed: ManagedLayerSurface,
    pub config: PanelConfig,
    pub ui: PanelUi,
    pub current_buffer: Option<ShmBuffer>,
}

impl PanelSurface {
    /// Instantiate a panel layer surface anchored to the configured screen edge.
    pub fn new(
        compositor: &WlCompositor,
        layer_shell: &ZwlrLayerShellV1,
        qh: &QueueHandle<ShellWaylandState>,
        config: PanelConfig,
    ) -> ShellResult<Self> {
        let surface = compositor.create_surface(qh, ());

        let anchor = match config.position {
            PanelPosition::Top => Anchor::Top | Anchor::Left | Anchor::Right,
            PanelPosition::Bottom => Anchor::Bottom | Anchor::Left | Anchor::Right,
            PanelPosition::Left => Anchor::Left | Anchor::Top | Anchor::Bottom,
            PanelPosition::Right => Anchor::Right | Anchor::Top | Anchor::Bottom,
        };

        let surface_cfg = LayerSurfaceConfig {
            surface_id: SURFACE_ID_PANEL,
            namespace: "nebu-panel".to_string(),
            layer: Layer::Top,
            anchor,
            width: 0, // Stretches across anchored horizontal/vertical edge
            height: config.height,
            exclusive_zone: config.exclusive_zone,
            margin: (0, 0, 0, 0),
            keyboard_interactivity: KeyboardInteractivity::None,
        };

        let managed = ManagedLayerSurface::new(layer_shell, surface, surface_cfg, qh)?;
        let ui = PanelUi::new()?;

        Ok(Self {
            managed,
            config,
            ui,
            current_buffer: None,
        })
    }

    /// Render Slint UI and commit the updated buffer to the compositor.
    pub fn render_and_commit(
        &mut self,
        shm: &WlShm,
        qh: &QueueHandle<ShellWaylandState>,
        width: u32,
        height: u32,
    ) -> ShellResult<()> {
        let argb_data = self.ui.render_to_argb8888(width, height)?;

        let mut buffer = ShmBuffer::allocate(shm, qh, width, height)?;
        buffer.write_pixels(&argb_data)?;

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
