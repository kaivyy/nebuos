#!/usr/bin/env python3
"""
Generator for Batch 2: Graphics subsystem missing specifications:
- graphics/04-dxvk-vkd3d.md
- graphics/05-gpu-profiles.md
- graphics/06-shader-cache.md
"""

import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {path} ({len(content.splitlines())} lines)")

# 1. graphics/04-dxvk-vkd3d.md
g4 = r"""# DXVK and VKD3D-Proton Translation Layer Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the deployment, DLL override configuration, runtime translation, dxvk.conf tuning, and memory management for DXVK (Direct3D 9/10/11 -> Vulkan) and VKD3D-Proton (Direct3D 12 -> Vulkan) in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P5 graphics translation pipeline.

## 2. Purpose
Windows productivity software (CAD, 3D modelling, media suites) and games rely heavily on Microsoft Direct3D APIs. Since NebuOS does not run Windows or a virtual machine, Direct3D calls must be translated natively to Vulkan. This specification defines how DXVK and VKD3D-Proton are packaged, injected into per-application Wine prefixes, configured, and optimized.

## 3. Scope
- Packaging and version pinning of DXVK (2.3+) and VKD3D-Proton (2.12+).
- DLL override mechanisms (`d3d9.dll`, `d3d10core.dll`, `d3d11.dll`, `dxgi.dll`, `d3d12.dll`, `d3d12core.dll`).
- Generation and injection of declarative `dxvk.conf` and `vkd3d-proton.conf` profiles.
- Asynchronous pipeline compilation and state cache management.
- Integration with Mesa RADV, ANV, and NVK drivers.

## 4. Non-goals
- Modifying the upstream source code of DXVK or VKD3D-Proton.
- Emulating DirectX 12 on legacy GPUs lacking native Vulkan 1.3 support.
- Translation of Direct3D to OpenGL (WineD3D used solely as legacy fallback).
- Bypassing GPU VRAM physical hardware constraints.

## 5. Requirements
1. **R-TRN-01:** Deploy pre-compiled 32-bit and 64-bit release binaries of DXVK and VKD3D-Proton in `/usr/lib/nebu/graphics/`.
2. **R-TRN-02:** Provide automated atomic symlinking or hardlinking of translation DLLs into prefix `drive_c/windows/system32/` and `syswow64/`.
3. **R-TRN-03:** Configure Wine DLL overrides to enforce `native,builtin` for translated Direct3D modules.
4. **R-TRN-04:** Provide fine-grained per-application `dxvk.conf` tuning for frame pacing, max frame latency, and pipeline caching.
5. **R-TRN-05:** Deliver >= 90% of native Windows Direct3D 11/12 performance on compatible hardware.

## 6. Architecture
Direct3D calls from Win32 applications execute within the Wine process space and are intercepted by DXVK/VKD3D libraries:

```mermaid
graph TD
    subgraph Win32Process[Windows Application in Wine]
        APP[CAD / Game Application]
        D3D11[d3d11.dll / dxgi.dll Native Override]
        D3D12[d3d12.dll Native Override]
    end

    subgraph TranslationLayer[NebuOS Translation Layer]
        DXVK[DXVK Translation Engine]
        VKD3D[VKD3D-Proton Translation Engine]
        CONF[dxvk.conf / Environment Injection]
    end

    subgraph VulkanDriver[Host Graphics Stack]
        VULKAN_LOADER[libvulkan.so.1]
        MESA_ICD[Mesa RADV / ANV / NVK ICD]
        DRM_KMS[Linux DRM / KMS]
    end

    APP -->|Direct3D 9/10/11 calls| D3D11
    APP -->|Direct3D 12 calls| D3D12
    D3D11 --> DXVK
    D3D12 --> VKD3D
    CONF -.-> DXVK
    CONF -.-> VKD3D
    DXVK -->|Standard Vulkan 1.3 API| VULKAN_LOADER
    VKD3D -->|Standard Vulkan 1.3 API| VULKAN_LOADER
    VULKAN_LOADER --> MESA_ICD
    MESA_ICD --> DRM_KMS
```

## 7. Components
1. **Translation Library Store (`/usr/lib/nebu/graphics/`):** Houses versioned releases:
   - `/usr/lib/nebu/graphics/dxvk/x64/` and `x32/`
   - `/usr/lib/nebu/graphics/vkd3d-proton/x64/` and `x32/`
2. **DLL Override Provisioner:** Copies or reflinks DLLs into prefix and sets `WINEDLLOVERRIDES="d3d11,dxgi,d3d9,d3d12=n"` in the app launch environment.
3. **Config Injector:** Generates dynamic `dxvk.conf` inside application working directory based on Compatibility Profile flags.
4. **State Cache Coordinator:** Directs DXVK pipeline state cache to persistent storage at `~/.cache/nebu/shaders/<app_id>/`.
5. **Vulkan Capability Validator:** Verifies device supports required extensions before activating DXVK/VKD3D.

## 8. Data Flow
1. Application initiates Direct3D device creation: `D3D11CreateDevice`.
2. Wine loader resolves `d3d11.dll` to DXVK native PE build in prefix `system32`.
3. DXVK initializes Vulkan physical device through `libvulkan.so.1`.
4. Shader bytecode (HLSL SM 4.0/5.0) intercepted by DXVK and compiled to SPIR-V intermediate representation.
5. SPIR-V passed to Mesa Vulkan driver, which compiles machine code for target GPU hardware.
6. Swapchain buffers presented directly to Wayland surface via `VK_KHR_wayland_surface`.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant App as Windows Executable
    participant DXVK as DXVK (d3d11.dll)
    participant Loader as Vulkan Loader
    participant Mesa as Mesa Vulkan Driver
    participant GPU as Hardware GPU

    App->>DXVK: D3D11CreateDeviceAndSwapChain()
    DXVK->>Loader: vkCreateInstance()
    Loader->>Mesa: Enumerate Physical Devices
    Mesa-->>DXVK: PhysicalDevice(Vulkan 1.3)
    DXVK->>Mesa: vkCreateDevice(extensions: timeline_semaphore, dynamic_rendering)
    App->>DXVK: DrawIndexed(primitive_count)
    DXVK->>DXVK: Compile D3D bytecode -> SPIR-V
    DXVK->>Mesa: vkCmdDrawIndexed()
    Mesa->>GPU: Submit command buffer to hardware queue
    DXVK->>Mesa: vkQueuePresentKHR()
```

## 10. Interfaces
- **Direct3D Client APIs:** Direct3D 9Ex, 10.0, 10.1, 11.0, 11.1, 11.2, 11.4, 12.0, 12.1, 12.2.
- **Vulkan Host APIs:** Vulkan 1.3 Core with required extensions:
  - `VK_EXT_custom_border_color`
  - `VK_EXT_descriptor_indexing`
  - `VK_KHR_timeline_semaphore`
  - `VK_EXT_transform_feedback`
- **Tuning Configuration (`dxvk.conf`):**
  ```ini
  dxvk.enableAsync = true
  dxvk.numCompilerThreads = 4
  dxvk.maxFrameLatency = 1
  d3d11.samplerAnisotropy = 16
  ```

## 11. Dependencies
- Upstream DXVK release builds (MPL-2.0 / Zlib).
- Upstream VKD3D-Proton release builds (LGPL-2.1).
- Mesa Vulkan drivers (`mesa-vulkan-drivers`): RADV (AMD), ANV (Intel), NVK (NVIDIA).
- Vulkan Loader (`vulkan-loader`) >= 1.3.275.

## 12. Security
- Translation libraries execute strictly within unprivileged Bubblewrap user sandbox.
- Direct hardware access restricted to `/dev/dri/renderD128` (KMS master nodes blocked).
- DXVK state cache parsed with bounds checking to prevent buffer overflow attacks from malicious cache files.

## 13. Resource Requirements
- **Disk Space:** ~85 MB for complete 32-bit and 64-bit DXVK + VKD3D library bundle.
- **RAM Overhead:** DXVK translation runtime structures: 35–80 MB RSS depending on scene complexity.
- **VRAM Footprint:** Translation tracking structures require ~120 MB VRAM overhead above raw application assets.

## 14. Failure Modes
1. **Missing Vulkan Extension:** Target GPU driver lacks mandatory extension (e.g. `VK_EXT_transform_feedback`).
2. **SPIR-V Compilation Failure:** Obscure Direct3D shader bytecode features unsupported by translator.
3. **VRAM Exhaustion:** Application requests more video memory than physically available.
4. **Pipeline Stutter:** Initial shader compilation introduces visible frame drops.

## 15. Recovery Behavior
- When mandatory Vulkan 1.3 extensions are absent, runtime falls back to WineD3D (OpenGL translation) and issues a warning notification.
- In shader compilation failure, DXVK falls back to safe reference compilation pipeline and dumps failing shader bytecode to `~/.local/share/nebu/shader-errors/`.
- Pipeline stutter mitigated by persistent state caching (`DXVK_STATE_CACHE=1`) and background multi-threaded compilation (`dxvk.enableAsync=true`).

## 16. Testing Requirements
- Automated test executing DXVK test suite across synthetic Direct3D 9, 11, and 12 benchmarks.
- Memory leak test running continuous rendering loops for 12 hours.
- Visual regression comparison between native Windows capture and NebuOS DXVK output (SSIM >= 0.98).

## 17. Performance Requirements
- Translation CPU overhead: <= 3% total CPU time spent in DXVK/VKD3D translation logic.
- Framerate parity: >= 90% of native Windows performance on AMD RADV and Intel ANV.
- Input latency impact: <= 1.0ms added by translation queue.

## 18. Compatibility Considerations
- CAD and 3D modeling tools (AutoCAD, Blender Windows build) utilize specific Direct3D 11 feature levels; DXVK exposes `D3D_FEATURE_LEVEL_11_1` cleanly.
- Legacy DirectX 9 games requiring fixed-function pipelines are handled via DXVK's D3D9 implementation.

## 19. Open Questions
- **OQ-TRN-01:** Should `dxvk-async` patches be enabled by default for gaming profiles despite potential minor visual pop-in?
- **OQ-TRN-02:** What is the optimal memory threshold for automatic DXVK state cache garbage collection?

## 20. Related Documents
- [00-graphics-specification.md](00-graphics-specification.md)
- [01-gpu-detection.md](01-gpu-detection.md)
- [02-mesa-integration.md](02-mesa-integration.md)
- [03-vulkan-opengl.md](03-vulkan-opengl.md)
- [05-gpu-profiles.md](05-gpu-profiles.md)
- [06-shader-cache.md](06-shader-cache.md)
"""

