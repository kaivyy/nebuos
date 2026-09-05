# ADR-0003: Pure Wayland Display Architecture and Rejection of X11

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Graphics Engineer  
**Consulted:** PRD §11, §52, §53  

---

## 1. Context and Problem Statement
The X Window System (X11) has served Linux for nearly four decades but possesses fatal architectural flaws: universal client snooping (no security boundaries between windows), lack of native tearing-free atomic frame pacing, complex multi-DPI scaling limitations, and high latency. NebuOS must provide a modern, secure, stutter-free display foundation with crisp fractional scaling for mixed Linux and Windows applications.

## 2. Decision Drivers
- **Security and Isolation:** Windows applications and web browsers must not be able to snoop keystrokes or capture pixels from adjacent windows.
- **Frame Presentation and Latency:** Tearing-free atomic KMS presentation, zero-copy direct scanout for games, and variable refresh rate (VRR) support.
- **Fractional Scaling:** Crisp HiDPI scaling without blurry nearest-neighbor bitmap scaling.
- **Maintenance Horizon:** Major Linux ecosystems (GNOME, KDE, Fedora, Red Hat) have deprecated X11 in favor of Wayland.

## 3. Considered Options
- **Option 1: Pure Wayland Architecture with Rootless Xwayland Fallback [SELECTED]**
- **Option 2: Hybrid X11 / Wayland Session Selection**
- **Option 3: Legacy X11 Display Server (Xorg)**

## 4. Decision Outcome
**Chosen Option: Option 1 — Pure Wayland Architecture with Rootless Xwayland.**

NebuOS runs exclusively on Wayland. All native userland desktop components (`nebu-compositor`, `nebu-shell`) communicate via core Wayland protocols and modern extensions (`xdg-shell`, `wlr-layer-shell`, `linux-dmabuf-v1`, `wp_fractional_scale_v1`). Legacy X11 applications and games run through an on-demand, rootless Xwayland compatibility bridge.

### Positive Consequences
- Total process security isolation: no window can snoop another window's buffers or input stream.
- Stutter-free atomic modesetting and presentation timing.
- Wine 9.0+ native `winewayland.drv` driver eliminates X11 translation overhead for modern Windows software.
- HiDPI fractional scaling works seamlessly across heterogeneous multi-monitor setups.

### Negative Consequences
- Legacy Windows games demanding raw X11 mode-switching require Xwayland emulation and `wp_viewporter`.
- Screen recording tools must use privileged desktop portals (`xdg-desktop-portal-wlr`) rather than raw window capture.

## 5. Pros and Cons of Alternatives

### Option 2: Hybrid X11 / Wayland Sessions
- *Pros:* Maximum backward compatibility for very old software.
- *Cons:* Doubles QA testing matrix; requires maintaining two display server stacks; perpetuates X11 security vulnerabilities.

### Option 3: Legacy X11
- *Pros:* Broad legacy compatibility.
- *Cons:* Terrible multi-monitor fractional scaling; zero window security isolation; tearing and presentation jitter; obsolete upstream support.

## 6. Confirmation and Validation
- Wayland protocol conformance verified using `wayland-scanner` and automated protocol fuzzing.
- Direct scanout validated on fullscreen Vulkan benchmarks with zero compositor overhead.
