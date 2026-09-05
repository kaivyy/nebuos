# Performance Goals and Engineering Targets — NebuOS

## 1. Status
**Status:** APPROVED  
**Type:** Master Engineering Specification  
**Domain:** Operating System Benchmarks, Resource Budgets, and Quality Gates  
**Target Architecture:** x86_64  
**Target Release:** NebuOS 1.0 (Milestones P0-P12)  

---

## 2. Purpose
This specification establishes the authoritative, measurable performance baselines, resource budgets, latency ceilings, and regression thresholds across all subsystems of NebuOS. It introduces a rigorous five-tier performance metrics taxonomy to distinguish between hard contractual obligations, design targets, empirical baselines, aspirational goals, and automated release-blocking regression triggers.

---

## 3. Five-Tier Performance Metrics Taxonomy

To eliminate ambiguity and prevent conflating benchmarks with hard release blockers, all performance indicators in NebuOS are classified under five formal tiers:

```
+-------------------------------------------------------------------------------+
|                      NebuOS Performance Metrics Taxonomy                      |
+-------------------+-----------------------------------------------------------+
| Tier              | Definition and Release Governance                         |
+-------------------+-----------------------------------------------------------+
| 1. Requirement    | Hard contractual constraint. Breaching a Requirement      |
|                   | unconditionally blocks CI merge and release promotion.     |
| 2. Target         | Expected design objective under nominal conditions.       |
|                   | Deviation > 10% requires formal architectural review.     |
| 3. Benchmark      | Empirical reference measurement against external baselines|
|                   | (e.g. Bare-metal Windows 11, Fedora Workstation).         |
| 4. Stretch Goal   | Aspirational optimization ceiling targeted for future      |
|                   | performance tuning phases; non-blocking.                  |
| 5. Regression     | Quantitative degradation boundary relative to the last     |
|    Threshold      | verified stable release that triggers release freeze.     |
+-------------------+-----------------------------------------------------------+
```

---

## 4. Master Operating System Performance Metrics

| Subsystem / Metric | Taxonomy Tier | Low-End (4GB RAM) | Standard (16GB RAM) | Measurement Tool / Method |
|---|---|---|---|---|
| **Boot Time to Compositor (NVMe)** | Requirement | $\le 6.0\text{ s}$ | $\le 3.5\text{ s}$ | `systemd-analyze` |
| **Boot Time to Compositor (SATA SSD)** | Target | $\le 8.5\text{ s}$ | $\le 5.0\text{ s}$ | `systemd-analyze` |
| **Total System Idle Memory (RAM)** | Requirement | $\le 850\text{ MB}$ | $\le 1100\text{ MB}$ | `free -m`, `ps_mem` |
| **System Idle CPU Utilization** | Requirement | $\le 0.5\%$ | $\le 0.2\%$ | `top -b -n 5` |
| **Shell UI Interaction Latency** | Target | $\le 60\text{ ms}$ | $\le 16.6\text{ ms}$ (1 frame) | High-speed camera / Wayland timing |
| **Application Graceful Close Time** | Target | $\le 400\text{ ms}$ | $\le 200\text{ ms}$ | Process exit timestamp monitor |
| **Suspend-to-RAM (`deep`/`s2idle`)** | Target | $\le 1.8\text{ s}$ | $\le 1.2\text{ s}$ | Kernel PM trace / ACPI timer |
| **Resume from Sleep to Desktop** | Requirement | $\le 2.0\text{ s}$ | $\le 1.0\text{ s}$ | Kernel PM trace / DRM KMS wake |

---

## 5. NebuWine and Windows Compatibility Performance Metrics

All metrics evaluated against reference hardware nodes running verified NebuWine runtimes on the decoupled `@runtimes` storage volume.

| Metric | Taxonomy Tier | Target Value | Regression Threshold | Measurement Tool / Methodology |
|---|---|---|---|---|
| **Cold Launch Overhead (NebuRuntime)** | Requirement | $\le 80\text{ ms}$ | $> 120\text{ ms}$ | Time spent in `nebu-runtime-daemon` before Wine exec |
| **Warm Launch Overhead (NebuRuntime)** | Requirement | $\le 20\text{ ms}$ | $> 40\text{ ms}$ | Cached prefix launch setup time |
| **Cold Launch: Enterprise App (AutoCAD/Office)** | Target | $\le 4.5\text{ s}$ | $> 7.0\text{ s}$ | Binary invoke to mapped Wayland surface |
| **Warm Launch: Enterprise App (AutoCAD/Office)** | Target | $\le 1.5\text{ s}$ | $> 2.8\text{ s}$ | Warm prefix launch to surface commit |
| **wineserver CPU Overhead at Idle** | Requirement | $\le 0.1\%$ | $> 0.5\%$ | Continuous 60s average via `pidstat -p <pid> 1 60` |
| **wineserver RSS Memory Footprint** | Benchmark | $\le 12\text{ MB}$ | $> 25\text{ MB}$ | `ps -p <pid> -o rss` |
| **NTSYNC vs. Futex Synchronization Latency** | Benchmark | $\le 1.2\,\mu\text{s}$ | $> 3.5\,\mu\text{s}$ | Micro-benchmark calling NT synchronization primitives |
| **Direct3D 11 Performance (vs Native Win11)** | Target (Empirical Benchmark)* | $\ge 92\%$ FPS | $< 85\%$ FPS | 3DMark FireStrike / Unigine Superposition |
| **Direct3D 12 Performance (vs Native Win11)** | Target (Empirical Benchmark)* | $\ge 90\%$ FPS | $< 80\%$ FPS | 3DMark TimeSpy / Cyberpunk 2077 Benchmark |
| **Native Vulkan Pass-Through Performance** | Target | $\ge 98\%$ FPS | $< 95\%$ FPS | DOOM Eternal / VKMark |
| **Frame Time Consistency (99th Percentile)** | Target | $\le 16.6\text{ ms}$ (60Hz) | $> 22.0\text{ ms}$ | Mangohud / PresentMon trace capture |
| **Shader Compilation Stutter Event Frequency**| Target | $0\text{ stutters}$ | $> 2\text{ hits/min}$ | DXVK asynchronous state cache validation |
| **Wayland Presentation Latency (Input to Photon)** | Target | $\le 16\text{ ms}$ | $> 32\text{ ms}$ | Latency testing rig with synthetic input |
| **Btrfs Reflink Prefix Provisioning Time** | Requirement | $\le 150\text{ ms}$ | $> 300\text{ ms}$ | Subvolume snapshot creation latency |
| **Memory Leak Ceiling (Long-Run L7)** | Requirement | $< 25\text{ MB/hr}$ | $> 50\text{ MB/hr}$ | 4-hour cyclical workflow execution |

