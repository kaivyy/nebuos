# ADR-0019: Slint Adoption for NebuShell Desktop Toolkit

**Status:** APPROVED  
**Date:** 2026-09-05  
**Authors:** Principal Desktop Systems Architect, Rust Architect, UX Architect, Performance Engineer  
**Deciders:** NebuOS Core Architecture Group  
**Resolves:** Open Question OQ-001 (Slint vs Iced)  
**Related ADRs:** ADR-0004 (Rust Implementation), ADR-0009 (NebuShell UI Architecture), ADR-0013 (UI Design System & Iconography)  
**Consulted:** PRD §12, §13, §62, §63, §96  

---

## 1. Context and Problem Statement

NebuOS requires a native, lightweight, memory-efficient GUI toolkit for its desktop shell (`nebu-shell`). The desktop shell orchestrates core human-interface surfaces: the bottom taskbar, top menu bar, floating application dock, fast application launcher (`nebu-launcher`), status tray, quick settings flyout, volume/brightness on-screen displays (OSD), and session lock screen.

Milestone P1 demonstrated that `nebu-compositor` can operate within ~28 MB RSS on headless and virtualized Linux baselines. To fulfill NebuOS foundational invariant of running smoothly on modest hardware (4GB RAM, Intel N4020/Celeron-class CPUs), the desktop shell must adhere to strict resource constraints:
- Steady-state idle memory footprint budgeted at <= 45 MB RSS.
- Combined compositor + shell memory footprint capped at <= 80 MB RSS.
- Sub-80ms application launcher invocation latency.
- Dynamic runtime switching between desktop interaction paradigms (Windows-like, macOS-like, Traditional) in <= 150 ms without process restart.

Open Question `OQ-001` left the selection between **Slint** and **Iced** unresolved, creating architectural ambiguity across roadmap and specification documents.

---

## 2. Decision

NebuOS formally adopts **Slint (version 1.7+)** as the authoritative, exclusive native GUI toolkit for `nebu-shell` and subsequent first-party desktop utilities (`nebu-installer-ui`, `nebu-marketplace-ui`).

`OQ-001` is hereby formally resolved and closed.

---

## 3. Alternatives Considered and Rejected

| Alternative | Evaluation & Technical Characteristics | Rejection Rationale |
|---|---|---|
| **Iced (0.12+)** | Pure Rust GUI library implementing the Elm architecture (Model-View-Update). Relies on WGPU/tiny-skia renderers. | **Rejected:** Elm architecture requires regenerating widget trees on state updates, leading to higher CPU overhead on idle. Measured baseline memory footprints in community benchmarks average 35–50 MB RSS. Lacks declarative hot-reloading markup for rapid theme switching; requires custom forks for `wlr-layer-shell` support. |
| **GTK4 / libadwaita** | Mature C/GObject desktop widget toolkit. | **Rejected:** Violates pure-Rust core invariant (ADR-0004). Heavy C runtime dependency graph (GLib, Pango, ATK, Cairo) adds >150 MB disk footprint and higher steady-state memory overhead (>70 MB RSS). |
| **Qt 6 / QML** | Mature C++ declarative UI framework. | **Rejected:** Introduces heavy C++ toolchains, complex MOC build steps, large shared library dependencies, and commercial licensing ambiguity. |
| **Electron / CEF / Tauri** | Webview and Chromium-based application shells. | **Rejected:** Categorically prohibited by ADR-0009 and PRD §12. Steady-state memory consumption exceeds 250 MB RSS, violating hardware targets. |

---

## 4. Architectural Justification: Why Slint?

### 4.1 Rust Integration and Build-Time Verification
Slint provides first-class Rust integration via `slint_build` in `build.rs`. Declarative `.slint` UI templates are compiled directly into native Rust structs and code at compile time. Property bindings, signal connections, and component types are statically verified by the Rust compiler (`rustc`), completely eliminating runtime markup parse failures.

### 4.2 Reactive Data Binding and Dirty-Flag Optimization
Unlike Elm-style frameworks that recreate view hierarchies, Slint uses two-way reactive property binding with fine-grained dirty tracking. When a system property changes (e.g. battery percentage incremented by 1%), only the single text glyph and progress bar are marked dirty and re-rendered. This enables near-zero idle CPU utilization (<0.2%).

### 4.3 Declarative Styling and ADR-0013 Alignment
Slint uses a clean, CSS-inspired declarative markup language. As codified in ADR-0013, NebuOS separates visual design tokens (colors, corner radii, elevation shadows, typography) from business logic. Slint templates bind natively to external design tokens loaded from TOML manifests, supporting instantaneous live hot-reloading without recompilation or shell restarts.

### 4.4 Wayland Integration and Layer-Shell Support
Slint natively supports Wayland via its `winit` and Smithay integrations. Furthermore, Slint provides low-level window handle extraction (`raw-window-handle`), allowing `nebu-shell` to attach underlying `wl_surface` handles directly to `zwlr_layer_shell_v1` surfaces managed by `nebu-compositor`.

