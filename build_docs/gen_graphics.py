#!/usr/bin/env python3
"""
Generate Graphics Documentation for NebuOS (docs/graphics/):
- 00-graphics-overview.md
- 01-gpu-detection.md
- 02-vulkan-opengl.md
- 03-dxvk-vkd3d.md
- 04-gpu-profiles.md
- 05-shader-cache.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs/graphics"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_file(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: graphics/{filename} ({len(content.splitlines())} lines)")

# 00-graphics-overview.md
write_file("00-graphics-overview.md", """# Graphics Subsystem Overview — NebuOS

**Status:** REVIEW  
**Purpose:** Establish the architectural design of the NebuOS graphics subsystem, hardware translation pipeline, and driver integration.

---

## 1. Scope & Rendering Philosophy
NebuOS provides uncompromising graphics performance for CAD viewports, 3D DCC tools (Maya, 3ds Max), and modern DirectX games. By utilizing Vulkan as the universal rendering substrate, NebuOS translates proprietary DirectX 9/10/11/12 and OpenGL calls directly into low-overhead GPU command streams without virtualization.

## 2. Universal Graphics Pipeline Architecture

```mermaid
graph TD
    subgraph APPS [Application API Calls]
        D3D9_11[DirectX 9 / 10 / 11: AutoCAD, Maya Viewport]
        D3D12[DirectX 12: Modern Games, Unreal Engine]
        WIN_GL[Windows OpenGL: 3ds Max, Legacy CAD]
        VULKAN_NATIVE[Native Vulkan PE / Linux]
    end

    subgraph TRANSLATION [Translation Engines]
        DXVK[DXVK 2.x - D3D9/10/11 to Vulkan]
        VKD3D[VKD3D-Proton - D3D12 to Vulkan]
        WINE_GL[Wine OpenGL Passthrough]
    end

    subgraph VULKAN_CORE [Vulkan Loader & Mesa Drivers]
        VK_LOADER[Vulkan Loader: libvulkan.so.1]
        MESA_RADV[AMD: RADV / ACO]
        MESA_ANV[Intel: ANV / Iris]
        NVIDIA_VK[NVIDIA: Proprietary Vulkan / NVK]
    end

    subgraph DISPLAY [Display Pipeline]
        WAYLAND[NebuCompositor: Wayland dmabuf]
        KMS[DRM / KMS Direct Scanout]
    end

    D3D9_11 --> DXVK
    D3D12 --> VKD3D
    WIN_GL --> WINE_GL
    VULKAN_NATIVE --> VK_LOADER

    DXVK --> VK_LOADER
    VKD3D --> VK_LOADER
    WINE_GL --> MESA_RADV
    WINE_GL --> MESA_ANV
    WINE_GL --> NVIDIA_VK

    VK_LOADER --> MESA_RADV
    VK_LOADER --> MESA_ANV
    VK_LOADER --> NVIDIA_VK

    MESA_RADV --> WAYLAND
    MESA_ANV --> WAYLAND
    NVIDIA_VK --> WAYLAND

    WAYLAND --> KMS
```

## 3. Related Documents
- [01-gpu-detection.md](01-gpu-detection.md)
- [03-dxvk-vkd3d.md](03-dxvk-vkd3d.md)
- [04-gpu-profiles.md](04-gpu-profiles.md)
""")

# 01-gpu-detection.md
write_file("01-gpu-detection.md", """# GPU Detection Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define device discovery, PCI vendor identification, driver capability queries, and hybrid graphics enumeration.

---

## 1. Detection Architecture (`nebu-gpu-probe`)
At boot and session initialization, `nebu-gpu-probe` queries DRM nodes via `drmGetDevices2()`:

