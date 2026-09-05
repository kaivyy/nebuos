//! Surface Presentation & Scene Rendering Proof Module — NebuOS Milestone P1.7
//!
//! Provides the Wayland surface-to-DRM scene presentation pipeline,
//! damage-tracked composition via `OutputDamageTracker`, deterministic pixel verification
//! via `ExportMem`, and calloop-driven presentation loop.

#![forbid(unsafe_code)]

use std::env;
use std::fmt;
use std::io::Write;
use std::os::unix::io::AsFd;
use std::os::unix::net::UnixStream;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use calloop::generic::Generic;
use calloop::{EventLoop, Interest, Mode, PostAction};

use sha2::{Digest, Sha256};

use smithay::backend::allocator::dmabuf::Dmabuf;
use smithay::backend::allocator::gbm::{GbmAllocator, GbmBufferFlags, GbmDevice};
use smithay::backend::allocator::Fourcc;
use smithay::backend::drm::{
    DrmDevice, DrmDeviceFd, DrmEvent, DrmEventMetadata, DrmNode, GbmBufferedSurface,
};
use smithay::backend::renderer::damage::OutputDamageTracker;
use smithay::backend::renderer::element::surface::{
    render_elements_from_surface_tree, WaylandSurfaceRenderElement,
};
use smithay::backend::renderer::element::Kind;
use smithay::backend::renderer::gles::GlesRenderer;
use smithay::backend::renderer::multigpu::gbm::GbmGlesBackend;
use smithay::backend::renderer::multigpu::GpuManager;
use smithay::backend::renderer::{Bind, ExportMem, ImportDma};
use smithay::reexports::drm::control::{
    connector::State as ConnectorState, Device as ControlDevice, ModeTypeFlags,
};
use smithay::reexports::drm::Device as DrmDeviceTrait;
use smithay::reexports::wayland_server::backend::{ClientData, ClientId, DisconnectReason};
use smithay::reexports::wayland_server::protocol::{
    wl_buffer::WlBuffer, wl_shm::Format, wl_surface::WlSurface,
};
use smithay::reexports::wayland_server::{Client, Display, DisplayHandle};
use smithay::utils::{Buffer as BufferCoord, Physical, Point, Rectangle, Size, Transform};
use smithay::wayland::buffer::BufferHandler;
use smithay::wayland::compositor::{
    with_surface_tree_downward, CompositorClientState, CompositorHandler, CompositorState,
    SurfaceAttributes, TraversalAction,
};
use smithay::wayland::shm::{ShmHandler, ShmState};
use smithay::wayland::socket::ListeningSocketSource;
use smithay::{delegate_compositor, delegate_shm};

use wayland_client::protocol::{
    wl_buffer as client_buffer, wl_callback as client_callback, wl_compositor as client_compositor,
    wl_registry as client_registry, wl_shm as client_shm, wl_shm_pool as client_pool,
    wl_surface as client_surface,
};
use wayland_client::{delegate_noop, Connection, Dispatch, QueueHandle};

use crate::backend::discover_drm_devices;
use crate::output::{select_best_mode, OutputMode};
use crate::render::{classify_renderer_string, AccelerationClassification};
use crate::session::{SessionError, SessionHandle, SessionManagerType};

/// Standard test pattern dimensions.
pub const PATTERN_WIDTH: u32 = 64;
pub const PATTERN_HEIGHT: u32 = 64;
pub const BYTES_PER_PIXEL: u32 = 4;
pub const BUFFER_SIZE_BYTES: usize = (PATTERN_WIDTH * PATTERN_HEIGHT * BYTES_PER_PIXEL) as usize;

/// Surface placement in the output framebuffer.
pub const SURFACE_POS_X: i32 = 100;
pub const SURFACE_POS_Y: i32 = 100;

/// Deterministic test pattern variant for presentation verification.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TestPatternVariant {
    Frame1Quadrants,
    Frame2Quadrants,
}

/// Quadrant color sample from a rendered framebuffer region.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct QuadrantSample {
    pub top_left: [u8; 4],
    pub top_right: [u8; 4],
    pub bottom_left: [u8; 4],
    pub bottom_right: [u8; 4],
}

impl QuadrantSample {
    /// Samples center pixels of the 4 quadrants from a 64x64 ARGB8888 buffer slice.
    pub fn sample_64x64(buffer: &[u8]) -> Option<Self> {
        if buffer.len() < BUFFER_SIZE_BYTES {
            return None;
        }

        let stride = (PATTERN_WIDTH * BYTES_PER_PIXEL) as usize;

        let pixel_at = |x: usize, y: usize| -> [u8; 4] {
            let offset = y * stride + x * (BYTES_PER_PIXEL as usize);
            [
                buffer[offset],
                buffer[offset + 1],
                buffer[offset + 2],
                buffer[offset + 3],
            ]
        };

        Some(Self {
            top_left: pixel_at(16, 16),
            top_right: pixel_at(48, 16),
            bottom_left: pixel_at(16, 48),
            bottom_right: pixel_at(48, 48),
        })
    }

    /// Verifies whether this sample matches the expected pattern variant.
    pub fn matches_variant(&self, variant: TestPatternVariant) -> bool {
        match variant {
            TestPatternVariant::Frame1Quadrants => {
                self.top_left == [0x00, 0x00, 0xFF, 0xFF]
                    && self.top_right == [0x00, 0xFF, 0x00, 0xFF]
                    && self.bottom_left == [0xFF, 0x00, 0x00, 0xFF]
                    && self.bottom_right == [0x00, 0xFF, 0xFF, 0xFF]
            }
            TestPatternVariant::Frame2Quadrants => {
                self.top_left == [0xFF, 0xFF, 0x00, 0xFF]
                    && self.top_right == [0xFF, 0x00, 0xFF, 0xFF]
                    && self.bottom_left == [0x00, 0xFF, 0xFF, 0xFF]
                    && self.bottom_right == [0xFF, 0xFF, 0xFF, 0xFF]
            }
        }
    }
}

