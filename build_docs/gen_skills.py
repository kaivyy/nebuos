import os

BASE_DIR = "/root/NebuOS/skills"

def write_skill(rel_dir, content):
    full_dir = os.path.join(BASE_DIR, rel_dir) if rel_dir else BASE_DIR
    os.makedirs(full_dir, exist_ok=True)
    file_path = os.path.join(full_dir, "SKILL.md" if rel_dir else "README.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created: {file_path} ({len(content)} bytes)")

# ==============================================================================
# skills/README.md
# ==============================================================================
readme_md = """# NebuOS Modular Agent Skills Catalog

**Catalog Authority:** Operational Workflow Guides for Engineering Agents  
**Status:** ACTIVE  

---

## 1. Purpose of Skills in NebuOS

Skills are specialized operational guides that teach human developers and AI coding agents **HOW TO WORK** within specific domains of the NebuOS project.
- **Skills are NOT sources of truth:** Architectural decisions come from `docs/decisions/` (ADRs), requirements come from `PRD.md`, and technical schemas come from `docs/specification/`.
- **Skills explain workflow and constraints:** They define domain boundaries, allowed/forbidden changes, mandatory verification procedures, common failure modes, and handoff expectations.
- **Read on Demand:** Agents should **ONLY** read skills directly relevant to their active task. Do not exhaust context by ingesting all skills indiscriminately.

---

## 2. Skill Discovery Catalog

| Domain Directory | Skill Name | Target Milestones | Primary Scope & Focus |
|---|---|---|---|
| [`architecture/`](architecture/SKILL.md) | Architecture Governance | All (P0–P8) | System layering, milestone boundaries, ADR rules, conflict protocol, traceability |
| [`rust/`](rust/SKILL.md) | Rust Systems Engineering | P1, P2, P3, P4 | Idiomatic Rust, error propagation, minimal unsafe, clippy, cargo policies |
| [`system/`](system/SKILL.md) | Base OS & System Services | P0, P8 | Fedora Atomic / bootc, Btrfs subvolumes, systemd, dracut, GRUB/BLS, TTY, updates |
| [`compositor/`](compositor/SKILL.md) | Wayland Compositor | P1 | Smithay 0.3+, DRM/KMS, libinput, Mesa, Xwayland boundary, pure Wayland |
| [`shell/`](shell/SKILL.md) | Desktop Shell & UI | P2 | NebuShell, Slint toolkit, Theme vs Layout vs Behavior, single shell paradigm |
| [`runtime/`](runtime/SKILL.md) | Windows App Runtime | P3 | Wine 9.x, Proton, per-app prefix isolation, Btrfs reflink, bwrap sandbox |
| [`compatibility/`](compatibility/SKILL.md) | Compatibility Platform | P4, P7 | SQLite compat DB, PE fingerprinting, patch engine DSL, certification tiers |
| [`graphics/`](graphics/SKILL.md) | 3D Graphics & Drivers | P5 | Mesa, Vulkan, OpenGL, DXVK, VKD3D-Proton, PRIME hybrid GPU, shader cache |
| [`security/`](security/SKILL.md) | Security & Containment | All (P0–P8) | SELinux (permissive->enforcing), Bubblewrap, seccomp BPF, capabilities, namespaces |
| [`testing/`](testing/SKILL.md) | Verification & Testing | All (P0–P8) | Test pyramid, boot testing, compatibility lab, Tested vs Verified vs Accepted |
| [`performance/`](performance/SKILL.md) | Performance Engineering | All (P0–P8) | Benchmarking methodology, latency budgets, idle memory limits, regression gates |
| [`documentation/`](documentation/SKILL.md) | Documentation Sync | All (P0–P8) | Doc synchronization, drift detection, traceability, ADR authoring |
| [`release/`](release/SKILL.md) | Release & Updates | P0, P8 | bootc image build, ostree deployment, signing, automatic rollback, recovery |

---

## 3. Mandatory Structure of Every SKILL.md

Every skill file adheres strictly to a 10-section schema:
1. **Purpose:** Why this skill exists and what problems it solves.
2. **Scope:** Target milestone and subsystems covered.
3. **Relevant Documentation:** Authoritative specifications and ADRs governing this domain.
4. **Allowed Changes:** Exact files and components permitted to be modified.
5. **Forbidden Changes:** Explicitly prohibited edits, anti-scope, and destructive actions.
6. **Architecture Constraints:** Invariants, protocols, and technical dependencies.
7. **Implementation Guidance:** Best practices, coding conventions, and design patterns.
8. **Verification:** Concrete commands, test scenarios, and evidence collection.
9. **Common Failure Modes:** Recurring pitfalls, subtle bugs, and how to avoid them.
10. **Handoff Requirements:** Mandatory reporting fields before yielding to the next agent.
"""