```mermaid
graph TD
    INIT[Boot / Session Start] --> PROBE[drmGetDevices2 PCI Scan]
    PROBE --> VENDOR{Inspect PCI Vendor ID}
    
    VENDOR -->|0x8086| INTEL_DEV[Intel: Probe Gen9, Xe, Arc]
    VENDOR -->|0x1002| AMD_DEV[AMD: Probe GCN, RDNA1/2/3/4]
    VENDOR -->|0x10DE| NVIDIA_DEV[NVIDIA: Probe Turing, Ampere, Ada]
    
    INTEL_DEV --> HYBRID_CHECK{Multiple GPUs Present?}
    AMD_DEV --> HYBRID_CHECK
    NVIDIA_DEV --> HYBRID_CHECK
    
    HYBRID_CHECK -->|Yes| HYBRID_MAP[Classify Primary iGPU vs Secondary dGPU]
    HYBRID_CHECK -->|No| SINGLE_MAP[Assign Default System GPU]
```

## 2. Hardware Capabilities Schema
For each detected GPU, NebuOS records capability records in `/run/nebu/gpu_topology.json`:
- PCI Address (e.g. `0000:01:00.0`)
- Vendor & Device ID
- Driver in use (`amdgpu`, `i915`, `xe`, `nvidia`)
- Vulkan API version support (e.g. Vulkan 1.3)
- Dedicated VRAM vs Shared System RAM
- DRI node paths (`/dev/dri/card0`, `/dev/dri/renderD128`)

## 3. Related Documents
- [00-graphics-overview.md](00-graphics-overview.md)
- [04-gpu-profiles.md](04-gpu-profiles.md)
""")

# 02-vulkan-opengl.md
write_file("02-vulkan-opengl.md", """# Vulkan and OpenGL Architecture — NebuOS

**Status:** REVIEW  
**Purpose:** Specify the native graphics driver layer, Vulkan loader configuration, and OpenGL fallback infrastructure.

---

## 1. Vulkan As First-Class Citizen
- **Loader:** Khronos Vulkan Loader (`libvulkan.so.1`) with ICD manifests in `/usr/share/vulkan/icd.d/`.
- **Mesa Compilers:**
  - AMD: RADV with ACO shader compiler (ultra-fast compilation and stutter-free gaming).
  - Intel: ANV driver supporting modern Intel Arc and integrated Iris Xe.
  - NVIDIA: Official proprietary Vulkan driver stack.

## 2. Legacy OpenGL Fallback (`wined3d`)
For legacy GPUs lacking hardware Vulkan 1.2+ support (e.g. Intel Sandy Bridge / Ivy Bridge HD Graphics):
- NebuRuntime detects missing Vulkan extensions and automatically toggles the application's graphics profile from `dxvk` to `wined3d` (Direct3D -> OpenGL).
- Ensures backwards compatibility on 10-year-old hardware, fulfilling NebuOS's commitment to low-end systems.

## 3. Related Documents
- [00-graphics-overview.md](00-graphics-overview.md)
- [03-dxvk-vkd3d.md](03-dxvk-vkd3d.md)
""")

# 03-dxvk-vkd3d.md
write_file("03-dxvk-vkd3d.md", """# DXVK and VKD3D Integration Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Detail the deployment, DLL overrides, configuration flags, and pipeline synchronization for DXVK and VKD3D-Proton.

---

## 1. Component Responsibilities
- **DXVK:** Replaces Wine's builtin `d3d9.dll`, `d3d10core.dll`, `d3d11.dll`, and `dxgi.dll` with custom high-performance Vulkan implementations.
- **VKD3D-Proton:** Replaces `d3d12.dll`, translating Direct3D 12 root signatures, command lists, and ray-tracing pipelines into Vulkan.

## 2. Configuration & Overrides Management
NebuRuntime injects application-specific tuning files (`dxvk.conf`):

```ini
# dxvk.conf for Autodesk AutoCAD 2024
dxgi.syncInterval = 1
d3d11.maxTessFactor = 64
d3d11.enableRtHoles = True
dxvk.enableAsync = True
```

## 3. Synchronization & Frame Pacing
- Utilizes `VK_KHR_present_id` and `VK_KHR_present_wait` to synchronize with `nebu-compositor`.
- Delivers tear-free, low-latency display presentation while eliminating micro-stutters.

