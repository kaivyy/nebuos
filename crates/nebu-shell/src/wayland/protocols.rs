//! Wayland registry, protocol dispatch, and global binding manager.
#![deny(unsafe_code)]

use crate::error::{ShellError, ShellResult};
use std::collections::HashMap;
use wayland_client::protocol::{
    wl_buffer::WlBuffer,
    wl_compositor::WlCompositor,
    wl_registry::{self, WlRegistry},
    wl_shm::{Format as ShmFormat, WlShm},
    wl_shm_pool::WlShmPool,
    wl_surface::WlSurface,
};
use wayland_client::{Connection, Dispatch, Proxy, QueueHandle};
use wayland_protocols::xdg::shell::client::xdg_wm_base::{self, XdgWmBase};
use wayland_protocols_wlr::layer_shell::v1::client::{
    zwlr_layer_shell_v1::ZwlrLayerShellV1,
    zwlr_layer_surface_v1::{self, ZwlrLayerSurfaceV1},
};

/// Identifiers for layer surfaces.
pub const SURFACE_ID_BACKGROUND: u32 = 1;
pub const SURFACE_ID_PANEL: u32 = 2;

/// Recorded layer surface configure event data.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ConfigureEvent {
    pub serial: u32,
    pub width: u32,
    pub height: u32,
}

/// Discovered protocol globals in Wayland registry.
#[derive(Debug, Default, Clone)]
pub struct DiscoveredGlobals {
    pub compositor_name: Option<u32>,
    pub shm_name: Option<u32>,
    pub xdg_wm_base_name: Option<u32>,
    pub layer_shell_name: Option<u32>,
}

/// Shell Wayland state managed during event dispatch.
#[derive(Debug, Default)]
pub struct ShellWaylandState {
    pub registry: Option<WlRegistry>,
    pub globals: DiscoveredGlobals,
    pub compositor: Option<WlCompositor>,
    pub shm: Option<WlShm>,
    pub xdg_wm_base: Option<XdgWmBase>,
    pub layer_shell: Option<ZwlrLayerShellV1>,
    pub supported_shm_formats: Vec<ShmFormat>,
    pub configures: HashMap<u32, ConfigureEvent>,
    pub closed_surfaces: Vec<u32>,
}

impl ShellWaylandState {
    pub fn new() -> Self {
        Self::default()
    }

    /// Verify all mandatory protocol globals have been discovered.
    pub fn verify_required_globals(&self) -> ShellResult<()> {
        if self.compositor.is_none() {
            return Err(ShellError::ProtocolMissing("wl_compositor".into()));
        }
        if self.shm.is_none() {
            return Err(ShellError::ProtocolMissing("wl_shm".into()));
        }
        if self.layer_shell.is_none() {
            return Err(ShellError::ProtocolMissing("zwlr_layer_shell_v1".into()));
        }
        Ok(())
    }
}

// --- Dispatch Implementations ---

impl Dispatch<WlRegistry, ()> for ShellWaylandState {
    fn event(
        state: &mut Self,
        registry: &WlRegistry,
        event: wl_registry::Event,
        _: &(),
        _: &Connection,
        qh: &QueueHandle<Self>,
    ) {
        if let wl_registry::Event::Global {
            name,
            interface,
            version,
        } = event
        {
            match interface.as_str() {
                "wl_compositor" => {
                    state.globals.compositor_name = Some(name);
                    let bound_version = std::cmp::min(version, 4);
                    let comp = registry.bind::<WlCompositor, _, _>(name, bound_version, qh, ());
                    state.compositor = Some(comp);
                }
                "wl_shm" => {
                    state.globals.shm_name = Some(name);
                    let bound_version = std::cmp::min(version, 1);
                    let shm = registry.bind::<WlShm, _, _>(name, bound_version, qh, ());
                    state.shm = Some(shm);
                }
                "xdg_wm_base" => {
                    state.globals.xdg_wm_base_name = Some(name);
                    let bound_version = std::cmp::min(version, 1);
                    let xdg = registry.bind::<XdgWmBase, _, _>(name, bound_version, qh, ());
                    state.xdg_wm_base = Some(xdg);
                }
                "zwlr_layer_shell_v1" => {
                    state.globals.layer_shell_name = Some(name);
                    let bound_version = std::cmp::min(version, 4);
                    let ls = registry.bind::<ZwlrLayerShellV1, _, _>(name, bound_version, qh, ());
                    state.layer_shell = Some(ls);
                }
                _ => {}
            }
        }
    }
}

impl Dispatch<WlCompositor, ()> for ShellWaylandState {
    fn event(
        _: &mut Self,
        _: &WlCompositor,
        _: <WlCompositor as Proxy>::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
    }
}

impl Dispatch<WlShm, ()> for ShellWaylandState {
    fn event(
        state: &mut Self,
        _: &WlShm,
        event: <WlShm as Proxy>::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
        if let wayland_client::protocol::wl_shm::Event::Format {
            format: wayland_client::WEnum::Value(fmt),
        } = event
        {
            state.supported_shm_formats.push(fmt);
        }
    }
}

impl Dispatch<WlShmPool, ()> for ShellWaylandState {
    fn event(
        _: &mut Self,
        _: &WlShmPool,
        _: <WlShmPool as Proxy>::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
    }
}

impl Dispatch<WlBuffer, ()> for ShellWaylandState {
    fn event(
        _: &mut Self,
        _: &WlBuffer,
        _: <WlBuffer as Proxy>::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
    }
}

impl Dispatch<WlSurface, ()> for ShellWaylandState {
    fn event(
        _: &mut Self,
        _: &WlSurface,
        _: <WlSurface as Proxy>::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
    }
}

impl Dispatch<XdgWmBase, ()> for ShellWaylandState {
    fn event(
        _: &mut Self,
        proxy: &XdgWmBase,
        event: <XdgWmBase as Proxy>::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
        if let xdg_wm_base::Event::Ping { serial } = event {
            proxy.pong(serial);
        }
    }
}

impl Dispatch<ZwlrLayerShellV1, ()> for ShellWaylandState {
    fn event(
        _: &mut Self,
        _: &ZwlrLayerShellV1,
        _: <ZwlrLayerShellV1 as Proxy>::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
    }
}

impl Dispatch<ZwlrLayerSurfaceV1, u32> for ShellWaylandState {
    fn event(
        state: &mut Self,
        proxy: &ZwlrLayerSurfaceV1,
        event: <ZwlrLayerSurfaceV1 as Proxy>::Event,
        surface_id: &u32,
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
        match event {
            zwlr_layer_surface_v1::Event::Configure {
                serial,
                width,
                height,
            } => {
                proxy.ack_configure(serial);
                state.configures.insert(
                    *surface_id,
                    ConfigureEvent {
                        serial,
                        width,
                        height,
                    },
                );
            }
            zwlr_layer_surface_v1::Event::Closed => {
                state.closed_surfaces.push(*surface_id);
            }
            _ => {}
        }
    }
}
