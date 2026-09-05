# NebuOS Systems Risk Register

**Status:** ACTIVE  
**Purpose:** Formal identification, quantitative scoring, mitigation planning, contingency routing, and owner tracking for all systems engineering, security, compatibility, and schedule risks in NebuOS.  
**Scope:** Covers architectural, operational, dependency, performance, security, and hardware testing risks across all milestones (P0–P12).  
**Non-goals:** Tracking ordinary product backlog bugs or individual software patch issues.

---

## 1. Risk Assessment Methodology

Each risk is evaluated across two dimensions using a 5-point scale:

- **Likelihood ($L$):** 1 (Rare, $<10\%$), 2 (Unlikely, $10\text{--}30\%$), 3 (Moderate, $30\text{--}60\%$), 4 (Likely, $60\text{--}85\%$), 5 (Almost Certain, $>85\%$).
- **Impact ($I$):** 1 (Negligible), 2 (Minor), 3 (Moderate), 4 (Major / System Degraded), 5 (Catastrophic / Project Blocker).
- **Risk Score ($R = L \times I$):** Ranges from 1 to 25.

### Risk Severity Tiers & Heat Map
```text
Impact  5 |  5 (M)   10 (H)   15 (H)   20 (C)   25 (C)
        4 |  4 (L)    8 (M)   12 (H)   16 (C)   20 (C)
        3 |  3 (L)    6 (M)    9 (M)   12 (H)   15 (H)
        2 |  2 (L)    4 (L)    6 (M)    8 (M)   10 (H)
        1 |  1 (L)    2 (L)    3 (L)    4 (L)    5 (M)
          +-------------------------------------------
             1        2        3        4        5
                         Likelihood
```
- **Critical ($R \ge 16$):** Immediate architectural safeguard and active daily tracking required.
- **High ($10 \le R \le 15$):** Subsystem architectural mitigation required before milestone exit.
- **Medium ($5 \le R \le 9$):** Managed via testing gates and operational policies.
- **Low ($R \le 4$):** Accepted residual risk.

---

## 2. Master Systems Risk Matrix

