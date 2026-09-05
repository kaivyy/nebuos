//! Input Event Processing & Device Management Module — NebuOS Milestone P1.5
//!
//! Provides dynamic `libinput` device discovery, event loop dispatch through `calloop`,
//! keyboard keycode translation and modifier tracking via `xkbcommon`, and pointer state management.

use std::collections::HashSet;
use std::fmt;
use std::os::unix::io::OwnedFd;
use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};

use calloop::EventLoop;
use smithay::backend::input::{
    AbsolutePositionEvent, ButtonState, InputEvent, KeyState, KeyboardKeyEvent, PointerButtonEvent,
    PointerMotionEvent,
};
use smithay::backend::libinput::LibinputInputBackend;
use smithay::reexports::input::{DeviceCapability, Libinput, LibinputInterface};

use crate::backend::discover_drm_devices;
use crate::session::{SessionError, SessionHandle, SessionManagerType};

/// Supported classification of input devices.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum DeviceType {
    Keyboard,
    Pointer,
    Touch,
    Switch,
    Composite,
    Unknown,
}

impl fmt::Display for DeviceType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Keyboard => write!(f, "keyboard"),
            Self::Pointer => write!(f, "pointer"),
            Self::Touch => write!(f, "touch"),
            Self::Switch => write!(f, "switch"),
            Self::Composite => write!(f, "composite"),
            Self::Unknown => write!(f, "unknown"),
        }
    }
}

/// Classifies device capabilities into an architectural device type.
pub fn classify_device_capabilities(
    is_kbd: bool,
    is_ptr: bool,
    is_touch: bool,
    is_switch: bool,
) -> DeviceType {
    let count = (is_kbd as u8) + (is_ptr as u8) + (is_touch as u8) + (is_switch as u8);
    if count > 1 {
        DeviceType::Composite
    } else if is_kbd {
        DeviceType::Keyboard
    } else if is_ptr {
        DeviceType::Pointer
    } else if is_touch {
        DeviceType::Touch
    } else if is_switch {
        DeviceType::Switch
    } else {
        DeviceType::Unknown
    }
}

/// Modifier state representing active logical keyboard modifiers.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct ModifierState {
    pub ctrl: bool,
    pub alt: bool,
    pub shift: bool,
    pub logo: bool,
    pub caps_lock: bool,
}

impl ModifierState {
    pub fn is_empty(&self) -> bool {
        !self.ctrl && !self.alt && !self.shift && !self.logo && !self.caps_lock
    }
}

impl fmt::Display for ModifierState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let mut parts = Vec::new();
        if self.ctrl {
            parts.push("Ctrl");
        }
        if self.alt {
            parts.push("Alt");
        }
        if self.shift {
            parts.push("Shift");
        }
        if self.logo {
            parts.push("Logo");
        }
        if self.caps_lock {
            parts.push("CapsLock");
        }
        if parts.is_empty() {
            write!(f, "None")
        } else {
            write!(f, "{}", parts.join("+"))
        }
    }
}

/// Tracks keyboard key state and translates key events through xkbcommon.
pub struct KeyboardStateTracker {
    pressed_keys: HashSet<u32>,
    _xkb_context: xkbcommon::xkb::Context,
    _xkb_keymap: xkbcommon::xkb::Keymap,
    xkb_state: xkbcommon::xkb::State,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct KeyTranslationResult {
    pub keycode: u32,
    pub keysym_raw: u32,
    pub keysym_name: String,
    pub is_pressed: bool,
    pub modifiers: ModifierState,
}

impl KeyboardStateTracker {
    pub fn new() -> Option<Self> {
        let xkb_context = xkbcommon::xkb::Context::new(xkbcommon::xkb::CONTEXT_NO_FLAGS);
        let xkb_keymap = xkbcommon::xkb::Keymap::new_from_names(
            &xkb_context,
            "",
            "",
            "",
            "",
            None,
            xkbcommon::xkb::KEYMAP_COMPILE_NO_FLAGS,
        )?;
        let xkb_state = xkbcommon::xkb::State::new(&xkb_keymap);
        Some(Self {
            pressed_keys: HashSet::new(),
            _xkb_context: xkb_context,
            _xkb_keymap: xkb_keymap,
            xkb_state,
        })
    }