# ==============================================================================
# 1. skills/architecture/SKILL.md
# ==============================================================================
architecture_skill = """# Architecture Governance Skill — NebuOS

## 1. Purpose
This skill governs how architects and agents maintain architectural integrity, enforce milestone boundaries, handle technical conflicts, and record architectural decisions (ADRs) across the NebuOS project.

## 2. Scope
Applies to all milestones (P0 through P8) and all top-level architectural documentation (`PRD.md`, `ARCHITECTURE.md`, `docs/decisions/`, `docs/roadmap/`).

## 3. Relevant Documentation
- `PRD.md`: Master Product Requirements and non-negotiable invariants.
- `ARCHITECTURE.md`: Conceptual layer topology and system navigation.
- `docs/decisions/ADR-0001` through `ADR-0010`: Approved architectural decisions.
- `docs/roadmap/00-implementation-roadmap.md`: Milestone dependency DAG.

## 4. Allowed Changes
- Drafting new Architecture Decision Records (ADRs) in `docs/decisions/`.
- Updating `ARCHITECTURE.md` navigation links and layer diagrams.
- Maintaining requirements traceability in `docs/TRACEABILITY.md`.

## 5. Forbidden Changes
- **NO SILENT ARCHITECTURE CHANGES:** Never replace chosen components (e.g., swapping Smithay for wlroots, bootc for raw ostree, Slint for GTK) without an approved ADR.
- **NO VIRTUAL MACHINES:** Never introduce KVM/QEMU guest hypervisors for Windows compatibility.
- **NO PREMATURE IMPLEMENTATION:** Never implement future milestone features in early milestones.

## 6. Architecture Constraints
- Maintain the strict layer hierarchy: Kernel -> Fedora bootc -> System Services -> Wayland -> Smithay -> NebuShell -> NebuRuntime -> Wine/Proton -> Windows Apps.
- Enforce strict milestone entry and exit criteria.

## 7. Implementation Guidance
- When resolving contradictions between docs: follow the Source of Truth Hierarchy (`PRD` > `ADRs` > `Specifications` > `Roadmap` > `Implementation`).
- Use the 9-step Conflict Protocol defined in `AGENTS.md` §5.

## 8. Verification
- Validate cross-references across specifications with static link checkers.
- Confirm that every PRD requirement maps cleanly to at least one specification in `docs/TRACEABILITY.md`.

## 9. Common Failure Modes
- "Architectural Drift": Code implements an unapproved pattern because it was "easier" or "more modern".
- "Bypassing ADRs": Deciding to add a large dependency without documenting the trade-off.

## 10. Handoff Requirements
- Document any identified architectural discrepancies under `Known Issues` in `HANDOFF.md`.
- Report ADR status changes (Proposed, Accepted, Superseded).
"""