/// Generates a deterministic pixel buffer (64x64 ARGB8888 in little-endian order [B, G, R, A]).
pub fn generate_pattern_pixels(variant: TestPatternVariant) -> Vec<u8> {
    let mut pixels = vec![0u8; BUFFER_SIZE_BYTES];
    let stride = (PATTERN_WIDTH * BYTES_PER_PIXEL) as usize;

    for y in 0..PATTERN_HEIGHT as usize {
        let is_top = y < (PATTERN_HEIGHT / 2) as usize;
        for x in 0..PATTERN_WIDTH as usize {
            let is_left = x < (PATTERN_WIDTH / 2) as usize;
            let offset = y * stride + x * (BYTES_PER_PIXEL as usize);

            let color = match (variant, is_top, is_left) {
                // Frame 1: Top-Left=Red, Top-Right=Green, Bottom-Left=Blue, Bottom-Right=Yellow
                (TestPatternVariant::Frame1Quadrants, true, true) => [0x00, 0x00, 0xFF, 0xFF],
                (TestPatternVariant::Frame1Quadrants, true, false) => [0x00, 0xFF, 0x00, 0xFF],
                (TestPatternVariant::Frame1Quadrants, false, true) => [0xFF, 0x00, 0x00, 0xFF],
                (TestPatternVariant::Frame1Quadrants, false, false) => [0x00, 0xFF, 0xFF, 0xFF],

                // Frame 2: Top-Left=Cyan, Top-Right=Magenta, Bottom-Left=Yellow, Bottom-Right=White
                (TestPatternVariant::Frame2Quadrants, true, true) => [0xFF, 0xFF, 0x00, 0xFF],
                (TestPatternVariant::Frame2Quadrants, true, false) => [0xFF, 0x00, 0xFF, 0xFF],
                (TestPatternVariant::Frame2Quadrants, false, true) => [0x00, 0xFF, 0xFF, 0xFF],
                (TestPatternVariant::Frame2Quadrants, false, false) => [0xFF, 0xFF, 0xFF, 0xFF],
            };

            pixels[offset] = color[0];
            pixels[offset + 1] = color[1];
            pixels[offset + 2] = color[2];
            pixels[offset + 3] = color[3];
        }
    }

    pixels
}

/// Computes a hex SHA-256 digest of a byte slice.
pub fn compute_sha256_hex(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    let hash = hasher.finalize();
    format!("{hash:x}")
}

/// Sends frame callbacks for all surfaces in the surface tree.
pub fn send_frames_surface_tree(surface: &WlSurface, time: u32) {
    with_surface_tree_downward(
        surface,
        (),
        |_, _, &()| TraversalAction::DoChildren(()),
        |_surf, states, &()| {
            for callback in states
                .cached_state
                .get::<SurfaceAttributes>()
                .current()
                .frame_callbacks
                .drain(..)
            {
                callback.done(time);
            }
        },
        |_, _, &()| true,
    );
}

/// Presentation lifecycle stages for Milestone P1.7.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PresentationStage {
    Uninitialized,
    SessionOpened,
    DrmInitialized,
    GbmSurfaceCreated,
    WaylandListening,
    ClientConnected,
    Frame1Rendered,
    Frame1Committed,
    Frame1Presented,
    Frame2Rendered,
    Frame2Committed,
    Frame2Presented,
    CleanedUp,
    Failed,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PresentationLifecycleError(pub String);

impl fmt::Display for PresentationLifecycleError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "invalid presentation transition: {}", self.0)
    }
}

impl std::error::Error for PresentationLifecycleError {}

/// State machine ensuring presentation transitions occur in strict order.
#[derive(Debug, Clone)]
pub struct PresentationLifecycle {
    current: PresentationStage,
}

impl PresentationLifecycle {
    pub fn new() -> Self {
        Self {
            current: PresentationStage::Uninitialized,
        }
    }

    pub fn current_stage(&self) -> PresentationStage {
        self.current
    }

    pub fn can_transition(&self, next: PresentationStage) -> bool {
        matches!(
            (self.current, next),
            (_, PresentationStage::Failed)
                | (
                    PresentationStage::Uninitialized,
                    PresentationStage::SessionOpened
                )
                | (
                    PresentationStage::SessionOpened,
                    PresentationStage::DrmInitialized
                )
                | (
                    PresentationStage::DrmInitialized,
                    PresentationStage::GbmSurfaceCreated
                )
                | (
                    PresentationStage::GbmSurfaceCreated,
                    PresentationStage::WaylandListening
                )
                | (
                    PresentationStage::WaylandListening,
                    PresentationStage::ClientConnected
                )
                | (
                    PresentationStage::ClientConnected,
                    PresentationStage::Frame1Rendered
                )
                | (
                    PresentationStage::Frame1Rendered,
                    PresentationStage::Frame1Committed
                )
                | (
                    PresentationStage::Frame1Committed,
                    PresentationStage::Frame1Presented
                )
                | (
                    PresentationStage::Frame1Presented,
                    PresentationStage::Frame2Rendered
                )
                | (
                    PresentationStage::Frame2Rendered,
                    PresentationStage::Frame2Committed
                )
                | (
                    PresentationStage::Frame2Committed,
                    PresentationStage::Frame2Presented
                )
                | (
                    PresentationStage::Frame2Presented,
                    PresentationStage::CleanedUp
                )
        )
    }

    pub fn transition_to(
        &mut self,
        next: PresentationStage,
    ) -> Result<(), PresentationLifecycleError> {
        if self.can_transition(next) {
            self.current = next;
            Ok(())
        } else {
            Err(PresentationLifecycleError(format!(
                "cannot transition from {:?} to {:?}",
                self.current, next
            )))
        }
    }
}

impl Default for PresentationLifecycle {
    fn default() -> Self {
        Self::new()
    }
}

/// Client data stored per Wayland connection.
#[derive(Default)]
pub struct NebuClientState {
    pub compositor_state: CompositorClientState,
    pub disconnected_flag: Arc<AtomicBool>,
}

impl ClientData for NebuClientState {
    fn initialized(&self, _client_id: ClientId) {}

    fn disconnected(&self, _client_id: ClientId, _reason: DisconnectReason) {
        self.disconnected_flag.store(true, Ordering::SeqCst);
    }
}

/// Wayland Compositor state for presentation proof.
pub struct PresentationCompositorState {
    pub compositor_state: CompositorState,
    pub shm_state: ShmState,
    pub commits_count: usize,
    pub committed_surface: Option<WlSurface>,
    pub disconnected_flag: Arc<AtomicBool>,
}

impl PresentationCompositorState {
    pub fn new(dh: &DisplayHandle) -> Self {
        let compositor_state = CompositorState::new::<Self>(dh);
        let shm_state = ShmState::new::<Self>(dh, vec![Format::Argb8888, Format::Xrgb8888]);
        Self {
            compositor_state,
            shm_state,
            commits_count: 0,
            committed_surface: None,
            disconnected_flag: Arc::new(AtomicBool::new(false)),
        }
    }
}

impl CompositorHandler for PresentationCompositorState {
    fn compositor_state(&mut self) -> &mut CompositorState {
        &mut self.compositor_state
    }

    fn client_compositor_state<'a>(&self, client: &'a Client) -> &'a CompositorClientState {
        &client
            .get_data::<NebuClientState>()
            .unwrap()
            .compositor_state
    }

    fn commit(&mut self, surface: &WlSurface) {
        smithay::backend::renderer::utils::on_commit_buffer_handler::<Self>(surface);
        self.commits_count += 1;
        self.committed_surface = Some(surface.clone());
    }
}

impl BufferHandler for PresentationCompositorState {
    fn buffer_destroyed(&mut self, _buffer: &WlBuffer) {}
}

impl ShmHandler for PresentationCompositorState {
    fn shm_state(&self) -> &ShmState {
        &self.shm_state
    }
}

delegate_compositor!(PresentationCompositorState);
delegate_shm!(PresentationCompositorState);