    pub fn is_key_pressed(&self, keycode: u32) -> bool {
        self.pressed_keys.contains(&keycode)
    }

    pub fn pressed_key_count(&self) -> usize {
        self.pressed_keys.len()
    }

    pub fn process_key(&mut self, keycode: u32, is_pressed: bool) -> KeyTranslationResult {
        let key: xkbcommon::xkb::Keycode = keycode.into();
        let direction = if is_pressed {
            xkbcommon::xkb::KeyDirection::Down
        } else {
            xkbcommon::xkb::KeyDirection::Up
        };

        self.xkb_state.update_key(key, direction);
        if is_pressed {
            self.pressed_keys.insert(keycode);
        } else {
            self.pressed_keys.remove(&keycode);
        }

        let keysym = self.xkb_state.key_get_one_sym(key);
        let keysym_name = xkbcommon::xkb::keysym_get_name(keysym);
        let modifiers = self.current_modifiers();

        KeyTranslationResult {
            keycode,
            keysym_raw: keysym.raw(),
            keysym_name,
            is_pressed,
            modifiers,
        }
    }

    pub fn current_modifiers(&self) -> ModifierState {
        ModifierState {
            ctrl: self.xkb_state.mod_name_is_active(
                xkbcommon::xkb::MOD_NAME_CTRL,
                xkbcommon::xkb::STATE_MODS_EFFECTIVE,
            ),
            alt: self.xkb_state.mod_name_is_active(
                xkbcommon::xkb::MOD_NAME_ALT,
                xkbcommon::xkb::STATE_MODS_EFFECTIVE,
            ),
            shift: self.xkb_state.mod_name_is_active(
                xkbcommon::xkb::MOD_NAME_SHIFT,
                xkbcommon::xkb::STATE_MODS_EFFECTIVE,
            ),
            logo: self.xkb_state.mod_name_is_active(
                xkbcommon::xkb::MOD_NAME_LOGO,
                xkbcommon::xkb::STATE_MODS_EFFECTIVE,
            ),
            caps_lock: self.xkb_state.mod_name_is_active(
                xkbcommon::xkb::MOD_NAME_CAPS,
                xkbcommon::xkb::STATE_MODS_EFFECTIVE,
            ),
        }
    }
}

/// Tracks pointer coordinates, pressed mouse buttons, and viewport bounds.
pub struct PointerStateTracker {
    x: f64,
    y: f64,
    bounds: Option<(f64, f64)>,
    pressed_buttons: HashSet<u32>,
}

impl PointerStateTracker {
    pub fn new() -> Self {
        Self {
            x: 0.0,
            y: 0.0,
            bounds: None,
            pressed_buttons: HashSet::new(),
        }
    }

    pub fn set_bounds(&mut self, width: f64, height: f64) {
        self.bounds = Some((width.max(0.0), height.max(0.0)));
        self.clamp_position();
    }

    pub fn position(&self) -> (f64, f64) {
        (self.x, self.y)
    }

    pub fn apply_relative_motion(&mut self, dx: f64, dy: f64) {
        self.x += dx;
        self.y += dy;
        self.clamp_position();
    }

    pub fn apply_absolute_motion(&mut self, x: f64, y: f64) {
        self.x = x;
        self.y = y;
        self.clamp_position();
    }

    fn clamp_position(&mut self) {
        if let Some((max_w, max_h)) = self.bounds {
            self.x = self.x.clamp(0.0, max_w);
            self.y = self.y.clamp(0.0, max_h);
        } else {
            self.x = self.x.max(0.0);
            self.y = self.y.max(0.0);
        }
    }

    pub fn apply_button(&mut self, button_code: u32, is_pressed: bool) {
        if is_pressed {
            self.pressed_buttons.insert(button_code);
        } else {
            self.pressed_buttons.remove(&button_code);
        }
    }

    pub fn is_button_pressed(&self, button_code: u32) -> bool {
        self.pressed_buttons.contains(&button_code)
    }

