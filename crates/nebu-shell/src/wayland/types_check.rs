#![allow(unused_imports)]

use wayland_client::protocol::{
    wl_compositor::WlCompositor,
    wl_shm::{WlShm, Format as ShmFormat},
    wl_shm_pool::WlShmPool,
    wl_buffer::WlBuffer,
    wl_surface::WlSurface,
    wl_registry::WlRegistry,
};
use wayland_protocols::xdg::shell::client::xdg_wm_base::XdgWmBase;
use wayland_protocols_wlr::layer_shell::v1::client::{
    zwlr_layer_shell_v1::{ZwlrLayerShellV1, Layer},
    zwlr_layer_surface_v1::{ZwlrLayerSurfaceV1, Anchor},
};

fn verify_types() {
    let _ = Layer::Background;
    let _ = Layer::Top;
    let _ = Anchor::Top;
    let _ = Anchor::Left;
    let _ = Anchor::Right;
    let _ = Anchor::Bottom;
    let _ = ShmFormat::Argb8888;
}