## 4. Related Documents
- [00-graphics-overview.md](00-graphics-overview.md)
- [05-shader-cache.md](05-shader-cache.md)
""")

# 04-gpu-profiles.md
write_file("04-gpu-profiles.md", """# GPU Profiles Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify application-level graphics policies, power-saving versus discrete performance selection, and multi-GPU routing.

---

## 1. Application-Specific GPU Routing
On hybrid dual-GPU laptops (e.g., Intel iGPU + NVIDIA RTX dGPU):

```mermaid
graph TD
    APP_LAUNCH[Application Launch Request] --> PROFILE_LOOKUP{Read GpuProfile}
    
    PROFILE_LOOKUP -->|Power Efficient| IGPU_PATH[Intel Iris Xe iGPU: Battery Friendly]
    PROFILE_LOOKUP -->|High Performance| DGPU_PATH[NVIDIA RTX dGPU: Maximum Compute]
    
    IGPU_PATH --> APP_OFFICE[Microsoft Word / Excel / Web Browser]
    DGPU_PATH --> APP_HEAVY[AutoCAD 2024 / Maya 2026 / 3ds Max / Steam Games]
```

## 2. Environment Variables Injection Table

| Policy Name | Target Workload | AMD Hybrid Environment | NVIDIA Hybrid Environment |
|---|---|---|---|
| `integrated_only` | Office, PDF viewer, media player | `DRI_PRIME=0` | `__NV_PRIME_RENDER_OFFLOAD=0` |
| `discrete_forced` | AutoCAD, Maya, 3ds Max, 3D Games | `DRI_PRIME=1` | `__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia __VK_LAYER_NV_optimus=NVIDIA_only` |
| `adaptive` | Image editors, CAD 2D | Defaults to iGPU; switches to dGPU if external monitor connected | Same as AMD |

## 3. Related Documents
- [00-graphics-overview.md](00-graphics-overview.md)
- [01-gpu-detection.md](01-gpu-detection.md)
""")

# 05-shader-cache.md
write_file("05-shader-cache.md", """# Shader Cache Architecture Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Detail Vulkan pipeline caching, DXVK state cache persistence, disk quotas, and shader compilation stutter elimination.

---

## 1. Problem Statement: Shader Compilation Stutter
Direct3D pipelines compile shaders synchronously during draw calls. Under Vulkan translation, compiling pipeline state objects (PSOs) at runtime introduces severe frame drops (stutter). NebuOS mitigates this via persistent two-tier caching.

## 2. Two-Tier Cache Topology

```mermaid
graph TD
    DRAW[Application Draw Call] --> MEM_CACHE{Vulkan Pipeline in Memory Cache?}
    MEM_CACHE -->|Hit| RENDER[Direct GPU Execution - 0ms Delay]
    MEM_CACHE -->|Miss| DISK_CACHE{Present in ~/.nebu/cache/shaders?}
    DISK_CACHE -->|Hit| LOAD_DISK[Fast Binary Load from Disk]
    LOAD_DISK --> RENDER
    DISK_CACHE -->|Miss| COMPILE[Mesa ACO / Driver Compilation]
    COMPILE --> WRITE_DISK[Write to Disk State Cache]
    WRITE_DISK --> RENDER
```

## 3. Cache Storage & Maintenance
- **Directory:** `~/.nebu/cache/shaders/<app_id>/`.
- **Format:** DXVK `.dxvk-cache` state files + Mesa driver cache (`mesa_shader_cache_db`).
- **Disk Quota:** 2 GB per application max; automated LRU (Least Recently Used) cache pruning when disk capacity falls below 10% free space.

## 4. Related Documents
- [03-dxvk-vkd3d.md](03-dxvk-vkd3d.md)
- [../performance/05-storage.md](../performance/05-storage.md)
""")

print("Graphics documentation generated successfully.")
