# ADR-0015: Compatibility Lab Architecture and Automated Testing Farm

**Status:** APPROVED  
**Date:** 2026-09-05  
**Authors:** Principal OS Architect, Testing Architect, Hardware Compatibility Engineer, QA/Release Engineer  
**Deciders:** NebuOS Core Architecture Group  
**Supercedes:** None  
**Related ADRs:** ADR-0001 (Linux Kernel), ADR-0005 (Wine Integration), ADR-0006 (Proton/DXVK), ADR-0010 (Hardware Compatibility), ADR-0016 (NebuWine Downstream Distribution), ADR-0017 (Decoupled Runtime Storage), ADR-0018 (Gaming Runtime)  
**Consulted:** PRD §31, §32, §33, §34, §35, §36, §76, §77, §78, §79, §98, §102  

---

## 1. Context and Problem Statement

NebuOS promises high-fidelity execution of native Linux and Windows applications without relying on a Windows virtual machine. However, the matrix of target software (office productivity, CAD/BIM suites, digital content creation, modern Vulkan/Direct3D games) running across disparate PC hardware (Intel Core/Ultra, AMD Ryzen, NVIDIA RTX, hybrid dual-GPU laptops) presents an astronomical state space for regressions.

Without an automated, reproducible, multi-tiered testing farm:
1. Upstream Wine or driver updates silently break mission-critical applications.
2. Graphic regressions (shader compilation stutters, atomic KMS page flip delays, memory leaks) escape into production releases.
3. Compatibility claims remain purely anecdotal rather than backed by quantitative, verifiable evidence.
4. Developers and release engineers lack a deterministic gate to block broken updates.

Previous planning documents referenced `ADR-0015` in traceability matrices (PRD §31, §76, §77, §102) but the document itself was missing, leaving the physical architecture, automation protocols, hardware topologies, and quality gates underspecified.

This ADR formally establishes the architecture, topology, governance, and operational model for the **NebuOS Compatibility Lab** (planned for Milestone P7).

---

## 2. Decision Drivers

- **Evidence-Driven Certification:** Compatibility is never an assumption. Every compatibility certification (Gold, Silver, Bronze) must be generated from reproducible workflow execution runs.
- **Hardware Diversity:** Testing must cover physical bare-metal hardware across all major GPU vendors (Intel, AMD, NVIDIA) as well as virtualized CI runners.
- **Continuous Regression Prevention:** Upstream kernel, Mesa, DXVK, VKD3D-Proton, and Wine changes must pass automated regression gates before being promoted to release channels.
- **Resource Feasibility & Scalability:** Virtualized and headless automation must execute on every pull request, while physical bare-metal testing executes nightly or per-candidate build.
- **Non-Destructive Test Execution:** Test runners must execute within ephemeral Btrfs snapshots and bubblewrap sandboxes to guarantee test idempotency and zero host contamination.
- **Deterministic Workflows:** Moving beyond trivial "does it launch?" checks to multi-level application workflow testing (L0 launch through L7 stress/stability).

---

## 3. Considered Alternatives

### Option A: Manual Community Testing Only (AppDB Model)
- Rely solely on user crowd-sourced feedback and wiki reports.
- *Pros:* Zero hardware lab capital expenditure.
- *Cons:* Inconsistent reports, subjective scoring, uncontrolled hardware variables, zero pre-release regression blocking. Unacceptable for a commercial-grade operating system.

### Option B: Cloud VM-Only Virtualized Farm (QEMU/KVM Software Emulation)
- Run all automated tests in cloud CI (GitHub Actions / GitLab CI) using software rendering (llvmpipe/lavapipe) or virtualized VirtIO-GPU.
- *Pros:* High parallelism, low physical infrastructure maintenance.
- *Cons:* Incapable of validating real hardware driver quirks, KMS modesetting, proprietary NVIDIA driver boundaries, GPU power states (S0ix/D3cold), or real-time gaming frame timings.

### Option C: Multi-Tiered Hybrid Compatibility Lab (CHOSEN)
- Tier 1: Cloud/Containerized Virtualized CI (Headless Wayland, VirtIO-GPU, mock testing).
- Tier 2: Dedicated Bare-Metal PXE/iPXE Lab Rack (Physical Intel, AMD, NVIDIA desktop and laptop hardware rigs).
- Tier 3: Differential Golden-Master Trace Comparison (Windows 11 reference vs. NebuWine execution).
- *Pros:* Combines fast pull-request feedback with uncompromising real-world hardware verification.
- *Cons:* Requires dedicated lab infrastructure management (scheduled for P7 implementation).