# ==============================================================================
# 2. skills/rust/SKILL.md
# ==============================================================================
rust_skill = """# Rust Systems Engineering Skill — NebuOS

## 1. Purpose
This skill establishes strict coding, error-handling, memory-safety, and dependency standards for all Rust components in NebuOS (`nebu-compositor`, `nebu-shell`, `nebu-runtime-daemon`).

## 2. Scope
Applies to milestones P1 through P4 and any custom Rust crates in the workspace.

## 3. Relevant Documentation
- `docs/development/05-coding-guidelines.md`: Rust coding standards.
- `docs/development/04-dependency-policy.md`: Approved external crate list and licensing.
- `docs/interfaces/02-runtime-interfaces.md`: Rust trait definitions.

## 4. Allowed Changes
- Creating and editing Rust files in `src/` or Cargo workspace crates.
- Adding unit and integration tests under `tests/`.
- Writing Rustdoc comments on public APIs.

## 5. Forbidden Changes
- **NO UNJUSTIFIED `unsafe`:** Never use `unsafe` for speed or convenience. All `unsafe` blocks require a detailed `// SAFETY:` rationale.
- **NO PRODUCTION PANICS:** Never call `.unwrap()` or `.expect()` in production codepaths.
- **NO UNAUTHORIZED DEPENDENCIES:** Never add external crates to `Cargo.toml` without satisfying the 10-point Dependency Policy in `AGENTS.md` §11.

## 6. Architecture Constraints
- All daemons must interface asynchronously via `zbus` 4.x.
- Memory allocations must respect individual process budgets (Compositor < 60MB, Shell < 25MB, Runtime Daemon < 15MB).

## 7. Implementation Guidance
- Use `thiserror` for library error enums and `anyhow` for binary application top-levels.
- Structure error types with rich context (e.g., `PrefixError::ReflinkFailed { path, source }`).
- Adhere to the Rust API Guidelines (`clippy`, idiomatic borrowing, RAII).

## 8. Verification
- `cargo fmt --check` must return exit code 0.
- `cargo clippy --workspace --all-targets -- -D warnings` must return exit code 0.
- `cargo test --workspace` must pass all tests.

## 9. Common Failure Modes
- Leaking file descriptors or child processes during process supervisor crashes.
- High memory usage caused by unbounded IPC buffers.

## 10. Handoff Requirements
- Record `clippy` and `cargo test` execution outputs in `HANDOFF.md`.
- Explicitly list any new crate dependencies added to workspace `Cargo.toml`.
"""

# ==============================================================================
# 3. skills/system/SKILL.md
# ==============================================================================
system_skill = """# Base OS & System Services Skill — NebuOS

## 1. Purpose
Governs the creation, configuration, and maintenance of the Fedora Atomic / bootc base operating system, Btrfs subvolumes, systemd services, dracut initramfs, and bootloader integration.

## 2. Scope
Applies primarily to Milestone P0 (Foundation OS) and Milestone P8 (Production Hardening).

## 3. Relevant Documentation
- `docs/roadmap/01-p0-foundation.md`: Milestone P0 execution plan.
- `docs/specification/00-system-specification.md`: Base image package manifests.
- `docs/specification/01-boot-specification.md`: dracut, GRUB2, and BLS sequence.
- `docs/specification/03-filesystem-specification.md`: Btrfs subvolumes and mount table.
- `docs/decisions/ADR-0001-base-os-architecture.md`: Fedora Atomic and bootc.
- `docs/decisions/ADR-0002-btrfs-filesystem-layout.md`: Btrfs storage layout.

## 4. Allowed Changes
- Authoring and updating `Containerfile.p0` and future container build layers.
- Configuring dracut configuration files in `/etc/dracut.conf.d/`.
- Creating systemd unit files and presets in `/usr/lib/systemd/system/`.
- Authoring automated QEMU boot test scripts in `tests/integration/`.

## 5. Forbidden Changes
- **ZERO GUI PACKAGES IN P0:** Never add Wayland, Smithay, Slint, Weston, X11, or Mesa 3D packages to the P0 container manifest.
- **ZERO WINE IN P0:** Never install Wine or Proton packages in the P0 container.
- **NO HOST MODIFICATIONS:** Never execute partitioning or bootloader commands against the development host.

## 6. Architecture Constraints
- Target architecture: x86_64 UEFI with Boot Loader Specification (BLS Type 1).
- Immutable root: `/usr` mounted strictly read-only (`ro`).
- Subvolume layout: `@` (`/sysroot`), `@home` (`/var/home`), and `@var` (`/var`).
- Default target in P0: `multi-user.target` with TTY login on `tty1` and `ttyS0`.

## 7. Implementation Guidance
- Base image: Use `quay.io/fedora/fedora-bootc:40`.
- In P0, configure `SELINUX=permissive` in `/etc/selinux/config` to prevent false boot denials.
- Keep package manifest minimal: use the 7 core packages specified in `01-p0-foundation.md`.

## 8. Verification
- `podman build -t nebu-os:p0 -f Containerfile.p0 .` builds successfully.
- `bootc container lint` reports 0 errors.
- Automated QEMU boot test boots to `agetty` login prompt in < 3.5s with idle RAM < 150 MB RSS.

## 9. Common Failure Modes
- dracut omitting Btrfs module, causing root subvolume mount timeout and emergency shell drop.
- Forgetting `rootflags=subvol=@` in kernel parameters.

## 10. Handoff Requirements
- Record QEMU boot log and `systemd-analyze` timing report in `HANDOFF.md`.
- Report total container image size and idle memory RSS.
"""