| Risk ID | Category | Description | $L$ | $I$ | $R$ | Mitigation Strategy | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| **RSK-001** | Compatibility | Windows Kernel Driver Dependency (`.sys`, Anti-Cheat, Hardware Dongles) | 5 | 4 | **20** | Explicit Non-Goal. Pre-execution PE inspection detects kernel drivers and blocks launch with clear UI dialog. NO VM fallback. | Compatibility Lead | ACTIVE |
| **RSK-002** | Performance | Memory Exhaustion / OOM Freezing on 4GB Low-End Devices | 4 | 4 | **16** | Implement Nebu Lite Mode: disable compositor blurs, aggressive warm-cache eviction, zram swap compression, systemd-oomd cgroup kills. | Systems Architect | ACTIVE |
| **RSK-003** | Compatibility | Deep COM/OLE/ActiveX Coupling in Microsoft Office & CAD Suites | 4 | 4 | **16** | Curate custom DLL override profiles (`ole32`, `oleaut32`, `rpcrt4`), pre-register OLE servers in isolated prefix registry. | Compatibility Lead | ACTIVE |
| **RSK-004** | Updates | Atomic OS Image Update Regression Breaks GPU Acceleration or Wine | 3 | 5 | **15** | Automated Tier 0–2 regression test gates in CI; dual-root OSTree staging with automated GRUB rollback on boot failure. | Release Engineer | MONITORING |
| **RSK-005** | Graphics | Proprietary NVIDIA Driver Packaging Instability on Immutable Base | 4 | 3 | **12** | Pre-compile signed NVIDIA driver container layers in cloud CI for every kernel ABI; explicit sync support via Wayland protocol. | Graphics Lead | ACTIVE |
| **RSK-006** | Security | Malicious Windows PE Binary Exploits Linux User Space / Host | 3 | 4 | **12** | Bubblewrap sandbox per prefix: isolate user home, restrict virtual `Z:\` drive, drop network if unneeded, apply Landlock LSM. | Security Lead | ACTIVE |
| **RSK-007** | Technical | Wayland Compositor Panic Causes Immediate Loss of Running Client Apps | 2 | 5 | **10** | Strict separation of compositor and shell; robust Smithay panic boundaries; session lock preservation; decoupled client socket proxy. | Compositor Lead | ACTIVE |
| **RSK-008** | Storage | Prefix Disk Bloat from Multiple Isolated Wine Environments | 4 | 3 | **12** | Btrfs `reflink` provisioning from golden base template; share read-only runtimes; automated deduplication scanner. | Storage Lead | ACTIVE |
| **RSK-009** | Compatibility | Autodesk / Adobe Proprietary Licensing Daemons Fail under Wine | 4 | 3 | **12** | Emulate background licensing services via Wine system services; mock local loopback authentication endpoints in profiles. | Compatibility Lead | ACTIVE |
| **RSK-010** | Performance | Direct3D Shader Compilation Triggers Severe In-Game / In-App Stutter | 4 | 3 | **12** | Global content-addressed shader cache in `~/.cache/nebu/shaders/`; pre-compiled Fossilize pipelines for certified applications. | Graphics Lead | ACTIVE |
| **RSK-011** | Dependency | Upstream Wine-Staging Regressions Break Previously Certified Software | 4 | 3 | **12** | Dual-track runtime architecture: freeze certified enterprise applications to validated Stable builds; isolate Fast track updates. | Compatibility Lead | ACTIVE |
| **RSK-012** | Compatibility | WPF / .NET Framework 4.8 Rendering Failures in Heavy CAD Tools | 4 | 3 | **12** | Fallback from Wine-Mono to automated profile-driven installation of official Microsoft .NET redistributables via winetricks bridge. | Runtime Lead | ACTIVE |
| **RSK-013** | Performance | Cold Application Launch Latency Exceeds 2.5s Target on HDDs/SATA SSDs | 4 | 3 | **12** | Pre-warm Wine runtime pool (wineserver + core DLLs); optimize SQLite metadata indexing; defer non-critical DLL loading. | Runtime Lead | ACTIVE |
| **RSK-014** | Technical | Btrfs Write Amplification & Registry Fragmentation from Wine I/O | 3 | 4 | **12** | Automatically apply `chattr +C` (`nodatacow`) to prefix directories; tune Btrfs commit intervals and metadata caching. | Storage Lead | ACTIVE |
| **RSK-015** | Security | Virtual Drive `Z:\` Host Mapping Exposes Sensitive User Files | 3 | 4 | **12** | Never map `Z:\` to `/`; map exclusively to application sandbox directory; expose documents via XDG Desktop Portal file picker. | Security Lead | ACTIVE |
| **RSK-016** | Legal | Accidental Redistribution of Proprietary Microsoft or Autodesk Binaries | 2 | 5 | **10** | Strict zero-binary policy: NebuOS distributes only recipes and open-source shims; users supply licensed media; CI license scanner. | Lead Architect | MONITORING |
| **RSK-017** | Schedule | Bare-Metal Hardware Diversity Bottleneck in Compatibility Lab | 3 | 3 | **9** | Prioritize 4 reference hardware tiers (Intel low-end, AMD laptop, NVIDIA desktop, Intel Iris Xe); automate remote PXE execution. | QA/Lab Lead | ACTIVE |
| **RSK-018** | Technical | Smithay Compositor Framework Upstream API Churn | 3 | 3 | **9** | Pin Smithay git revisions; contribute upstream; encapsulate compositor internal state behind stable Nebu abstraction traits. | Compositor Lead | MONITORING |
| **RSK-019** | Compatibility | Case-Sensitive Linux Filesystem Breaks Hardcoded Windows Paths | 3 | 3 | **9** | Enable Wine built-in case-insensitive lookup cache; enforce Btrfs directory case-folding (`+F`) on `drive_c` root. | Runtime Lead | MITIGATED |
| **RSK-020** | Dependency | Fedora Atomic Upstream Base Deprecates Critical Packaging Components | 2 | 4 | **8** | Rely strictly on upstream standardized `bootc` and standard OCI container primitives; isolate NebuOS components in `/usr/local` / `/opt`. | Release Engineer | MONITORING |
| **RSK-021** | Performance | CPU Core Wakeups from Uncooperative Polling Daemons Drain Laptop Battery | 3 | 2 | **6** | Strict zero-polling invariant: enforce event-driven epoll/kqueue architecture; timer slack coalescing via systemd cgroups. | Systems Architect | MONITORING |
| **RSK-022** | Graphics | Wayland Fractional Scaling Causes Blurry Rendering in Win32 GDI Apps | 3 | 3 | **9** | Inject Wine prefix DPI scaling registry flags matching Wayland output scale; use viewport downsampling only as fallback. | Graphics Lead | ACTIVE |
| **RSK-023** | Security | Bubblewrap Sandbox Escape via Unprivileged User Namespace Vulnerability | 2 | 4 | **8** | Keep host kernel up-to-date; enforce secondary containment via Landlock LSM and restrictive seccomp syscall filters. | Security Lead | MONITORING |
| **RSK-024** | Schedule | Engineering Scope Creep into Custom Drivers or VM Hypervisors | 2 | 4 | **8** | Strict enforcement of PRD Non-Goals: reject any architecture proposals requiring hypervisors or custom in-tree GPU drivers. | Lead Architect | ACCEPTED |
| **RSK-025** | Dependency | Valve Proton Runtime Divergences from Upstream Wine Break Standalone Apps | 3 | 3 | **9** | Maintain dedicated Proton runtime wrapper specifically for gaming, keeping Wine-Staging for desktop applications. | Runtime Lead | ACTIVE |
| **RSK-026** | Technical | Direct Scanout Pipeline Tears or Glitches on Multi-Monitor Configurations | 2 | 3 | **6** | Enable KMS direct scanout only when focused surface matches output bounds exactly; fallback to composited pass immediately on overlap. | Compositor Lead | MONITORING |
| **RSK-027** | Compatibility | Windows Installer Child Processes Evade Termination on App Close | 3 | 3 | **9** | Run all application processes inside transient systemd user scopes (`nebu-app-<id>.scope`); SIGTERM/SIGKILL kills entire cgroup. | Runtime Lead | MITIGATED |
| **RSK-028** | Performance | High Disk I/O Saturation During Parallel Application Installations | 3 | 2 | **6** | Serialize prefix creation queues; rate-limit background winetricks downloads; enforce I/O scheduling class (BFQ/Kyber). | Storage Lead | MONITORING |
| **RSK-029** | Power/ACPI | Broken OEM ACPI Firmware Causes S0ix Modern Standby Battery Drain (>2.5%/hr) | 4 | 4 | **16** | Dynamic S0ix/S3 detection; automated fallback to `deep` S3 sleep; SoC PMC residency verification (ADR-0010). | Power Mgmt Lead | ACTIVE |
| **RSK-030** | Hardware | Hybrid GPU Crash/Freeze During Dynamic PRIME Switching or Resume from Sleep | 3 | 4 | **12** | Pre-suspend cgroups v2 freezing of Wine processes (`nebu-wine-freeze.sh`); D3cold powerdown; explicit sync. | Graphics Lead | ACTIVE |
| **RSK-031** | Peripherals | USB-C / Thunderbolt Dock Display Dropout or Compositor Crash on Hotplug | 3 | 3 | **9** | Dynamic DRM connector uevent handling in `nebu-compositor`; surface auto-migration to active displays. | Compositor Lead | ACTIVE |
| **RSK-032** | Network | Wi-Fi 6E/7 Realtek/MediaTek Driver Regressions on Sleep/Resume | 3 | 3 | **9** | Automated interface power cycling via NetworkManager dispatcher; firmware version pinning via LVFS/kernel. | Network Lead | ACTIVE |
| **RSK-033** | Infrastructure | OCI Container Registry Outage or DNS Resolution Failure | 3 | 3 | **9** | Client-side exponential backoff; dual-origin registry mirrors; existing active deployment continues undisturbed. | DevOps Lead | ACTIVE |
| **RSK-034** | Release | Faulty OS Image Accidentally Promoted to Stable Channel | 2 | 5 | **10** | Phased canary rollout (5% -> 25% -> 100%); automated error threshold fast-abort; publisher-side release rollback re-pointing `:stable`. | Release Engineer | ACTIVE |
| **RSK-035** | Security | OCI Container Image Signing Key Compromise or Expiration | 1 | 5 | **5** | HSM-backed root key; automated Rekor transparency logging; secondary offline revocation key; client trust update path. | Security Lead | MONITORING |
| **RSK-036** | Storage | Insufficient Disk Space for Dual Deployment Staging (< 2.5 GB) | 4 | 3 | **12** | Pre-staging free space probe (5GB warning, 2.5GB blocking); automated `bootc prune`; Btrfs extent sharing reduces delta. | Storage Lead | ACTIVE |
| **RSK-037** | Kernel/Boot | Post-Update Kernel Panic or Display Driver Initialization Hang | 3 | 5 | **15** | Hardware watchdog timer (60s); GRUB BLS boot counter (`boot_counter=3`); automated fallback to previous deployment upon boot hang. | Systems Architect | ACTIVE |
| **RSK-038** | Bootloader | Automated Boot Counter Rollback Failure or Corruption of `grubenv` | 2 | 4 | **8** | Atomic `grubenv` updates; interactive GRUB fallback entry accessible via Shift/ESC; read-only fallback defaults to last good entry. | Systems Architect | MONITORING |
| **RSK-039** | Network | Network Interruption or Packet Corruption During Layer Download | 4 | 2 | **8** | Content-addressed OCI blob chunking; HTTP range resumable downloads; SHA-256 layer digest verification before staging. | DevOps Lead | MITIGATED |
| **RSK-040** | Upstream | Upstream Major Fedora Base Upgrade (e.g. F44 -> F45) Breaks Core Stack | 3 | 4 | **12** | Dedicated 30-day soak period in testing; full 11-stage compatibility test farm re-execution; ABI symbol compatibility gates. | Release Engineer | ACTIVE |
| **RSK-041** | Graphics | Proprietary NVIDIA Driver Incompatibility Across Kernel Bumps | 4 | 4 | **16** | Lockstep OCI driver container layers; kernel header ABI pinning; release gating blocks OS promotion if NVIDIA layer fails. | Graphics Lead | ACTIVE |
| **RSK-042** | Hardware | Laptop Modern Standby S0ix or Peripheral Regression After OS Update | 3 | 4 | **12** | Compatibility Lab bare-metal 25x sleep/wake stress matrix; automated PMC substate validation before stable release. | Hardware QA Lead | ACTIVE |
| **RSK-043** | Release | Staged Rollout Cohort Failure and Ineffective Fast-Abort | 2 | 4 | **8** | Anonymous local machine hashing into 100 buckets; client respects metadata `rollout_percentage`; zero server telemetry required. | Release Engineer | ACTIVE |
| **RSK-044** | Dependency | Flathub Upstream CDN/API Availability Outage Interrupts Downloads | 3 | 3 | **9** | Local SQLite metadata cache (`marketplace.db`) enables offline browsing; client exponential backoff; direct fallback CDN mirrors. | App Platform Lead | ACTIVE |
| **RSK-045** | Upstream | Upstream AppStream Metadata Format Changes or Schema Drift | 2 | 3 | **6** | Schema normalization in App Manager; resilient fallback to basic manifest fields if extended tags missing. | App Platform Lead | ACTIVE |
| **RSK-046** | Security | Publisher Trust Compromise or Malicious Package Submission on Flathub | 2 | 5 | **10** | Unprivileged Bubblewrap sandbox containment; mandatory pre-install permission consent; emergency remote revocation list. | Security Lead | ACTIVE |
| **RSK-047** | Security | Application Signing Key Compromise or Undetected Supply-Chain Tampering | 1 | 5 | **5** | Mandatory SHA-256 digest validation; Sigstore Rekor transparency audit; rapid remote quarantine mechanism. | Security Lead | MONITORING |
| **RSK-048** | Security | Supply-Chain Vulnerability in Bundled Flatpak Shared Library | 3 | 4 | **12** | Bubblewrap sandbox severs unneeded network/device access; automated CVE tracking; automated notification of available patches. | Security Lead | ACTIVE |
| **RSK-049** | Security | Flatpak / Bubblewrap User Namespace Sandbox Escape Vulnerability | 2 | 5 | **10** | Secondary containment via Landlock LSM and seccomp BPF filters; keep host kernel updated via bootc transactional deployments. | Security Lead | MONITORING |
| **RSK-050** | Compatibility | Incompatible Upstream Application Update Breaks User Workflow | 4 | 3 | **12** | Support Flatpak commit pinning; one-click user rollback to previous application commit in Marketplace Installed tab. | App Platform Lead | ACTIVE |
| **RSK-051** | Storage | Disk Space / Cache Exhaustion from Redundant Flatpak Runtimes | 4 | 3 | **12** | Pre-flight disk space probe; Btrfs zstd compression; App Manager automated unused runtime prune wizard. | Storage Lead | ACTIVE |
| **RSK-052** | Network | Network Disconnect or Packet Corruption During Multi-Gigabyte App Download | 4 | 2 | **8** | HTTP range request resumable downloads; atomic staging directory; SHA-256 payload checksum validation before extraction. | DevOps Lead | MITIGATED |
| **RSK-053** | Legal | DMCA Notice or Copyright Dispute Regarding Third-Party App Recipe | 2 | 4 | **8** | Zero proprietary binary distribution; recipes fetch legal media from official vendor CDNs; formal notice-and-takedown protocol. | Lead Architect | MONITORING |
| **RSK-054** | Infrastructure | Nebu Marketplace Metadata Origin Server Outage | 2 | 3 | **6** | Static anycast CDN distribution with multi-origin replication; client-side stale-while-revalidate local cache. | DevOps Lead | ACTIVE |
| **RSK-055** | Compatibility | Windows Application Compatibility Drift Across Wine Runtime Updates | 3 | 4 | **12** | Freeze Wine version per application prefix; gate runtime upgrades behind Compatibility Lab automated regression benchmarks. | Compatibility Lead | ACTIVE |
| **RSK-056** | Technical | Display Modesetting Flicker During DRM/KMS Handover | 3 | 3 | **9** | Inherit EFI framebuffer scanout plane via SimpleDRM (with BGRT metadata); atomic modesetting under scanout preservation principle (ADR-0014). | Compositor Lead | ACTIVE |
| **RSK-057** | Kernel/Boot | Early Boot Silent Hang Obscuring Critical Diagnostic Information | 3 | 4 | **12** | Emergency Escape/F8 unblank keypress; explicit diagnostic BLS entry; hardware watchdog 60s timeout with automatic rollback. | Systems Architect | ACTIVE |
| **RSK-058** | Governance | Milestone Scope Creep via Premature Splash Implementation in Headless P0 | 2 | 5 | **10** | Strict milestone isolation in AGENTS.md Sec 24; omit Plymouth in P0 dracut; CI image linting blocks GUI packages. | Lead Architect | ACTIVE |

---

## 3. Deep-Dive Containment Plans for Critical & High Risks

### 3.1 RSK-001: Windows Kernel Driver Dependency (.sys / Anti-Cheat)
- **Score:** 20 (Likelihood: 5, Impact: 4) — CRITICAL
- **Root Cause:** Competitive multiplayer games (Valorant, Fortnite) and enterprise CAD USB dongles install ring-0 Windows drivers that execute privileged kernel instructions not supported by user-space compatibility layers.
- **Architectural Safeguards:**
  1. *Early PE Static Inspection:* At application launch, `nebu-runtime-daemon` parses the PE header and import tables. If imports reference `ntoskrnl.exe`, `hal.dll`, or known anti-cheat drivers (EasyAntiCheat.sys, BattlEye.sys, vgkrn.sys), execution is intercepted before Wine initialization.
  2. *Definitive User Messaging:* Display an explicit system modal dialog stating: *"This application requires a Windows kernel-level driver or anti-cheat system which cannot run on NebuOS without compromising system security."*
  3. *Zero-VM Guarantee:* Under no circumstances will NebuOS spawn a Windows virtual machine fallback. The application status is recorded as `UNSUPPORTED_KERNEL_DRIVER` in the local compatibility database.

### 3.2 RSK-002: Memory Exhaustion on 4GB Baseline Hardware
- **Score:** 16 (Likelihood: 4, Impact: 4) — CRITICAL
- **Root Cause:** A 4GB physical memory budget leaves only ~3.2GB for userland after kernel allocations. Running modern web browsers alongside Wine applications can rapidly exhaust RAM.
- **Architectural Safeguards:**
  1. *ZRAM Swap Compression:* Configure `zram-generator` with `zstd` compression algorithm allocating up to 100% of RAM as compressed swap.
  2. *Nebu Lite Mode:* When available RAM drops below 700MB (detected via Pressure Stall Information `some avg10 > 40`), the system triggers Lite Mode:
     - Compositor turns off blur filters, drop shadows, and window animations.
     - `nebu-runtime-daemon` evicts the 64MB pre-warmed Wine cache immediately.
     - Background indexing and update checks are paused.
  3. *systemd-oomd Enforcement:* If memory pressure persists, `systemd-oomd` terminates the most memory-intensive transient application scope without crashing the compositor or desktop session.

### 3.3 RSK-003: Deep COM/OLE/ActiveX Coupling in Office & CAD
- **Score:** 16 (Likelihood: 4, Impact: 4) — CRITICAL
- **Root Cause:** Microsoft Office (Word, Excel, PowerPoint) and Autodesk suites rely on internal Component Object Model (COM) servers, in-process RPCs, and ActiveX controls for macro execution and dynamic linking.
- **Architectural Safeguards:**
  1. *Curated Native DLL Overrides:* Provide tested native DLL overrides (`riched20.dll`, `mso.dll`, `ole32.dll`) packaged inside the certified application profile.
  2. *Prefix Registry Pre-Configuration:* Automatically inject verified CLSID entries and typelib registrations into the application prefix registry during silent provisioning.
  3. *Automated Headless Test Suite:* In the Compatibility Lab, run automated PowerShell/VBScript macros inside headless Wine instances on every release candidate to verify COM stability.

### 3.4 RSK-004: Atomic OS Update Regressions Breaking Graphics or Wine
- **Score:** 15 (Likelihood: 3, Impact: 5) — HIGH
- **Root Cause:** An upstream Mesa or kernel update may introduce regressions that break Vulkan swapchains or Wine compatibility.
- **Architectural Safeguards:**
  1. *Four-Stage Release Channels:* Updates flow from Nightly -> Canary -> Beta -> Stable. Stable releases require 100% pass rates on automated Tier 0, 1, and 2 test gates.
  2. *Transactional Bootc Rollback:* The OS uses OSTree/bootc transactional deployments. The previous working deployment is retained in GRUB.
  3. *Automatic Boot Health Checker:* `nebu-boot-checker.service` verifies display server startup and GPU acceleration post-update; failure to start triggers an automatic fallback reboot into the previous deployment.

### 3.5 RSK-005: NVIDIA Driver Packaging on Immutable OS
- **Score:** 12 (Likelihood: 4, Impact: 3) — HIGH
- **Root Cause:** Fedora Atomic forbids local compilation via `akmods` in immutable deployments without layering packages.
- **Architectural Safeguards:**
  1. *Containerized Pre-Compiled Drivers:* Cloud CI builds signed NVIDIA kernel modules and userspace libraries packaged into dedicated OCI container layers (`quay.io/nebu-os/nvidia`).
  2. *Driver Version Pinning:* Maintain driver compatibility across stable kernel ABIs; test Vulkan explicit sync (`linux-drm-syncobj-v1`) before promoting images.

### 3.6 RSK-006: UI Toolkit Memory Regression and Slint Resource Bloat
- **Score:** 9 (Likelihood: 3, Impact: 3) — MEDIUM
- **Root Cause:** Slint UI templates accumulating uncompressed textures or deep component trees could cause `nebu-shell` to exceed its 45 MB idle RSS budget.
- **Architectural Safeguards:**
  1. *Automated Memory CI Assertion:* Headless QEMU benchmark gates commits on memory consumption (`RSS <= 45MB`).
  2. *Strict Icon Cache Cap:* In-memory texture cache capped at <= 8.0 MB with LRU eviction (`docs/design/01-iconography.md`).
  3. *systemd Slice Enforcement:* `nebu-shell.service` runs under `MemoryHigh=50M` and `MemoryMax=64M`.

### 3.7 RSK-007: Third-Party Application Icon Vector Exploits & XML Expansion
- **Score:** 12 (Likelihood: 3, Impact: 4) — HIGH
- **Root Cause:** Untrusted SVG icons from Flathub or Windows PE resources could contain XML entity expansion (Billion Laughs) attacks or malformed vector buffers that crash the shell.
- **Architectural Safeguards:**
  1. *Sandboxed Icon Pipeline:* All third-party SVGs and `.ico` files are parsed in an isolated unprivileged Bubblewrap container (`bwrap --unshare-all`).
  2. *Memory and Time Budgets:* The sanitizer helper enforces a 50ms processing timeout and a 10MB memory allocation ceiling.

### 3.8 RSK-008: Icon Library Lock-in and Licensing Ambiguity
- **Score:** 8 (Likelihood: 2, Impact: 4) — MEDIUM
- **Root Cause:** Direct hardcoding of third-party icon glyph names or paths into UI templates could create severe vendor lock-in and complicate transitioning to a dedicated custom Nebu Icon Set.
- **Architectural Safeguards:**
  1. *Abstract NebuIcon API:* All UI components reference icons via the `NebuIcon` enum/key API (`ADR-0013`).
  2. *SPDX Compliance Gates:* CI checks license manifests and ensures candidate icons remain isolated in `assets/prototype/`.

### 3.9 RSK-009: Fractional Scaling Visual Degradation and Subpixel Blurring
- **Score:** 9 (Likelihood: 3, Impact: 3) — MEDIUM
- **Root Cause:** Wayland fractional scaling (125%, 150%, 175%) causing bilinear interpolation blur on high-DPI laptop displays.
- **Architectural Safeguards:**
  1. *Protocol Binding:* Native implementation of `wp_fractional_scale_v1`.
  2. *Integer Rasterization Snapping:* Vector masters are rasterized at exact target physical device pixel dimensions.

### 3.10 RSK-056: Display Modesetting Flicker During DRM/KMS Handover
- **Score:** 9 (Likelihood: 3, Impact: 3) — MEDIUM
- **Root Cause:** Kernel GPU driver initialization or Wayland compositor startup resetting the CRTC or toggling display planes, causing visual black flashes or backlight flicker during boot transition.
- **Architectural Safeguards:**
  1. *EFI Framebuffer & SimpleDRM Continuity:* Kernel maintains UEFI GOP linear framebuffer scanout via `simpledrm` (guided by ACPI BGRT metadata) without pipeline teardown.
  2. *Fastboot Parameters:* Embed driver-specific fastboot parameters (e.g. `i915.fastboot=1`) in dracut.
  3. *Atomic KMS Inheritance in NebuCompositor:* Smithay backend queries active CRTC and inherits scanout plane via atomic commit under the scanout preservation principle (avoiding unnecessary modeset when compatible, while permitting clean atomic modeset if hardware requires link retraining) (ADR-0014).

### 3.11 RSK-057: Early Boot Silent Hang Obscuring Critical Diagnostic Information
- **Score:** 12 (Likelihood: 3, Impact: 4) — HIGH
- **Root Cause:** Aggressive silent boot parameters (`quiet splash loglevel=3`) suppress all console output, leaving users and developers with a blank screen if Dracut or early systemd fails to mount root storage.
- **Architectural Safeguards:**
  1. *Emergency Escape Hatch:* Pressing `Escape` or `F8` unblanks the console and reveals live log streams immediately.
  2. *Dedicated Diagnostic BLS Entry:* `ostree-1-nebuos-diag.conf` with `debug loglevel=7 console=tty1` available in GRUB menu.
  3. *Automated Hardware Watchdog & Panic Reboot:* Kernel panic triggers automatic reboot (`panic=10`); watchdog timer triggers hardware reset after 60s, decrementing boot counter and initiating rollback.

### 3.12 RSK-058: Milestone Scope Creep via Premature Splash Implementation in Headless P0
- **Score:** 10 (Likelihood: 2, Impact: 5) — HIGH
- **Root Cause:** Developers attempting to implement Plymouth splash animations or Wayland GUI components prematurely during Milestone P0, destabilizing the minimal base image.
- **Architectural Safeguards:**
  1. *Strict Milestone Isolation Governance:* Section 24 in `AGENTS.md` strictly confines P0 to 100% headless foundation (`omit_dracutmodules+=" plymouth "`).
  2. *Automated CI Package Audits:* CI tests fail immediately if graphical, Plymouth, or Wayland packages are detected in the P0 image manifest.

---

## 4. Risk Review Cadence & Ownership Governance

1. **Weekly Risk Standup:** The Systems Architect and Lead Engineers review Critical ($R \ge 16$) and High ($R \ge 10$) risks every Monday.
2. **Mitigation Sign-Off:** A risk cannot be transitioned to `MITIGATED` without verifiable test results (e.g. unit tests, integration test logs, or Compatibility Lab automated benchmarks).
3. **Escalation Protocol:** If any risk escalates into an active blocker during milestone execution, a mitigation review meeting is convened within 24 hours to reassign engineering capacity.

---

## 5. Related Documents
- [README.md](file:///root/NebuOS/docs/README.md) — Master architecture overview
- [OPEN_QUESTIONS.md](file:///root/NebuOS/docs/OPEN_QUESTIONS.md) — Unresolved design decisions and trade-offs
- [ASSUMPTIONS.md](file:///root/NebuOS/docs/ASSUMPTIONS.md) — Foundational engineering assumptions
- [decisions/ADR-0009-no-vm.md](file:///root/NebuOS/docs/decisions/ADR-0009-no-vm.md) — Prohibition of Virtual Machines
- [testing/00-testing-strategy.md](file:///root/NebuOS/docs/testing/00-testing-strategy.md) — Testing strategy and QA gates
- [updates/04-rollback.md](file:///root/NebuOS/docs/updates/04-rollback.md) — Atomic rollback and boot recovery
- [decisions/ADR-0014-boot-experience-and-graphical-handoff.md](file:///root/NebuOS/docs/decisions/ADR-0014-boot-experience-and-graphical-handoff.md) — Boot experience and graphical handoff