*\*Note on Direct3D Targets:* The D3D11 ($\ge 92\%$) and D3D12 ($\ge 90\%$) targets represent empirical engineering benchmarks evaluated on modern reference hardware nodes (Node-INTEL, Node-AMD, Node-NVIDIA) equipped with Vulkan 1.3-capable GPUs running at native resolution without thermal throttling. Legacy or budget GPUs lacking Vulkan 1.3 fall back to WineD3D/OpenGL and are evaluated under separate functional baseline criteria.

---

## 6. Five System Operating Performance Profiles

NebuOS provides 5 dynamic operating profiles managed by `nebu-power-daemon` and `systemd`:

1. **Nebu Lite Mode:** Enforced on systems with $\le 4\text{ GB}$ RAM or battery $< 20\%$. Compositor disables blur effects and animations, zram compression set to `lz4`, background indexing paused, aggressive page compaction.
2. **Balanced Mode:** Default desktop profile. Dynamic CPU frequency scaling via `schedutil`, GPU runtime power management enabled (D3hot/D3cold on hybrid laptops), PipeWire quantum = 256.
3. **Performance Mode:** CPU governor set to `performance` with biased energy-performance preferences (`EPP = performance`), dGPU remains active, PipeWire quantum = 128.
4. **Gaming Profile (ADR-0018):** Activated automatically for games running under NebuWine Gaming. Sets process `nice` priority to -10, configures DXVK pipeline compiler threads to match physical CPU cores, enables direct scanout / tearing control if display supports VRR, and lowers PipeWire quantum to 64.
5. **Workstation Mode:** Dedicated to professional CAD, BIM, and DCC applications. Locks CPU affinity for viewport threads, allocates isolated GPU memory pools, disables background OS update tasks.

---

## 7. Performance Verification and Release Gates

Performance verification is integrated into the Compatibility Lab (ADR-0015 / Milestone P7):
- **Tier 0 CI PR Gate:** Micro-benchmarks verify that `nebu-runtime-daemon`, `nebu-compositor`, and core crates introduce zero CPU or memory regressions.
- **Nightly Bare-Metal Gate:** Full automated run of 3D benchmarks and CAD model loading across reference nodes (Node-INTEL, Node-AMD, Node-NVIDIA).
- **Regression Policy:** Any candidate build exhibiting $> 5\%$ drop in frame rate or $> 10\%$ increase in cold launch time is blocked from entering the `Stable` channel.

### 7.1 Automated Benchmark Test Suite Identifiers
- **`TEST-PERF-001` (System Idle Resource Consumption):** Verifies idle RAM $\le 850\text{ MB}$ (low-end) / $\le 1100\text{ MB}$ (standard) and idle CPU $\le 0.5\%$.
- **`TEST-PERF-002` (Boot Sequence Latency):** Validates NVMe cold boot to compositor $\le 3.5\text{ s}$ via `systemd-analyze`.
- **`TEST-PERF-003` (Cold Application Launch):** Validates cold enterprise application launch $\le 4.5\text{ s}$ and runtime daemon overhead $\le 80\text{ ms}$.
- **`TEST-PERF-004` (Warm Application Launch):** Validates warm application launch $\le 1.5\text{ s}$ and cached daemon overhead $\le 20\text{ ms}$.
- **`TEST-PERF-005` (Differential Cold Start vs. Warm Start Benchmark):** Measures differential performance between cold launch (cold page cache, uninitialized wineserver) and warm launch (populated page cache, pre-warmed wineserver state). Enforces a minimum differential speedup ratio of $\ge 2.5\times$ for warm launch over cold launch across reference test suites (e.g. AutoCAD, Word, Blender), verifying that prefix caching and memory pinning remain functional.

---

## 8. Related Documents
- [01-memory.md](01-memory.md) — Subsystem memory allocation limits.
- [02-cpu.md](02-cpu.md) — CPU scheduling and real-time priorities.
- [03-boot.md](03-boot.md) — Boot stage analysis.
- [04-launch.md](04-launch.md) — Application launch timings.
- [05-storage.md](05-storage.md) — Storage I/O and filesystem performance.
- [../decisions/ADR-0018-gaming-runtime-architecture.md](../decisions/ADR-0018-gaming-runtime-architecture.md) — Gaming frame rate and input latency targets.
- [../decisions/ADR-0015-compatibility-lab.md](../decisions/ADR-0015-compatibility-lab.md) — Compatibility Lab architecture.
- [../runtime/08-nebuwine-specification.md](../runtime/08-nebuwine-specification.md) — NebuWine technical specification.
- [../testing/09-compatibility-lab-specification.md](../testing/09-compatibility-lab-specification.md) — Compatibility Lab specification.