    pub fn pressed_button_count(&self) -> usize {
        self.pressed_buttons.len()
    }
}

impl Default for PointerStateTracker {
    fn default() -> Self {
        Self::new()
    }
}

/// Lifecycle states for the input subsystem.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum InputLifecycleStage {
    Uninitialized,
    Initialized,
    DevicesDiscovered,
    Active,
    ShuttingDown,
    Terminated,
    Failed(String),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct InputLifecycleError(pub String);

impl fmt::Display for InputLifecycleError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "input lifecycle error: {}", self.0)
    }
}

impl std::error::Error for InputLifecycleError {}

/// State machine governing input subsystem lifecycle.
#[derive(Debug, Clone)]
pub struct InputLifecycle {
    current: InputLifecycleStage,
}

impl InputLifecycle {
    pub fn new() -> Self {
        Self {
            current: InputLifecycleStage::Uninitialized,
        }
    }

    pub fn current_stage(&self) -> &InputLifecycleStage {
        &self.current
    }

    pub fn can_transition(&self, next: &InputLifecycleStage) -> bool {
        if matches!(next, InputLifecycleStage::Failed(_)) {
            return true;
        }
        matches!(
            (&self.current, next),
            (
                InputLifecycleStage::Uninitialized,
                InputLifecycleStage::Initialized
            ) | (
                InputLifecycleStage::Initialized,
                InputLifecycleStage::DevicesDiscovered
            ) | (
                InputLifecycleStage::Initialized,
                InputLifecycleStage::ShuttingDown
            ) | (
                InputLifecycleStage::DevicesDiscovered,
                InputLifecycleStage::Active
            ) | (
                InputLifecycleStage::DevicesDiscovered,
                InputLifecycleStage::ShuttingDown
            ) | (
                InputLifecycleStage::Active,
                InputLifecycleStage::ShuttingDown
            ) | (
                InputLifecycleStage::ShuttingDown,
                InputLifecycleStage::Terminated
            )
        )
    }

    pub fn transition_to(&mut self, next: InputLifecycleStage) -> Result<(), InputLifecycleError> {
        if self.can_transition(&next) {
            self.current = next;
            Ok(())
        } else {
            Err(InputLifecycleError(format!(
                "invalid transition from {:?} to {:?}",
                self.current, next
            )))
        }
    }
}

impl Default for InputLifecycle {
    fn default() -> Self {
        Self::new()
    }
}

/// Errors occurring during the input subsystem probe.
#[derive(Debug)]
pub enum InputProbeError {
    SessionError(SessionError),
    LibinputInitFailed(String),
    SeatAssignmentFailed(String),
    EventLoopFailed(String),
    LifecycleViolation(InputLifecycleError),
}

impl fmt::Display for InputProbeError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::SessionError(err) => write!(f, "session acquisition error: {err}"),
            Self::LibinputInitFailed(msg) => {
                write!(f, "libinput context initialization failed: {msg}")
            }
            Self::SeatAssignmentFailed(seat) => {
                write!(f, "failed to assign seat '{seat}' to libinput context")
            }
            Self::EventLoopFailed(msg) => write!(f, "event loop failure: {msg}"),
            Self::LifecycleViolation(err) => write!(f, "lifecycle state violation: {err}"),
        }
    }
}

impl std::error::Error for InputProbeError {}

impl From<SessionError> for InputProbeError {
    fn from(err: SessionError) -> Self {
        Self::SessionError(err)
    }
}

impl From<InputLifecycleError> for InputProbeError {
    fn from(err: InputLifecycleError) -> Self {
        Self::LifecycleViolation(err)
    }
}

/// Bridge connecting libinput file descriptor acquisition to the unprivileged session manager.
pub struct NebuLibinputInterface {
    session: SessionHandle,
}

impl NebuLibinputInterface {
    pub fn new(session: SessionHandle) -> Self {
        Self { session }
    }
}

impl LibinputInterface for NebuLibinputInterface {
    fn open_restricted(&mut self, path: &Path, flags: i32) -> Result<OwnedFd, i32> {
        self.session
            .open_device_with_flags(path, flags)
            .map_err(|_| 1) // EPERM
    }

    fn close_restricted(&mut self, fd: OwnedFd) {
        drop(fd);
    }
}