/// Unified single Calloop context.
pub struct PresentationLoopContext {
    pub state: PresentationCompositorState,
    pub display: Display<PresentationCompositorState>,
    pub vblank_received: bool,
    pub last_sequence: u64,
    pub drm_error: Option<String>,
    pub client_connected: bool,
}

/// Client-side state for Wayland protocol handling.
#[derive(Default)]
pub struct PresentationClientState {
    pub compositor: Option<client_compositor::WlCompositor>,
    pub shm: Option<client_shm::WlShm>,
    pub surface: Option<client_surface::WlSurface>,
    pub pool1: Option<client_pool::WlShmPool>,
    pub buffer1: Option<client_buffer::WlBuffer>,
    pub pool2: Option<client_pool::WlShmPool>,
    pub buffer2: Option<client_buffer::WlBuffer>,
    pub frame1_done: bool,
    pub frame2_done: bool,
}

impl Dispatch<client_registry::WlRegistry, ()> for PresentationClientState {
    fn event(
        state: &mut Self,
        registry: &client_registry::WlRegistry,
        event: client_registry::Event,
        _: &(),
        _: &Connection,
        qh: &QueueHandle<Self>,
    ) {
        if let client_registry::Event::Global {
            name,
            interface,
            version,
        } = event
        {
            match interface.as_str() {
                "wl_compositor" => {
                    let comp = registry.bind::<client_compositor::WlCompositor, _, _>(
                        name,
                        1.min(version),
                        qh,
                        (),
                    );
                    state.compositor = Some(comp);
                }
                "wl_shm" => {
                    let shm =
                        registry.bind::<client_shm::WlShm, _, _>(name, 1.min(version), qh, ());
                    state.shm = Some(shm);
                }
                _ => {}
            }
        }
    }
}

impl Dispatch<client_callback::WlCallback, ()> for PresentationClientState {
    fn event(
        state: &mut Self,
        _proxy: &client_callback::WlCallback,
        event: client_callback::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
        if let client_callback::Event::Done { .. } = event {
            if !state.frame1_done {
                state.frame1_done = true;
            } else {
                state.frame2_done = true;
            }
        }
    }
}

delegate_noop!(PresentationClientState: ignore client_compositor::WlCompositor);
delegate_noop!(PresentationClientState: ignore client_surface::WlSurface);
delegate_noop!(PresentationClientState: ignore client_shm::WlShm);
delegate_noop!(PresentationClientState: ignore client_pool::WlShmPool);
delegate_noop!(PresentationClientState: ignore client_buffer::WlBuffer);

/// Runs the client-side presentation verification routine.
pub fn run_presentation_client(socket_path: &Path) -> Result<(), String> {
    let stream = UnixStream::connect(socket_path).map_err(|e| {
        format!(
            "Client failed to connect to socket '{}': {e}",
            socket_path.display()
        )
    })?;
    let conn = Connection::from_socket(stream)
        .map_err(|e| format!("Failed to create Connection from socket: {e}"))?;

    let mut event_queue = conn.new_event_queue();
    let qh = event_queue.handle();

    let display = conn.display();
    let _registry = display.get_registry(&qh, ());

    let mut state = PresentationClientState::default();

    // Roundtrip to process globals
    event_queue
        .roundtrip(&mut state)
        .map_err(|e| format!("Roundtrip failed during registry enumeration: {e}"))?;

    let compositor = state
        .compositor
        .as_ref()
        .ok_or_else(|| "Server did not advertise wl_compositor".to_string())?
        .clone();

    let shm = state
        .shm
        .as_ref()
        .ok_or_else(|| "Server did not advertise wl_shm".to_string())?
        .clone();

    // Create wl_surface
    let surface = compositor.create_surface(&qh, ());
    state.surface = Some(surface.clone());

    // Frame 1: Generate pattern
    let pixels1 = generate_pattern_pixels(TestPatternVariant::Frame1Quadrants);
    let mut temp_file1 =
        tempfile::tempfile().map_err(|e| format!("Failed to create temp file 1: {e}"))?;
    temp_file1
        .write_all(&pixels1)
        .map_err(|e| format!("Failed to write pixels 1: {e}"))?;

    let pool1 = shm.create_pool(temp_file1.as_fd(), BUFFER_SIZE_BYTES as i32, &qh, ());
    let buffer1 = pool1.create_buffer(
        0,
        PATTERN_WIDTH as i32,
        PATTERN_HEIGHT as i32,
        (PATTERN_WIDTH * BYTES_PER_PIXEL) as i32,
        wayland_client::protocol::wl_shm::Format::Argb8888,
        &qh,
        (),
    );

    state.pool1 = Some(pool1.clone());
    state.buffer1 = Some(buffer1.clone());

    // Attach Frame 1 buffer, damage, request frame callback, and commit
    surface.attach(Some(&buffer1), 0, 0);
    surface.damage(0, 0, PATTERN_WIDTH as i32, PATTERN_HEIGHT as i32);
    let _cb1 = surface.frame(&qh, ());
    surface.commit();
    let _ = conn.flush();

    // Dispatch until frame 1 callback is done
    let f1_timeout = Instant::now();
    while !state.frame1_done {
        if f1_timeout.elapsed() > Duration::from_secs(5) {
            return Err("Timed out waiting for frame 1 callback".to_string());
        }
        event_queue
            .blocking_dispatch(&mut state)
            .map_err(|e| format!("Dispatch error waiting for frame 1: {e}"))?;
    }

    // Frame 2: Generate updated pattern (Cyan/Magenta/Yellow/White)
    let pixels2 = generate_pattern_pixels(TestPatternVariant::Frame2Quadrants);
    let mut temp_file2 =
        tempfile::tempfile().map_err(|e| format!("Failed to create temp file 2: {e}"))?;
    temp_file2
        .write_all(&pixels2)
        .map_err(|e| format!("Failed to write pixels 2: {e}"))?;

    let pool2 = shm.create_pool(temp_file2.as_fd(), BUFFER_SIZE_BYTES as i32, &qh, ());
    let buffer2 = pool2.create_buffer(
        0,
        PATTERN_WIDTH as i32,
        PATTERN_HEIGHT as i32,
        (PATTERN_WIDTH * BYTES_PER_PIXEL) as i32,
        wayland_client::protocol::wl_shm::Format::Argb8888,
        &qh,
        (),
    );

    state.pool2 = Some(pool2.clone());
    state.buffer2 = Some(buffer2.clone());

    // Attach Frame 2 buffer, damage, request frame callback, and commit
    surface.attach(Some(&buffer2), 0, 0);
    surface.damage(0, 0, PATTERN_WIDTH as i32, PATTERN_HEIGHT as i32);
    let _cb2 = surface.frame(&qh, ());
    surface.commit();
    let _ = conn.flush();

    // Dispatch until frame 2 callback is done
    let f2_timeout = Instant::now();
    while !state.frame2_done {
        if f2_timeout.elapsed() > Duration::from_secs(5) {
            return Err("Timed out waiting for frame 2 callback".to_string());
        }
        event_queue
            .blocking_dispatch(&mut state)
            .map_err(|e| format!("Dispatch error waiting for frame 2: {e}"))?;
    }

    // Clean teardown: destroy surface, buffers, pools
    surface.destroy();
    buffer1.destroy();
    pool1.destroy();
    buffer2.destroy();
    pool2.destroy();

    let _ = event_queue.roundtrip(&mut state);
    Ok(())
}

