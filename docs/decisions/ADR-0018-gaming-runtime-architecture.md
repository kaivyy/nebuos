# ADR-0018: NebuWine Gaming Runtime Architecture and Graphics Translation Pipeline

**Status:** APPROVED  
**Date:** 2026-09-05  
**Authors:** Principal OS Architect, Gaming Compatibility Architect, Graphics Engineer, Performance Engineer  
**Deciders:** NebuOS Core Architecture Group  
**Supercedes:** Extends and formalizes the gaming runtime boundary introduced in ADR-0006  
**Related ADRs:** ADR-0003 (Smithay Wayland), ADR-0006 (Proton/DXVK), ADR-0010 (Hardware Compatibility), ADR-0015 (Compatibility Lab), ADR-0016 (NebuWine Architecture), ADR-0017 (Decoupled Runtime Storage)  
**Consulted:** PRD §17, §25, §26, §73, §74, §88, §89  

---

## 1. Context and Problem Statement

ADR-0006 established that NebuOS integrates DXVK and VKD3D-Proton to translate Direct3D calls to Vulkan. However, the exact architectural relationship between NebuWine, Valve's Proton ecosystem, and gaming runtimes remained loosely defined. In the Linux gaming community, "Proton" is often colloquially described as "just Wine plus DXVK", while in reality, Valve's Proton represents a specialized runtime combining Wine source patches (fsync/ntsync, raw input, audio routing, media-foundation video decoding), container runtimes (SteamLinuxRuntime / Pressure-Vessel), Direct3D translation layers, and customized gamepad/OpenXR stacks.

We must decide how NebuOS supports high-performance Windows gaming without:
1. Creating a permanently diverged "NebuProton" hard fork.
2. Compromising the clean, general-purpose Win32/NT design of core NebuWine.
3. Breaking enterprise and professional CAD/productivity workloads with experimental gaming hacks.
4. Attempting to circumvent or undermine commercial anti-cheat (EAC, BattlEye, Ricochet, Vanguard) or DRM systems.

---

## 2. Core Architectural Model

NebuOS formally defines **NebuWine Gaming** as a composable extension profile of NebuWine, rather than an isolated, forked operating system or separate Wine codebase:

$$\text{NebuWine Gaming} = \text{NebuWine Core} + \text{Gaming Runtime Components}$$

```
+-------------------------------------------------------------------------------+
|                       NebuWine Gaming Runtime Architecture                    |
+-------------------------------------------------------------------------------+
| Windows 3D Game / Interactive Title                                          |
+-------------------------------------------------------------------------------+
       | Direct3D / Vulkan / Win32 Calls
       v
+-------------------------------------------------------------------------------+
| NebuWine Gaming Profile (Prefix Overrides & Configuration)                    |
| - Environment Flags: WINEESYNC=1, WINENTSYNC=1 (where supported)               |
| - Low-latency audio routing (PipeWire quantum = 64/128)                       |
| - Gamepad / DualSense / XInput evdev mapping                                  |
+-------------------------------------------------------------------------------+
       |
       +--------------------------------+-------------------------------+
       | Direct3D 9 / 10 / 11           | Direct3D 12                   | Native Vulkan
       v                                v                               v
+-------------------------------+ +-------------------------------+ +-----------+
| DXVK (2.4+)                   | | VKD3D-Proton (2.13+)          | | Direct    |
| (D3D to Vulkan Translation)   | | (D3D12 to Vulkan Translation) | | Vulkan    |
+-------------------------------+ +-------------------------------+ +-----------+
       |                                |                               |
       +--------------------------------+-------------------------------+
                                        | Pure Vulkan Commands
                                        v
+-------------------------------------------------------------------------------+
| Mesa Vulkan Driver (RADV / ANV) OR NVIDIA Proprietary Vulkan Driver           |
+-------------------------------------------------------------------------------+
                                        | Direct DRM / KMS & Wayland Presentation
                                        v
+-------------------------------------------------------------------------------+
| NebuCompositor (Wayland / Linux Kernel DRM Subsystem)                         |
+-------------------------------------------------------------------------------+
```

---

## 3. Decision Drivers

- **Zero Core Contamination:** Gaming-specific fast paths (e.g. aggressive thread scheduling, specialized memory allocators) must never compromise the data integrity or stability of professional CAD/BIM applications.
- **Direct Vulkan Path:** D3D translation must map directly to Vulkan 1.3+ via DXVK and VKD3D-Proton to achieve $\ge 90\%$ of native Windows performance on supported hardware.
- **Legacy Fallback Preservation:** Legacy Direct3D 8/9 applications and vintage hardware without Vulkan 1.3 support must gracefully fall back to WineD3D (OpenGL) without crashing.
- **Synchronous vs. Asynchronous Scheduling:** Kernel-level synchronization mechanisms (NTSYNC / fastfutex) must be leveraged when present, with automatic fallback to eventfd/futex (`esync`/`fsync`).
- **Security & Integrity Strictness:** NebuOS will never tamper with, bypass, or spoof anti-cheat systems. Anti-cheat compatibility is achieved strictly through official upstream developer support (e.g. Proton-enabled Easy Anti-Cheat / BattlEye Linux modules).

---

## 4. Considered Alternatives

