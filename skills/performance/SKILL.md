# Performance Engineering & Benchmarking Skill — NebuOS

## 1. Purpose
Governs performance benchmarking methodology, latency budgets, memory allocation ceilings, and regression detection thresholds across NebuOS.

## 2. Scope
Applies across all milestones (P0 through P8).

## 3. Relevant Documentation
- `docs/specification/06-resource-management.md`: Memory and CPU budgets.
- `docs/performance/00-performance-specification.md`: Master performance SLA table.
- `docs/performance/03-boot-performance.md`: Boot timing targets.
- `docs/performance/04-launch-performance.md`: Application launch timing.

## 4. Allowed Changes
- Authoring benchmark automation scripts under `tests/benchmarks/`.
- Tuning kernel parameters and systemd service resource limits (`MemoryMax`).
- Optimizing hot code paths in Rust daemons.

## 5. Forbidden Changes
- **NO UNQUALIFIED BENCHMARK CLAIMS:** Never record a benchmark number without hardware and software baseline metadata.
- **DO NOT CONFLATE BENCHMARK WITH REQUIREMENT:** Lightweight app launch (< 2.5s) is a benchmark target, not an SLA for heavy CAD suites.

## 6. Architecture Constraints
- P0 Foundation Boot Time: < 3.5s (UEFI to TTY login).
- P0 Foundation Idle RAM: < 150 MB RSS.
- Full Desktop Boot Time (P2): < 8.0s (UEFI to interactive shell).
- Full Desktop Idle RAM (P2): < 450 MB RSS.

## 7. Implementation Guidance
- Every benchmark must record: CPU model, RAM amount, Storage type (NVMe/SSD), Kernel version, Toolchain version, Sample size (N >= 5), Mean, and Standard Deviation.
- Measure memory using Proportional Set Size (PSS) or Resident Set Size (RSS) via `smem` or `/proc/<pid>/smaps_rollup`.

## 8. Verification
- Validate boot performance via `systemd-analyze` and `systemd-analyze blame`.
- Validate memory budgets under low-end constraints (4GB RAM with zram active).

## 9. Common Failure Modes
- Measuring cold launch times without clearing the kernel page cache (`drop_caches`).
- Profiling unoptimized debug builds instead of `--release` builds.

## 10. Handoff Requirements
- Record structured benchmark tables with full hardware and environment metadata in `HANDOFF.md`.
