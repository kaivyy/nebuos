# Performance Goals & Engineering Targets — NebuOS

**Status:** REVIEW  
**Purpose:** Establish measurable, non-negotiable performance baselines and metrics across all operating system tiers.

---

## 1. Master Performance Metrics Table

| Metric Category | Target (Low-End 4GB System) | Target (Standard 16GB System) | Measurement Tool |
|---|---|---|---|
| **Boot Duration (SATA SSD)** | < 7.5 seconds | < 5.0 seconds | `systemd-analyze` |
| **Boot Duration (NVMe)** | N/A | < 3.5 seconds | `systemd-analyze` |
| **Idle Memory (RAM)** | < 800 MB total OS consumption | < 1.0 GB | `free -m`, `ps_mem` |
| **Idle CPU Utilization** | < 0.5% average load | < 0.2% average load | `top -b -n 5` |
| **Launcher UI Response** | < 100 milliseconds | < 50 milliseconds | Wayland presentation time |
| **Wine Cold Launch (CAD)** | < 8.0 seconds | < 4.0 seconds | Wall-clock execution timer |
| **Wine Warm Launch (CAD)** | < 2.5 seconds | < 1.2 seconds | Wall-clock execution timer |
| **Application Close Time** | < 500 milliseconds | < 250 milliseconds | Process exit signal monitor |

## 2. Five Performance Modes
NebuOS provides 5 user-selectable and automated performance profiles:
1. **Nebu Lite Mode:** Strictly enforced on 4GB systems. Minimal compositor animations, aggressive memory compaction, no background caching.
2. **Balanced Mode:** Default desktop profile balancing responsive UI and thermal efficiency.
3. **Performance Mode:** High-frequency CPU scaling (`schedutil` with high bias), GPU power profiles unconstrained.
4. **Gaming Mode:** Activates `gamemode` daemon, prioritizes process nice levels, maximizes GPU clocks, sets tearing policy if requested.
5. **Workstation Mode:** Optimizes multi-threaded CPU affinity and locks VRAM buffers for CAD and 3D rendering DCC workloads.

## 3. Related Documents
- [01-memory.md](01-memory.md)
- [03-boot.md](03-boot.md)
- [04-launch.md](04-launch.md)