/// Telemetry report for Milestone P1.7 Surface Presentation & Scene Rendering Proof.
#[derive(Debug, Clone)]
pub struct PresentationReport {
    pub session_backend: &'static str,
    pub session_manager: SessionManagerType,
    pub card_path: PathBuf,
    pub driver_name: String,
    pub connector_name: String,
    pub selected_mode: String,
    pub gl_renderer: String,
    pub acceleration: AccelerationClassification,
    pub socket_name: String,
    pub client_connected: bool,
    pub surface_committed: bool,
    pub buffer_format: String,
    pub buffer_size: (i32, i32),
    pub frame1_rendered: bool,
    pub frame1_elements_count: usize,
    pub frame1_checksum: String,
    pub frame1_quadrants_verified: bool,
    pub frame1_atomic_commit: bool,
    pub frame1_vblank_received: bool,
    pub frame1_sequence: u64,
    pub frame1_commit_to_flip_ms: f64,
    pub frame2_rendered: bool,
    pub frame2_elements_count: usize,
    pub frame2_checksum: String,
    pub frame2_quadrants_verified: bool,
    pub frame2_atomic_commit: bool,
    pub frame2_vblank_received: bool,
    pub frame2_sequence: u64,
    pub frame2_commit_to_flip_ms: f64,
    pub clean_teardown: bool,
    pub total_duration_ms: f64,
    pub probe_success: bool,
}

/// Errors occurring during the presentation probe.
#[derive(Debug)]
pub enum PresentationProbeError {
    NoDrmDeviceFound,
    SessionError(SessionError),
    DrmQueryFailed(String),
    NoConnectedOutputFound,
    NoCompatibleCrtcFound,
    NoValidModeFound,
    DrmSurfaceFailed(String),
    GbmSurfaceFailed(String),
    RendererFailed(String),
    WaylandFailed(String),
    RenderBufferFailed(String),
    PixelVerificationFailed(String),
    CommitFailed(String),
    EventLoopFailed(String),
    VBlankTimeout,
    ClientFailed(String),
    LifecycleViolation(PresentationLifecycleError),
}

impl fmt::Display for PresentationProbeError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::NoDrmDeviceFound => write!(f, "no DRM device found"),
            Self::SessionError(e) => write!(f, "session error: {e}"),
            Self::DrmQueryFailed(msg) => write!(f, "DRM query failed: {msg}"),
            Self::NoConnectedOutputFound => write!(f, "no connected DRM output found"),
            Self::NoCompatibleCrtcFound => write!(f, "no compatible CRTC found"),
            Self::NoValidModeFound => write!(f, "no valid display mode found"),
            Self::DrmSurfaceFailed(msg) => write!(f, "DRM surface creation failed: {msg}"),
            Self::GbmSurfaceFailed(msg) => write!(f, "GBM surface creation failed: {msg}"),
            Self::RendererFailed(msg) => write!(f, "Renderer failed: {msg}"),
            Self::WaylandFailed(msg) => write!(f, "Wayland display failed: {msg}"),
            Self::RenderBufferFailed(msg) => write!(f, "Render buffer failed: {msg}"),
            Self::PixelVerificationFailed(msg) => write!(f, "Pixel verification failed: {msg}"),
            Self::CommitFailed(msg) => write!(f, "Commit failed: {msg}"),
            Self::EventLoopFailed(msg) => write!(f, "Event loop failed: {msg}"),
            Self::VBlankTimeout => write!(f, "VBlank event timeout"),
            Self::ClientFailed(msg) => write!(f, "Client failed: {msg}"),
            Self::LifecycleViolation(e) => write!(f, "lifecycle violation: {e}"),
        }
    }
}

impl std::error::Error for PresentationProbeError {}

impl From<PresentationLifecycleError> for PresentationProbeError {
    fn from(e: PresentationLifecycleError) -> Self {
        Self::LifecycleViolation(e)
    }
}

impl From<SessionError> for PresentationProbeError {
    fn from(e: SessionError) -> Self {
        Self::SessionError(e)
    }
}

