# ADR-0006: Proton and DXVK/VKD3D Integration for 3D and Gaming Workloads

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Graphics Engineer  
**Consulted:** PRD §17, §25, §26, §73, §74  

---

## 1. Context and Problem Statement
Standard upstream Wine translates Microsoft Direct3D calls to OpenGL via WineD3D. While sufficient for basic 2D utilities, WineD3D suffers from poor performance, high CPU overhead, and limited compatibility with modern Direct3D 11 and Direct3D 12 applications (CAD software, 3D renderers, and modern games). Valve’s Proton, DXVK, and VKD3D-Proton project translate Direct3D 9/10/11/12 directly to Vulkan. We must determine how to incorporate these technologies into NebuOS.

## 2. Decision Drivers
- **Graphics Performance:** Native-level frame rates (>= 90% of bare-metal Windows performance) on modern GPUs.
- **Vulkan Efficiency:** Direct utilization of Mesa RADV, ANV, and NVIDIA Vulkan drivers with explicit synchronization.
- **Low CPU Overhead:** Asynchronous pipeline compilation and state caching to eliminate shader stutter.
- **Modern API Coverage:** Complete support for Direct3D 11 and Direct3D 12 workloads.

## 3. Considered Options
- **Option 1: Integrated Proton and DXVK/VKD3D-Proton Layer alongside Wine [SELECTED]**
- **Option 2: Rely Solely on Upstream WineD3D (OpenGL)**
- **Option 3: Write a Custom Direct3D-to-Vulkan Translator**

## 4. Decision Outcome
**Chosen Option: Option 1 — Integrated Proton and DXVK/VKD3D-Proton Stack.**

NebuOS bundles pre-compiled, upstream-validated DXVK (2.3+) and VKD3D-Proton (2.12+) libraries in `/usr/lib/nebu/graphics/`. For 3D CAD software and games, NebuRuntime automatically configures Wine prefixes to override `d3d11.dll`, `d3d12.dll`, and `dxgi.dll` with DXVK/VKD3D binaries. For standalone gaming titles, NebuOS provisions Proton runtimes directly.

### Positive Consequences
- Dramatic performance gains: 3x to 5x higher framerates compared to WineD3D on Direct3D 11 workloads.
- Flawless execution of modern Direct3D 12 applications on Vulkan 1.3 hardware.
- Persistent shader state caching (`.dxvk-cache`) eliminates visual hitching and stutter.

### Negative Consequences
- Requires Vulkan 1.3 capable GPU hardware (legacy GPUs fall back to WineD3D OpenGL).
- Increases disk footprint of compatibility runtimes by ~120 MB.

## 5. Pros and Cons of Alternatives

### Option 2: Rely Solely on WineD3D
- *Pros:* Works on older GPUs lacking Vulkan.
- *Cons:* Terrible performance; stuttering; inability to run Direct3D 12 software; unacceptable for modern desktop OS.

### Option 3: Custom Translator
- *Pros:* Theoretical custom tailoring.
- *Cons:* Multi-year engineering effort duplicating Valve's multimillion-dollar investment in DXVK/VKD3D.

## 6. Confirmation and Validation
- Automated benchmarking comparing D3D11 rendering performance on NebuOS vs. bare-metal Windows 11 on identical hardware.
