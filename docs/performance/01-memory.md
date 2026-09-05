# Memory Management & Low-End Mode Specification — NebuOS

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