# ==============================================================================
# 4. skills/compositor/SKILL.md
# ==============================================================================
compositor_skill = """# Wayland Compositor Engineering Skill — NebuOS

## 1. Purpose
Governs the design, implementation, and maintenance of `nebu-compositor`, the pure-Rust Wayland display compositor built upon the Smithay framework.

## 2. Scope
Applies strictly to Milestone P1 (NebuCompositor) and its subsequent integration points.

## 3. Relevant Documentation
- `docs/roadmap/02-p1-nebucompositor.md`: Milestone P1 execution blueprint.
- `docs/desktop/01-compositor.md`: Compositor architectural overview.
- `docs/interfaces/03-compositor-interfaces.md`: Wayland protocol definitions.
- `docs/decisions/ADR-0003-smithay-wayland-compositor.md`: Smithay architecture decision.

## 4. Allowed Changes
- Implementing compositor source code under `crates/nebu-compositor/`.
- Authoring Wayland protocol extension XML and generated bindings.
- Configuring DRM/KMS backend pipelines and libinput event loops.

## 5. Forbidden Changes
- **DO NOT WORK IN P0:** This skill is **LOCKED** until Milestone P0 passes all exit gates.
- **NO SHELL WIDGETS IN COMPOSITOR:** The compositor handles display surfaces and window trees; desktop UI (taskbars, docks, launchers) belongs strictly in `nebu-shell`.
- **NO IN-PROCESS WINE EXECUTION:** The compositor does not launch or supervise Windows applications directly.

## 6. Architecture Constraints
- Framework: Smithay 0.3+ in pure Rust.
- Core Protocols: `xdg-shell`, `wlr-layer-shell-unstable-v1`, `linux-dmabuf-v1`, `viewporter`, `fractional-scale-v1`.
- Display Target: Direct DRM/KMS TTY takeover (seatd / logind).
- Legacy Apps: Rootless Xwayland spawned exclusively on-demand.

## 7. Implementation Guidance
- Implement strict damage tracking to eliminate unnecessary frame repaints and preserve CPU/GPU power.
- Expose window management state to the shell via D-Bus interface `org.nebu.Compositor1`.
- Keep memory footprint strictly under 60 MB RSS.

## 8. Verification
- Headless compositor test running under `Winit` or virtual DRM backend.
- Wayland client compliance verification using `weston-simple-shm` and `weston-terminal`.
- Frame timing verification: 60 FPS presentation without frame drops.

## 9. Common Failure Modes
- Zombie Xwayland processes lingering after legacy client termination.
- Deadlocks in event loops when waiting on D-Bus synchronous calls.

## 10. Handoff Requirements
- Record verified Wayland protocol versions and client test execution results in `HANDOFF.md`.
"""