write_file("/root/NebuOS/docs/graphics/04-dxvk-vkd3d.md", g4)

# 2. graphics/05-gpu-profiles.md
g5 = r"""# GPU Profiles Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the declarative GPU profile schema, per-application hardware assignment, multi-GPU routing (iGPU vs dGPU), and runtime environment variable injection in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P5 GPU management.

## 2. Purpose
Modern computing devices frequently feature heterogeneous graphics hardware: power-efficient integrated GPUs (iGPU) alongside high-performance discrete GPUs (dGPU). This specification defines how NebuOS models GPU profiles, matches applications to optimal graphics hardware, and configures runtime environment variables (PRIME, DRI_PRIME, VK_ICD_FILENAMES) transparently.

## 3. Scope
- Declarative JSON schema for GPU profiles.
- Automated GPU routing heuristics (productivity vs. 3D rendering/gaming).
- Dynamic runtime environment variable generation.
- Fallback chain when requested GPU hardware is disconnected or unavailable.
- User customization and override persistence in SQLite and configuration files.

## 4. Non-goals
- Dynamic real-time migration of active rendering contexts across physical GPUs without application restart.
- Proprietary multi-GPU SLI/Crossfire bridging.
- Direct PCI passthrough to virtual machines (NebuOS does not use VMs).

## 5. Requirements
1. **R-PRF-01:** Automatically detect multi-GPU topologies (Intel+NVIDIA, AMD+NVIDIA, Intel+AMD) during system initialization.
2. **R-PRF-02:** Route desktop compositor and lightweight applications to low-power iGPU by default to conserve battery and thermal budget.
3. **R-PRF-03:** Route certified 3D CAD software, video editors, and games to discrete GPU (dGPU) automatically via profile database.
4. **R-PRF-04:** Support declarative profile overrides stored in JSON and queryable via D-Bus `org.nebu.Runtime1`.
5. **R-PRF-05:** Provide seamless fallback to iGPU if external eGPU is detached during system operation.

## 6. Architecture
GPU profile selection operates during application launch preparation inside `nebu-runtime-daemon`:

```mermaid
graph TD
    subgraph AppLaunch[Launch Request]
        REQ[Launch Request for App ID]
        PROBE[GPU Detection Cache]
    end

    subgraph ProfileEngine[GPU Profile Engine]
        DB[compat.db / Local Overrides]
        RESOLVER[Profile & GPU Resolver]
        ENV_GEN[Environment Variable Generator]
    end

    subgraph ExecutionTarget[Execution Environment]
        BWRAP[Bubblewrap Container]
        IGPU[Render Node: /dev/dri/renderD128 - iGPU]
        DGPU[Render Node: /dev/dri/renderD129 - dGPU]
    end

    REQ --> RESOLVER
    PROBE --> RESOLVER
    DB --> RESOLVER
    RESOLVER --> ENV_GEN
    ENV_GEN --> BWRAP
    BWRAP -->|DRI_PRIME=0| IGPU
    BWRAP -->|DRI_PRIME=1 / VK_DEVICE| DGPU
```

## 7. Components
1. **GPU Topology Store (`/run/nebu/gpu_topology.json`):** Ephemeral system state generated by `nebu-gpu-probe` on boot.
2. **Profile Resolver:** Matches application fingerprint against database profiles and resolves optimal GPU assignment: `Integrated`, `Discrete`, `External`, or `Auto`.
3. **PRIME Environment Injector:** Sets standard Linux offload environment variables:
   - For AMD/Intel dGPU: `DRI_PRIME=1`
   - For NVIDIA proprietary/open dGPU: `__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia __VK_LAYER_NV_optimus=NVIDIA_only`
4. **Device Node Filter:** Ensures Bubblewrap sandbox mounts the correct `/dev/dri/renderD12X` node based on profile.

## 8. Data Flow
1. User requests launch of `autocad.exe`.
2. `neburuntimed` queries `compat.db` for app profile.
3. Profile indicates:
   ```json
   {
     "gpu": {
       "preferred_device": "discrete",
       "power_profile": "performance",
       "dxvk_config": {
         "d3d11.maxTessFactor": "64"
       }
     }
   }
   ```
4. Resolver inspects `/run/nebu/gpu_topology.json`: finds AMD Radeon 780M (iGPU, node 128) and NVIDIA RTX 4060 (dGPU, node 129).
5. Injects offload variables into launch command and maps `/dev/dri/renderD129` into sandbox container.
6. Application starts on RTX 4060; compositing presentation surfaces handed over to `nebu-compositor` via Wayland DMA-BUF sharing.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant Runtime as nebu-runtime-daemon
    participant Resolver as GPU Profile Resolver
    participant Topo as GPU Topology
    participant Sandbox as Bubblewrap Sandbox

    Runtime->>Resolver: ResolveGpuAssignment(app_id="autocad-2024")
    Resolver->>Topo: Read active devices
    Topo-->>Resolver: [Device 0: Intel UHD, Device 1: NVIDIA RTX]
    Resolver->>Resolver: Match preference ("discrete") -> Device 1
    Resolver-->>Runtime: GpuAssignmentResult(device=1, env_vars={...}, render_node="/dev/dri/renderD129")
    Runtime->>Sandbox: Spawn with resolved environment and device nodes
```

## 10. Interfaces
- **JSON Profile Schema:**
  ```json
  {
    "$schema": "https://nebuos.org/schemas/gpu-profile-v1.json",
    "app_id": "com.autodesk.autocad2024",
    "gpu_preference": "discrete",
    "vulkan_icd": "/usr/share/vulkan/icd.d/nvidia_icd.json",
    "power_state": "high_performance",
    "environment": {
      "DXVK_HUD": "0",
      "VKD3D_CONFIG": "no_upload_hvv"
    }
  }
  ```
- **CLI Inspection Interface:** `nebu-gpu-probe --list-devices --json`

## 11. Dependencies
- `mesa-demos` / `vulkan-tools` (`vulkaninfo`).
- Linux DRM subsystem (`libdrm`).
- System topology cache `/run/nebu/gpu_topology.json`.

## 12. Security
- Application sandboxes are restricted strictly to designated GPU render nodes; DRM master control nodes (`/dev/dri/card*`) remain completely blocked.
- Privileged GPU firmware debugging interfaces (`/sys/kernel/debug/dri/*`) are never exposed inside containers.

## 13. Resource Requirements
- Profile resolution execution time: <= 1.5ms.
- Memory footprint of resolver module: <= 200 KB RSS.
- Zero polling threads; state generated statically at boot and updated strictly on hotplug uevents.

## 14. Failure Modes
1. **Discrete GPU Power Gated:** dGPU is asleep via Runtime D3 and fails to power on within timeout.
2. **Missing dGPU Driver:** NVIDIA proprietary driver module missing after kernel update.
3. **eGPU Sudden Disconnection:** External Thunderbolt/USB4 GPU unplugged during active session.

## 15. Recovery Behavior
- If dGPU fails to respond within 2.0s, resolver falls back immediately to iGPU and logs warning to `journald`.
- Missing kernel module triggers automatic fallback to Nouveau or integrated graphics.
- eGPU disconnection sends SIGTERM to affected sandboxed processes with interactive data recovery alert.

## 16. Testing Requirements
- Unit tests validating JSON schema conformance across sample profiles.
- Mock multi-GPU test harness verifying correct environment variable injection for AMD, Intel, and NVIDIA configurations.
- Stress test verifying clean fallback behavior when secondary GPU is absent.

## 17. Performance Requirements
- GPU profile resolution latency: <= 2.0ms.
- Power overhead of idle dGPU when all apps routed to iGPU: 0 Watts (complete PCIe Runtime D3Cold poweroff).

## 18. Compatibility Considerations
- Certain legacy CAD applications fail when running under PRIME offloading due to hardcoded adapter enumeration; profiles inject `DXVK_FILTER_DEVICE_NAME` to present solely the target GPU.

## 19. Open Questions
- **OQ-GPU-01:** Should NebuOS provide an interactive GUI switcher in the Quick Settings tray allowing users to force all apps to dGPU on AC power?
- **OQ-GPU-02:** What is the optimal threshold for automatic battery-saving downclocking of iGPU shader clocks?

## 20. Related Documents
- [00-graphics-specification.md](00-graphics-specification.md)
- [01-gpu-detection.md](01-gpu-detection.md)
- [02-mesa-integration.md](02-mesa-integration.md)
- [04-dxvk-vkd3d.md](04-dxvk-vkd3d.md)
- [06-shader-cache.md](06-shader-cache.md)
"""