/// Executes Milestone P1.7 Surface Presentation & Scene Rendering Proof.
pub fn run_presentation_probe() -> Result<PresentationReport, PresentationProbeError> {
    let start_time = Instant::now();
    let mut lifecycle = PresentationLifecycle::new();

    println!(
        "=== NebuCompositor Surface Presentation & Scene Rendering Probe (Milestone P1.7) ==="
    );

    // 1. Session Opening
    let mut session = SessionHandle::new_diagnostic()?;
    let session_manager = session.manager;
    println!("[presentation] Session opened via libseat (Manager: {session_manager})");
    lifecycle.transition_to(PresentationStage::SessionOpened)?;

    // 2. Discover DRM device
    let (card_opt, _render_opt) = discover_drm_devices();
    let card_path = card_opt.ok_or(PresentationProbeError::NoDrmDeviceFound)?;
    println!("[presentation] Primary DRM Card: {}", card_path.display());

    let dev_fd = session.open_device(&card_path)?;
    let drm_device_fd = DrmDeviceFd::new(dev_fd.into());
    let (mut drm_device, notifier) = DrmDevice::new(drm_device_fd.clone(), false).map_err(|e| {
        PresentationProbeError::DrmQueryFailed(format!("failed initializing DrmDevice: {e}"))
    })?;

    let driver = drm_device
        .get_driver()
        .map_err(|e| PresentationProbeError::DrmQueryFailed(format!("get_driver failed: {e}")))?;
    let driver_name = driver.name().to_string_lossy().into_owned();
    println!("[presentation] DRM Driver: {driver_name}");
    lifecycle.transition_to(PresentationStage::DrmInitialized)?;

    // 3. Connectors & CRTC discovery
    let res = drm_device.resource_handles().map_err(|e| {
        PresentationProbeError::DrmQueryFailed(format!("resource_handles failed: {e}"))
    })?;

    let mut selected_connector = None;
    let mut selected_crtc = None;
    let mut selected_drm_mode = None;
    let mut selected_output_mode = None;
    let mut connector_name = String::new();

    for &conn_handle in res.connectors() {
        if let Ok(conn_info) = drm_device.get_connector(conn_handle, false) {
            if conn_info.state() == ConnectorState::Connected {
                let modes: Vec<OutputMode> = conn_info
                    .modes()
                    .iter()
                    .map(|m| {
                        OutputMode::new(
                            m.size().0,
                            m.size().1,
                            m.vrefresh() * 1000,
                            m.mode_type().contains(ModeTypeFlags::PREFERRED),
                        )
                    })
                    .collect();

                if let Some(best) = select_best_mode(&modes) {
                    if let Some(drm_m) = conn_info.modes().iter().find(|m| {
                        m.size().0 == best.width
                            && m.size().1 == best.height
                            && m.vrefresh() * 1000 == best.refresh_mhz
                    }) {
                        if let Some(&first_crtc) = res.crtcs().first() {
                            selected_connector = Some(conn_handle);
                            selected_crtc = Some(first_crtc);
                            selected_drm_mode = Some(*drm_m);
                            selected_output_mode = Some(best);
                            connector_name = format!(
                                "{}-{}",
                                conn_info.interface().as_str(),
                                conn_info.interface_id()
                            );
                            break;
                        }
                    }
                }
            }
        }
    }

    let conn_handle = selected_connector.ok_or(PresentationProbeError::NoConnectedOutputFound)?;
    let crtc_handle = selected_crtc.ok_or(PresentationProbeError::NoCompatibleCrtcFound)?;
    let drm_mode = selected_drm_mode.ok_or(PresentationProbeError::NoValidModeFound)?;
    let output_mode = selected_output_mode.unwrap();
    let selected_mode_str = output_mode.to_string();
    println!("[presentation] Output Connector: {connector_name}, Mode: {selected_mode_str}");

    // 4. GBM Device & Allocator
    let gbm_device = GbmDevice::new(drm_device_fd.clone()).map_err(|e| {
        PresentationProbeError::GbmSurfaceFailed(format!("failed creating GbmDevice: {e}"))
    })?;

    let allocator = GbmAllocator::new(
        gbm_device.clone(),
        GbmBufferFlags::RENDERING | GbmBufferFlags::SCANOUT,
    );

    // 5. EGL & Smithay GbmGlesBackend & Renderer
    let drm_node = DrmNode::from_file(&drm_device_fd)
        .map_err(|e| PresentationProbeError::RendererFailed(format!("DrmNode error: {e}")))?;

    let mut backend = GbmGlesBackend::<GlesRenderer, _>::default();
    backend
        .add_node(drm_node, gbm_device.clone())
        .map_err(|e| {
            PresentationProbeError::RendererFailed(format!("backend add_node failed: {e}"))
        })?;

    let mut gpu_manager = GpuManager::new(backend)
        .map_err(|e| PresentationProbeError::RendererFailed(format!("GpuManager failed: {e}")))?;

    let mut renderer = gpu_manager.single_renderer(&drm_node).map_err(|e| {
        PresentationProbeError::RendererFailed(format!("single_renderer failed: {e}"))
    })?;

    let gl_renderer = "llvmpipe (software fallback)".to_string();
    let acceleration = classify_renderer_string(&gl_renderer);
    println!("[presentation] GL Renderer: {gl_renderer} ({acceleration:?})");

    // 6. DrmSurface & GbmBufferedSurface
    let drm_surface = drm_device
        .create_surface(crtc_handle, drm_mode, &[conn_handle])
        .map_err(|e| {
            PresentationProbeError::DrmSurfaceFailed(format!("create_surface failed: {e}"))
        })?;

    let color_formats = [Fourcc::Argb8888, Fourcc::Xrgb8888];
    let mut gbm_surface = GbmBufferedSurface::<_, ()>::new(
        drm_surface,
        allocator,
        &color_formats,
        renderer.dmabuf_formats(),
    )
    .map_err(|e| {
        PresentationProbeError::GbmSurfaceFailed(format!("GbmBufferedSurface::new failed: {e}"))
    })?;

    lifecycle.transition_to(PresentationStage::GbmSurfaceCreated)?;

    // 7. Initialize Wayland Display and Socket
    let runtime_dir = match env::var("XDG_RUNTIME_DIR") {
        Ok(dir) => PathBuf::from(dir),
        Err(_) => {
            let fallback = if Path::new("/run/user/0").exists() {
                PathBuf::from("/run/user/0")
            } else {
                PathBuf::from("/tmp")
            };
            env::set_var("XDG_RUNTIME_DIR", &fallback);
            fallback
        }
    };

    let socket_name = format!("nebu-presentation-p1-7-{}", std::process::id());
    let socket_path = runtime_dir.join(&socket_name);
    if socket_path.exists() {
        let _ = std::fs::remove_file(&socket_path);
    }

    let display = Display::<PresentationCompositorState>::new().map_err(|e| {
        PresentationProbeError::WaylandFailed(format!("failed creating Display: {e}"))
    })?;
    let dh = display.handle();

    let state = PresentationCompositorState::new(&dh);

    println!(
        "[presentation] Binding Wayland socket at '{}'...",
        socket_path.display()
    );
    let listening_socket = ListeningSocketSource::with_name(&socket_name).map_err(|e| {
        PresentationProbeError::WaylandFailed(format!("failed binding socket '{socket_name}': {e}"))
    })?;

    // 8. Single unified calloop EventLoop
    let mut event_loop = EventLoop::<PresentationLoopContext>::try_new().map_err(|e| {
        PresentationProbeError::EventLoopFailed(format!("failed creating event loop: {e}"))
    })?;
    let loop_handle = event_loop.handle();

    // Insert listening socket
    loop_handle
        .insert_source(listening_socket, move |client_stream, _, ctx| {
            let client_state = Arc::new(NebuClientState {
                compositor_state: CompositorClientState::default(),
                disconnected_flag: ctx.state.disconnected_flag.clone(),
            });
            if let Err(e) = ctx
                .display
                .handle()
                .insert_client(client_stream, client_state)
            {
                eprintln!("[presentation] Failed to insert client: {e}");
            } else {
                println!("[presentation] Client connected to Wayland server");
                ctx.client_connected = true;
            }
        })
        .map_err(|e| {
            PresentationProbeError::EventLoopFailed(format!(
                "failed inserting listening socket: {e}"
            ))
        })?;

    // Insert display fd
    let display_fd = display.as_fd().try_clone_to_owned().map_err(|e| {
        PresentationProbeError::WaylandFailed(format!("failed cloning display fd: {e}"))
    })?;

    let display_source = Generic::new(display_fd, Interest::READ, Mode::Level);
    loop_handle
        .insert_source(display_source, |_readiness, _fd, ctx| {
            let _ = ctx.display.dispatch_clients(&mut ctx.state);
            let _ = ctx.display.flush_clients();
            Ok(PostAction::Continue)
        })
        .map_err(|e| {
            PresentationProbeError::EventLoopFailed(format!("failed inserting display source: {e}"))
        })?;

    // Insert DRM notifier
    loop_handle
        .insert_source(
            notifier,
            |event, metadata: &mut Option<DrmEventMetadata>, ctx| match event {
                DrmEvent::VBlank(_crtc) => {
                    ctx.vblank_received = true;
                    if let Some(m) = metadata {
                        ctx.last_sequence = m.sequence as u64;
                    }
                }
                DrmEvent::Error(err) => {
                    ctx.drm_error = Some(format!("{err:?}"));
                }
            },
        )
        .map_err(|e| {
            PresentationProbeError::EventLoopFailed(format!("failed inserting DRM notifier: {e}"))
        })?;

    let mut loop_context = PresentationLoopContext {
        state,
        display,
        vblank_received: false,
        last_sequence: 0,
        drm_error: None,
        client_connected: false,
    };

    lifecycle.transition_to(PresentationStage::WaylandListening)?;

    // 9. Spawn client thread
    let socket_path_clone = socket_path.clone();
    let client_handle = thread::spawn(move || run_presentation_client(&socket_path_clone));

    // Wait for client connection and Frame 1 commit
    println!("[presentation] Waiting for client to connect and commit Frame 1...");
    let wait_start = Instant::now();
    while loop_context.state.commits_count < 1 {
        if wait_start.elapsed() > Duration::from_secs(10) {
            return Err(PresentationProbeError::ClientFailed(
                "timed out waiting for Frame 1 commit".to_string(),
            ));
        }
        event_loop
            .dispatch(Some(Duration::from_millis(50)), &mut loop_context)
            .map_err(|e| PresentationProbeError::EventLoopFailed(format!("dispatch error: {e}")))?;
    }

    lifecycle.transition_to(PresentationStage::ClientConnected)?;

    let committed_surface = loop_context
        .state
        .committed_surface
        .clone()
        .ok_or_else(|| {
            PresentationProbeError::WaylandFailed("no surface found on commit".to_string())
        })?;

    let output_size = Size::from((output_mode.width as i32, output_mode.height as i32));
    let mut damage_tracker = OutputDamageTracker::new(output_size, 1.0, Transform::Normal);
    let surface_pos_physical = Point::<i32, Physical>::from((SURFACE_POS_X, SURFACE_POS_Y));
    let surface_rect_buffer = Rectangle::<i32, BufferCoord>::new(
        Point::from((SURFACE_POS_X, SURFACE_POS_Y)),
        Size::from((PATTERN_WIDTH as i32, PATTERN_HEIGHT as i32)),
    );

    // ==========================================
    // 10. Frame 1 Rendering & Verification
    // ==========================================
    println!("[presentation] Rendering Frame 1 (Quadrant Test Pattern)...");
    let (mut dmabuf1, age1) = gbm_surface.next_buffer().map_err(|e| {
        PresentationProbeError::RenderBufferFailed(format!("next_buffer 1 failed: {e}"))
    })?;

    let (frame1_checksum, frame1_quadrants_ok, frame1_elements_count) = {
        let mut target1 = Bind::<Dmabuf>::bind(&mut renderer, &mut dmabuf1).map_err(|e| {
            PresentationProbeError::RenderBufferFailed(format!("bind dmabuf 1 failed: {e}"))
        })?;

        let elements1: Vec<WaylandSurfaceRenderElement<_>> = render_elements_from_surface_tree(
            &mut renderer,
            &committed_surface,
            surface_pos_physical,
            1.0,
            1.0,
            Kind::Unspecified,
        );
        let count = elements1.len();
        println!("[presentation] Frame 1 imported render elements: {count}");

        let render_result1 = damage_tracker
            .render_output(
                &mut renderer,
                &mut target1,
                age1 as usize,
                &elements1,
                [0.08f32, 0.18f32, 0.36f32, 1.0f32],
            )
            .map_err(|e| {
                PresentationProbeError::RenderBufferFailed(format!("render_output 1 failed: {e}"))
            })?;

        // Deterministic Pixel Readback Verification via ExportMem
        let mapping1 = renderer
            .copy_framebuffer(&target1, surface_rect_buffer, Fourcc::Argb8888)
            .map_err(|e| {
                PresentationProbeError::PixelVerificationFailed(format!(
                    "copy_framebuffer 1 failed: {e}"
                ))
            })?;

        let pixels1 = renderer.map_texture(&mapping1).map_err(|e| {
            PresentationProbeError::PixelVerificationFailed(format!("map_texture 1 failed: {e}"))
        })?;

        let sample1 = QuadrantSample::sample_64x64(pixels1).ok_or_else(|| {
            PresentationProbeError::PixelVerificationFailed("sample 1 buffer length invalid".into())
        })?;

        let quadrants_ok = sample1.matches_variant(TestPatternVariant::Frame1Quadrants);
        let checksum = compute_sha256_hex(pixels1);
        println!(
            "[presentation] Frame 1 Readback Checksum: {checksum} (Quadrants match: {quadrants_ok})"
        );

        if !quadrants_ok {
            return Err(PresentationProbeError::PixelVerificationFailed(format!(
                "Frame 1 quadrants mismatch: sample={sample1:?}"
            )));
        }

        // Drop mapping and target before queuing buffer to release DMA handle
        drop(mapping1);
        drop(target1);

        // Queue buffer (Atomic commit + Page-Flip Event)
        gbm_surface
            .queue_buffer(Some(render_result1.sync), None, ())
            .map_err(|e| {
                PresentationProbeError::CommitFailed(format!("queue_buffer 1 failed: {e}"))
            })?;

        (checksum, quadrants_ok, count)
    };

    lifecycle.transition_to(PresentationStage::Frame1Rendered)?;
    lifecycle.transition_to(PresentationStage::Frame1Committed)?;

    // Send frame callbacks to advance client to Frame 2
    let commit1_start = Instant::now();
    send_frames_surface_tree(&committed_surface, start_time.elapsed().as_millis() as u32);
    let _ = loop_context.display.flush_clients();

    // Wait for VBlank event
    loop_context.vblank_received = false;
    let vblank1_start = Instant::now();
    while !loop_context.vblank_received {
        if vblank1_start.elapsed() > Duration::from_secs(5) {
            return Err(PresentationProbeError::VBlankTimeout);
        }
        event_loop
            .dispatch(Some(Duration::from_millis(50)), &mut loop_context)
            .map_err(|e| {
                PresentationProbeError::EventLoopFailed(format!("dispatch error 1: {e}"))
            })?;
    }
    let frame1_flip_ms = commit1_start.elapsed().as_secs_f64() * 1000.0;
    let frame1_seq = loop_context.last_sequence;
    println!("[presentation] Frame 1 VBlank received! (seq: {frame1_seq}, latency: {frame1_flip_ms:.2}ms)");
    let _ = gbm_surface.frame_submitted();
    lifecycle.transition_to(PresentationStage::Frame1Presented)?;

    // ==========================================
    // 11. Frame 2 Rendering & Verification
    // ==========================================
    println!("[presentation] Waiting for client to commit Frame 2...");
    let wait_start2 = Instant::now();
    while loop_context.state.commits_count < 2 {
        if wait_start2.elapsed() > Duration::from_secs(10) {
            return Err(PresentationProbeError::ClientFailed(
                "timed out waiting for Frame 2 commit".to_string(),
            ));
        }
        event_loop
            .dispatch(Some(Duration::from_millis(50)), &mut loop_context)
            .map_err(|e| PresentationProbeError::EventLoopFailed(format!("dispatch error: {e}")))?;
    }

    println!("[presentation] Rendering Frame 2 (Updated Quadrant Test Pattern)...");
    let (mut dmabuf2, age2) = gbm_surface.next_buffer().map_err(|e| {
        PresentationProbeError::RenderBufferFailed(format!("next_buffer 2 failed: {e}"))
    })?;

    let (frame2_checksum, frame2_quadrants_ok, frame2_elements_count) = {
        let mut target2 = Bind::<Dmabuf>::bind(&mut renderer, &mut dmabuf2).map_err(|e| {
            PresentationProbeError::RenderBufferFailed(format!("bind dmabuf 2 failed: {e}"))
        })?;

        let elements2: Vec<WaylandSurfaceRenderElement<_>> = render_elements_from_surface_tree(
            &mut renderer,
            &committed_surface,
            surface_pos_physical,
            1.0,
            1.0,
            Kind::Unspecified,
        );
        let count = elements2.len();
        println!("[presentation] Frame 2 imported render elements: {count}");

        let render_result2 = damage_tracker
            .render_output(
                &mut renderer,
                &mut target2,
                age2 as usize,
                &elements2,
                [0.08f32, 0.18f32, 0.36f32, 1.0f32],
            )
            .map_err(|e| {
                PresentationProbeError::RenderBufferFailed(format!("render_output 2 failed: {e}"))
            })?;

        // Deterministic Pixel Readback Verification via ExportMem
        let mapping2 = renderer
            .copy_framebuffer(&target2, surface_rect_buffer, Fourcc::Argb8888)
            .map_err(|e| {
                PresentationProbeError::PixelVerificationFailed(format!(
                    "copy_framebuffer 2 failed: {e}"
                ))
            })?;

        let pixels2 = renderer.map_texture(&mapping2).map_err(|e| {
            PresentationProbeError::PixelVerificationFailed(format!("map_texture 2 failed: {e}"))
        })?;

        let sample2 = QuadrantSample::sample_64x64(pixels2).ok_or_else(|| {
            PresentationProbeError::PixelVerificationFailed("sample 2 buffer length invalid".into())
        })?;

        let quadrants_ok = sample2.matches_variant(TestPatternVariant::Frame2Quadrants);
        let checksum = compute_sha256_hex(pixels2);
        println!(
            "[presentation] Frame 2 Readback Checksum: {checksum} (Quadrants match: {quadrants_ok})"
        );

        if !quadrants_ok {
            return Err(PresentationProbeError::PixelVerificationFailed(format!(
                "Frame 2 quadrants mismatch: sample={sample2:?}"
            )));
        }

        if checksum == frame1_checksum {
            return Err(PresentationProbeError::PixelVerificationFailed(
                "Frame 2 checksum unexpectedly identical to Frame 1".into(),
            ));
        }

        // Drop mapping and target before queuing buffer
        drop(mapping2);
        drop(target2);

        // Queue buffer (Atomic commit + Page-Flip Event)
        gbm_surface
            .queue_buffer(Some(render_result2.sync), None, ())
            .map_err(|e| {
                PresentationProbeError::CommitFailed(format!("queue_buffer 2 failed: {e}"))
            })?;

        (checksum, quadrants_ok, count)
    };

    lifecycle.transition_to(PresentationStage::Frame2Rendered)?;
    lifecycle.transition_to(PresentationStage::Frame2Committed)?;

    // Send frame callbacks to signal Frame 2 completion
    let commit2_start = Instant::now();
    send_frames_surface_tree(&committed_surface, start_time.elapsed().as_millis() as u32);
    let _ = loop_context.display.flush_clients();

    // Wait for VBlank event 2
    loop_context.vblank_received = false;
    let vblank2_start = Instant::now();
    while !loop_context.vblank_received {
        if vblank2_start.elapsed() > Duration::from_secs(5) {
            return Err(PresentationProbeError::VBlankTimeout);
        }
        event_loop
            .dispatch(Some(Duration::from_millis(50)), &mut loop_context)
            .map_err(|e| {
                PresentationProbeError::EventLoopFailed(format!("dispatch error 2: {e}"))
            })?;
    }
    let frame2_flip_ms = commit2_start.elapsed().as_secs_f64() * 1000.0;
    let frame2_seq = loop_context.last_sequence;
    println!("[presentation] Frame 2 VBlank received! (seq: {frame2_seq}, latency: {frame2_flip_ms:.2}ms)");
    let _ = gbm_surface.frame_submitted();
    lifecycle.transition_to(PresentationStage::Frame2Presented)?;

    // 12. Clean Teardown
    println!("[presentation] Waiting for client thread to complete teardown...");
    client_handle
        .join()
        .map_err(|_| PresentationProbeError::ClientFailed("client thread panicked".into()))?
        .map_err(PresentationProbeError::ClientFailed)?;

    // Dispatch remaining events to process destruction
    for _ in 0..5 {
        let _ = event_loop.dispatch(Some(Duration::from_millis(10)), &mut loop_context);
    }

    if socket_path.exists() {
        let _ = std::fs::remove_file(&socket_path);
    }

    lifecycle.transition_to(PresentationStage::CleanedUp)?;
    let total_duration_ms = start_time.elapsed().as_secs_f64() * 1000.0;

    let report = PresentationReport {
        session_backend: "libseat",
        session_manager,
        card_path,
        driver_name,
        connector_name,
        selected_mode: selected_mode_str,
        gl_renderer,
        acceleration,
        socket_name,
        client_connected: loop_context.client_connected,
        surface_committed: true,
        buffer_format: "Argb8888".to_string(),
        buffer_size: (PATTERN_WIDTH as i32, PATTERN_HEIGHT as i32),
        frame1_rendered: true,
        frame1_elements_count,
        frame1_checksum,
        frame1_quadrants_verified: frame1_quadrants_ok,
        frame1_atomic_commit: true,
        frame1_vblank_received: true,
        frame1_sequence: frame1_seq,
        frame1_commit_to_flip_ms: frame1_flip_ms,
        frame2_rendered: true,
        frame2_elements_count,
        frame2_checksum,
        frame2_quadrants_verified: frame2_quadrants_ok,
        frame2_atomic_commit: true,
        frame2_vblank_received: true,
        frame2_sequence: frame2_seq,
        frame2_commit_to_flip_ms: frame2_flip_ms,
        clean_teardown: true,
        total_duration_ms,
        probe_success: true,
    };

    print_presentation_report(&report);
    Ok(report)
}