# ==============================================================================
# 5. skills/shell/SKILL.md
# ==============================================================================
shell_skill = """# Desktop Shell & UI Engineering Skill — NebuOS

## 1. Purpose
Governs the development of `nebu-shell`, the unified, pluggable desktop shell environment providing panels, docks, application launchers, system tray, and notifications.

## 2. Scope
Applies strictly to Milestone P2 (NebuShell).

## 3. Relevant Documentation
- `docs/roadmap/03-p2-nebushell.md`: Milestone P2 roadmap.
- `docs/desktop/02-shell.md`: Shell architecture overview.
- `docs/desktop/03-ui-theme-system.md`: Theme engine specification.
- `docs/desktop/04-layout-system.md`: Layout engine specification.
- `docs/decisions/ADR-0009-nebushell-ui-architecture.md`: Single shell pluggable architecture.

## 4. Allowed Changes
- Authoring shell source code under `crates/nebu-shell/`.
- Developing Slint UI markup files (`.slint`).
- Defining built-in theme presets (Default Dark, Windows-like, macOS-like).

## 5. Forbidden Changes
- **DO NOT WORK IN P0 OR P1:** Locked until P0 and P1 exit criteria are fully satisfied.
- **NO SEPARATE SHELL BINARIES:** Never build separate binaries for Windows-like vs macOS-like layouts. Use a single binary with runtime layout switching.
- **THEME != LAYOUT != BEHAVIOR:** Do not conflate styling (Theme), panel geometry (Layout), and window management logic (Behavior).

## 6. Architecture Constraints
- UI Toolkit: **Slint** (ADR-0009).
- Integration Protocol: `wlr-layer-shell` for anchoring panels and overlays.
- Shell Memory Budget: Idle RAM strictly under 25 MB RSS.

## 7. Implementation Guidance
- Keep Slint UI definitions clean, declarative, and decoupled from business logic.
- Connect to `nebu-compositor` via layer-shell protocol and `org.nebu.Compositor1` D-Bus.
- Implement Freedesktop specifications: Notification Daemon (`org.freedesktop.Notifications`) and StatusNotifierItem system tray.

## 8. Verification
- Validate layout switching dynamically without restarting the shell process.
- Benchmark idle RAM footprint (`free -m` / `smem`) asserting shell RSS < 25 MB.

## 9. Common Failure Modes
- Slint UI thread blocking on synchronous D-Bus or disk I/O.
- Memory bloat caused by uncompressed icon caches.

## 10. Handoff Requirements
- Document active UI toolkit version, layout switching test results, and RAM measurements in `HANDOFF.md`.
"""

# ==============================================================================
# 6. skills/runtime/SKILL.md
# ==============================================================================
runtime_skill = """# Windows Application Runtime Skill — NebuOS

## 1. Purpose
Governs the architecture, isolation, and execution lifecycle of Windows applications running under Wine/Proton, supervised by `nebu-runtime-daemon`.

## 2. Scope
Applies strictly to Milestone P3 (NebuRuntime).

## 3. Relevant Documentation
- `docs/roadmap/04-p3-neburuntime.md`: Milestone P3 execution plan.
- `docs/specification/02-process-ipc-specification.md`: Process model and cgroups.
- `docs/runtime/00-runtime-specification.md`: Master runtime daemon specification.
- `docs/runtime/04-prefix-management.md`: Prefix directory tree and reflink cloning.
- `docs/decisions/ADR-0004-wine-proton-integration.md`: Dual Wine/Proton strategy.
- `docs/decisions/ADR-0006-btrfs-reflink-prefix-management.md`: Btrfs reflink prefixes.

## 4. Allowed Changes
- Authoring runtime daemon code in `crates/nebu-runtime-daemon/`.
- Managing Btrfs prefix templates in `/usr/share/nebu/prefix-template/`.
- Authoring Bubblewrap (`bwrap`) argument templates.

## 5. Forbidden Changes
- **DO NOT WORK IN P0, P1, OR P2:** Locked until P0, P1, and P2 are complete.
- **NO GLOBAL UNCONFINED WINE:** Never invoke raw `/usr/bin/wine` directly without container sandboxing.
- **NO EXPOSING ROOT AS Z: DRIVE:** The Linux root filesystem (`/`) must NEVER be mounted as `Z:`. Only sandboxed user folders (`~/Documents`) may be mapped.

## 6. Architecture Constraints
- **Per-Application Prefix Isolation:** Every Windows application operates in its own dedicated prefix:
  `~/.var/nebu/prefixes/<app-id>/`
  - `pfx/drive_c/`
  - `pfx/system.reg`, `user.reg`
  - `logs/`
  - `metadata.json`
- **Instant Provisioning:** Prefixes instantiated via Btrfs reflink (`cp --reflink=always -r ...`) in < 50ms.
- **Process Supervision:** Controlled process tree via systemd transient cgroups (`app-nebu-<app-id>.scope`).

## 7. Implementation Guidance
- Maintain separate `wineserver` instances per prefix.
- Implement robust shutdown: terminate child processes cleanly with `SIGTERM` followed by `SIGKILL` on timeout.
- Expose D-Bus API `org.nebu.Runtime1` for application launch, termination, and prefix health repair.

## 8. Verification
- Verify that killing one Windows application leaves other prefixes completely unaffected.
- Verify that modifying files inside `C:\Windows\` does not contaminate the master template.

## 9. Common Failure Modes
- Orphaned `wineserver` processes hanging indefinitely in background.
- Concurrent access corrupting registry hives when locking is omitted.

## 10. Handoff Requirements
- Record prefix creation benchmarks and process tree cleanup test results in `HANDOFF.md`.
"""