---

## 4. Decision Outcome

**Chosen Option: Option C — Multi-Tiered Hybrid Compatibility Lab.**

NebuOS establishes a structured Compatibility Lab architecture comprising three test tiers, automated test harnesses, a central telemetry and report repository, and automated quality gates.

```
+-------------------------------------------------------------------------------+
|                       NebuOS Compatibility Lab Architecture                   |
+-------------------------------------------------------------------------------+
                                        |
       +--------------------------------+-------------------------------+
       |                                                                |
       v                                                                v
+-------------------------------+                     +-------------------------------+
| Tier 1: Virtualized CI Farm   |                     | Tier 2: Physical Bare-Metal   |
| (Per-PR & Nightly)            |                     | (Nightly & Release Candidate) |
+-------------------------------+                     +-------------------------------+
| - Headless Smithay Compositor |                     | - Intel Core / Arc Rig        |
| - VirtIO-GPU / lavapipe       |                     | - AMD Ryzen / Radeon Rig      |
| - Wayland Protocol Conformance|                     | - NVIDIA RTX Studio Rig       |
| - Unit & Subsystem Tests      |                     | - Hybrid Dual-GPU Laptop Rig  |
| - Fast Feedback (< 15 mins)   |                     | - Real Display KMS & Audio    |
+-------------------------------+                     +-------------------------------+
       |                                                                |
       +--------------------------------+-------------------------------+
                                        | Test Execution Telemetry
                                        v
                    +---------------------------------------+
                    | Central Compatibility Database (P4/P7)|
                    | - Per-app workflow logs (L0 - L7)     |
                    | - Performance traces & frame times    |
                    | - Crash dumps & dmesg logs            |
                    +---------------------------------------+
                                        |
                                        v
                    +---------------------------------------+
                    | Tier 3: Quality Gate Engine           |
                    | - Release Blocking Gate               |
                    | - Certification Level Calculation     |
                    | - Differential Trace Analysis         |
                    +---------------------------------------+
```

---

## 5. Lab Topology and Hardware Tiers

### 5.1 Physical Lab Test Rigs (Milestone P7 Target)
The physical lab encompasses four primary reference hardware nodes:

1. **Node-INTEL (Modern Intel Platform):**
   - CPU: Intel Core Ultra 7 / i7 (Alder Lake or newer with P/E core topology).
   - GPU: Intel Arc Graphics (Xe / Xe2 architecture).
   - Target Validation: Mesa ANV (Vulkan), Iris (OpenGL), Intel Thread Director scheduling, S0ix Modern Standby.

2. **Node-AMD (Modern AMD Platform):**
   - CPU: AMD Ryzen 7 (Zen 4 / Zen 5).
   - GPU: AMD Radeon RX 7000/8000 series (RDNA3/RDNA4).
   - Target Validation: Mesa RADV (Vulkan), ACO compiler, amdgpu kernel driver, FreeSync/VRR.

3. **Node-NVIDIA (NVIDIA Workstation/Gaming Rig):**
   - CPU: AMD Ryzen or Intel Core.
   - GPU: NVIDIA GeForce RTX 40-series / RTX Ada Generation.
   - Target Validation: NVIDIA proprietary driver (open-gpu-kernel-modules + userspace), GBM Wayland presentation, NVDEC/NVENC, VKD3D-Proton Direct3D 12 ray tracing.

4. **Node-HYBRID (Mobile Laptop Platform):**
   - Platform: Modern dual-GPU laptop (Intel iGPU + NVIDIA dGPU or AMD iGPU + Radeon dGPU).
   - Target Validation: PRIME render offloading (`DRI_PRIME`, `__NV_PRIME_RENDER_OFFLOAD`), display multiplexer (MUX switch / Advanced Optimus), lid-close ACPI suspend/resume, battery drain profiling.

### 5.2 Test Deployment Automation
- Bare-metal nodes boot via automated iPXE into ephemeral bootc/ostree deployment targets.
- Local system storage uses Btrfs subvolumes created on-the-fly; prefixes are generated from clean golden templates (`/var/lib/nebu/runtimes/templates/`).
- Post-test teardown re-images or rolls back subvolume snapshots via `btrfs subvolume delete` to ensure 100% test isolation.

