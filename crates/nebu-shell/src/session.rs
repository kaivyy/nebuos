//! High-level NebuShell session orchestrator.
#![deny(unsafe_code)]

use crate::config::ShellConfig;
use crate::error::{ShellError, ShellResult};
use crate::lifecycle::{ShellLifecycle, ShellState};
use crate::surfaces::{BackgroundSurface, PanelSurface};
use crate::wayland::{
    connect_to_wayland,
    protocols::{ShellWaylandState, SURFACE_ID_BACKGROUND, SURFACE_ID_PANEL},
};
use std::path::PathBuf;
use wayland_client::{Connection, EventQueue};

/// Summary of automated P2.1 verification probe.
#[derive(Debug, Clone)]
pub struct ProbeReport {
    pub socket_path: PathBuf,
    pub globals_verified: bool,
    pub background_configured: bool,
    pub panel_configured: bool,
    pub rendered_frames: u32,
    pub lifecycle_reached_active: bool,
    pub clean_shutdown: bool,
}

/// Active NebuShell runtime session.
pub struct NebuShellSession {
    pub config: ShellConfig,
    pub lifecycle: ShellLifecycle,
    pub connection: Connection,
    pub socket_path: PathBuf,
    pub event_queue: EventQueue<ShellWaylandState>,
    pub wayland_state: ShellWaylandState,
    pub background: Option<BackgroundSurface>,
    pub panel: Option<PanelSurface>,
}

impl NebuShellSession {
    /// Initialize and connect to the Wayland compositor.
    pub fn connect(config: ShellConfig) -> ShellResult<Self> {
        let mut lifecycle = ShellLifecycle::new();
        lifecycle.transition_to(ShellState::Connecting)?;

        let (connection, socket_path) = connect_to_wayland(config.socket_override.as_deref())?;
        let mut event_queue = connection.new_event_queue();
        let qh = event_queue.handle();

        let mut wayland_state = ShellWaylandState::new();
        let display = connection.display();
        let registry = display.get_registry(&qh, ());
        wayland_state.registry = Some(registry);

        // Initial roundtrip to populate registry and discover globals
        event_queue.roundtrip(&mut wayland_state).map_err(|e| {
            ShellError::DispatchError(format!("Initial registry roundtrip failed: {e}"))
        })?;

        // Validate mandatory globals (wl_compositor, wl_shm, zwlr_layer_shell_v1)
        wayland_state.verify_required_globals()?;

        lifecycle.transition_to(ShellState::Connected)?;

        Ok(Self {
            config,
            lifecycle,
            connection,
            socket_path,
            event_queue,
            wayland_state,
            background: None,
            panel: None,
        })
    }

    /// Instantiate background and panel layer surfaces.
    pub fn setup_surfaces(&mut self) -> ShellResult<()> {
        let comp = self
            .wayland_state
            .compositor
            .as_ref()
            .ok_or_else(|| ShellError::ProtocolMissing("wl_compositor".into()))?;
        let layer_shell = self
            .wayland_state
            .layer_shell
            .as_ref()
            .ok_or_else(|| ShellError::ProtocolMissing("zwlr_layer_shell_v1".into()))?;
        let qh = self.event_queue.handle();

        let bg = BackgroundSurface::new(comp, layer_shell, &qh, self.config.background.clone())?;
        let pnl = PanelSurface::new(comp, layer_shell, &qh, self.config.panel.clone())?;

        self.background = Some(bg);
        self.panel = Some(pnl);

        Ok(())
    }

    /// Dispatch events and process configure responses from compositor.
    pub fn wait_for_configures(&mut self, max_rounds: usize) -> ShellResult<()> {
        for _ in 0..max_rounds {
            self.event_queue
                .roundtrip(&mut self.wayland_state)
                .map_err(|e| {
                    ShellError::DispatchError(format!(
                        "Roundtrip during configure wait failed: {e}"
                    ))
                })?;

            let has_bg = self
                .wayland_state
                .configures
                .contains_key(&SURFACE_ID_BACKGROUND);
            let has_panel = self
                .wayland_state
                .configures
                .contains_key(&SURFACE_ID_PANEL);

            if has_bg && has_panel {
                // Update managed surface tracking
                if let (Some(bg_conf), Some(bg)) = (
                    self.wayland_state.configures.get(&SURFACE_ID_BACKGROUND),
                    self.background.as_mut(),
                ) {
                    bg.managed
                        .handle_configure(bg_conf.serial, bg_conf.width, bg_conf.height);
                }

                if let (Some(pnl_conf), Some(pnl)) = (
                    self.wayland_state.configures.get(&SURFACE_ID_PANEL),
                    self.panel.as_mut(),
                ) {
                    pnl.managed
                        .handle_configure(pnl_conf.serial, pnl_conf.width, pnl_conf.height);
                }

                self.lifecycle
                    .transition_to(ShellState::SurfacesConfigured)?;
                return Ok(());
            }
        }

        Err(ShellError::SurfaceError(
            "Timed out waiting for compositor configure events on layer surfaces".into(),
        ))
    }

    /// Render initial frame for all configured layer surfaces.
    pub fn render_frame(&mut self) -> ShellResult<()> {
        let shm = self
            .wayland_state
            .shm
            .as_ref()
            .ok_or_else(|| ShellError::ProtocolMissing("wl_shm".into()))?;
        let qh = self.event_queue.handle();

        if let Some(bg) = self.background.as_mut() {
            let width = if bg.managed.configured_width > 0 {
                bg.managed.configured_width
            } else {
                1920
            };
            let height = if bg.managed.configured_height > 0 {
                bg.managed.configured_height
            } else {
                1080
            };
            bg.render_and_commit(shm, &qh, width, height)?;
        }

        if let Some(pnl) = self.panel.as_mut() {
            let width = if pnl.managed.configured_width > 0 {
                pnl.managed.configured_width
            } else {
                1920
            };
            let height = pnl.config.height;
            pnl.render_and_commit(shm, &qh, width, height)?;
        }

        // Roundtrip to flush buffers and ensure compositor receives them
        self.event_queue
            .roundtrip(&mut self.wayland_state)
            .map_err(|e| {
                ShellError::DispatchError(format!("Roundtrip during frame commit failed: {e}"))
            })?;

        if self.lifecycle.current() == ShellState::SurfacesConfigured {
            self.lifecycle.transition_to(ShellState::Active)?;
        }

        Ok(())
    }

    /// Execute the complete automated Milestone P2.1 verification probe.
    pub fn run_verification_probe(mut self) -> ShellResult<ProbeReport> {
        self.setup_surfaces()?;
        self.wait_for_configures(5)?;
        self.render_frame()?;

        let report = ProbeReport {
            socket_path: self.socket_path.clone(),
            globals_verified: true,
            background_configured: self
                .background
                .as_ref()
                .is_some_and(|b| b.managed.configured),
            panel_configured: self.panel.as_ref().is_some_and(|p| p.managed.configured),
            rendered_frames: 1,
            lifecycle_reached_active: self.lifecycle.current() == ShellState::Active,
            clean_shutdown: false,
        };

        // Gracefully teardown
        self.lifecycle.transition_to(ShellState::ShuttingDown)?;

        if let Some(bg) = self.background.take() {
            bg.destroy();
        }
        if let Some(pnl) = self.panel.take() {
            pnl.destroy();
        }

        let _ = self.event_queue.roundtrip(&mut self.wayland_state);
        self.lifecycle.transition_to(ShellState::Terminated)?;

        let mut final_report = report;
        final_report.clean_shutdown = self.lifecycle.current() == ShellState::Terminated;

        Ok(final_report)
    }
}