# ==============================================================================
# 7. skills/compatibility/SKILL.md
# ==============================================================================
compatibility_skill = """# Compatibility Platform & Database Skill — NebuOS

## 1. Purpose
Governs the SQLite compatibility database, application binary fingerprinting, declarative patch engine DSL, and compatibility certification tiers.

## 2. Scope
Applies to Milestone P4 (Compatibility Engine) and Milestone P7 (Compatibility Lab).

## 3. Relevant Documentation
- `docs/roadmap/05-p4-compatibility-engine.md`: Milestone P4 roadmap.
- `docs/compatibility/00-compatibility-specification.md`: Compatibility platform.
- `docs/compatibility/01-database-schema.md`: SQLite schema and queries.
- `docs/compatibility/02-compatibility-profile.md`: Profile JSON schema.
- `docs/compatibility/03-patch-engine.md`: 9-tier patch hierarchy.

## 4. Allowed Changes
- Creating SQLite database migrations and schema files.
- Implementing PE header parser and SHA-256 fingerprinting algorithms.
- Authoring declarative application compatibility profiles (`profiles/*.json`).

## 5. Forbidden Changes
- **NO UNSUPPORTED CLAIMS:** Never certify an application as compatible without executing the full 12-point compatibility lifecycle test.
- **NO PROPRIETARY ASSETS:** Never embed proprietary Microsoft DLLs or fonts in compatibility profiles.

## 6. Architecture Constraints
- Application Certification Tiers: Platinum, Gold, Silver, Bronze, Broken.
- Verification Lifecycle: Install -> Launch -> Open -> Edit -> Save -> Export -> Print -> GPU -> Plugin -> Stress -> Close -> Reopen.

## 7. Implementation Guidance
- Fingerprint executables by hashing the `.text` section and matching PE header fields (`Subsystem`, `Characteristics`, `TimeDateStamp`) to prevent false matches across versions.
- Execute patches in declarative order: DLL overrides -> Registry tweaks -> Environment variables.

## 8. Verification
- Run automated SQLite schema migration tests against seed databases.
- Test PE parser against known benign Win32/x64 binaries (7-Zip, Notepad++ installers).

## 9. Common Failure Modes
- Profile conflicts when multiple patch recipes modify the same registry key.
- False positive binary identification due to generic installer wrappers.

## 10. Handoff Requirements
- Report total registered application profiles and schema migration test logs in `HANDOFF.md`.
"""

# ==============================================================================
# 8. skills/graphics/SKILL.md
# ==============================================================================
graphics_skill = """# 3D Graphics & Driver Architecture Skill — NebuOS

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
"""