---

## 6. Test Harness and Execution Architecture

### 6.1 Headless Test Runner (`nebu-test-runner`)
For automated CI execution without physical monitors, tests execute against a headless Wayland display server backed by Smithay's headless backend or `wlroots` headless backend:
- Virtual outputs with configurable resolutions (e.g. 1920x1080@60Hz, 3840x2160@120Hz).
- Synthetic Wayland input injection via `wl_test` / `virtual-keyboard-v1` / `virtual-pointer-v1` protocol extensions.
- Deterministic frame capture: Render targets are read directly from offscreen framebuffers for pixel-perfect visual regression testing.

### 6.2 Application Workflow Levels (L0 through L7)
Testing moves beyond process execution to structured functional levels:
- **L0 (Launch):** Process spawns, creates a Wayland surface within 15 seconds, does not immediately abort.
- **L1 (UI Display):** Window paints non-blank buffer, handles resize, repaints properly.
- **L2 (Core Interaction):** Automated script triggers menu clicks, dialog boxes open, text input succeeds.
- **L3 (File Interoperability):** Creates, saves, and reopens files in native formats (`.docx`, `.dwg`, `.blend`, `.prproj`).
- **L4 (Graphics Acceleration):** Direct3D/OpenGL context created via DXVK/VKD3D; renders 3D primitives without GPU hang.
- **L5 (External Extensions):** Loads third-party VST plugins, CAD add-ins, or macros without crash.
- **L6 (Production Pipeline):** Executes complex batch processing (e.g. video export, 3D scene rendering, CAD calculation).
- **L7 (Long-Running Stability):** Runs under continuous simulation for >= 4 hours without memory leak (> 100 MB/hr) or deadlock.

---

## 7. Differential Testing Model

To isolate whether a defect is caused by NebuOS, NebuWine, or the application itself, the Compatibility Lab incorporates a Differential Trace Comparator:
- **Reference Capture:** Automated test scripts execute on a reference Windows 11 installation under a hypervisor with API tracing enabled (e.g., API Monitor, DXVK traces, Wine API trace).
- **Target Capture:** Identical scripts execute under NebuWine with equivalent trace channels enabled.
- **Comparative Classification:**
  - `MATCH`: Output and return codes match within acceptable timing tolerance.
  - `EXPECTED DIFFERENCE`: Known architectural divergence (e.g., Linux path mapping, POSIX UID semantics, font substitution).
  - `REGRESSION`: Return code divergence, unhandled exception, missing Win32 stub, or visual defect.
  - `UNKNOWN`: Unclassified divergent behavior requiring human triage.

---

## 8. Quality Gates and Release Governance

The Compatibility Lab acts as the authoritative gatekeeper for updates:
1. **Tier 0 (Build Gate):** Unit tests, lints, Rust safety audits (`cargo audit`, `cargo clippy -- -D warnings`). Must be 100% PASS.
2. **Tier 1 (Compositor & Wayland Gate):** Headless Wayland protocol conformance tests. Zero regressions allowed.
3. **Tier 2 (Core Application Gate):** Automated L0-L3 testing on the top 20 certified productivity applications. Must achieve 100% PASS.
4. **Tier 3 (Graphics & Gaming Gate):** Bare-metal frame-rate stability and visual regression across reference GPUs. No performance regression > 5% allowed on Stable releases.

---

## 9. Consequences

### Positive Consequences
- Guarantees high release confidence backed by empirical test logs and frame-time metrics.
- Eliminates "works on my machine" triage debates.
- Resolves the missing architectural link identified in PRD §31, §76, §77, and §102.
- Enables automated bi-weekly synchronization with upstream Wine and Mesa.

### Negative Consequences
- Lab hardware requires physical space, power, cooling, and hardware maintenance in Phase P7.
- Proprietary software licensing for CAD/creative suites requires license server configuration in the lab environment.

---

## 10. Verification and Acceptance Criteria

- [x] Architectural specification completed in ADR-0015 and technical specification in `docs/testing/09-compatibility-lab-specification.md`.
- [x] Traceability link from PRD §31, §76, §77, §102 resolved and verified.
- [x] Implementation plan deferred strictly to Phase P7 per project roadmap.