### 4.5 Rendering Backend Flexibility
Slint supports multiple interchangeable rendering backends:
1. **FemtoVG (OpenGL ES 2.0+):** Accelerated GPU rendering for standard Intel, AMD, and NVIDIA hardware.
2. **Software Renderer:** Pure CPU rasterizer rendering directly into shared-memory (`wl_shm`) pixel buffers. This guarantees that `nebu-shell` functions seamlessly in virtualized environments (e.g. Proxmox VM 102 with Mesa `llvmpipe`) where hardware 3D acceleration may be disabled.

### 4.6 Accessibility (AT-SPI2) Integration
Slint integrates natively with `accesskit`, generating standardized semantic accessibility trees that map directly to Linux screen readers (Orca) via AT-SPI2 D-Bus interfaces (`org.a11y.atspi.Accessible`).

### 4.7 HiDPI and Fractional Scaling
Slint handles physical vs. logical pixel coordinates cleanly. In conjunction with Wayland protocol `wp_fractional_scale_v1`, Slint rasterizes text and vector assets at the exact target device pixel ratio (e.g. 1.25x or 1.5x), preventing the bilinear scaling blur common in webviews.

---

## 5. Performance Distinctions: Evidence vs. Targets

To maintain strict engineering rigor, performance metrics are classified according to NebuOS 5-tier taxonomy:

| Metric | Stated Target | Empirical Classification | Verification Strategy |
|---|---|---|---|
| **Shell Idle RSS** | <= 45 MB RSS | **Engineering Target** (Based on Slint benchmark baselines; unverified in NebuOS production) | Measure `nebu-shell` RSS via `smaps_rollup` during steady-state idle in VM 102. |
| **Combined Compositor + Shell RSS** | <= 80 MB RSS | **Hard Requirement** | Non-negotiable release gate. P1 compositor verified at 28 MB; shell must remain <= 52 MB. |
| **Launcher Open Latency** | <= 80 ms | **Hard Requirement** | Timestamp from hotkey release event to first damaged frame commit. |
| **OSD Visibility Latency** | <= 20 ms | **Hard Requirement** | Pre-allocated layer surface alpha toggled on hardware volume/brightness keysym. |
| **Paradigm Switch Time** | <= 150 ms | **Engineering Target** | In-memory layout swap; assert zero dropped compositor frames. |

---

## 6. Dependency and Licensing Policy

1. **Approved Version:** Slint version `1.7` (or newer stable release).
2. **Cargo Dependencies:**
   - `slint = { version = "1.7", default-features = false, features = ["compat-1-2", "renderer-femtovg", "renderer-software"] }`
   - `slint-build = "1.7"` (in `build-dependencies`)
3. **Licensing Compliance:**
   - Slint is dual-licensed under GPLv3 and the Slint Royalty-Free Desktop/Embedded License.
   - NebuOS components licensed under MPL-2.0 utilize Slint in full compliance with Slint desktop royalty-free terms, permitting distribution of unmodified and customized binaries.

---

## 7. Security Implications

- **Memory Safety:** Slint is implemented in 100% safe Rust. Its template compiler generates safe Rust code governed by `#![forbid(unsafe_code)]`.
- **Privilege Separation:** `nebu-shell` runs entirely as an unprivileged user process (`UID 1000`). Slint code never touches raw hardware device nodes or invokes privileged ioctls.
- **Asset Sanitization:** Slint parses vector assets safely. Third-party application icons are ingested via sanitized PNG/SVG rasterizers to protect against XML entity expansion attacks.

---

## 8. Testing Implications

- **Headless Testing:** Slint supports a headless rendering backend (`backend-testing`), allowing automated unit and integration tests to instantiate UI widgets, simulate pointer/keyboard events, and verify widget state assertions in CI without requiring an active DRM display.
- **Visual Regression Testing:** Headless frame grabber captures framebuffers and asserts pixel/checksum consistency against reference golden images.

---

## 9. Consequences

### Positive Consequences
- Resolves the long-standing toolkit ambiguity across the NebuOS documentation suite.
- Eliminates risk of webview bloat (>250 MB RAM).
- Enables live theme hot-reloading matching ADR-0013.
- Unifies styling across `nebu-shell`, `nebu-installer-ui`, and `nebu-marketplace-ui`.

### Negative Consequences / Trade-offs
- Core desktop widgets (taskbar buttons, volume sliders, menus) must be authored from foundational Slint primitives.
- Slint template language (`.slint`) requires familiarization for developers accustomed to HTML/CSS or GTK XML.

---

## 10. Reconsideration Conditions

This architectural decision will be reopened for technical review only if:
1. Slint steady-state idle memory footprint in `nebu-shell` empirically exceeds 65 MB RSS despite optimization.
2. An unresolvable protocol incompatibility arises between Slint windowing backend and `wlr-layer-shell-unstable-v1` in `nebu-compositor`.
3. Upstream Slint introduces restrictive licensing changes that prevent open distribution of NebuOS.