# ==============================================================================
# 9. skills/security/SKILL.md
# ==============================================================================
security_skill = """# Security Architecture & Containment Skill — NebuOS

## 1. Purpose
Governs the defense-in-depth security architecture: SELinux policies, Bubblewrap unprivileged namespaces, seccomp BPF syscall filters, and cgroups resource limits.

## 2. Scope
Applies across all milestones (P0 through P8).

## 3. Relevant Documentation
- `docs/specification/04-security-specification.md`: Security architecture.
- `docs/decisions/ADR-0010-bubblewrap-security-isolation.md`: Bubblewrap isolation.
- `docs/audit/P0_READY_GATE.md`: P0 SELinux permissive mandate.

## 4. Allowed Changes
- Authoring Bubblewrap arguments (`--ro-bind`, `--unshare-net`, `--tmpfs`).
- Writing BPF seccomp filter definitions.
- Authoring custom SELinux type enforcement files (`nebu-sandbox.te`).

## 5. Forbidden Changes
- **NO PERMANENT SECURITY DISABLEMENT:** Never disable SELinux or seccomp globally to "make something work" without documenting an explicit security exception.
- **NO SETUID ROOT BINARIES:** All containerization must use unprivileged user namespaces (`bwrap`).

## 6. Architecture Constraints
- Multi-tier containment model: cgroups v2 -> Bubblewrap -> seccomp-bpf -> SELinux.
- SELinux Policy: `permissive` during P0–P4; `enforcing` activated in P5 with `nebu-sandbox.te`.
- Root filesystem isolation: `/usr` is strictly read-only; `/` is never exposed to Windows apps.

## 7. Implementation Guidance
- Ensure offline applications have their network namespace severed via `bwrap --unshare-net`.
- Block dangerous syscalls via seccomp: `ptrace`, `kexec_load`, `sys_rawio`, `reboot`.

## 8. Verification
- Verify that a compromised binary inside `bwrap` cannot read files in `~/.ssh` or `/var/log`.
- Inspect `/var/log/audit/audit.log` for unexpected SELinux avc denials.

## 9. Common Failure Modes
- Incompatible seccomp filters breaking Wine's Windows NT exception handling.
- Spurious SELinux avc denials blocking `bwrap` pseudo-terminal allocation.

## 10. Handoff Requirements
- Document active SELinux mode, audit log status, and containment test results in `HANDOFF.md`.
"""

# ==============================================================================
# 10. skills/testing/SKILL.md
# ==============================================================================
testing_skill = """# Verification & Testing Engineering Skill — NebuOS

## 1. Purpose
Governs the testing pyramid, test environment provisioning, headless QEMU boot harnesses, automated compatibility suites, and release gate certification.

## 2. Scope
Applies to all milestones (P0 through P8).

## 3. Relevant Documentation
- `docs/testing/00-testing-specification.md`: Testing pyramid.
- `docs/testing/02-integration-testing.md`: QEMU test environments.
- `docs/testing/03-compatibility-testing.md`: Windows application test matrix.
- `docs/audit/P0_READY_GATE.md`: P0 12-test acceptance matrix.

## 4. Allowed Changes
- Authoring automated test scripts in `tests/integration/` and `tests/system/`.
- Adding unit test modules within Rust crates (`#[cfg(test)]`).
- Maintaining regression test manifests.

## 5. Forbidden Changes
- **NO FALSE SUCCESS CLAIMS:** Never assert a test has passed without executing the command and capturing terminal output.
- **NO DESTRUCTIVE TEST CLEANUP:** Never delete host directories or uncommitted work during test cleanup.

## 6. Architecture Constraints
- Distinguish strictly between:
  - **Tested:** Verification command executed.
  - **Verified:** Acceptance criteria mathematically and functionally proven.
  - **Accepted:** Formal sign-off against roadmap exit gates.

## 7. Implementation Guidance
- Author deterministic, reproducible test scripts with explicit timeouts and exit codes.
- Structure QEMU integration tests with serial console logging (`-serial stdio -display none`).

## 8. Verification
- Verify that test runners clean up all child processes, virtual disk images, and tap interfaces upon exit.

## 9. Common Failure Modes
- Flaky tests caused by arbitrary `sleep` calls instead of polling ready states with timeouts.
- Test suites passing falsely because assertions were omitted or errors were swallowed.

## 10. Handoff Requirements
- Include raw execution commands, exit codes, and stdout/stderr summaries in `HANDOFF.md`.
"""

# ==============================================================================
# 11. skills/performance/SKILL.md
# ==============================================================================
performance_skill = """# Performance Engineering & Benchmarking Skill — NebuOS

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
"""

