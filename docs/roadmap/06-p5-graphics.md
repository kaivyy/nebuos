# Phase P5: Graphics Subsystem Specification — NebuOS

**Status:** APPROVED  
**Phase:** P5  
**Target Duration:** Sprint 15–17  
**Prerequisite:** Phase P1, P3, P4  

---

## 1. Objective
Integrate the DirectX-to-Vulkan translation layers (DXVK and VKD3D-Proton), multi-GPU dynamic routing (PRIME offload), and the centralized shader caching engine. P5 enables hardware-accelerated 3D rendering for CAD software, video editing suites, and modern games with >= 90% of native Windows performance.

## 2. Scope (What's IN)
- Packaging and version pinning of DXVK (2.3+) and VKD3D-Proton (2.12+).
- Automated DLL override injection (`d3d9`, `d3d11`, `dxgi`, `d3d12`) into application prefixes.
- GPU detection CLI and library `crates/nebu-gpu-probe`.
- Dynamic PRIME multi-GPU offload (desktop on iGPU, 3D on dGPU).
- Centralized shader state caching (`~/.cache/nebu/shaders/<app_id>/`).
- Per-application `dxvk.conf` tuning generation.

## 3. Anti-Scope (What's NOT IN)
- NO recompilation or source-level forks of DXVK/VKD3D.
- NO DirectX 12 emulation on pre-Vulkan 1.3 hardware (OpenGL WineD3D fallback used).
- NO proprietary SLI/Crossfire multi-GPU rendering.

## 4. Dependencies
- Mesa Drivers >= 24.0 (RADV, ANV, NVK).
- Vulkan Loader >= 1.3.275.
- DXVK and VKD3D-Proton release binaries.

## 5. Deliverables
- Binary Stores: `/usr/lib/nebu/graphics/{dxvk,vkd3d-proton}/`.
- CLI: `/usr/bin/nebu-gpu-probe`.
- System Cache Directory: `/usr/share/nebu/preseeded-caches/`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P5-01 (D3D11 Parity Gate):** Direct3D 11 benchmark (Heaven / Valley) achieves >= 90% of bare-metal Windows framerate on identical hardware.
2. **EC-P5-02 (D3D12 Vulkan Execution):** Direct3D 12 benchmark initializes and renders cleanly via VKD3D-Proton with zero Vulkan validation errors.
3. **EC-P5-03 (PRIME Offload Routing):** Setting `gpu_preference: "discrete"` routes rendering to discrete GPU node while compositing scanout remains on primary display.
4. **EC-P5-04 (Shader Cache Deduplication):** Subsequent application runs exhibit zero shader compilation stutters (99th percentile frame time <= 16.6ms).
5. **EC-P5-05 (Idle Power Gate):** Discrete GPU enters PCIe D3Cold state (0 Watts) when no 3D applications are active.

## 7. Known Risks & Mitigations
- **Risk:** Shader compilation hitching during initial application run.
  - *Mitigation:* Enable `dxvk.enableAsync = true` and utilize persistent state caching (`DXVK_STATE_CACHE=1`).
