# Phase P1: NebuCompositor Specification — NebuOS

**Status:** APPROVED  
**Phase:** P1  
**Target Duration:** Sprint 3–5  
**Prerequisite:** Phase P0  

---

## 1. Objective
Implement `nebu-compositor`, the native Rust Wayland display server built upon Smithay primitives. P1 establishes hardware DRM/KMS modesetting, libinput event dispatch, EGL/GBM hardware-accelerated rendering, core Wayland protocol support, and zero-copy direct scanout for fullscreen surfaces.

## 2. Scope (What's IN)
- Standalone Rust crate `crates/nebu-compositor`.
- Linux DRM/KMS atomic modesetting backend (`/dev/dri/card0`).
- Hardware input processing via `libinput` and `xkbcommon`.
- GBM (Generic Buffer Management) and EGL/GLES2 rendering pipeline.
- Core Wayland protocols: `wl_compositor`, `wl_subcompositor`, `wl_seat`, `wl_output`, `wl_shm`.
- Extension protocols: `xdg_shell`, `wlr-layer-shell-unstable-v1`, `linux_dmabuf_v1`, `wp_fractional_scale_v1`, `viewporter`.
- Explicit synchronization via `linux-drm-syncobj-v1`.
- Rootless Xwayland socket bridge for legacy X11 applications.
- Idle memory footprint <= 35 MB RSS.

## 3. Anti-Scope (What's NOT IN)
- NO desktop shell widgets, panels, or taskbars (governed by P2).
- NO Wine/Proton runtime integration or PE executable launching (governed by P3).
- NO custom compositor plugin architecture.
- NO software rendering fallback for desktop (GPU acceleration mandatory).

## 4. Dependencies
- Phase P0 Foundation base image.
- Rust 1.80+ toolchain.
- `smithay` = "0.3", `calloop` = "0.13".
- `mesa-dri-drivers` (radeonsi, iris, intel-anv, radv).
- `libdrm` >= 2.4.120, `libinput` >= 1.25.

## 5. Deliverables
- Rust Crate: `crates/nebu-compositor/`.
- Binary: `/usr/bin/nebu-compositor`.
- Systemd Unit: `/usr/lib/systemd/user/nebu-compositor.service`.
- Integration Tests: `tests/compositor_conformance/`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P1-01 (Wayland Socket Emergence):** Compositor initializes and binds `$XDG_RUNTIME_DIR/wayland-0` within 400ms.
2. **EC-P1-02 (Client Rendering):** Standard Wayland client (`weston-terminal` / `foot`) and X11 client (`glxgears` via Xwayland) render at locked 60 FPS without graphical tearing.
3. **EC-P1-03 (Direct Scanout):** Fullscreen test surface scans out directly to DRM primary plane without compositing shader passes.
4. **EC-P1-04 (Memory Budget):** Steady-state idle memory <= 35 MB RSS on a 1080p display.
5. **EC-P1-05 (Hotplug Handling):** Connecting and disconnecting an external HDMI/DisplayPort monitor adjusts layout within 500ms without crashing compositor.

## 7. Known Risks & Mitigations
- **Risk:** Atomic commit failures on legacy multi-monitor setups.
  - *Mitigation:* Fall back cleanly to single-plane composited backbuffer commit if multi-plane atomic test fails.