write_file("/root/NebuOS/docs/graphics/05-gpu-profiles.md", g5)

# 3. graphics/06-shader-cache.md
g6 = r"""# Shader Cache Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the unified shader cache architecture, disk layout, eviction policies, cross-prefix cache sharing, and corruption recovery mechanisms in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P5 shader caching.

## 2. Purpose
Shader compilation is a primary cause of runtime stutter and latency in translated Windows applications and games. NebuOS implements a high-performance, centralized shader caching architecture that manages DXVK state caches, Mesa pipeline caches, and Vulkan binary caches across isolated application prefixes without compromising security or data integrity.

## 3. Scope
- Directory layout for system and user shader caches.
- Hash-based cache key generation and validation.
- Cross-prefix state cache deduplication and sharing.
- Cache size budgeting, TTL expiration, and LRU eviction policies.
- Corruption detection and automated invalidation.

## 4. Non-goals
- Distributing proprietary copyrighted pre-compiled shader binaries over public networks.
- In-memory shader bytecode reverse engineering or de-compilation.
- Overriding hardware GPU instruction sets.

## 5. Requirements
1. **R-SHD-01:** Maintain centralized persistent shader cache at `~/.cache/nebu/shaders/<app_id>/`.
2. **R-SHD-02:** Share DXVK state caches (`.dxvk-cache`) across identical application binaries running in different user profiles.
3. **R-SHD-03:** Enforce strict disk storage limits: default cap of 2.0 GB per application, 10.0 GB total system-wide shader cache.
4. **R-SHD-04:** Implement CRC32/xxHash checksum validation on cache read to detect driver or filesystem corruption.
5. **R-SHD-05:** Invalidate and purge stale driver binary caches automatically upon Mesa or kernel driver updates.

## 6. Architecture
Shader caching operates across two distinct tiers: declarative DXVK state caches and driver-compiled GPU binary caches:

```mermaid
graph TD
    subgraph AppNamespace[Sandboxed Application]
        DXVK_ENG[DXVK / VKD3D Pipeline]
    end

    subgraph CacheSubsystem[NebuOS Shader Cache Subsystem]
        ROUTER[Shader Cache Manager]
        STATE_CACHE[DXVK State Cache: Portable SPIR-V State]
        MESA_CACHE[Mesa / Driver Binary Cache: GPU Machine Code]
    end

    subgraph Storage[Filesystem Storage]
        APP_CACHE[~/.cache/nebu/shaders/app_id/]
        SYS_CACHE[/usr/share/nebu/preseeded-caches/]
    end

    DXVK_ENG <-->|DXVK_STATE_CACHE_PATH| STATE_CACHE
    DXVK_ENG <-->|MESA_SHADER_CACHE_DIR| MESA_CACHE
    ROUTER --> STATE_CACHE
    ROUTER --> MESA_CACHE
    STATE_CACHE --> APP_CACHE
    MESA_CACHE --> APP_CACHE
    SYS_CACHE -.->|Read-only seed| STATE_CACHE
```

## 7. Components
1. **Cache Path Resolver:** Injects standardized environment variables into Bubblewrap sandboxes:
   - `DXVK_STATE_CACHE_PATH=~/.cache/nebu/shaders/<app_id>/`
   - `MESA_SHADER_CACHE_DIR=~/.cache/nebu/shaders/<app_id>/mesa/`
   - `VKD3D_SHADER_CACHE_PATH=~/.cache/nebu/shaders/<app_id>/`
2. **Cache Eviction Daemon (`nebu-cache-cleaner.timer`):** Systemd user timer running weekly or under disk pressure to enforce quota caps.
3. **Mesa Version Invalidator:** Compares stored Mesa version hash in `cache.meta` against `/usr/lib64/libvulkan.so.1` build ID; flushes binary caches if mismatch detected.
4. **Btrfs Deduplicator:** Deduplicates shared state cache blocks using Btrfs extent sharing.

## 8. Data Flow
1. Windows application submits Direct3D draw call requiring a new shader combination.
2. DXVK queries local state cache in memory:
   - If present: loads pre-parsed pipeline state immediately.
   - If absent: compiles D3D bytecode -> SPIR-V and records state entry in `.dxvk-cache` file.
3. Vulkan driver receives SPIR-V and checks Mesa shader cache (`~/.cache/nebu/shaders/<app_id>/mesa/`):
   - If present: loads compiled GPU binary code into hardware command queue (< 0.5ms).
   - If absent: executes full compiler pipeline, stores binary in cache, and uploads to GPU.
4. Subsequent executions achieve stutter-free frame delivery.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant App as Application
    participant DXVK as DXVK Engine
    participant Cache as Shader Cache on Disk
    participant Mesa as Mesa Driver
    participant GPU as Hardware GPU

    App->>DXVK: Issue Draw Command (Unseen Shader)
    DXVK->>Cache: Read state cache entry (SHA-256 key)
    alt Cache Hit
        Cache-->>DXVK: Return cached pipeline state
        DXVK->>Mesa: vkCreateGraphicsPipelines(cached_state)
    else Cache Miss
        DXVK->>DXVK: Translate D3D bytecode -> SPIR-V
        DXVK->>Cache: Write state entry to disk
        DXVK->>Mesa: vkCreateGraphicsPipelines(new_state)
    end
    Mesa->>GPU: Execute Draw
```

## 10. Interfaces
- **Filesystem Directory Layout:**
  ```text
  ~/.cache/nebu/shaders/<app_id>/
  ├── dxvk.dxvk-cache       # DXVK portable state cache
  ├── vkd3d.cache           # VKD3D pipeline cache
  ├── cache.meta            # JSON metadata (Mesa version, timestamps)
  └── mesa/                 # Mesa driver machine code cache
      └── index
  ```
- **Environment Invariants:** `DXVK_STATE_CACHE=1`, `MESA_SHADER_CACHE_MAX_SIZE=2G`.

## 11. Dependencies
- Linux Btrfs filesystem (for reflink/deduplication support).
- Mesa Vulkan driver stack >= 24.0.
- `xxhash` / `crc32fast` for rapid integrity validation.

## 12. Security
- Cache directory mounted private to application sandbox (`0700` POSIX permissions).
- Other applications cannot read or tamper with another app's shader cache.
- Binary cache parser runs with strict memory bounds to prevent memory corruption from malformed cache headers.

## 13. Resource Requirements
- **Disk Budget:** Default per-app cap: 2.0 GB; low-end mode (4GB RAM systems) cap: 512 MB.
- **Cache Read Latency:** Cache hit retrieval < 0.8ms.
- **CPU Overhead:** Background asynchronous cache writes consume < 1% CPU.

## 14. Failure Modes
1. **Cache Corruption from Hard Power Loss:** Machine loses power during write to `.dxvk-cache`.
2. **Driver ABI Mismatch:** Mesa updated across OS image upgrade while old binary cache remains.
3. **Disk Exhaustion:** Shader cache fills remaining free space on root subvolume.

## 15. Recovery Behavior
- When `.dxvk-cache` header CRC check fails, DXVK automatically truncates corrupted tail entries and continues with valid prefix entries.
- Mesa automatically invalidates binary caches when driver build ID changes, rebuilding clean shaders on demand.
- Cache cleaner automatically purges LRU shader caches whenever free disk space drops below 10%.

## 16. Testing Requirements
- Automated test validating cache creation, read hit, and write commit across 1,000 synthetic shaders.
- Corruption simulation test injecting random bitflips into cache files and asserting graceful recovery without crashes.
- Eviction policy test asserting disk usage never exceeds configured hard cap.

## 17. Performance Requirements
- Warm application launch time: >= 60% faster startup due to pre-compiled shader cache.
- Frame time variance during gameplay/rendering: 99th percentile frame time <= 16.6ms (zero compilation stutters).

## 18. Compatibility Considerations
- State caches generated by DXVK are portable across different GPU vendors (AMD, Intel, NVIDIA) because they store SPIR-V pipeline descriptions rather than vendor-specific machine code.

## 19. Open Questions
- **OQ-SHD-01:** Should NebuOS pre-seed popular open-source application shader caches directly in the base OS image?
- **OQ-SHD-02:** What is the optimal compression algorithm (zstd vs lz4) for storing Mesa disk caches on low-end eMMC drives?

## 20. Related Documents
- [00-graphics-specification.md](00-graphics-specification.md)
- [01-gpu-detection.md](01-gpu-detection.md)
- [02-mesa-integration.md](02-mesa-integration.md)
- [04-dxvk-vkd3d.md](04-dxvk-vkd3d.md)
- [05-gpu-profiles.md](05-gpu-profiles.md)
"""

write_file("/root/NebuOS/docs/graphics/06-shader-cache.md", g6)