# ==============================================================================
# 12. skills/documentation/SKILL.md
# ==============================================================================
documentation_skill = """# Documentation Synchronization & Drift Control Skill — NebuOS

## 1. Purpose
Governs documentation integrity, bidirectional traceability between specs and code, cross-referencing consistency, and documentation drift detection.

## 2. Scope
Applies across all 111+ documentation files in `docs/` and root registers.

## 3. Relevant Documentation
- `docs/INDEX.md`: Master documentation index.
- `docs/TRACEABILITY.md`: Requirements traceability matrix.
- `docs/audit/DOCUMENTATION_AUDIT_REPORT.md`: Comprehensive documentation audit.

## 4. Allowed Changes
- Updating technical specifications when system behavior or APIs change.
- Refreshing cross-reference links in `docs/INDEX.md` and `docs/TRACEABILITY.md`.
- Adding deprecation notices to legacy blueprint files in `docs/architecture/`.

## 5. Forbidden Changes
- **NO SILENT DRIFT:** Never change implementation behavior without updating corresponding specifications.
- **NO REDUNDANT SOURCES OF TRUTH:** Do not create duplicate files that compete with existing specifications.

## 6. Architecture Constraints
- Maintain the documentation hierarchy: `PRD.md` > `ADRs` > `Specifications` > `Roadmap` > `Implementation`.
- Ensure all 103 PRD requirements remain mapped in `docs/TRACEABILITY.md`.

## 7. Implementation Guidance
- Detect documentation drift whenever a PR modifies code without touching `docs/`.
- Ensure GitHub Markdown relative links use correct relative paths from their directory.

## 8. Verification
- Run static link validation to guarantee 0 broken relative links across `docs/`.
- Verify that every ADR in `docs/decisions/` is indexed in `docs/INDEX.md`.

## 9. Common Failure Modes
- Updating a file path during refactoring but leaving broken links in `docs/INDEX.md`.
- Describing speculative, unimplemented features as "current capabilities" in docs.

## 10. Handoff Requirements
- Report total documentation files modified and link verification results in `HANDOFF.md`.
"""

# ==============================================================================
# 13. skills/release/SKILL.md
# ==============================================================================
release_skill = """# Release Engineering & Update Lifecycle Skill — NebuOS

## 1. Purpose
Governs container image packaging, ostree artifact signing, transactional update distribution (`bootc update`), automatic rollback mechanisms, and release gates.

## 2. Scope
Applies to Milestone P0 (Base image provisioning) and Milestone P8 (Production Release).

## 3. Relevant Documentation
- `docs/updates/00-update-specification.md`: Master update specification.
- `docs/updates/01-image-build.md`: Containerfile layer optimization.
- `docs/updates/04-rollback-recovery.md`: Rollback procedures and boot counter.
- `docs/development/06-release-engineering.md`: Release engineering workflow.

## 4. Allowed Changes
- Configuring OCI container registry push/pull manifests.
- Authoring update verification scripts.
- Managing release notes and compatibility matrix changelogs.

## 5. Forbidden Changes
- **NO MUTABLE UPDATES:** Never perform live in-place package upgrades on the root filesystem (`dnf upgrade` on running system is strictly forbidden).
- **NO DATA LOSS ON ROLLBACK:** Rollback operations must NEVER delete or alter `/var` or `/var/home`.

## 6. Architecture Constraints
- Updates are 100% container-native via `bootc update`.
- Rollbacks are instantaneous via selecting the previous ostree deployment entry in GRUB BLS.
- Automatic recovery triggers if 3 consecutive boot attempts fail to reach `multi-user.target`.

## 7. Implementation Guidance
- Ensure release container images are cryptographically signed using `cosign` or GPG.
- Verify that image layer caching minimizes bandwidth consumption during incremental OTA updates.

## 8. Verification
- Simulate a failed update in QEMU and assert that GRUB automatically rolls back to the prior deployment.
- Verify that `/var/home` user documents remain 100% intact across updates and rollbacks.

## 9. Common Failure Modes
- Update modifying `/etc` configuration files without preserving user customizations via 3-way merge.
- Missing `grubenv` boot counter update, preventing automated rollback on boot hangs.

## 10. Handoff Requirements
- Record image digest hashes, update test logs, and rollback verification evidence in `HANDOFF.md`.
"""

# Write README and all 13 skills
write_skill("", readme_md)
write_skill("architecture", architecture_skill)
write_skill("rust", rust_skill)
write_skill("system", system_skill)
write_skill("compositor", compositor_skill)
write_skill("shell", shell_skill)
write_skill("runtime", runtime_skill)
write_skill("compatibility", compatibility_skill)
write_skill("graphics", graphics_skill)
write_skill("security", security_skill)
write_skill("testing", testing_skill)
write_skill("performance", performance_skill)
write_skill("documentation", documentation_skill)
write_skill("release", release_skill)
print("Skills directory generated successfully.")