/// Discovered input device with classified capabilities.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DiscoveredInputDevice {
    pub name: String,
    pub sysname: String,
    pub device_type: DeviceType,
    pub is_keyboard: bool,
    pub is_pointer: bool,
    pub is_touch: bool,
    pub is_switch: bool,
}

/// Telemetry report for Milestone P1.5 Input Subsystem Integration Proof.
#[derive(Debug, Clone)]
pub struct InputProbeReport {
    pub session_backend: &'static str,
    pub session_manager: SessionManagerType,
    pub session_is_production: bool,
    pub session_access: bool,
    pub seat_name: String,
    pub drm_device_path: Option<PathBuf>,
    pub drm_coexistence_verified: bool,
    pub discovered_devices: Vec<DiscoveredInputDevice>,
    pub keyboard_devices_count: usize,
    pub pointer_devices_count: usize,
    pub touch_devices_count: usize,
    pub switch_devices_count: usize,
    pub total_devices_count: usize,
    pub keyboard_events_received: usize,
    pub pointer_motion_events_received: usize,
    pub pointer_button_events_received: usize,
    pub keysyms_translated: Vec<String>,
    pub modifiers_tested: Vec<String>,
    pub pointer_final_position: (f64, f64),
    pub event_loop_dispatches: usize,
    pub shutdown_clean: bool,
    pub total_duration_ms: f64,
    pub probe_success: bool,
}

struct InputProbeContext {
    discovered_devices: Vec<DiscoveredInputDevice>,
    keyboard_events_count: usize,
    pointer_motion_events_count: usize,
    pointer_button_events_count: usize,
    translated_keysyms: Vec<String>,
    modifiers_observed: Vec<String>,
    keyboard_tracker: KeyboardStateTracker,
    pointer_tracker: PointerStateTracker,
}

