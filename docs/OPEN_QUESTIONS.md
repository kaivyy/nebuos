# NebuOS Open Architectural Questions Register

**Status:** OPEN  
**Purpose:** Formal tracking, trade-off analysis, option evaluation, and deadline management for unresolved engineering design decisions across all NebuOS subsystems.  
**Scope:** Architectural ambiguities and design branch points affecting the Linux base, NebuCompositor, NebuShell, NebuRuntime, compatibility engine, and graphics pipeline.  
**Non-goals:** Tracking bug tickets, sprint tasks, or implementation-level code review questions.

---

## 1. Summary Matrix

| ID | Priority | Domain | Question Summary | Current Recommendation | Decision Deadline |
|---|---|---|---|---|---|
| **OQ-001** | P0 | Shell | Slint vs Iced for native NebuShell toolkit? | **RESOLVED (ADR-0019):** Slint 1.7+ adopted as exclusive native desktop toolkit | RESOLVED |
| **OQ-002** | P0 | Compatibility | Exact Wine version pinning strategy: Stable vs Staging? | **RESOLVED (ADR-0016/0017):** NebuWine downstream distribution with Stable/Candidate/Gaming/Legacy channels on `/var/lib/nebu/runtimes/` | RESOLVED |
| **OQ-003** | P0 | Compatibility | Proton vs Wine Staging for non-Steam applications? | Wine Staging for Desktop/CAD, Proton for Games | Milestone P6 Exit |
| **OQ-004** | P0 | System | SELinux enforcing vs permissive initial policy? | Permissive during P0–P4, Enforcing at P5 | Milestone P1 Exit |
| **OQ-005** | P1 | System | Flatpak vs native packaging for NebuOS components? | Native OSTree for OS, Flatpak for 3rd-party Linux apps | Milestone P2 Exit |
| **OQ-006** | P0 | System | Default root filesystem: Btrfs subvolumes vs Ext4 fallback? | Btrfs mandatory (`nodatacow` for Wine prefixes) | Milestone P1 Exit |
| **OQ-007** | P1 | System | Session bus daemon: `dbus-broker` vs standard `dbus-daemon`? | `dbus-broker` (zero-copy linux-memfd, low latency) | Milestone P1 Exit |
| **OQ-008** | P0 | System | Low-memory killer strategy: `systemd-oomd` vs `earlyoom`? | `systemd-oomd` with PSI thresholds + cgroups v2 | Milestone P3 Exit |
| **OQ-009** | P1 | System | Target kernel cadence: 6.6 LTS vs Fedora Fast-Moving Stable? | Fedora Stable with automated hardware regression gates | Milestone P2 Exit |
| **OQ-010** | P0 | Compositor | Smithay pure-Rust framework vs wlroots C-bindings? | Smithay (pure Rust, zero FFI, memory safety) | Milestone P0 Exit |
| **OQ-011** | P1 | Compositor | Fractional scaling: `wp-fractional-scale-v1` vs viewport downsampling? | Native `wp-fractional-scale-v1` with integer fallback | Milestone P2 Exit |
| **OQ-012** | P1 | Compositor | Direct scanout pipeline: Fullscreen bypass vs compositor overlay? | Direct scanout for uninhibited single-surface clients | Milestone P2 Exit |
| **OQ-013** | P0 | Compositor | Compositor crash recovery & process survivability? | Session preservation via `ext-session-lock-v1` & respawn | Milestone P3 Exit |
| **OQ-014** | P2 | Compositor | Variable Refresh Rate (VRR) multi-monitor arbitration? | Per-connector VRR enabled only on active focused output | Milestone P9 Exit |
| **OQ-015** | P1 | Shell | Shell component IPC: Wayland layer-shell vs D-Bus control? | Wayland `wlr-layer-shell` for visuals, D-Bus for data | Milestone P3 Exit |
| **OQ-016** | P2 | Shell | Shell Low-End Mode asset handling: SVG vs pre-baked raster atlases? | Pre-rasterized atlas cache with zero run-time SVG parse | Milestone P3 Exit |
| **OQ-017** | P2 | Shell | Notification daemon: In-process shell module vs standalone daemon? | In-process shell submodule exposing `org.freedesktop.Notifications` | Milestone P4 Exit |
| **OQ-018** | P1 | Shell | Taskbar window preview generation: Compositor DMA-BUF vs screencopy? | Compositor-driven shared DMA-BUF thumbnail export | Milestone P3 Exit |
| **OQ-019** | P0 | Runtime | Sandboxing mechanism: Bubblewrap (`bwrap`) vs Landlock LSM + seccomp? | Bubblewrap baseline, Landlock LSM secondary confinement | Milestone P5 Exit |
| **OQ-020** | P0 | Runtime | Prefix deduplication: Btrfs reflink vs shared read-only base templates? | Btrfs `reflink` provisioning from golden base template | Milestone P5 Exit |
| **OQ-021** | P1 | Runtime | Process lifecycle supervision: Rust daemon supervisor vs systemd scopes? | Systemd transient user scopes (`nebu-app-<id>.scope`) | Milestone P5 Exit |
| **OQ-022** | P1 | Runtime | Warm cache resident memory budget on 4GB systems? | Strict 64MB budget; auto-evict on RAM pressure >80% | Milestone P5 Exit |
| **OQ-023** | P0 | Runtime | Virtual drive (`Z:\`) host filesystem mount security policy? | Strict portal-based file picker mounting, NO full `/` read | Milestone P6 Exit |
| **OQ-024** | P1 | Compatibility | .NET runtime bridge: Wine-Mono vs native Microsoft CoreCLR injection? | Wine-Mono baseline; native winetricks fallback for CAD | Milestone P6 Exit |
| **OQ-025** | P0 | Compatibility | Anti-cheat / kernel driver (.sys) policy? | Hard block with immediate user-facing explanation (NO VM) | Milestone P6 Exit |
| **OQ-026** | P1 | Compatibility | Local compatibility DB update delivery: SQLite snapshot vs OCI delta? | Incremental SQLite delta patches signed over HTTPS/OCI | Milestone P7 Exit |
| **OQ-027** | P1 | Compatibility | Proprietary licensing daemons (Autodesk Access, Adobe CC)? | Headless stub background services with mock loopback sockets | Milestone P10 Exit |
| **OQ-028** | P0 | Compatibility | Multi-instance `wineserver` vs shared `wineserver`? | Strict isolated `wineserver` per application prefix | Milestone P5 Exit |
| **OQ-029** | P0 | Graphics | Direct3D 9–11 translation: DXVK Vulkan vs WineD3D OpenGL fallback? | DXVK Vulkan primary; WineD3D restricted to non-Vulkan iGPUs | Milestone P9 Exit |
| **OQ-030** | P1 | Graphics | Hybrid GPU switching: Dynamic PRIME offloading vs static multiplexing? | Dynamic offloading via `DRI_PRIME` / `NV_PRIME_RENDER_OFFLOAD` | Milestone P9 Exit |
| **OQ-031** | P1 | Graphics | Global vs per-app shader cache architecture? | Global pipeline cache with deduplicated content addressing | Milestone P9 Exit |
| **OQ-032** | P0 | Graphics | Proprietary NVIDIA driver packaging in atomic OSTree? | Pre-built OCI container driver layers signed per kernel ABI | Milestone P1 Exit |
| **OQ-033** | P2 | Graphics | VKD3D-Proton D3D12 memory allocation strategy? | Sub-allocated Vulkan memory pools with automatic defrag | Milestone P9 Exit |
| **OQ-034** | P1 | Graphics | Presentation timing: `VK_KHR_present_id` vs Wayland presentation-time? | Wayland `wp_presentation` fed directly by Vulkan present | Milestone P9 Exit |
| **OQ-035** | P1 | Power Management | Modern Standby S0ix vs S3 Sleep Fallback Configuration? | Probe `/sys/power/mem_sleep`; quirk DB + fallback to `suspend-then-hibernate` if S3 absent | Milestone P2 Exit |
| **OQ-036** | P1 | Compositor & Display | Multi-Monitor Mixed-DPI Scaling Protocol in Wayland? | `wp_fractional_scale_v1` for Wayland/Wine, Viewporter downscaling for legacy X11 | Milestone P1 Exit |
| **OQ-037** | P2 | Firmware & Platform | Automated Firmware Updates via LVFS / fwupd safety workflow? | Safety-gated GUI staged updates requiring AC power + battery > 50% + explicit user consent | Milestone P6 Exit |
| **OQ-038** | P1 | Infrastructure & Updates | Primary OCI Container Registry Provider & CDN Infrastructure Strategy? | Quay.io primary with Cloudflare R2 / CDN cache distribution | Milestone P8 Exit |
| **OQ-039** | P1 | Security & Updates | Hardware Security Module (HSM) vs Cloud KMS for Image Signing? | Cloud KMS with YubiKey / HSM backup offline root key | Milestone P8 Exit |
| **OQ-040** | P2 | Updates & Privacy | Privacy-Preserving Opt-In Rollout Health Telemetry Architecture? | Anonymous local bucket hashing (0-99); opt-in crash count reports | Milestone P8 Exit |
| **OQ-041** | P1 | Security & Updates | Critical Zero-Day Security Update Escalation Cadence & User Deferral Limits? | 2-hour polling acceleration; maximum 72-hour deferral banner | Milestone P8 Exit |
| **OQ-042** | P1 | Storage & Updates | Rollback Deployment Retention vs Disk Space Pruning Floor on Budget Devices? | Retain 1 rollback deployment minimum; abort staging if free space < 2.5 GB | Milestone P2 Exit |
| **OQ-043** | P1 | App Platform | Flathub Metadata Sync Strategy: Full Local AppStream Cache vs On-Demand API? | Hybrid: Pre-indexed SQLite trigram FTS5 cache with on-demand API query for screenshots | Milestone P6 Exit |
| **OQ-044** | P1 | App Platform | Future Nebu Repository Hosting Infrastructure and Storage Architecture? | OCI container registry storage using standard Flatpak OCI remote backend | Milestone P6 Exit |
| **OQ-045** | P2 | Security & Store | Publisher Verification Levels and Identity Validation Workflow? | Three-tier model (Official Upstream WebPKI, Community Vetted GPG, Unverified Amber notice) | Milestone P6 Exit |
| **OQ-046** | P2 | Store & Ecosystem | Commercial Software & Donation Support Model in Nebu Marketplace? | Free / FOSS baseline; external verified payment links; no proprietary in-app billing in P6 | Milestone P8 Exit |
| **OQ-047** | P1 | Security & Store | Emergency Remote Package Revocation and Automated Quarantine Protocol? | Signed metadata revocation feed (`revocations.json`) triggering immediate launcher unmap | Milestone P6 Exit |
| **OQ-048** | P2 | Enterprise | Multi-Source Enterprise and Private Application Repository Configuration? | Declarative `ApplicationSource` config files in `/etc/nebu/sources.d/` | Milestone P8 Exit |
| **OQ-049** | P2 | Boot & Shell | Plymouth Boot Splash vs Native Rust Splash Daemon in Milestone P2? | Plymouth baseline for initial P2; native Rust daemon optimization in P8 | Milestone P2 Start |
| **OQ-050** | P2 | Graphics & Boot | Dynamic BGRT Geometry Normalization across Non-Standard Displays? | Aspect ratio validation with center-snapped letterboxing | Milestone P1 Exit |
| **OQ-051** | P1 | Boot & Systems | Silent Boot Diagnostic Mode Persistent Logging Retention? | Dedicated diagnostic snapshot dumped to `/var/log/nebu-diag-boot-<timestamp>.log` | Milestone P0 Exit |
| **OQ-052** | P1 | Compatibility | Upstream Wine Candidate Quarantine Duration Before Stable Promotion? | 14-day zero-regression quarantine in Compatibility Lab | Milestone P4 Exit |
| **OQ-053** | P1 | Compatibility | Downstream Delta Eviction Thresholds & Upstream Escalation Policy past 180 days? | Mandatory architectural audit; convert to prefix workaround or drop | Milestone P4 Exit |
| **OQ-054** | P1 | Testing & Lab | Compatibility Lab Bare-Metal Farm Scaling Model for Milestone P7? | Hybrid: On-premise 4-node reference rack + virtualized cloud CI | Milestone P7 Start |
| **OQ-055** | P1 | Kernel & Runtime | NTSYNC Kernel Integration: In-Tree Fedora Module vs Out-of-Tree DKMS? | In-tree preferred (kernel 7.x upstream adoption); futex_waitv fallback | Milestone P5 Exit |

---

## 2. Detailed Question Specifications by Domain

### 2.1 System Architecture & Base OS

#### OQ-004: SELinux Enforcing vs Permissive Initial Policy
- **Priority:** P0 | **Domain:** System | **Deadline:** Milestone P1 Exit
- **Question:** Should NebuOS launch initial developer milestones in SELinux `Enforcing` or `Permissive` mode?
- **Context:** Fedora Atomic enforces strict SELinux policies by default. However, custom Rust daemons, Bubblewrap prefix namespaces, and Wine memory mapping (W^X violations, anonymous shared memory) will generate policy denials that can stall early bring-up.
- **Options:**
  1. *Enforcing with custom targeted policy:* Write dedicated `.te` policies for `nebu-runtime-daemon` and `nebu-compositor` from Day 1. High engineering overhead, potential early blocking.
  2. *Permissive with audit logging during P0–P4:* Log all `avc: denied` events, auto-generate production policies using `audit2allow`, and switch to strict `Enforcing` at Milestone P5.
- **Recommendation:** Option 2. Enables rapid milestone progression while ensuring production builds reach strict containment before end-user exposure.

#### OQ-005: Flatpak vs Native Packaging for NebuOS Core Components
- **Priority:** P1 | **Domain:** System | **Deadline:** Milestone P2 Exit
- **Question:** Should native NebuOS desktop utilities (file manager, settings, terminal) be packaged as Flatpaks or baked into the OSTree base image?
- **Context:** NebuOS emphasizes low memory consumption (<800MB idle). Flatpaks introduce runtime overhead (portal latency, duplicate runtime layers, separate cgroups).
- **Options:**
  1. *Flatpak for all userland apps:* High isolation, uniform sandboxing, independent update cycles, but adds 30–50MB memory overhead per runtime and slower cold starts.
  2. *Bake core utilities into the OSTree base, Flatpak for 3rd-party apps:* Zero runtime duplication, instant startup, sub-millisecond D-Bus bindings for core OS tools.
- **Recommendation:** Option 2. Core OS components live inside the atomic base image; 3rd-party Linux desktop applications use Flatpak via Flathub.

#### OQ-006: Default Root Filesystem Strategy (Btrfs vs Ext4 Fallback)
- **Priority:** P0 | **Domain:** System | **Deadline:** Milestone P1 Exit
- **Question:** Should the installation image mandate Btrfs partitions or support Ext4 fallback for older hardware?
- **Context:** Btrfs `reflink` cloning is essential for instantaneous Wine prefix creation and zero-cost template duplication. However, Btrfs Copy-on-Write causes severe SQLite and Wine registry fragmentation without `nodatacow`.
- **Options:**
  1. *Btrfs Mandatory:* Enforce subvolume hierarchy (`@`, `@home`, `@nebu_apps`). Apply `chattr +C` (`nodatacow`) automatically to prefix directories.
  2. *Dual Support (Btrfs + Ext4):* Allow Ext4 on legacy disks. Prefix creation on Ext4 falls back to full physical file copy (`cp -r`), which takes 15–30s on spinning HDDs.
- **Recommendation:** Option 1. Mandate Btrfs with automated subvolume mounting and `nodatacow` attribute flags for prefix storage.

#### OQ-007: Session Bus Daemon Selection (`dbus-broker` vs `dbus-daemon`)
- **Priority:** P1 | **Domain:** System | **Deadline:** Milestone P1 Exit
- **Question:** Should NebuOS standardize on `dbus-broker` or classic reference `dbus-daemon`?
- **Context:** D-Bus is the primary control channel between `nebu-shell`, `nebu-runtime-daemon`, and system services. Method call latency must meet $\le 1.0\text{ ms}$.
- **Options:**
  1. *dbus-broker:* Written in C, optimized for Linux epoll, in-kernel accounting, zero-copy socket transfers, fully integrated into systemd user sessions.
  2. *dbus-daemon:* Classic implementation, highly portable, but higher context switching overhead and higher memory footprint.
- **Recommendation:** Option 1 (`dbus-broker`). Demonstrates lower IPC jitter and strict resource accounting.

#### OQ-008: Low-Memory Killer Strategy (`systemd-oomd` vs `earlyoom`)
- **Priority:** P0 | **Domain:** System | **Deadline:** Milestone P3 Exit
- **Question:** How should NebuOS prevent total UI freezes when RAM exceeds 95% on 4GB systems?
- **Context:** Running heavy Windows applications (e.g. AutoCAD or multi-tab browser) on a 4GB baseline risks kernel thrashing and unrecoverable compositor freezing.
- **Options:**
  1. *systemd-oomd:* Integrated with cgroups v2 Pressure Stall Information (PSI). Kills entire cgroup scopes cleanly based on memory pressure duration.
  2. *earlyoom:* Simple userspace daemon checking `/proc/meminfo`. Fast reaction, but lacks fine-grained cgroup context and can kill parent processes unexpectedly.
- **Recommendation:** Option 1 (`systemd-oomd`). Configure per-cgroup memory pressure limits (`ManagedOOMMemoryPressure=kill`) on `nebu-app-*.scope` while protecting `nebu-compositor.service`.

#### OQ-009: Target Kernel Cadence (Long-Term Support vs Fedora Stable)
- **Priority:** P1 | **Domain:** System | **Deadline:** Milestone P2 Exit
- **Question:** Should NebuOS lock to a specific Linux LTS kernel (e.g., 6.6 LTS) or track Fedora upstream kernel updates?
- **Context:** Wine and DXVK heavily depend on cutting-edge kernel features (futex2/sys_futex_waitv, explicit sync, modern Mesa GPU drivers). LTS kernels lack new GPU support.
- **Options:**
  1. *LTS Baseline (Kernel 6.6):* High stability, minimal driver churn, but delays Vulkan explicit sync (`linux-drm-syncobj-v1`) and new AMD/Intel GPU bring-up.
  2. *Fedora Upstream Stable:* Rapid access to upstream graphics and scheduling enhancements, backed by automated hardware test gates in the Compatibility Lab.
- **Recommendation:** Option 2. Maintain Fedora upstream stable kernel cadence validated by automated Compatibility Lab regression gates.

---

### 2.2 Compositor & Display

#### OQ-010: Compositor Foundation (Smithay vs wlroots)
- **Priority:** P0 | **Domain:** Compositor | **Deadline:** Milestone P0 Exit
- **Question:** Should `NebuCompositor` be implemented using pure Rust via the `smithay` framework, or using C-bindings to `wlroots`?
- **Context:** NebuOS mandates memory safety for core desktop daemons, a strict sub-100MB idle RAM ceiling, and deterministic rendering.
- **Options:**
  1. *Smithay:* Pure Rust, memory-safe, native async handling, zero C FFI overhead, active modern Wayland implementation.
  2. *wlroots (C / Rust FFI):* Battle-tested in Sway/Hyprland, but introduces unsafe C boundaries, lifetime mismatches in Rust, and frequent breaking API changes.
- **Recommendation:** Option 1 (Smithay). Aligns strictly with project memory safety and Rust architecture guidelines.

#### OQ-011: Fractional Scaling Strategy
- **Priority:** P1 | **Domain:** Compositor | **Deadline:** Milestone P2 Exit
- **Question:** How should NebuCompositor handle fractional scaling (125%, 150%) for legacy Xwayland/Wine applications?
- **Context:** Wayland native apps support `wp-fractional-scale-v1`. However, Windows GDI and non-DPI-aware Win32 apps render at 96 DPI and look blurry when upscaled.
- **Options:**
  1. *Integer Scaling + Viewport Downsampling:* Render client surface at $2\times$ integer scale, downsample via GPU bilinear filter to $1.5\times$. Sharp text, higher GPU fill-rate.
  2. *Wayland Fractional Scale Protocol with Wine GDI DPI Awareness:* Inject Wine registry flags (`LogPixels=120` for 125%) directly into the application prefix to render natively at target DPI.
- **Recommendation:** Option 2 as primary; fallback to Option 1 for uncooperative legacy Win32 binaries.

#### OQ-012: Direct Scanout Pipeline
- **Priority:** P1 | **Domain:** Compositor | **Deadline:** Milestone P2 Exit
- **Question:** Should fullscreen Wine/Proton games completely bypass compositor composition via KMS direct scanout?
- **Context:** Compositing introduces a 1-frame latency penalty and GPU memory bandwidth consumption. Direct scanout feeds the client DMA-BUF directly to the KMS plane.
- **Options:**
  1. *Strict Direct Scanout:* Promote fullscreen matching buffers directly to the primary hardware plane, disabling shell overlays. Zero-copy, lowest possible input lag.
  2. *Always-Composited:* Route all buffers through OpenGL/Vulkan compositor render pass. Preserves system notifications, but adds 8–16ms latency.
- **Recommendation:** Option 1. Enable direct scanout whenever a client surface matches output geometry, dropping to composited mode only when notifications or system UI are drawn.

#### OQ-013: Compositor Crash Recovery & Process Survivability
- **Priority:** P0 | **Domain:** Compositor | **Deadline:** Milestone P3 Exit
- **Question:** How should the system handle an unexpected panic or fatal GPU reset in `nebu-compositor`?
- **Context:** Under traditional Wayland compositors, a crash tears down all running clients, causing total user data loss in open Office or CAD documents.
- **Options:**
  1. *Standard Respawn:* Systemd restarts `nebu-compositor`, but all client socket connections are broken; applications terminate.
  2. *Stateful Reconnect Architecture:* Decouple the Wayland display socket into a lightweight proxy (`nebu-wayland-proxy`) that preserves client buffer state across compositor restarts.
- **Recommendation:** Option 1 for initial milestones (P0–P4); transition to a resilient architecture in P12.

#### OQ-014: Variable Refresh Rate (VRR / Adaptive Sync) Multi-Monitor Arbitration
- **Priority:** P2 | **Domain:** Compositor | **Deadline:** Milestone P9 Exit
- **Question:** How should VRR (G-Sync/FreeSync) be scheduled when multiple monitors have mismatched refresh capabilities?
- **Context:** A 144Hz VRR primary display paired with a 60Hz fixed secondary display can cause frame stutter or tearing if global page flipping is synchronized incorrectly.
- **Options:**
  1. *Global VRR Lock:* Lock all monitors to the lowest common refresh rate. Poor gaming experience.
  2. *Per-Connector Asynchronous Flipping:* Enable KMS VRR properties only on the output containing the focused fullscreen surface, running secondary outputs with fixed vblank timers.
- **Recommendation:** Option 2.

---

### 2.3 Desktop Shell & User Interface

#### OQ-001: Slint vs Iced for Native NebuShell UI Toolkit
- **Priority:** P0 | **Domain:** Shell | **Deadline:** Milestone P1 Exit
- **Status:** **RESOLVED** via [ADR-0019](decisions/ADR-0019-slint-toolkit-adoption.md)
- **Question:** Which pure-Rust GUI toolkit should power `nebu-shell` (taskbar, launcher, quick settings)?
- **Context:** The shell must idle at $\le 45\text{MB}$ RAM, render at 60 FPS on low-end Intel Gen 8 iGPUs, and provide declarative component styling.
- **Decision:** **Slint (1.7+)** is formally adopted. Offers compile-time verified DSL, fine-grained reactive dirty tracking, native layer-shell handle extraction, AT-SPI2 accessibility integration, and comfortable compliance with the $\le 45\text{MB}$ idle RSS target.

#### OQ-015: Shell Component IPC Architecture
- **Priority:** P1 | **Domain:** Shell | **Deadline:** Milestone P3 Exit
- **Question:** Should shell modules (taskbar, system tray, quick settings) communicate via internal Rust mpsc channels or external D-Bus interfaces?
- **Context:** A monolithic shell process is simpler, but a modular architecture allows restarting an unstable widget without tearing down the taskbar.
- **Options:**
  1. *Single Monolithic Process:* All UI components compile into one `nebu-shell` binary sharing an internal Tokio/async event loop. Lowest RAM usage (<50MB).
  2. *Multi-Process Micro-Shell:* Taskbar, app drawer, and system tray run as separate binaries communicating over D-Bus. Higher crash resilience, but consumes ~20MB RAM per process.
- **Recommendation:** Option 1 for memory conservation, using internal actor isolation with panic catchers.

#### OQ-016: Shell Low-End Mode Asset Handling
- **Priority:** P2 | **Domain:** Shell | **Deadline:** Milestone P3 Exit
- **Question:** How should shell iconography and system graphics be packaged to optimize startup and memory on 4GB devices?
- **Context:** Parsing hundreds of vector SVG icons at startup consumes 150–250ms of CPU time and 20MB of heap space.
- **Options:**
  1. *Dynamic SVG Parsing:* Render SVGs at runtime via `resvg`. High visual flexibility for arbitrary HiDPI scaling, but CPU and memory intensive.
  2. *Pre-Compiled Texture Atlas Cache:* Bake standard desktop icons into mip-mapped binary texture atlases at build time, loading via zero-copy mmap.
- **Recommendation:** Option 2. Use pre-rendered texture atlases for core UI icons with runtime fallback for third-party application icons.

#### OQ-017: Notification Server Daemon Architecture
- **Priority:** P2 | **Domain:** Shell | **Deadline:** Milestone P4 Exit
- **Question:** Should the Freedesktop notification service (`org.freedesktop.Notifications`) run as an internal thread of `nebu-shell` or as an external daemon?
- **Context:** Standalone daemons (like Dunst or Mako) add IPC hops; an integrated notification center enables fluid drawer animations.
- **Options:**
  1. *Integrated Module:* NebuShell directly exports the D-Bus interface and renders notification toasts natively within its layer-shell overlay.
  2. *External Daemon:* Standalone `nebu-notifyd` communicating with the shell via D-Bus signals.
- **Recommendation:** Option 1. Minimizes process overhead and simplifies window layering.

#### OQ-018: Taskbar Window Preview Generation
- **Priority:** P1 | **Domain:** Shell | **Deadline:** Milestone P3 Exit
- **Question:** How should hovering over a taskbar icon obtain live window thumbnail previews?
- **Context:** Capturing window contents under Wayland requires strict security permissions to prevent unauthorized screen snooping.
- **Options:**
  1. *Wayland Screencopy Protocol (`wlr-screencopy-unstable-v1`):* Shell requests frame copies over Wayland socket. High CPU/GPU copy overhead.
  2. *Compositor Internal Export:* Compositor exports scaled-down DMA-BUF handles directly to `nebu-shell` via a privileged private Wayland extension (`nebu-foreign-toplevel-preview`).
- **Recommendation:** Option 2. Zero-copy hardware-scaled preview buffers.

---

### 2.4 Runtime Engine & Sandboxing

#### OQ-019: Sandboxing Mechanism for Windows Executables (Bubblewrap vs Landlock)
- **Priority:** P0 | **Domain:** Runtime | **Deadline:** Milestone P5 Exit
- **Question:** What isolation primitive should `nebu-runtime-daemon` use to sandbox Windows PE processes?
- **Context:** Untrusted Windows binaries must not access arbitrary user files or host system directories.
- **Options:**
  1. *Bubblewrap (`bwrap`):* Unprivileged user namespaces, robust mount isolation, battle-tested in Flatpak. Adds ~5ms launch overhead.
  2. *Landlock LSM + seccomp:* In-kernel unprivileged access control, zero mount overhead, but limited path redirection and requires newer kernels.
- **Recommendation:** Bubblewrap for P1–P5; layer Landlock LSM inside the container for internal process containment starting at P6.

#### OQ-020: Prefix Storage Deduplication (Btrfs Reflink vs Base Overlay)
- **Priority:** P0 | **Domain:** Runtime | **Deadline:** Milestone P5 Exit
- **Question:** How should per-application Wine prefixes be provisioned without consuming gigabytes of duplicate disk space?
- **Context:** A standard 64-bit Wine prefix occupies 500MB–1.2GB. Installing 10 applications would consume over 10GB of storage for duplicate system files.
- **Options:**
  1. *Btrfs Reflink Copy:* Clone a pristine template prefix via `cp --reflink=always`. Instantaneous (<50ms), shares physical extents on disk, modifies only changed blocks.
  2. *OverlayFS Mount:* Mount a read-only golden `drive_c` base with a per-app writable upper layer. Complicated Wine registry file locking and cross-device rename issues.
- **Recommendation:** Option 1 (Btrfs `reflink`). Provides standard POSIX filesystem semantics without OverlayFS edge-case bugs.

#### OQ-021: Application Process Lifecycle Supervision
- **Priority:** P1 | **Domain:** Runtime | **Deadline:** Milestone P5 Exit
- **Question:** How should NebuOS track child processes spawned by complex Windows installers and applications?
- **Context:** Windows installers routinely spawn helper executables and detach from the parent process, evading traditional PID tracking.
- **Options:**
  1. *Systemd Transient Scopes (`systemd-run --user --scope`):* Every application launch creates a dedicated cgroup v2 scope (`nebu-app-<id>.scope`). Guaranteed containment and clean termination.
  2. *Internal Rust Process Group Monitor:* Track PIDs via `/proc` polling or netlink process connectors. Vulnerable to race conditions and PID recycling.
- **Recommendation:** Option 1 (systemd transient scopes). Guaranteed clean termination of the entire Windows process tree.

#### OQ-022: Pre-Warmed Runtime Resident Memory Budget
- **Priority:** P1 | **Domain:** Runtime | **Deadline:** Milestone P5 Exit
- **Question:** How much RAM should the pre-warmed Wine daemon cache occupy on 4GB systems?
- **Context:** Keeping a pre-initialized Wine process warm reduces launch latency from 2.5s to 400ms, but consumes background memory.
- **Options:**
  1. *Fixed 128MB Pool:* Holds pre-initialized `wineserver` and core DLL mappings permanently in memory.
  2. *Adaptive 64MB Pool with Low-End Auto-Eviction:* Pre-load only core libraries; immediately terminate the warm pool if system available memory drops below 800MB.
- **Recommendation:** Option 2. Prioritizes base system stability under heavy memory pressure.

#### OQ-023: Virtual Drive (`Z:\`) Host Filesystem Access Security
- **Priority:** P0 | **Domain:** Runtime | **Deadline:** Milestone P6 Exit
- **Question:** Should the Windows virtual drive `Z:\` map to the host root (`/`) or be restricted?
- **Context:** Default Wine maps `Z:\` to `/`, allowing any Windows binary to read user files, SSH keys, and system configs.
- **Options:**
  1. *Full Host Mapping (`Z:\` -> `/`):* Maximum compatibility for broken installers, but catastrophic security risk.
  2. *Restricted Sandbox Mapping:* Map `Z:\` only to application-specific portal directories and user Documents/Downloads via Bubblewrap bind mounts. Completely hide `/etc`, `/var`, and `~/.ssh`.
- **Recommendation:** Option 2. Restrict host path exposure by default.

---

### 2.5 Compatibility & Wine/Proton Engine

#### OQ-002: Exact Wine Upstream Version Pinning Strategy
- **Priority:** P0 | **Domain:** Compatibility | **Status:** **RESOLVED** by [ADR-0016](decisions/ADR-0016-nebuwine-architecture.md) and [ADR-0017](decisions/ADR-0017-decoupled-runtime-packaging-and-storage.md)
- **Question:** Which upstream Wine release cadence should NebuOS integrate and certify?
- **Resolution:** Formally resolved via the Upstream-First Downstream Distribution Model ($\text{NebuWine} = \text{Upstream Wine} + \text{Minimal Maintained Delta}$) with decoupled packaging on `/var/lib/nebu/runtimes/`. NebuWine manages four channels (`Stable`, `Candidate`, `Gaming`, `Legacy`) tracking official WineHQ releases (Wine 11 through Wine 16+) with an automated 17-stage synchronization pipeline and Compatibility Lab regression gates.

#### OQ-003: Proton vs Wine Staging for Non-Steam Applications
- **Priority:** P0 | **Domain:** Compatibility | **Status:** **RESOLVED** by [ADR-0018](decisions/ADR-0018-gaming-runtime-architecture.md)
- **Question:** Should Proton be used for general productivity software or kept exclusively for gaming?
- **Resolution:** Formally resolved in ADR-0018: NebuWine Gaming is defined as an extension profile ($\text{NebuWine Gaming} = \text{NebuWine Core} + \text{Gaming Runtime Components}$). Core NebuWine powers CAD and enterprise productivity without gaming hacks, while the Gaming profile dynamically provisions DXVK, VKD3D-Proton, NTSYNC/fsync, and low-latency audio for interactive 3D and gaming workloads.

#### OQ-024: Microsoft .NET Framework Runtime Bridge
- **Priority:** P1 | **Domain:** Compatibility | **Deadline:** Milestone P6 Exit
- **Question:** How should NebuOS satisfy deep dependencies on .NET Framework 3.5/4.8 in AutoCAD and 3ds Max?
- **Context:** Open-source Wine-Mono does not fully implement WPF or WCF remoting required by proprietary licensing and UI engines.
- **Options:**
  1. *Wine-Mono Only:* Zero proprietary Microsoft redistribution, but breaks CAD installers.
  2. *Automated Profile-Driven Native .NET Injection:* Default to Wine-Mono; for certified CAD profiles, automate downloading and installing official Microsoft redistributables inside the isolated prefix.
- **Recommendation:** Option 2. Achieves 100% CAD compatibility without violating redistribution terms.

#### OQ-025: Anti-Cheat and Kernel-Level DRM Handling
- **Priority:** P0 | **Domain:** Compatibility | **Deadline:** Milestone P6 Exit
- **Question:** How should the system respond when an application attempts to load a Windows ring-0 kernel driver (`.sys`)?
- **Context:** Kernel-level anti-cheat (EasyAntiCheat, BattlEye, Vanguard) and CAD hardware dongles cannot run under Wine without a virtual machine. NebuOS strictly prohibits VMs.
- **Options:**
  1. *Silent Failure:* Allow the PE loader to fail silently, resulting in an unexplained crash.
  2. *PE Header Inspection & Explicit Notification:* Inspect PE imports at launch. If kernel drivers or known anti-cheat drivers are detected, abort launch and show an informative UI modal explaining the architectural limitation.
- **Recommendation:** Option 2. Delivers transparent user communication without false compatibility promises.

#### OQ-026: Local Compatibility Database Distribution & Update
- **Priority:** P1 | **Domain:** Compatibility | **Deadline:** Milestone P7 Exit
- **Question:** How should application profile updates be delivered to offline or air-gapped systems?
- **Context:** The SQLite compatibility database requires frequent recipe updates as new applications and patches emerge.
- **Options:**
  1. *Full OS Image Updates:* Update the database only via OSTree image rollouts. Slow cadence.
  2. *Decoupled Signed Delta Sync:* Deliver signed SQLite incremental changes via HTTPS and local import, independent of OS image builds.
- **Recommendation:** Option 2. Allows rapid compatibility hotfixes without rebooting the OS.

#### OQ-027: Proprietary Licensing Daemons Handling
- **Priority:** P1 | **Domain:** Compatibility | **Deadline:** Milestone P10 Exit
- **Question:** How should NebuOS handle background licensing daemons (e.g., Autodesk Access, Adobe Genuine Service)?
- **Context:** These services frequently fail under Wine due to missing Windows service manager RPCs and WMI queries.
- **Options:**
  1. *Require User Patches:* Leave licensing configuration to manual community workarounds.
  2. *Automated Service Emulation Layer:* Provide stub Wine service wrappers and mock local loopback endpoints in certified application profiles.
- **Recommendation:** Option 2. Automates professional application onboarding.

#### OQ-028: Multi-Instance `wineserver` vs Shared System `wineserver`
- **Priority:** P0 | **Domain:** Compatibility | **Deadline:** Milestone P5 Exit
- **Question:** Should all running Windows applications connect to a single shared `wineserver` or maintain isolated instances?
- **Context:** A shared `wineserver` saves ~15MB RAM per app, but if one application crashes or hangs `wineserver`, all open Windows applications terminate.
- **Options:**
  1. *Shared Wineserver:* Lower memory footprint, but zero fault isolation.
  2. *Isolated Wineserver per Prefix:* Total fault isolation. A crash in Photoshop cannot crash Excel. Slight memory overhead (~15MB per prefix).
- **Recommendation:** Option 2 (Strict isolation per prefix). Essential for production reliability.

---

### 2.6 Graphics & Driver Pipeline

#### OQ-029: Direct3D 9–11 Translation Strategy for Legacy GPUs
- **Priority:** P0 | **Domain:** Graphics | **Deadline:** Milestone P9 Exit
- **Question:** How should NebuOS handle legacy GPUs (Intel Gen 7/8, Ivy Bridge) lacking complete Vulkan 1.2 support?
- **Context:** DXVK requires Vulkan 1.2+. Running DXVK on legacy Intel iGPUs produces initialization crashes.
- **Options:**
  1. *Drop Legacy GPUs:* Mandate Vulkan 1.2 hardware support. Excludes older 4GB hardware targets.
  2. *Adaptive Translation Backend:* Detect Vulkan capabilities via `vulkaninfo`. Use DXVK on modern GPUs; automatically fall back to WineD3D (OpenGL) on legacy GPUs.
- **Recommendation:** Option 2. Preserves functionality across low-end target hardware.

#### OQ-030: Hybrid GPU Switching Mechanism
- **Priority:** P1 | **Domain:** Graphics | **Deadline:** Milestone P9 Exit
- **Question:** How should the graphics subsystem manage laptops with dual Intel/AMD integrated and NVIDIA discrete GPUs?
- **Context:** Windows applications expect to select high-performance adapters dynamically.
- **Options:**
  1. *Manual User Toggle:* Require the user to set a "Run on Discrete GPU" toggle in the app properties.
  2. *Automatic Profile-Driven Offloading:* NebuCompatDB marks 3D CAD and gaming profiles with `gpu_performance_mode=discrete`, automatically injecting `DRI_PRIME=1` or `NV_PRIME_RENDER_OFFLOAD=1`.
- **Recommendation:** Option 2 with user override in the GUI context menu.

#### OQ-031: Global vs Per-App Shader Cache Architecture
- **Priority:** P1 | **Domain:** Graphics | **Deadline:** Milestone P9 Exit
- **Question:** Should compiled DXVK/Mesa shader caches be stored globally or isolated within each prefix?
- **Context:** Direct3D shader compilation causes in-game micro-stutter. Sharing compiled shaders between games using identical engines avoids duplicate compilation.
- **Options:**
  1. *Per-Prefix Cache:* Strict isolation, but wastes disk space and requires duplicate compile passes.
  2. *Global Content-Addressed Shader Cache:* Store compiled pipelines in `~/.cache/nebu/shaders/` indexed by shader hash and driver build UUID.
- **Recommendation:** Option 2. Significantly reduces launch-time shader stutter.

#### OQ-032: Proprietary NVIDIA Driver Packaging in Atomic OSTree
- **Priority:** P0 | **Domain:** Graphics | **Deadline:** Milestone P1 Exit
- **Question:** How should proprietary NVIDIA kernel modules (`nvidia.ko`) be delivered within an immutable bootc operating system?
- **Context:** Standard Fedora uses Akmods to compile NVIDIA drivers locally, but compilation requires gcc, kernel headers, and takes minutes on slow CPUs.
- **Options:**
  1. *Local Akmods Compilation:* High flexibility, but breaks immutable image guarantees and prolongs updates.
  2. *Pre-Compiled Driver Container Layers:* Build and sign NVIDIA kernel modules in the NebuOS cloud CI pipeline for each kernel ABI; distribute as layered bootc container images.
- **Recommendation:** Option 2. Provides deterministic, zero-compilation atomic updates for NVIDIA users.

#### OQ-033: VKD3D-Proton Direct3D 12 Memory Allocation Strategy
- **Priority:** P2 | **Domain:** Graphics | **Deadline:** Milestone P9 Exit
- **Question:** How should VKD3D-Proton manage Vulkan device memory under severe VRAM constraints on integrated GPUs?
- **Context:** Integrated GPUs share system RAM. Aggressive Direct3D 12 heap allocation triggers out-of-memory errors on 4GB systems.
- **Options:**
  1. *Default Unbounded Allocation:* Allow VKD3D to request memory without limits. Risks instant OOM killer invocation.
  2. *Constrained Heap Sub-Allocation:* Configure VKD3D environment flags (`VKD3D_CONFIG=no_upload_hvv`) to throttle heap expansion and return out-of-memory gracefully.
- **Recommendation:** Option 2 for Low-End Mode hardware profiles.

#### OQ-034: Presentation Timing Synchronization
- **Priority:** P1 | **Domain:** Graphics | **Deadline:** Milestone P9 Exit
- **Question:** What synchronization protocol should bind Vulkan presentation surfaces to NebuCompositor's frame schedule?
- **Context:** Tearing, jitter, and frame pacing issues occur when DXVK presents frames out of phase with Wayland display refresh cycles.
- **Options:**
  1. *Standard Wayland Surface Commit:* Rely on standard buffer callbacks. Prone to double-buffering queue stalls.
  2. *Wayland Presentation Time Protocol (`wp_presentation`):* Feed precise vblank hardware timestamps from KMS back into DXVK's frame timing engine.
- **Recommendation:** Option 2. Delivers buttery smooth frame pacing and minimal latency.

#### OQ-035: Modern Standby S0ix vs S3 Sleep Fallback Configuration
- **Priority:** P1 | **Domain:** Power Management | **Deadline:** Milestone P2 Exit
- **Question:** Under what criteria and mechanisms should NebuOS handle high battery drain during Modern Standby (`s2idle`), given that modern platforms increasingly omit ACPI S3 (`deep`)?
- **Context:** Broken OEM ACPI tables and driver power-state gating frequently cause excessive S0ix sleep drain (>1200 mW, or >2.0%/hr on a 50Wh battery). However, modern platforms (Intel Tiger Lake/Alder Lake/Meteor Lake, AMD Phoenix/Hawk Point) often completely remove S3 support from firmware (`/sys/power/mem_sleep` only exposes `[s2idle]`), rendering simple S3 fallback physically impossible.
- **Options:**
  1. *Blind S3 Forcing via Kernel Arg:* Set `mem_sleep_default=deep`. Fails silently or hangs platforms without ACPI S3.
  2. *Capability-Aware Quirk Table with PMC Diagnostics:* Check `/sys/power/mem_sleep`. If `deep` is supported and DMI matches a quirk in `compat.db`, set `deep`. If only `s2idle` is supported, run kernel PMC diagnostics (`/sys/kernel/debug/pmc_core` or `amd_pmc`) to identify blocking subsystems.
  3. *Safety Fallback to `suspend-then-hibernate`:* If S0ix drain is elevated and S3 is absent, configure systemd `suspend-then-hibernate` with a configurable battery or time threshold (e.g., hibernate after 120 minutes of sleep or when battery drops 5%) to prevent dead batteries in backpacks.
- **Recommendation:** Combination of Option 2 (capability probing + DMI quirk) and Option 3 (`suspend-then-hibernate` safety guardrail when S3 is unavailable).

#### OQ-036: Multi-Monitor Mixed-DPI Scaling Protocol in Wayland
- **Priority:** P1 | **Domain:** Compositor & Display | **Deadline:** Milestone P1 Exit
- **Question:** How should `nebu-compositor` handle legacy Win32/X11 applications dragged across monitors with differing fractional scale factors (e.g. 100% and 150%)?
- **Context:** While native Wayland applications and the upstream Wine 9+ Wayland driver natively support fractional scaling via `wp_fractional_scale_v1` and `wp_viewporter`, legacy Win32 applications running through Xwayland lack dynamic per-monitor DPI awareness, leading to blurriness or incorrect hit-testing when scaled via standard bilinear texture sampling.
- **Options:**
  1. *Highest-DPI Rendering with Viewporter Downsampling:* Render Xwayland surfaces at the highest monitor scale factor and use `wp_viewporter` to downscale onto lower-DPI outputs. Sharp text but higher GPU memory and fill-rate overhead.
  2. *Integer-Only Xwayland Scaling with Client-Side DPI:* Keep Xwayland scaling at 1x or 2x integer factors and inject Windows DPI awareness flags into the application's PE manifest or prefix registry.
  3. *Hybrid Protocol Routing:* Direct Wayland-capable applications to `wp_fractional_scale_v1` with viewporter; for legacy X11/Win32 GDI applications, apply nearest-integer scale and downsample with a sharpening shader.
- **Recommendation:** Option 3. Provides crisp native rendering for modern applications while ensuring stable, legible fallback for legacy Win32 binaries.

#### OQ-037: Automated Firmware Updates via LVFS / fwupd Safety Architecture
- **Priority:** P2 | **Domain:** Firmware & Platform | **Deadline:** Milestone P6 Exit
- **Question:** What safety preconditions and user interaction model should govern UEFI, EC, and peripheral firmware updates via `fwupd`?
- **Context:** Firmware updates resolve critical platform bugs (e.g. S0ix state gating, USB-C PD negotiation, touchpad jitter), but interrupted or unverified flashing risks permanent hardware bricking.
- **Options:**
  1. *Silent Background Flashing:* Automatically stage and apply updates during standard system reboot. Rejected due to catastrophic risk of user disconnecting power during flash.
  2. *Strict Safety-Gated User Workflow:* NebuShell notifies user of updates via LVFS metadata. Flashing is strictly blocked unless: AC adapter is connected, battery is $\ge 50\%$, and system battery health is verified. System stages capsule update via UEFI ESRT and explicitly warns user not to power off.
  3. *Terminal/CLI Only:* Restrict firmware updates to command-line `fwupdmgr` utility for advanced administrators only.
- **Recommendation:** Option 2. Maximizes firmware security and hardware reliability while preventing power-loss-induced bricking through strict hardware preconditions.

#### OQ-038: Primary OCI Container Registry Provider & CDN Distribution Strategy
- **Priority:** P1 | **Domain:** Infrastructure & Updates | **Deadline:** Milestone P8 Exit
- **Question:** Which cloud OCI container registry infrastructure and CDN caching architecture should serve production base OS images?
- **Context:** NebuOS base images are ~1.2 GB compressed. Distributing image updates to tens of thousands of consumer desktop machines requires high-bandwidth, globally distributed CDN edge caching to prevent network congestion and high cloud egress costs.
- **Options:**
  1. *Quay.io Public Organization:* Rely entirely on Red Hat Quay.io. Simple to configure, but bandwidth rate limits or downtime would impact updates.
  2. *Self-Hosted Distribution Registry with Cloudflare CDN:* Host an open-source OCI distribution registry backed by S3/B2 storage behind Cloudflare CDN edge caching.
  3. *Hybrid Multi-Registry Mirrors:* Primary registry on Quay.io with automated replication to GitHub Container Registry (GHCR) and an AWS/Cloudflare CDN mirror.
- **Recommendation:** Option 3. Guarantees global high availability and prevents single-vendor lock-in.

#### OQ-039: Hardware Security Module (HSM) vs Cloud KMS for Image Signing
- **Priority:** P1 | **Domain:** Security & Updates | **Deadline:** Milestone P8 Exit
- **Question:** How should the cryptographic Ed25519 private keys for Sigstore / Cosign image signing be secured and accessed during automated CI releases?
- **Context:** If the private signing key is compromised, an attacker could publish malicious OS updates to user devices.
- **Options:**
  1. *CI Environment Secrets:* Store key in GitHub Secrets. Highly vulnerable to workflow compromise.
  2. *Cloud Key Management Service (AWS KMS / GCP Cloud KMS / HashiCorp Vault):* Keys never leave the KMS; CI runner signs via authenticated IAM OIDC role.
  3. *Physical Air-Gapped HSM / Smartcards:* Keys stored on physical YubiKey HSMs; releases require manual dual-operator touch.
- **Recommendation:** Option 2 for automated Canary/Nightly builds; Option 3 for final GA Stable releases.

#### OQ-040: Privacy-Preserving Opt-In Rollout Health Telemetry Architecture
- **Priority:** P2 | **Domain:** Updates & Privacy | **Deadline:** Milestone P8 Exit
- **Question:** How can NebuOS measure canary update stability (boot success rate, kernel panics, compositor crashes) without violating user privacy?
- **Context:** Staged canary rollouts require health signals to trigger automated fast-abort, but NebuOS maintains a strict zero-surveillance architecture.
- **Options:**
  1. *Mandatory Minimal Telemetry:* System sends an anonymous heartbeat after successful boot. Rejected due to privacy violation.
  2. *Client-Side Anonymous Cohorts with Opt-In Crash Reports:* Cohorts are computed locally without server knowledge ($\text{SHA256}(\text{MachineID}) \pmod{100}$). Only users who explicitly toggle "Help Improve NebuOS" transmit crash reports.
  3. *Pure Forum / Bug Tracker Feedback:* Zero telemetry; rely on community issue reports during canary phase.
- **Recommendation:** Option 2. Strikes the ideal balance between privacy guarantees and release engineering safety.

#### OQ-041: Critical Zero-Day Security Update Escalation Cadence & User Deferral Limits
- **Priority:** P1 | **Domain:** Security & Updates | **Deadline:** Milestone P8 Exit
- **Question:** Under what criteria and deadlines should NebuOS escalate a critical security update, and should user reboot deferrals be bounded?
- **Context:** Unlike standard Linux distros where users defer rebooting indefinitely, critical vulnerabilities in browsers, libc, or kernel require swift activation. However, forced reboots alienate desktop users.
- **Options:**
  1. *Forced Auto-Reboot after 48h:* System gives 48-hour countdown, then forces reboot. Highly disruptive; rejected.
  2. *Persistent High-Priority Banner with Max 7-Day Soft Reminder:* NebuShell displays a prominent non-modal security notification explaining the risk, but never forcibly restarts without user consent.
  3. *Configurable Enterprise vs Consumer Policy:* Consumers retain full control; managed enterprise fleets can configure administrative reboot deadlines.
- **Recommendation:** Option 3. Respects personal device ownership while giving enterprise administrators necessary compliance controls.

#### OQ-042: Rollback Deployment Retention vs Disk Space Pruning Floor on Budget Devices
- **Priority:** P1 | **Domain:** Storage & Updates | **Deadline:** Milestone P2 Exit
- **Question:** How should `NebuUpdateService` arbitrate between maintaining rollback deployments and preventing disk full errors on 64GB eMMC laptops?
- **Context:** A full deployment with Flatpak apps and Wine prefixes can occupy 10–20 GB. On budget devices, storing two deployments can consume 40% of available disk space.
- **Options:**
  1. *Always Retain Rollback:* If disk is full, block update staging completely until user frees space.
  2. *Aggressive Auto-Prune:* Delete the rollback deployment immediately after a 24-hour soak period to recover disk space.
  3. *Dynamic Extent Sharing & Reflink Pruning:* Rely on Btrfs extent sharing so rollback only consumes delta (~800 MB); enforce hard blocking threshold at 2.5 GB free space.
- **Recommendation:** Option 3. Maximizes safety without prematurely discarding rollback protection.

#### OQ-043: Candidate Icon Set Selection for Prototype Phase (Lucide vs Material Symbols)
- **Priority:** P1 | **Domain:** UI/UX & Design | **Deadline:** Milestone P2 Start
- **Question:** Which open-source candidate icon library should be integrated into `assets/prototype/icons/` during early development?
- **Context:** Milestone P2 requires a functional icon set to render panels, launchers, and system dialogs without prematurely investing in full custom icon design.
- **Options:**
  1. *Lucide Icons (ISC License):* Crisp 1.5–2px stroke vector design, lightweight, highly consistent geometry, permissive license.
  2. *Google Material Symbols (Apache 2.0):* Enormous glyph coverage, variable optical weight axes, but visually heavier and generic.
- **Recommendation:** Option 1 (Lucide Icons). Provides superior aesthetic alignment with modern desktop environments and minimal vector footprint.

#### OQ-044: Dedicated Production Nebu Icon Set Commissioning Timeline
- **Priority:** P1 | **Domain:** UI/UX & Design | **Deadline:** Milestone P6 Exit
- **Question:** At what milestone should the dedicated, custom Nebu Icon Set be commissioned and integrated to replace the prototype library?
- **Context:** Designing hundreds of custom icons is labor-intensive and premature before all system and marketplace UI workflows stabilize.
- **Options:**
  1. *Commission Early in P2:* Design icons alongside initial Slint templates. Risk of redesign churn.
  2. *Commission in P7/P8 (Production Hardening):* Leverage the `NebuIcon` abstraction to swap in the dedicated icon set during pre-release polish with zero UI code refactoring.
- **Recommendation:** Option 2. Preserves engineering bandwidth during core system bringup.

#### OQ-045: User Custom Accent Color Palette Strategy: Arbitrary Color Picker vs Curated Accessible Palette
- **Priority:** P2 | **Domain:** UI/UX & Design | **Deadline:** Milestone P2 Exit
- **Question:** Should users be allowed to select arbitrary 24-bit hex accent colors in Settings, or should accents be constrained to a curated accessible palette?
- **Context:** Arbitrary color selection can produce extremely poor luminance contrast against surface tokens, breaking WCAG 2.1 AA compliance.
- **Options:**
  1. *Free Color Wheel Picker:* Maximum user freedom, but requires dynamic runtime contrast compensation (darkening/lightening).
  2. *Curated 12-Color High-Contrast Palette:* Restricts choices to 12 mathematically validated accent tokens (Blue, Teal, Green, Amber, Coral, Purple, etc.) guaranteeing >= 4.5:1 contrast across all modes.
- **Recommendation:** Option 2. Guarantees accessibility and visual polish by default.

#### OQ-046: Commercial Software & Donation Support Model in Nebu Marketplace
- **Priority:** P2 | **Domain:** Store & Ecosystem | **Deadline:** Milestone P8 Exit
- **Question:** How should Nebu Marketplace facilitate monetization, developer donations, and commercial proprietary software without building a complex in-house payment processor?
- **Context:** NebuOS must not construct a custom payment gateway or proprietary store escrow backend in early phases.
- **Options:**
  1. *In-House Payment Engine:* High compliance burden (PCI-DSS), legal entity overhead, anti-scope.
  2. *External Verified Payment / Donation Links:* Marketplace client displays certified external links (GitHub Sponsors, Open Collective, Patreon, vendor checkout).
- **Recommendation:** Option 2. Zero payment infrastructure overhead while supporting developer sustainability.

#### OQ-047: Emergency Remote Package Revocation and Automated Quarantine Protocol
- **Priority:** P1 | **Domain:** Security & Store | **Deadline:** Milestone P6 Exit
- **Question:** If malware or a critical vulnerability is detected in an upstream Flathub or third-party Flatpak package, how is it quarantined?
- **Context:** Malicious packages must be immediately neutralized on user machines without requiring a base OS upgrade.
- **Options:**
  1. *Manual User Action:* Users manually uninstall upon reading security advisories.
  2. *Signed Cryptographic Revocation Feed:* `Nebu App Manager` ingests `revocations.json`, disables launcher entries, and halts runtime execution.
- **Recommendation:** Option 2. Proactive client-side security defense.

#### OQ-048: Multi-Source Enterprise and Private Application Repository Configuration
- **Priority:** P2 | **Domain:** Enterprise | **Deadline:** Milestone P8 Exit
- **Question:** How should managed IT environments configure custom internal Flatpak remotes and private registries?
- **Context:** Enterprise fleets need to distribute proprietary internal tools alongside Flathub apps.
- **Options:**
  1. *Hardcoded System Remotes:* Enterprise must rebuild custom OS images.
  2. *Declarative Configuration in `/etc/nebu/sources.d/`:* Drop-in TOML configuration files allowing managed endpoint configuration.
- **Recommendation:** Option 2. Standardized declarative sysadmin interface.

#### OQ-049: Plymouth Boot Splash vs Native Rust Splash Daemon in Milestone P2
- **Priority:** P2 | **Domain:** Boot & Shell | **Deadline:** Milestone P2 Start
- **Question:** In Milestone P2, should NebuOS integrate Plymouth or develop a lightweight native Rust splash daemon anchored directly to DRM/KMS?
- **Context:** Milestone P0 is strictly 100% headless and omits Plymouth (`omit_dracutmodules+=" plymouth "`). Milestone P2 introduces user-facing graphical branding. Plymouth is mature in Fedora, but has C dependencies; a native Rust daemon using `drm-rs` could achieve tighter binding to `nebu-design-tokens` and sub-100ms startup.
- **Options:**
  1. *Plymouth with Custom Nebu Theme:* Standard Fedora Plymouth infrastructure; saves development time, but carries legacy C baggage.
  2. *Lightweight Native Rust Splash Daemon (`nebu-splash`):* Extremely small footprint (< 5 MB RSS), direct binding to `nebu-design-tokens`, zero legacy baggage, seamless atomic handoff to `nebu-compositor`.
- **Recommendation:** Option 1 as baseline for initial P2 bringup with Option 2 evaluated as an optimization during Phase P8.

#### OQ-050: Dynamic BGRT Geometry Normalization across Non-Standard Displays
- **Priority:** P2 | **Domain:** Graphics & Boot | **Deadline:** Milestone P1 Exit
- **Question:** How should the boot display engine handle ultra-wide, vertical, or non-standard aspect ratio laptop displays when inheriting ACPI BGRT OEM logos?
- **Context:** Some vendor UEFI firmware scales BGRT bitmaps with distorted pixel aspect ratios on 16:10 or 3:2 panels.
- **Options:**
  1. *Exact BGRT Coordinates:* Display bitmap exactly at coordinates specified in ACPI table; risk of slight visual distortion if UEFI miscalculated.
  2. *Aspect Ratio Validation & Center Snapping:* Parse BGRT image dimensions, compare against EDID native aspect ratio, and center-snap with letterboxing if distortion exceeds 5%.
- **Recommendation:** Option 2. Guarantees visual symmetry across diverse OEM hardware.

#### OQ-051: Silent Boot Diagnostic Mode Persistent Logging Retention
- **Priority:** P1 | **Domain:** Boot & Systems | **Deadline:** Milestone P0 Exit
- **Question:** When a user triggers Diagnostic Boot via Escape key, should the resulting verbose console log be automatically persisted to disk as an archived boot report?
- **Context:** Users entering diagnostic mode usually experience boot slowdowns or errors. Capturing this log helps support engineers diagnose transient hardware issues.
- **Options:**
  1. *Standard Journald Persistence:* Rely solely on systemd journal logging; no special file created.
  2. *Dedicated Diagnostic Snapshot (`/var/log/nebu-diag-boot-<timestamp>.log`):* Systemd unit detects diagnostic boot flag and dumps full dmesg and journal trace to a dedicated file for easy export.
- **Recommendation:** Option 2. Provides immediate, user-accessible troubleshooting artifact.

#### OQ-052: Upstream Wine Candidate Quarantine Duration Before Stable Promotion
- **Priority:** P1 | **Domain:** Compatibility | **Deadline:** Milestone P4 Exit
- **Question:** How long must a newly synchronized Wine upstream release candidate (`Candidate` channel) remain in quarantine under Compatibility Lab automation before being promoted to `Stable`?
- **Context:** Rapid promotion risks shipping regressions into enterprise workflows (e.g. AutoCAD, Revit, Office), while excessively long quarantine leaves users without modern upstream fixes.
- **Options:**
  1. *7-Day Rapid Quarantine:* Fast turnaround, but insufficient time to detect subtle memory leaks or long-running stability defects.
  2. *14-Day Quarantine with Multi-Tier Lab Gates:* Standard 14-day burn-in across physical lab nodes running L0-L7 workflows; zero regressions required.
  3. *30-Day Extended Quarantine:* Maximizes stability at the cost of slow upstream feature delivery.
- **Recommendation:** Option 2 (14-day quarantine). Balances stability guarantees with continuous upstream alignment.

#### OQ-053: Downstream Delta Eviction Thresholds and Upstream Escalation Policy
- **Priority:** P1 | **Domain:** Compatibility | **Deadline:** Milestone P4 Exit
- **Question:** What operational protocol must govern downstream source patches in `wine.git` that remain unmerged upstream past 180 days?
- **Context:** The upstream-first principle mandates minimal maintained delta ($\le 60\text{ patches}$). Long-lived downstream patches create rebase drag and merge conflict debt.
- **Options:**
  1. *Permanent Local Maintenance:* Continue rebasing indefinitely as long as an application depends on it.
  2. *Mandatory 180-Day Architectural Review:* If a patch cannot be upstreamed within 180 days, either refactor into a prefix-level configuration workaround (`nebu-patcher`), redesign the patch with WineHQ feedback, or flag for deprecation.
- **Recommendation:** Option 2. Enforces delta discipline and prevents perpetual fork accumulation.

#### OQ-054: Compatibility Lab Bare-Metal Farm Scaling Model for Milestone P7
- **Priority:** P1 | **Domain:** Testing & Lab | **Deadline:** Milestone P7 Start
- **Question:** How should the physical hardware farm for Milestone P7 be scaled and housed to support 24/7 automated matrix validation?
- **Context:** The lab requires testing physical Intel, AMD, NVIDIA, and laptop platforms across disparate display, power, and graphics topologies.
- **Options:**
  1. *Pure Colocated Bare-Metal Cloud (e.g. Equinix Metal / AWS Bare Metal):* High operating expense, limited consumer GPU and laptop display/lid testing capabilities.
  2. *On-Premise 4-Node Reference Rack + Virtualized Cloud CI:* Low-cost, high-control physical rack for specialized hardware nodes (Node-INTEL, Node-AMD, Node-NVIDIA, Node-HYBRID) paired with scalable cloud CI for headless Wayland runs.
- **Recommendation:** Option 2. Delivers necessary hardware access (displays, laptop S0ix, dGPU switching) at manageable capital expenditure.

#### OQ-055: NTSYNC Kernel Synchronization Integration Strategy
- **Priority:** P1 | **Domain:** Kernel & Runtime | **Deadline:** Milestone P5 Exit
- **Question:** How should NebuOS package and maintain the NTSYNC kernel synchronization driver (`/dev/ntsync`) across kernel updates?
- **Context:** NTSYNC provides high-performance kernel-level NT synchronization, dramatically reducing wineserver context switching for multi-threaded applications and games. Upstream Linux kernel adoption is progressing.
- **Options:**
  1. *DKMS / Out-of-Tree Kernel Module:* Complex build management across atomic OSTree image deployments.
  2. *Wait for In-Tree Linux Kernel Integration:* Rely on standard `futex_waitv` (`fsync`) until NTSYNC lands in upstream Fedora kernel trees (Linux 7.x+).
- **Recommendation:** Option 2. Avoids out-of-tree kernel module brittleness while preserving native Linux `futex_waitv` acceleration as baseline.

---

## 3. Governance & Decision Process

1. **Resolution Mechanism:** An Open Question is resolved by authoring or updating an Architectural Decision Record (ADR) in [decisions/](decisions/) signed off by the Lead Systems Architect.
2. **Empirical Evidence Requirement:** Performance-critical questions (OQ-001, OQ-008, OQ-010, OQ-022) cannot be decided based on theoretical debate; resolution requires benchmark results from the Compatibility Lab running on minimum specification hardware (4GB RAM, Intel N4020 / Celeron class).
3. **Escalation Trigger:** Any P0 question unresolved within 14 days of its designated milestone deadline escalates directly to the Technical Steering Committee for binding arbitration.

---

## 4. Related Documents
- [README.md](README.md) — Master documentation index and architectural overview
- [RISK_REGISTER.md](RISK_REGISTER.md) — Risk scoring and mitigation planning
- [ASSUMPTIONS.md](ASSUMPTIONS.md) — Foundational engineering assumptions
- [decisions/](decisions/) — Formal Architectural Decision Records
- [decisions/ADR-0014-boot-experience-and-graphical-handoff.md](decisions/ADR-0014-boot-experience-and-graphical-handoff.md) — Boot experience and graphical handoff
- [roadmap/00-implementation-roadmap.md](roadmap/00-implementation-roadmap.md) — Phase deliverables and milestones P0–P12
