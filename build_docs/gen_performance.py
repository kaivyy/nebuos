#!/usr/bin/env python3
"""
Generate Performance Documentation for NebuOS (docs/performance/):
- 00-performance-goals.md
- 01-memory.md
- 02-cpu.md
- 03-boot.md
- 04-launch.md
- 05-storage.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs/performance"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_file(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: performance/{filename} ({len(content.splitlines())} lines)")

# 00-performance-goals.md
write_file("00-performance-goals.md", r"""# Performance Goals & Engineering Targets — NebuOS

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
""")

# 01-memory.md
write_file("01-memory.md", r"""# Memory Management & Low-End Mode Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify memory budgeting, zram swap compression, memory pressure stall mitigation, and Nebu Lite Mode on 4GB RAM hardware.

---

## 1. The 4GB RAM First-Class Citizen Rule
NebuOS treats 4GB RAM machines not as an afterthought, but as an essential engineering benchmark. On a 4GB machine:
- Base OS + Compositor + Shell MUST consume under 800 MB RSS at idle, leaving > 3.2 GB available for user applications.

```mermaid
graph TD
    subgraph RAM_4GB [4 GB Physical RAM Distribution]
        OS_BASE[Kernel + systemd + PipeWire: 350 MB]
        COMP_SHELL[NebuCompositor + NebuShell: 120 MB]
        APP_AVAIL[Free for User Applications: 3200 MB]
    end

    RAM_4GB --> ZRAM[zram RAM Swap - 2 GB Compressed Buffer - zstd]
    ZRAM --> PSI_MONITOR[systemd-oomd PSI Pressure Monitor]
    
    PSI_MONITOR -->|Pressure > 25%| TRIM[Trigger Proactive Cache Eviction]
    PSI_MONITOR -->|Pressure > 50%| LITE_MODE[Enforce Nebu Lite Mode]
```

## 2. Low-End Mode Architectural Adaptations
When Nebu Lite Mode is engaged:
1. **Compositor Shaders:** Window drop shadows, translucent glass blurs, and minimize/maximize scale animations are deactivated.
2. **Cache Eviction:** Unused prefix metadata, font caches, and shader pipelines are pruned from RAM immediately upon app close.
3. **Warm Runtime Unloading:** Background pre-warmed Wine instances are completely terminated.

## 3. Related Documents
- [00-performance-goals.md](00-performance-goals.md)
- [02-cpu.md](02-cpu.md)
""")

# 02-cpu.md
write_file("02-cpu.md", r"""# CPU Utilization & Wakeup Architecture — NebuOS

**Status:** REVIEW  
**Purpose:** Detail the zero-polling invariant, timer coalescing, event-driven daemons, and energy-aware CPU frequency governance.

---

## 1. The Zero-Polling Invariant
No NebuOS daemon or userland component is permitted to use `sleep()` in an active loop or poll filesystems/hardware at high frequency.
- **Event-Driven Architecture:** All daemon main loops are strictly driven by `epoll`, `timerfd`, `signalfd`, and `eventfd`.
- **Timer Coalescing:** Non-urgent background timers (e.g. update checks, battery polling) are aligned to 60-second ticks to allow the CPU to remain in deep C-states (C6/C7/C8).

## 2. Idle State Invariant
At idle desktop (no user interaction, no background tasks), total CPU utilization across all CPU cores must measure **< 0.5%**, preventing laptop fan spin-up and maximizing battery endurance.

## 3. Related Documents
- [00-performance-goals.md](00-performance-goals.md)
- [01-memory.md](01-memory.md)
""")

# 03-boot.md
write_file("03-boot.md", r"""# Boot Optimization Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify initramfs optimization, systemd service ordering, Plymouth reduction, and fast userspace handover.

---

## 1. Boot Latency Budget Breakdown (Target: < 5.0s NVMe)

```mermaid
gantt
    title NebuOS Boot Timeline Budget
    dateFormat X
    axisFormat %s s
    
    section Hardware
    UEFI Firmware Init :0, 1500
    
    section Kernel
    Kernel & Driver Decompression :1500, 2300
    Initramfs OSTree Pivot :2300, 2900
    
    section Userspace
    systemd Core Services :2900, 3900
    NebuCompositor KMS DRM Init :3900, 4400
    NebuShell Presentation :4400, 4800
```

## 2. Architectural Optimizations
1. **Initramfs Pruning:** Dracut profile includes only essential storage and display drivers, shrinking initramfs to < 22 MB.
2. **Parallel Daemon Startup:** NetworkManager, Bluetooth, and audio services initialize asynchronously; they do not block the graphical target.
3. **Direct Login:** The display greeter hands off the active DRM master directly to `nebu-compositor` without screen flicker or VT switching.

## 3. Related Documents
- [00-performance-goals.md](00-performance-goals.md)
- [../architecture/02-boot-and-init.md](../architecture/02-boot-and-init.md)
""")

# 04-launch.md
write_file("04-launch.md", r"""# Application Launch Optimization Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Detail cold start versus warm start pipelines, SQLite indexed metadata, and warm runtime caching.

---

## 1. Cold vs Warm Launch Pipelines

```mermaid
graph TD
    LAUNCH[Application Triggered] --> CACHE_CHECK{Is Warm Runtime Cached in RAM?}
    
    CACHE_CHECK -->|Warm Cache Hit| FAST_PATH[Inject Arguments into Pre-initialized wineserver]
    FAST_PATH --> FORK_EXEC[Process Fork & Direct Scanout - < 1.5s]
    
    CACHE_CHECK -->|Cold Cache Miss| FULL_PATH[Spawn Sandbox -> Load DLLs -> Init Server]
    FULL_PATH --> FORK_EXEC
```

## 2. Pre-Indexed Launch Architecture
When the user opens the application launcher:
- `nebu-shell` queries an in-memory SQLite table containing application names, keywords, and icon paths.
- Zero disk stat calls or directory walking occurs during the search keystroke event, ensuring sub-100ms response even under heavy disk I/O.

## 3. Related Documents
- [00-performance-goals.md](00-performance-goals.md)
- [../runtime/01-application-lifecycle.md](../runtime/01-application-lifecycle.md)
""")

# 05-storage.md
write_file("05-storage.md", r"""# Storage Performance & Quota Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify Btrfs compression tuning, prefix disk quota management, and shader cache garbage collection.

---

## 1. Filesystem Compression Tuning
- **Compression Algorithm:** Transparent `zstd:1` compression enabled on root (`@`) and home (`@home`) subvolumes.
- **Benefits:**
  - Reduces operating system install footprint from ~18 GB to **< 9 GB**.
  - Doubles effective SATA SSD read bandwidth by compressing data before bus transfer.

## 2. Automated Storage Quota & Garbage Collection
- **Shader Cache Pruning:** `~/.nebu/cache/shaders/` is capped at 5 GB system-wide. An LRU daemon prunes caches older than 90 days.
- **Prefix Snapshots:** Point-in-time prefix snapshots are automatically rotated; older snapshots are removed after 14 days unless pinned by the user.

## 3. Related Documents
- [00-performance-goals.md](00-performance-goals.md)
- [../architecture/04-filesystem.md](../architecture/04-filesystem.md)
""")

print("Performance documentation generated successfully.")