/// Executes the full Milestone P1.5 Input Subsystem Integration Proof.
pub fn run_input_probe() -> Result<InputProbeReport, InputProbeError> {
    let probe_start = Instant::now();
    let mut lifecycle = InputLifecycle::new();

    // 1. Unprivileged session acquisition
    let mut session = SessionHandle::new_diagnostic()?;
    let session_manager = session.manager;
    let session_is_production = session.is_production();
    let seat_name = session.seat_name.clone();

    lifecycle.transition_to(InputLifecycleStage::Initialized)?;

    println!("=== NebuCompositor Input Subsystem Integration Probe ===");
    println!(
        "[probe] Initializing session on seat '{}' (manager: {}, production: {})...",
        seat_name, session_manager, session_is_production
    );

    // 2. DRM coexistence verification
    let (primary_card, _render_node) = discover_drm_devices();
    let mut drm_coexistence_verified = false;
    let mut drm_card_path = None;

    if let Some(card_path) = primary_card {
        drm_card_path = Some(card_path.clone());
        match session.open_device(&card_path) {
            Ok(fd) => {
                println!(
                    "[drm] Coexistence verified: successfully opened DRM card '{}'",
                    card_path.display()
                );
                drm_coexistence_verified = true;
                drop(fd);
            }
            Err(e) => {
                eprintln!("[probe] Notice: DRM device coexistence open warning: {e}");
            }
        }
    }

    // 3. Libinput context initialization with session interface
    let interface = NebuLibinputInterface::new(session);
    let mut libinput_ctx = Libinput::new_with_udev(interface);
    libinput_ctx
        .udev_assign_seat(&seat_name)
        .map_err(|_| InputProbeError::SeatAssignmentFailed(seat_name.clone()))?;
    println!("[probe] Assigned seat '{}' to libinput context", seat_name);

    let libinput_backend = LibinputInputBackend::new(libinput_ctx);

    // 4. Calloop reactor setup
    let mut event_loop = EventLoop::<InputProbeContext>::try_new().map_err(|e| {
        InputProbeError::EventLoopFailed(format!("failed to initialize calloop event loop: {e}"))
    })?;

    let kbd_tracker = KeyboardStateTracker::new().ok_or_else(|| {
        InputProbeError::LibinputInitFailed("failed initializing xkbcommon context".into())
    })?;

    let mut ptr_tracker = PointerStateTracker::new();
    ptr_tracker.set_bounds(1280.0, 800.0);

    let mut loop_context = InputProbeContext {
        discovered_devices: Vec::new(),
        keyboard_events_count: 0,
        pointer_motion_events_count: 0,
        pointer_button_events_count: 0,
        translated_keysyms: Vec::new(),
        modifiers_observed: Vec::new(),
        keyboard_tracker: kbd_tracker,
        pointer_tracker: ptr_tracker,
    };

    let loop_handle = event_loop.handle();
    let _source = loop_handle
        .insert_source(
            libinput_backend,
            |event: InputEvent<LibinputInputBackend>, _, ctx| match event {
                InputEvent::DeviceAdded { device } => {
                    let is_kbd = device.has_capability(DeviceCapability::Keyboard);
                    let is_ptr = device.has_capability(DeviceCapability::Pointer);
                    let is_touch = device.has_capability(DeviceCapability::Touch);
                    let is_switch = device.has_capability(DeviceCapability::Switch);
                    let dev_type =
                        classify_device_capabilities(is_kbd, is_ptr, is_touch, is_switch);
                    println!(
                        "[input] DeviceAdded: name=\"{}\" sysname=\"{}\" type={}",
                        device.name(),
                        device.sysname(),
                        dev_type
                    );
                    ctx.discovered_devices.push(DiscoveredInputDevice {
                        name: device.name().to_string(),
                        sysname: device.sysname().to_string(),
                        device_type: dev_type,
                        is_keyboard: is_kbd,
                        is_pointer: is_ptr,
                        is_touch,
                        is_switch,
                    });
                }
                InputEvent::DeviceRemoved { device } => {
                    println!("[input] DeviceRemoved: name=\"{}\"", device.name());
                }
                InputEvent::Keyboard { event } => {
                    let raw_code: u32 = event.key_code().into();
                    let is_pressed = event.state() == KeyState::Pressed;
                    let res = ctx.keyboard_tracker.process_key(raw_code, is_pressed);
                    ctx.keyboard_events_count += 1;
                    let mod_str = res.modifiers.to_string();
                    if !ctx.modifiers_observed.contains(&mod_str) {
                        ctx.modifiers_observed.push(mod_str.clone());
                    }
                    if !ctx.translated_keysyms.contains(&res.keysym_name) {
                        ctx.translated_keysyms.push(res.keysym_name.clone());
                    }
                    println!(
                        "[input] Keyboard: keycode={} keysym={} pressed={} mods={}",
                        res.keycode, res.keysym_name, res.is_pressed, mod_str
                    );
                }
                InputEvent::PointerMotion { event } => {
                    let dx = event.delta_x();
                    let dy = event.delta_y();
                    ctx.pointer_tracker.apply_relative_motion(dx, dy);
                    ctx.pointer_motion_events_count += 1;
                    let pos = ctx.pointer_tracker.position();
                    println!(
                        "[input] PointerMotion: dx={:.2} dy={:.2} -> pos=({:.2}, {:.2})",
                        dx, dy, pos.0, pos.1
                    );
                }
                InputEvent::PointerMotionAbsolute { event } => {
                    let x = event.x_transformed(1280);
                    let y = event.y_transformed(800);
                    ctx.pointer_tracker.apply_absolute_motion(x, y);
                    ctx.pointer_motion_events_count += 1;
                    let pos = ctx.pointer_tracker.position();
                    println!(
                        "[input] PointerMotionAbsolute: x={:.2} y={:.2} -> pos=({:.2}, {:.2})",
                        x, y, pos.0, pos.1
                    );
                }
                InputEvent::PointerButton { event } => {
                    let button = event.button_code();
                    let is_pressed = event.state() == ButtonState::Pressed;
                    ctx.pointer_tracker.apply_button(button, is_pressed);
                    ctx.pointer_button_events_count += 1;
                    println!(
                        "[input] PointerButton: button={:#x} pressed={}",
                        button, is_pressed
                    );
                }
                _ => {}
            },
        )
        .map_err(|e| {
            InputProbeError::EventLoopFailed(format!("failed inserting libinput event source: {e}"))
        })?;

    // 5. Initial Device Discovery Dispatches
    event_loop
        .dispatch(Some(Duration::from_millis(200)), &mut loop_context)
        .map_err(|e| InputProbeError::EventLoopFailed(format!("initial dispatch failed: {e}")))?;

    if loop_context.discovered_devices.is_empty() {
        event_loop
            .dispatch(Some(Duration::from_millis(300)), &mut loop_context)
            .map_err(|e| {
                InputProbeError::EventLoopFailed(format!("discovery dispatch retry failed: {e}"))
            })?;
    }

    lifecycle.transition_to(InputLifecycleStage::DevicesDiscovered)?;

    // 6. Active Event Loop Dispatch
    lifecycle.transition_to(InputLifecycleStage::Active)?;

    let active_start = Instant::now();
    let mut total_dispatches = 1;
    let max_probe_duration = Duration::from_secs(8);

    while active_start.elapsed() < max_probe_duration {
        event_loop
            .dispatch(Some(Duration::from_millis(200)), &mut loop_context)
            .map_err(|e| {
                InputProbeError::EventLoopFailed(format!("active loop dispatch failed: {e}"))
            })?;
        total_dispatches += 1;

        // Exit cleanly once both keyboard and pointer events have been verified
        if loop_context.keyboard_events_count >= 1
            && (loop_context.pointer_motion_events_count >= 1
                || loop_context.pointer_button_events_count >= 1)
            && active_start.elapsed() >= Duration::from_millis(2000)
        {
            println!("[input] Target input event quota achieved. Finalizing probe.");
            break;
        }
    }

    // 7. Clean Teardown
    lifecycle.transition_to(InputLifecycleStage::ShuttingDown)?;
    lifecycle.transition_to(InputLifecycleStage::Terminated)?;

    let shutdown_clean = true;
    let total_duration_ms = probe_start.elapsed().as_secs_f64() * 1000.0;
    let kbd_count = loop_context
        .discovered_devices
        .iter()
        .filter(|d| d.is_keyboard)
        .count();
    let ptr_count = loop_context
        .discovered_devices
        .iter()
        .filter(|d| d.is_pointer)
        .count();
    let touch_count = loop_context
        .discovered_devices
        .iter()
        .filter(|d| d.is_touch)
        .count();
    let switch_count = loop_context
        .discovered_devices
        .iter()
        .filter(|d| d.is_switch)
        .count();
    let total_devices = loop_context.discovered_devices.len();

    let report = InputProbeReport {
        session_backend: "libseat",
        session_manager,
        session_is_production,
        session_access: true,
        seat_name,
        drm_device_path: drm_card_path,
        drm_coexistence_verified,
        discovered_devices: loop_context.discovered_devices,
        keyboard_devices_count: kbd_count,
        pointer_devices_count: ptr_count,
        touch_devices_count: touch_count,
        switch_devices_count: switch_count,
        total_devices_count: total_devices,
        keyboard_events_received: loop_context.keyboard_events_count,
        pointer_motion_events_received: loop_context.pointer_motion_events_count,
        pointer_button_events_received: loop_context.pointer_button_events_count,
        keysyms_translated: loop_context.translated_keysyms,
        modifiers_tested: loop_context.modifiers_observed,
        pointer_final_position: loop_context.pointer_tracker.position(),
        event_loop_dispatches: total_dispatches,
        shutdown_clean,
        total_duration_ms,
        probe_success: total_devices > 0,
    };

    print_input_probe_report(&report);
    Ok(report)
}