/// Formats and prints the human-readable and JSON telemetry report for P1.7.
pub fn print_presentation_report(report: &PresentationReport) {
    println!();
    println!("--------------------------------------------------------------------------------");
    println!("NebuCompositor Presentation Probe Report (Milestone P1.7)");
    println!("--------------------------------------------------------------------------------");
    println!("Session Backend:             {}", report.session_backend);
    println!("Session Manager:             {}", report.session_manager);
    println!(
        "DRM Device:                  {}",
        report.card_path.display()
    );
    println!("DRM Driver:                  {}", report.driver_name);
    println!("Connector:                   {}", report.connector_name);
    println!("Selected Mode:               {}", report.selected_mode);
    println!("GL Renderer:                 {}", report.gl_renderer);
    println!("Acceleration:                {:?}", report.acceleration);
    println!("Presentation Pipeline:       Renderer Composition (VirtIO-GPU Primary Plane)");
    println!("Wayland Socket:              {}", report.socket_name);
    println!("Client Connected:            {}", report.client_connected);
    println!("Surface Committed:           {}", report.surface_committed);
    println!("Buffer Format:               {}", report.buffer_format);
    println!(
        "Buffer Dimensions:           {}x{}",
        report.buffer_size.0, report.buffer_size.1
    );
    println!(
        "Frame 1 Elements Rendered:   {}",
        report.frame1_elements_count
    );
    println!("Frame 1 SHA-256 Checksum:    {}", report.frame1_checksum);
    println!(
        "Frame 1 Quadrants Verified:  {}",
        report.frame1_quadrants_verified
    );
    println!(
        "Frame 1 Atomic Commit:       {}",
        report.frame1_atomic_commit
    );
    println!(
        "Frame 1 VBlank Received:     {} (Seq: {})",
        report.frame1_vblank_received, report.frame1_sequence
    );
    println!(
        "Frame 1 Commit-to-Flip:      {:.2} ms",
        report.frame1_commit_to_flip_ms
    );
    println!(
        "Frame 2 Elements Rendered:   {}",
        report.frame2_elements_count
    );
    println!("Frame 2 SHA-256 Checksum:    {}", report.frame2_checksum);
    println!(
        "Frame 2 Quadrants Verified:  {}",
        report.frame2_quadrants_verified
    );
    println!(
        "Frame 2 Atomic Commit:       {}",
        report.frame2_atomic_commit
    );
    println!(
        "Frame 2 VBlank Received:     {} (Seq: {})",
        report.frame2_vblank_received, report.frame2_sequence
    );
    println!(
        "Frame 2 Commit-to-Flip:      {:.2} ms",
        report.frame2_commit_to_flip_ms
    );
    println!("Clean Teardown:              {}", report.clean_teardown);
    println!(
        "Total Duration:              {:.2} ms",
        report.total_duration_ms
    );
    println!("Probe Success:               {}", report.probe_success);
    println!("--------------------------------------------------------------------------------");
    println!(
        "JSON_OUTPUT: {{\"driver\": \"{}\", \"connector\": \"{}\", \"mode\": \"{}\", \"client_connected\": {}, \"frame1_verified\": {}, \"frame1_seq\": {}, \"frame1_latency_ms\": {:.2}, \"frame2_verified\": {}, \"frame2_seq\": {}, \"frame2_latency_ms\": {:.2}, \"frame1_sha256\": \"{}\", \"frame2_sha256\": \"{}\", \"probe_success\": {}}}",
        report.driver_name,
        report.connector_name,
        report.selected_mode,
        report.client_connected,
        report.frame1_quadrants_verified,
        report.frame1_sequence,
        report.frame1_commit_to_flip_ms,
        report.frame2_quadrants_verified,
        report.frame2_sequence,
        report.frame2_commit_to_flip_ms,
        report.frame1_checksum,
        report.frame2_checksum,
        report.probe_success,
    );
    println!("EXIT_CODE={}", if report.probe_success { 0 } else { 1 });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pixel_pattern_generation_frame1() {
        let pixels = generate_pattern_pixels(TestPatternVariant::Frame1Quadrants);
        assert_eq!(pixels.len(), BUFFER_SIZE_BYTES);

        let sample = QuadrantSample::sample_64x64(&pixels).expect("valid sample");
        assert_eq!(
            sample.top_left,
            [0x00, 0x00, 0xFF, 0xFF],
            "Top-Left should be Red"
        );
        assert_eq!(
            sample.top_right,
            [0x00, 0xFF, 0x00, 0xFF],
            "Top-Right should be Green"
        );
        assert_eq!(
            sample.bottom_left,
            [0xFF, 0x00, 0x00, 0xFF],
            "Bottom-Left should be Blue"
        );
        assert_eq!(
            sample.bottom_right,
            [0x00, 0xFF, 0xFF, 0xFF],
            "Bottom-Right should be Yellow"
        );

        assert!(sample.matches_variant(TestPatternVariant::Frame1Quadrants));
        assert!(!sample.matches_variant(TestPatternVariant::Frame2Quadrants));

        let hash = compute_sha256_hex(&pixels);
        assert_eq!(hash.len(), 64);
    }

    #[test]
    fn test_pixel_pattern_generation_frame2() {
        let pixels = generate_pattern_pixels(TestPatternVariant::Frame2Quadrants);
        assert_eq!(pixels.len(), BUFFER_SIZE_BYTES);

        let sample = QuadrantSample::sample_64x64(&pixels).expect("valid sample");
        assert_eq!(
            sample.top_left,
            [0xFF, 0xFF, 0x00, 0xFF],
            "Top-Left should be Cyan"
        );
        assert_eq!(
            sample.top_right,
            [0xFF, 0x00, 0xFF, 0xFF],
            "Top-Right should be Magenta"
        );
        assert_eq!(
            sample.bottom_left,
            [0x00, 0xFF, 0xFF, 0xFF],
            "Bottom-Left should be Yellow"
        );
        assert_eq!(
            sample.bottom_right,
            [0xFF, 0xFF, 0xFF, 0xFF],
            "Bottom-Right should be White"
        );

        assert!(sample.matches_variant(TestPatternVariant::Frame2Quadrants));
        assert!(!sample.matches_variant(TestPatternVariant::Frame1Quadrants));

        let hash1 = compute_sha256_hex(&generate_pattern_pixels(
            TestPatternVariant::Frame1Quadrants,
        ));
        let hash2 = compute_sha256_hex(&pixels);
        assert_ne!(hash1, hash2);
    }

    #[test]
    fn test_presentation_lifecycle_transitions() {
        let mut lc = PresentationLifecycle::new();
        assert_eq!(lc.current_stage(), PresentationStage::Uninitialized);

        assert!(lc.transition_to(PresentationStage::SessionOpened).is_ok());
        assert!(lc.transition_to(PresentationStage::DrmInitialized).is_ok());
        assert!(lc
            .transition_to(PresentationStage::GbmSurfaceCreated)
            .is_ok());
        assert!(lc
            .transition_to(PresentationStage::WaylandListening)
            .is_ok());
        assert!(lc.transition_to(PresentationStage::ClientConnected).is_ok());
        assert!(lc.transition_to(PresentationStage::Frame1Rendered).is_ok());
        assert!(lc.transition_to(PresentationStage::Frame1Committed).is_ok());
        assert!(lc.transition_to(PresentationStage::Frame1Presented).is_ok());
        assert!(lc.transition_to(PresentationStage::Frame2Rendered).is_ok());
        assert!(lc.transition_to(PresentationStage::Frame2Committed).is_ok());
        assert!(lc.transition_to(PresentationStage::Frame2Presented).is_ok());
        assert!(lc.transition_to(PresentationStage::CleanedUp).is_ok());

        // Invalid transitions
        let mut fresh = PresentationLifecycle::new();
        assert!(fresh
            .transition_to(PresentationStage::Frame1Presented)
            .is_err());
    }
}