### Option A: Complete Standalone Proton Fork ("NebuProton")
- Maintain an entire independent Proton tree cloned from Valve.
- *Pros:* Matches Steam Deck behavior closely.
- *Cons:* Massive maintenance overhead (Valve's Proton tree carries thousands of downstream commits); complete duplication of runtime storage; diverts resources from core upstream Wine fixes. Rejected.

### Option B: Monolithic NebuWine (Merge All Gaming Patches into Base NebuWine)
- Apply all gaming, fsync, media-foundation, and DXVK overrides into the single standard NebuWine build.
- *Pros:* Single runtime to build and test.
- *Cons:* Causes subtle regressions in enterprise software (e.g. Microsoft Office, AutoCAD, accounting software); violates Upstream-First discipline. Rejected.

### Option C: Composable Gaming Runtime Profile over NebuWine Baseline (CHOSEN)
- NebuWine core remains clean, disciplined, and upstream-aligned.
- The **Gaming Profile** dynamically augments the environment:
  1. Injects versioned DXVK (`d3d9.dll`, `d3d10core.dll`, `d3d11.dll`, `dxgi.dll`) and VKD3D-Proton (`d3d12.dll`, `d3d12core.dll`) into the game prefix.
  2. Enables low-latency synchronization (NTSYNC / `fsync`) via capability detection.
  3. Provisions upstream Wine Wayland / Xwayland gaming extensions (tearing control, fractional scaling, relative pointer lock).
  4. Manages persistent shader caches (`~/.cache/nebu/shaders/<game-id>/`).
- *Pros:* Total isolation from enterprise apps; modular updates for DXVK/VKD3D without touching Wine binaries; maximal code reuse.

---

## 5. Decision Outcome

**Chosen Option: Option C — Composable Gaming Runtime Profile over NebuWine Baseline.**

### 5.1 Graphics Translation Layer Versioning & Pipeline Rules

#### Translation Component Versioning Matrix
| Component | Minimum Supported | Preferred Validated Baseline | Latest Tested / Fast-Track | Hardware Requirement |
|---|---|---|---|---|
| **Vulkan Host API** | Vulkan 1.2 | Vulkan 1.3 (with `timeline_semaphore`, `descriptor_indexing`) | Vulkan 1.3.280+ | Modern GPU driver (RADV, ANV, NVIDIA $\ge 550$) |
| **DXVK (D3D9/10/11)** | DXVK 2.1 | DXVK 2.4.1 | DXVK 2.5.x | Vulkan 1.3 host support |
| **VKD3D-Proton (D3D12)**| VKD3D-Proton 2.10 | VKD3D-Proton 2.13.1 | VKD3D-Proton 2.14.x | Vulkan 1.3 + `buffer_device_address` |
| **WineD3D (Fallback)** | OpenGL 4.1 | OpenGL 4.5 Core Profile | OpenGL 4.6 | Legacy GPU lacking Vulkan 1.3 support |

#### Translation Pipeline Routing
The graphics translation route is determined strictly by application API and GPU capabilities:

1. **Direct3D 9, 10, 11:**
   - *Default:* DXVK translates D3D to Vulkan 1.3.
   - *Fallback:* If GPU lacks Vulkan 1.3 (e.g. legacy Intel Gen8 or older), automatically fallback to WineD3D (OpenGL 4.5).
2. **Direct3D 12:**
   - *Default:* VKD3D-Proton translates D3D12 to Vulkan 1.3+.
   - *Requirement:* Hardware must support Vulkan 1.3 with descriptor indexing, timeline semaphores, and buffer device address.
3. **Direct3D 8 and Legacy APIs:**
   - WineD3D natively translates to OpenGL, or d8vk translates to Vulkan.
4. **Vulkan (Native Windows Win32 Vulkan):**
   - Wine passes Win32 Vulkan calls directly to the host Vulkan ICD (`winevulkan.dll` pass-through). Zero CPU/GPU translation penalty.

### 5.2 Synchronization Engine Hierarchy
To eliminate thread contention and CPU bottlenecks during frame rendering:
- **Tier 1 (Preferred):** `NTSYNC` kernel module (`/dev/ntsync`) if exposed by the NebuOS kernel. Provides direct kernel-level NT primitive synchronization matching Windows NT kernel behavior.
- **Tier 2 (Fallback):** `fsync` (Linux `futex_waitv` system call, standard in Linux 5.16+ and NebuOS kernel 7.x).
- **Tier 3 (Safe Fallback):** Standard wineserver eventfd polling (used if futex interfaces are restricted).

---

## 6. Anti-Cheat and DRM Policy

NebuOS establishes a strict, non-negotiable architectural policy regarding anti-cheat and DRM:
1. **Zero Bypass / Zero Exploitation:** NebuOS will never ship, endorse, or integrate tools designed to circumvent kernel anti-cheat systems (e.g. Riot Vanguard, BattlEye, Easy Anti-Cheat, Ricochet).
2. **Supported Integration:** NebuOS fully supports anti-cheat systems that officially provide Linux/Proton compatibility modules (e.g., Easy Anti-Cheat Proton bridge, BattlEye Proton library).
3. **Sandboxing Respect:** Anti-cheat modules must run within userland boundaries defined by NebuOS bubblewrap containers; no third-party ring-0 kernel modules will be loaded.

---

## 7. Consequences

### Positive Consequences
- Preserves the purity, safety, and upstream-discipline of core NebuWine.
- Delivers maximum possible gaming performance through native Vulkan drivers (Mesa RADV/ANV, NVIDIA).
- Decouples DXVK and VKD3D-Proton release cycles from the base operating system.
- Transparently protects enterprise users from gaming-related regressions.

### Negative Consequences
- Games requiring proprietary Windows kernel-mode drivers (Ring 0 anti-cheat) cannot function on NebuOS without official vendor-provided userland compatibility bridges.

---

## 8. Verification and Acceptance Criteria

- [x] Documented in ADR-0018; integrated into `docs/runtime/08-nebuwine-specification.md`.
- [x] Graphics translation path aligned with `docs/graphics/00-graphics-specification.md`.
- [x] Gaming performance metrics codified in `docs/performance/00-performance-goals.md`.