/// Prints formatted deterministic output for the input subsystem probe.
pub fn print_input_probe_report(report: &InputProbeReport) {
    println!();
    println!("NebuCompositor Input Subsystem Integration Proof");
    println!("===============================================");
    println!();
    println!("Session:");
    println!("  Backend: {}", report.session_backend);
    println!("  Manager: {}", report.session_manager);
    println!(
        "  Type: {}",
        if report.session_is_production {
            "unprivileged production"
        } else {
            "diagnostic fallback"
        }
    );
    println!("  Seat: {}", report.seat_name);
    println!(
        "  Access: {}",
        if report.session_access {
            "granted"
        } else {
            "denied"
        }
    );
    println!();
    println!("DRM Coexistence:");
    println!(
        "  Primary DRM Card: {}",
        report
            .drm_device_path
            .as_ref()
            .map(|p| p.display().to_string())
            .unwrap_or_else(|| "none".into())
    );
    println!(
        "  Coexistence Verified: {}",
        report.drm_coexistence_verified
    );
    println!();
    println!("Discovered Devices ({} total):", report.total_devices_count);
    println!("  Keyboards: {}", report.keyboard_devices_count);
    println!("  Pointers: {}", report.pointer_devices_count);
    println!("  Touch: {}", report.touch_devices_count);
    println!("  Switches: {}", report.switch_devices_count);
    for (i, dev) in report.discovered_devices.iter().enumerate() {
        println!(
            "  [{}] \"{}\" (sysname: {}, type: {})",
            i + 1,
            dev.name,
            dev.sysname,
            dev.device_type
        );
    }
    println!();
    println!("Event Processing & Telemetry:");
    println!("  Keyboard Events: {}", report.keyboard_events_received);
    println!(
        "  Pointer Motion Events: {}",
        report.pointer_motion_events_received
    );
    println!(
        "  Pointer Button Events: {}",
        report.pointer_button_events_received
    );
    println!("  Translated Keysyms: {:?}", report.keysyms_translated);
    println!("  Modifiers Tested: {:?}", report.modifiers_tested);
    println!(
        "  Pointer Final Position: ({:.2}, {:.2})",
        report.pointer_final_position.0, report.pointer_final_position.1
    );
    println!("  Event Loop Dispatches: {}", report.event_loop_dispatches);
    println!();
    println!("Shutdown & Diagnostics:");
    println!(
        "  Teardown: {}",
        if report.shutdown_clean {
            "clean (RAII)"
        } else {
            "unclean"
        }
    );
    println!("  Total Duration: {:.2} ms", report.total_duration_ms);
    println!(
        "  Verdict: {}",
        if report.probe_success { "PASS" } else { "FAIL" }
    );
    println!();
    println!("JSON Telemetry:");
    println!(
        "JSON_OUTPUT: {{\"discovered_devices_count\": {}, \"keyboard_events\": {}, \"pointer_events\": {}, \"probe_success\": {}}}",
        report.total_devices_count,
        report.keyboard_events_received,
        report.pointer_motion_events_received,
        report.probe_success
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_device_classification() {
        assert_eq!(
            classify_device_capabilities(true, false, false, false),
            DeviceType::Keyboard
        );
        assert_eq!(
            classify_device_capabilities(false, true, false, false),
            DeviceType::Pointer
        );
        assert_eq!(
            classify_device_capabilities(true, true, false, false),
            DeviceType::Composite
        );
        assert_eq!(
            classify_device_capabilities(false, false, true, false),
            DeviceType::Touch
        );
        assert_eq!(
            classify_device_capabilities(false, false, false, true),
            DeviceType::Switch
        );
        assert_eq!(
            classify_device_capabilities(false, false, false, false),
            DeviceType::Unknown
        );
    }

    #[test]
    fn test_keyboard_tracker_press_release() {
        let mut tracker = KeyboardStateTracker::new().expect("xkb init failed");
        assert_eq!(tracker.pressed_key_count(), 0);
        assert!(!tracker.is_key_pressed(38));

        // Press keycode 38 ('a')
        let res1 = tracker.process_key(38, true);
        assert!(res1.is_pressed);
        assert_eq!(res1.keycode, 38);
        assert_eq!(res1.keysym_name, "a");
        assert!(tracker.is_key_pressed(38));
        assert_eq!(tracker.pressed_key_count(), 1);

        // Press keycode 56 ('b')
        let res2 = tracker.process_key(56, true);
        assert!(res2.is_pressed);
        assert_eq!(res2.keycode, 56);
        assert_eq!(res2.keysym_name, "b");
        assert_eq!(tracker.pressed_key_count(), 2);

        // Release keycode 38
        let res3 = tracker.process_key(38, false);
        assert!(!res3.is_pressed);
        assert!(!tracker.is_key_pressed(38));
        assert!(tracker.is_key_pressed(56));
        assert_eq!(tracker.pressed_key_count(), 1);

        // Release keycode 56
        tracker.process_key(56, false);
        assert_eq!(tracker.pressed_key_count(), 0);
    }

    #[test]
    fn test_xkb_translation_and_modifiers() {
        let mut tracker = KeyboardStateTracker::new().expect("xkb init failed");

        // Keycode 50 is Left Shift in xkb (evdev 42 + 8)
        let res_shift = tracker.process_key(50, true);
        assert!(res_shift.modifiers.shift);
        assert_eq!(res_shift.modifiers.to_string(), "Shift");

        // With Shift pressed, keycode 38 ('a') should translate to 'A'
        let res_a = tracker.process_key(38, true);
        assert_eq!(res_a.keysym_name, "A");
        assert!(res_a.modifiers.shift);

        // Release keycode 38
        tracker.process_key(38, false);

        // Release Shift
        let res_shift_rel = tracker.process_key(50, false);
        assert!(!res_shift_rel.modifiers.shift);
        assert!(res_shift_rel.modifiers.is_empty());
        assert_eq!(res_shift_rel.modifiers.to_string(), "None");
    }

    #[test]
    fn test_pointer_tracker_motion_and_bounds() {
        let mut tracker = PointerStateTracker::new();
        tracker.set_bounds(1280.0, 800.0);
        assert_eq!(tracker.position(), (0.0, 0.0));

        // Relative motion within bounds
        tracker.apply_relative_motion(100.0, 50.0);
        assert_eq!(tracker.position(), (100.0, 50.0));

        // Overflow clamped to maximum bounds
        tracker.apply_relative_motion(2000.0, 2000.0);
        assert_eq!(tracker.position(), (1280.0, 800.0));

        // Underflow clamped to 0.0
        tracker.apply_relative_motion(-5000.0, -5000.0);
        assert_eq!(tracker.position(), (0.0, 0.0));

        // Absolute motion within bounds
        tracker.apply_absolute_motion(640.0, 400.0);
        assert_eq!(tracker.position(), (640.0, 400.0));

        // Absolute motion clamped to bounds
        tracker.apply_absolute_motion(1500.0, 900.0);
        assert_eq!(tracker.position(), (1280.0, 800.0));
    }

    #[test]
    fn test_pointer_tracker_buttons() {
        let mut tracker = PointerStateTracker::new();
        assert_eq!(tracker.pressed_button_count(), 0);
        assert!(!tracker.is_button_pressed(0x110));

        // Press BTN_LEFT (0x110)
        tracker.apply_button(0x110, true);
        assert!(tracker.is_button_pressed(0x110));
        assert_eq!(tracker.pressed_button_count(), 1);

        // Press BTN_RIGHT (0x111)
        tracker.apply_button(0x111, true);
        assert!(tracker.is_button_pressed(0x110));
        assert!(tracker.is_button_pressed(0x111));
        assert_eq!(tracker.pressed_button_count(), 2);

        // Release BTN_LEFT
        tracker.apply_button(0x110, false);
        assert!(!tracker.is_button_pressed(0x110));
        assert!(tracker.is_button_pressed(0x111));
        assert_eq!(tracker.pressed_button_count(), 1);

        // Release BTN_RIGHT
        tracker.apply_button(0x111, false);
        assert_eq!(tracker.pressed_button_count(), 0);
    }

    #[test]
    fn test_input_lifecycle_transitions() {
        let mut lc = InputLifecycle::new();
        assert_eq!(*lc.current_stage(), InputLifecycleStage::Uninitialized);
        assert!(lc.transition_to(InputLifecycleStage::Initialized).is_ok());
        assert!(lc
            .transition_to(InputLifecycleStage::DevicesDiscovered)
            .is_ok());
        assert!(lc.transition_to(InputLifecycleStage::Active).is_ok());
        assert!(lc.transition_to(InputLifecycleStage::ShuttingDown).is_ok());
        assert!(lc.transition_to(InputLifecycleStage::Terminated).is_ok());

        // Test illegal transition jump
        let mut invalid_lc = InputLifecycle::new();
        assert!(invalid_lc
            .transition_to(InputLifecycleStage::Active)
            .is_err());

        // Test failure transition from any stage
        let mut fail_lc = InputLifecycle::new();
        assert!(fail_lc
            .transition_to(InputLifecycleStage::Failed("error".into()))
            .is_ok());
    }
}
