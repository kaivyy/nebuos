# 3D Graphics & Driver Architecture Skill — NebuOS

## 1. Purpose
Governs GPU hardware detection, Mesa 3D driver integration, Vulkan ICD configuration, DXVK/VKD3D translation layers, and shader cache management.

## 2. Scope
Applies to Milestone P5 (Graphics Runtime) and hardware support across all milestones.

## 3. Relevant Documentation
- `docs/roadmap/06-p5-graphics-runtime.md`: Milestone P5 execution plan.
- `docs/graphics/00-graphics-specification.md`: Rendering pipeline.
- `docs/graphics/04-dxvk-vkd3d.md`: Direct3D translation configuration.
- `docs/decisions/ADR-0005-nvidia-driver-strategy.md`: NVIDIA driver strategy.

## 4. Allowed Changes
- Configuring `dxvk.conf` parameters per application class.
- Developing GPU topology detection scripts in `crates/nebu-gpu/`.
- Managing shared shader cache directory layout in `/var/cache/nebu/shaders/`.

## 5. Forbidden Changes
- **NO MONOLITHIC GPU ASSUMPTIONS:** Never assume AMD, Intel, and NVIDIA share identical Vulkan features or driver paths.
- **DO NOT WORK IN P0:** P0 uses virtualized framebuffers (virtio-gpu/bochs); complex GPU tuning is strictly P5.

## 6. Architecture Constraints
- Modern Turing+ NVIDIA: Mesa NVK + Nova kernel driver out-of-the-box.
- Legacy NVIDIA: Optional external bootc container driver layer.
- Hybrid Laptops (PRIME): Automatic dynamic GPU offloading (`DRI_PRIME=1` or `__NV_PRIME_RENDER_OFFLOAD=1`).

## 7. Implementation Guidance
- Enable state cache sharing across prefixes running the same DXVK release.
- Evict shader caches safely when Mesa or DXVK version updates occur to prevent pipeline corruption.

## 8. Verification
- `vulkaninfo --summary` returns valid device extensions without validation layer errors.
- Frame time benchmarking verifying input latency overhead < 5% vs native Linux Vulkan.

## 9. Common Failure Modes
- Pipeline stutter caused by missing async shader compilation flags.
- Dual-GPU laptops failing to engage discrete GPU for 3D applications.

## 10. Handoff Requirements
- Record GPU test matrix results and Vulkan validation logs in `HANDOFF.md`.
