# ADR-0014: NebuOS Boot Experience Architecture and Graphical Handoff

**Status:** APPROVED  
**Date:** 2026-09-04  
**Authority Level:** Binding Architectural Decision Record  
**Deciders:** Principal OS Architect, Linux Kernel/Hardware Compatibility Engineer, Desktop Systems Engineer, Security Architect, Release Gate Auditor  
**Consulted:** PRD §5–8 (Platform Base), §11–13 (Desktop & Compositor), §43–44 (Storage & Deployment), §58 (Reliability & Recovery); ADR-0001 (Kernel); ADR-0002 (Fedora Base); ADR-0003 (Wayland); ADR-0008 (Atomic Updates); ADR-0009 (NebuShell UI); ADR-0010 (Hardware & Power); ADR-0011 (OS Updates & Rollback); ADR-0013 (UI Design System)  

---

## 1. Context and Problem Statement

NebuOS aims to provide a modern, distraction-free operating system experience. In conventional Linux distributions, the boot process is notoriously unpolished: users are greeted with scrolling kernel dmesg logs, rapid-fire systemd service initialization notices (`[  OK  ] Started ...`), blinking virtual terminal (VT) text cursors, and jarring screen flicker caused by repeated display mode-setting transitions between UEFI GOP, early kernel SimpleDRM, KMS drivers, and the display manager.

Modern operating systems (macOS, Windows 11, ChromeOS) present an unbroken, branded visual flow from firmware power-on to the interactive desktop. However, naive attempts to achieve this in Linux distributions routinely lead to severe architectural pitfalls:
1. **Premature Graphical Bloat in Early Boot:** Embedding complex graphical frameworks (GTK, Qt, Slint) into the initial ramdisk (`initramfs`) bloats image size by 50MB–150MB, slows cold storage I/O, increases boot latency by seconds, and risks hard boot deadlocks if proprietary graphics drivers fail.
2. **Violation of Milestone P0 Headless Invariant:** Introducing graphical boot splash daemons or desktop dependencies into Milestone P0 compromises its clean headless boundary, complicating automated QEMU CI verification and regression testing.
3. **Loss of Diagnostic Visibility:** Overly aggressive silencing of boot logs frequently turns minor service failures into opaque "black screen hangs", leaving field users and developers with zero troubleshooting information.
4. **Display Flicker Across Subsystems:** Transitioning the display framebuffer across UEFI, kernel KMS, splash daemons, Wayland compositors, and the desktop shell causes repeated screen blanks and monitor signal re-syncs unless strict hardware handoff protocols are observed.
5. **Decoupled Update and Rollback Experience:** When an OS update fails or a kernel panics, users are often stranded at a grub prompt or emergency shell without clear visual guidance or automated reversion to the prior known-good deployment.

NebuOS requires an authoritative Architectural Decision Record establishing a silent, flicker-free boot experience across the entire lifecycle, strictly enforcing milestone phase boundaries, defining three distinct boot modes, decoupling boot stages from deployment health criteria, and integrating automated transactional rollback.

---

## 2. Decision Drivers

- **Silent & Polished by Default:** Under normal boot, users must experience an unbroken, branded visual flow without kernel logs, systemd service messages, or blinking terminal cursors.
- **Strict Phase Boundaries (P0 Remains 100% Headless):**
  - **Milestone P0:** Strictly headless foundation (UEFI GOP, GRUB2 BLS, kernel, Dracut without Plymouth, systemd multi-user target, bootc rollback counter, serial/TTY diagnostics). ZERO graphical desktop UI, ZERO Slint, ZERO Wayland, ZERO compositor.
  - **Milestone P1:** Display server and hardware presentation infrastructure (DRM/KMS drivers, scanout preservation, Wayland protocol server, NebuCompositor).
  - **Milestone P2:** NebuOS graphical boot experience, splash branding presentation, seamless desktop shell transition, and shutdown/restart visual flow.
- **Display Continuity & Anti-Flicker:** Continuous preservation of the display framebuffer from UEFI GOP through early kernel SimpleDRM, native GPU KMS driver takeover, and Wayland compositor scanout.
- **Pragmatic Modeset Policy:** Atomic modesetting is the transition mechanism. Principle: *"Preserve existing scanout and avoid unnecessary modeset when compatible."* Native KMS drivers may modeset if hardware/panel timings mandate it.
- **Uncompromised Diagnostic Escape Hatch:** Pressing the `Escape` or `F8` key (or selecting the Diagnostic BLS entry) immediately reveals real-time kernel and systemd logs.
- **Deterministic Rollback & Recovery:** Full integration with `bootc` and GRUB `grubenv` boot counters; failed boots trigger automatic fallback to the previous deployment without requiring a GUI.
- **Unified Design System:** Visual boot elements must bind to tokens from `ADR-0013` and `docs/design/` (`Color.Background #0D1117`, `Color.Accent #388BFD`). No parallel or competing design system may be created for boot.
- **Separation of Concerns:** Clear boundary between Boot Infrastructure, Boot Visual Presentation, and Desktop UI.

---

## 3. Considered Options

### Option 1: Layered Boot Architecture with Headless P0, DRM Handshake in P1, and Token-Driven Splash in P2 [SELECTED]
Adopt a disciplined, layered boot architecture:
1. P0 implements the headless, silenced kernel/systemd foundation using GRUB2 BLS entries (`quiet splash loglevel=3 rd.systemd.show_status=false systemd.show_status=false vt.global_cursor_default=0 udev.log_level=3`), Dracut with Plymouth omitted (`omit_dracutmodules+=" plymouth "`), and the transactional rollback counter.
2. P1 implements the DRM/KMS atomic handover in `nebu-compositor`, preserving the active framebuffer scanout without VT switching.
3. P2 implements the visual boot splash (via a lightweight, hardened splash engine integrating `nebu-design-tokens`) and coordinates the smooth cross-fade to `nebu-shell`.
- *Pros:* Completely protects P0 headless purity; eliminates all display flicker; provides robust diagnostic fallback; integrates seamlessly with `bootc` rollback; adheres to the master design system.
- *Cons:* Requires disciplined synchronization across milestones P0, P1, and P2.

### Option 2: Monolithic Early Userspace Graphical UI in Initramfs
Embed Slint, Mesa, and Wayland components directly into the Dracut initramfs to render the desktop shell directly from early boot.
- *Rejected:* Destroys P0 headless architecture; inflates initramfs to 120MB+; creates massive GPU driver synchronization hazards; risks unbootable systems if Mesa fails in ramdisk.

### Option 3: Traditional Linux Verbose TTY Console Boot
Retain raw text scrolling (`systemd.show_status=true`, `loglevel=7`) as the permanent boot experience.
- *Rejected:* Directly violates the product vision of a polished, consumer-grade desktop operating system.

### Option 4: Static Kernel Logo (fbcon logo)
Rely solely on the Linux kernel framebuffer logo (`CONFIG_LOGO=y`) displayed at top-left of the screen.
- *Rejected:* Visually crude; unable to display animated progress indicators, OS update states, or automated rollback explanations.

---

## 4. Decision Outcome

**Chosen Option: Option 1 — Layered Boot Architecture with Headless P0, DRM Handshake in P1, and Token-Driven Splash in P2.**

### 4.1 Canonical 10-Stage Boot Lifecycle

```mermaid
sequenceDiagram
    autonumber
    participant HW as Stage 1: POWER_ON (Firmware)
    participant UEFI as Stage 2: UEFI (GOP & BGRT)
    participant BL as Stage 3: BOOTLOADER (GRUB2 BLS)
    participant K as Stage 4: KERNEL (SimpleDRM)
    participant RD as Stage 5: INITRAMFS (Dracut)
    participant S as Stage 6: SYSTEMD (PID 1)
    participant GH as Stage 7: GRAPHICAL_HANDOFF (KMS)
    participant NC as Stage 8: NEBUCOMPOSITOR (P1)
    participant NS as Stage 9: NEBUSHELL (P2)
    participant RDY as Stage 10: READY (Interactive Session)

    HW->>UEFI: Power rails up, POST complete
    Note over UEFI: Displays OEM Logo in EFI FB; exports ACPI BGRT
    UEFI->>BL: Launch /EFI/BOOT/BOOTX64.EFI (GRUB2)
    Note over BL: Evaluates boot_counter; parses BLS entry silently
    BL->>K: Boot vmlinuz (quiet splash loglevel=3)
    Note over K: Binds SimpleDRM to EFI FB; retains OEM logo
    K->>RD: Decompress initramfs
    Note over RD: Mounts Btrfs sysroot (@); switch_root to /sysroot
    RD->>S: Exec /usr/lib/systemd/systemd
    Note over S: Starts services silently (multi-user.target)
    S->>GH: Probe native GPU KMS driver (i915/amdgpu/nouveau)
    Note over GH: Inherits active scanout plane without mode reset where compatible
    GH->>NC: Launch nebu-compositor (acquires DRM Master)
    Note over NC: Stages initial frame (#0D1117); commits atomically
    NC->>NS: Launch nebu-shell over Wayland socket
    Note over NS: Renders layer surfaces; executes 200ms cross-fade
    NS->>RDY: Input focus unblocked; health check validates deployment
```

---

## 5. Detailed Architecture & Subsystem Responsibilities

### 5.1 Canonical 10-Stage Specification Matrix

| Stage | Stage Name | Owner Subsystem | Inputs | Outputs | Screen / Display Owner | State Transition Trigger | Failure Condition | Fallback Action | Observability Location | Primary Milestone Phase |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | `POWER_ON` | Firmware / SoC | Power button / AC power | Hardware reset line deasserted | None (display unpowered or panel syncing) | Reset vector executed | Hardware power failure / bad RAM | POST beep codes / LED flash codes | Motherboard diagnostics | Hardware / Pre-OS |
| **2** | `UEFI` | UEFI Firmware | SPI Flash UEFI binary | EFI GOP initialized, ACPI BGRT table | UEFI GOP (EFI Framebuffer) | Boot entry selected in NVRAM | Corrupt NVRAM / missing EFI boot manager | Firmware Setup utility / UEFI shell | Firmware console / setup | Firmware / Pre-OS |
| **3** | `BOOTLOADER` | GRUB2 (BLS) | `/boot/efi/` binary, `grubenv` | Selected BLS entry, decremented boot counter | EFI Framebuffer | Kernel & initrd loaded into RAM | Missing BLS entry / `grubenv` I/O error | Drops to GRUB command line / fallback entry | GRUB console | **Milestone P0** |
| **4** | `KERNEL` | Linux Kernel 6.14+ | Kernel cmdline, EFI handover | Early driver tree, SimpleDRM bind | Linux SimpleDRM (`/dev/fb0`) | Initramfs unpacked in RAM | Early kernel panic / driver crash | `panic=10` auto-reboot; unblank console | Kernel ring buffer (`dmesg`) | **Milestone P0** |
| **5** | `INITRAMFS` | Dracut Headless | Storage drivers, Dracut scripts | Root mounted (`@`), switch_root | SimpleDRM Framebuffer | `systemd` executed on `/sysroot` | Btrfs root subvolume `@` not found | Drops to Dracut emergency shell (`rdshell`) | `/run/initramfs/rdsosreport.txt` | **Milestone P0** |
| **6** | `SYSTEMD` | systemd (PID 1) | `/etc/systemd/system`, units | System targets reached (`multi-user`) | SimpleDRM Framebuffer | `display-manager.service` triggered | Critical systemd service deadlocks | Drops to `rescue.target` on TTY1 | `journalctl -b`, `/var/log/boot-failure.log` | **Milestone P0** |
| **7** | `GRAPHICAL_HANDOFF` | DRM/KMS Driver | PCI uevent, firmware scanout plane | Native DRM nodes (`/dev/dri/card0`) | Native KMS Display Plane | DRM Master available for acquisition | GPU driver initialization failure | Falls back to Linux SimpleDRM | `dmesg`, `udev` log | **Milestone P1** |
| **8** | `NEBUCOMPOSITOR` | NebuCompositor (Smithay) | DRM Master, libinput seat | Wayland socket (`wayland-0`), initial frame | `nebu-compositor` primary plane | Socket ready for client connections | Compositor crashes on launch | Throttle restart; fallback to software Mesa Pixman | `journalctl -u nebu-compositor` | **Milestone P1** |
| **9** | `NEBUSHELL` | NebuShell (Slint) | Wayland socket, design tokens | Desktop layer surfaces, 200ms cross-fade | Wayland Layer-Shell Surfaces | Shell surfaces committed to compositor | Shell crashes during startup | Compositor shows emergency recovery dialog | `journalctl -u nebu-shell` | **Milestone P2** |
| **10** | `READY` | User Session Hub | Interactive input, user credentials | Fully responsive desktop session | Accelerated Wayland desktop | `nebu-boot-check.service` commits deployment | Health check assertions fail within 45s | Triggers automated reboot & deployment rollback | `journalctl -u nebu-boot-check` | **Milestone P2** |

---

### 5.2 The Three Standard Boot Modes

#### 1. Normal Boot Mode (Default User Experience)
- **Design Intent:** A polished, silent, consumer-grade experience free of technical jargon, scrolling text, or blinking cursors.
- **Kernel Command-Line Parameters:**
  ```text
  quiet splash loglevel=3 rd.systemd.show_status=false systemd.show_status=false vt.global_cursor_default=0 udev.log_level=3
  ```
- **Visual Presentation:** The screen maintains continuity from the OEM logo to a dark background (`#0D1117`). In Milestone P2, a subtle brand element and progress indicator appears.
- **Diagnostic Escape Hatch:** Pressing `Escape` or `F8` at any time during boot immediately cancels suppression, unblanks the console, and exposes live kernel/systemd log streams on TTY1.

#### 2. Diagnostic Boot Mode (Developer & Troubleshooting Mode)
- **Design Intent:** Maximum transparency for engineers, QA, and advanced users resolving startup regressions.
- **Activation Vectors:**
  1. User presses `Escape` or `F8` during early boot.
  2. User selects `NebuOS (Diagnostic / Verbose Mode)` from the GRUB boot menu.
- **Kernel Command-Line Parameters:**
  ```text
  debug systemd.show_status=true rd.systemd.show_status=true loglevel=7 console=tty1
  ```
- **Visual Presentation:** Complete kernel dmesg scrolling, colorized systemd service transitions (`[  OK  ]`, `[FAILED]`), storage mount timings, and network lease acquisitions.

#### 3. Recovery / Rollback Boot Mode (Automated Resilience Mode)
- **Design Intent:** Transparent, safe recovery when an update or configuration renders the current deployment unbootable.
- **Activation Vectors:**
  1. Automated trigger: The GRUB bootloader detects `boot_counter <= 0` after 3 consecutive failed startup attempts.
  2. Manual trigger: User holds `Shift`/`Esc` at power-on and selects `NebuOS (Rollback to Previous Deployment)`.
- **Execution:** Boots silently into the prior verified OSTree deployment (`bootc rollback`).
- **User Notification:** In Milestone P2, upon reaching the desktop, `nebu-shell` displays a non-modal recovery status card:
  > **System Update Restored**  
  > NebuOS could not complete startup with the latest update. Your previous working version has been safely restored. All personal files, apps, and settings remain completely intact.  
  > `[ View Diagnostics ]` `[ Dismiss ]`
- **Headless P0 Independence:** In Milestone P0, the rollback mechanism functions entirely via GRUB BLS and systemd headless targets; it does **NOT** require NebuShell or any GUI.

---

### 5.3 Display Continuity & Graphical Handover Pipeline

```
[ UEFI GOP ]
     │ (Physical EFI framebuffer allocated in VRAM; OEM logo drawn)
     ▼
[ EFI Framebuffer ]  <── ACPI BGRT provides bitmap location & coordinate metadata
     │ (Linux SimpleDRM attaches to physical framebuffer without reinitializing clocks)
     ▼
[ Linux SimpleDRM ]
     │ (Preserves scanout while kernel unpacks initramfs and starts systemd)
     ▼
[ Native GPU Driver (KMS) ] (i915 / amdgpu / nouveau)
     │ (Binds hardware; inherits scanout plane; preserves timing where compatible)
     ▼
[ NebuCompositor (P1) ]
     │ (Acquires DRM Master; stages initial frame #0D1117; commits atomically)
     ▼
[ NebuShell (P2) ]
     │ (Connects via layer-shell; executes 200ms opacity cross-fade to interactive desktop)
     ▼
[ Interactive Desktop ]
```

#### Key Technical Principles:
1. **Physical Transport vs. Metadata:**
   - The **EFI Framebuffer** (provided by UEFI GOP) is the physical display transport.
   - **ACPI BGRT** is strictly an ACPI table holding metadata (bitmap pointer and coordinate offsets) for the OEM logo. ACPI BGRT is **NOT** a physical framebuffer transport.
2. **KMS Modesetting Policy:**
   - Universal `ALLOW_MODESET=0` is **NOT** locked as a hard requirement across all hardware.
   - The binding principle is: *"Preserve existing scanout and avoid unnecessary modeset when compatible."*
   - Native KMS drivers may execute a full modeset if panel timings, eDP link training, or hardware requirements necessitate it. Atomic modesetting provides a deterministic, synchronized transition mechanism rather than an absolute promise that modesets will never occur.
3. **Fallback Path:** If native GPU KMS drivers fail to probe or crash, the system falls back seamlessly to the Linux SimpleDRM framebuffer or Mesa `llvmpipe` software rasterizer.

---

### 5.4 Comprehensive Failed Subsystem Matrix

| Failure ID | Failure Scenario | Detection Mechanism | Primary Response | Secondary Fallback | Diagnostic Path | User-Visible Result | Responsible Milestone Phase |
|---|---|---|---|---|---|---|---|
| **FM-01** | UEFI / GOP Display Init Error | Firmware POST / video BIOS error | Firmware falls back to basic VESA/VGA mode | Beep code / diagnostic LED pattern | Motherboard diagnostics | Black screen or basic low-res text mode | Firmware / Pre-OS |
| **FM-02** | Bootloader Configuration Missing / Corrupt | GRUB2 fails to read `grub.cfg` or BLS entries | GRUB drops to interactive prompt | Boot from fallback EFI boot entry | Serial console / GRUB terminal | GRUB recovery shell displayed | **Milestone P0** |
| **FM-03** | Early Kernel Panic / Driver Deadlock | Kernel panic handler / Oops | `panic=10` triggers automatic reboot after 10s | Hardware watchdog (60s) resets board | Serial console / kdump | Panic trace unblanks screen; system reboots | **Milestone P0** |
| **FM-04** | Initramfs Decompression / Scripts Failure | Dracut early init failure | Dracut halts execution | Unblanks console; drops to `rdshell` | `/run/initramfs/rdsosreport.txt` | Emergency rescue shell on TTY1 | **Milestone P0** |
| **FM-05** | Btrfs Root Mount Failure | Subvolume `@` missing or Btrfs error | Dracut timeout (30s) triggers emergency hook | Mounts read-only fallback snapshot if configured | Dracut log on TTY1 | Emergency maintenance shell on screen | **Milestone P0** |
| **FM-06** | systemd Critical Service Failure | `systemd-boot-check-no-failures.service` | Drops to `rescue.target` | Unblanks TTY1 for administrative login | `journalctl -b`, `/var/log/boot-failure.log` | Root login prompt with failure explanation | **Milestone P0** |
| **FM-07** | GPU KMS Driver Load Failure | DRM driver probe returns error code | System falls back to `simpledrm` | Falls back to Mesa `llvmpipe` software rasterizer | `dmesg \| grep -E 'drm\|kms'` | Desktop boots in safe 60Hz basic mode | **Milestone P1** |
| **FM-08** | NebuCompositor Crash on Startup | Process exits with non-zero status | `systemd` restart policy retries up to 5x | Drops to emergency diagnostic console on TTY2 | `journalctl -u nebu-compositor` | Screen switches to text console diagnostic | **Milestone P1** |
| **FM-09** | NebuShell Start Failure | Shell process fails to bind Wayland layer | Shell service auto-restarts | Compositor renders solid background + terminal shortcut | `journalctl -u nebu-shell` | Wallpaper visible with recovery dialog | **Milestone P2** |
| **FM-10** | Staged Deployment Boot Hang | System stalls before `desktop.target` | Hardware watchdog resets host after 60s | Boot counter decrements; boots previous deployment | Prior boot journal (`journalctl -b -1`) | Silent reboot into prior deployment | **Milestone P0** |
| **FM-11** | Health-Check Service Assertion Failure | `nebu-boot-check.service` timeout (45s) | Service issues `bootc rollback` and reboots | Drops to maintenance shell if rollback locked | `/var/log/nebu-boot-check.log` | Automatic reboot into prior deployment | **Milestone P0** |
| **FM-12** | Repeated Boot Failure (Counter Exhaustion) | GRUB detects `boot_counter <= 0` | Automatically selects Deployment 0 (Rollback) | Prompts user with interactive GRUB menu | `grubenv` inspection | Silent rollback boot into stable OS | **Milestone P0** |
| **FM-13** | Total Deployment Failure (No Known-Good Left) | Both primary and secondary deployments fail | System halts reboot loop; enters Emergency Mode | Unblanks TTY1; provides static manual repair prompt | Offline USB rescue media | High-visibility emergency recovery console | **Milestone P0** |

---

### 5.5 Canonical Boot Success & Deployment Health Criteria

NebuOS explicitly decouples low-level boot completion from graphical session readiness and transactional deployment health:

```
[ kernel booted ]
       │
       ▼
[ initramfs completed ]
       │
       ▼
[ root filesystem mounted (@) ]
       │
       ▼
[ systemd healthy (multi-user.target reached) ] ───>> [ MILESTONE P0: BOOT COMPLETED ]
       │
       ▼
[ critical system services healthy ]
       │
       ▼
[ graphical stack healthy (KMS probe successful) ]
       │
       ▼
[ NebuCompositor healthy (DRM Master acquired) ]
       │
       ▼
[ NebuShell healthy (layer surfaces active) ]
       │
       ▼
[ desktop / session ready (user input unblocked) ] ───>> [ MILESTONES P1/P2: SESSION READY ]
       │
       ▼
[ nebu-boot-check.service passes all assertions ]
       │
       ▼
[ DEPLOYMENT COMMITTED HEALTHY (boot_success=1) ] ───>> [ TRANSACTIONAL DEPLOYMENT HEALTHY ]
```

#### Decoupling Rules & Three Distinct States:
NebuOS explicitly differentiates between three operational states across milestone boundaries:
$$\text{P0 Boot Completed} \neq \text{P0 Deployment Healthy} \neq \text{P1/P2 Graphical Session Ready}$$

1. **P0 Boot Completed:** Reached when the kernel boots, Dracut completes pivot, and systemd reaches `multi-user.target`. Reaching `multi-user.target` does **NOT** automatically mean the deployment is healthy or ready to be committed!
2. **P0 Deployment Healthy (Deterministic Minimal Health Gate):** In Milestone P0, `nebu-boot-check.service` is a minimal, deterministic oneshot script/service (NOT a complex background daemon) with a strict timeout (e.g. 45s). It marks the deployment healthy **ONLY** after verifying the minimal deterministic health gate:
   - **PID 1 / systemd Health:** systemd operational state is `running` without deadlock.
   - **Root Filesystem Integrity:** Root filesystem is mounted properly with `/usr` read-only.
   - **Critical Mounts Available:** Essential paths (`/var`, `/var/home` or `/home`, `/boot`, `/proc`, `/sys`, `/dev`) are mounted with sufficient free space.
   - **Basic Networking Ready:** NetworkManager or loopback/interface carrier verified (if networking is in the baseline).
   - **Critical Headless Services Active:** Core headless services are active and running.
   - **Zero Critical Unit Failures:** `systemctl --failed` reports 0 failed critical units.
   - **Commit Execution:** Once assertions pass, writes `boot_success=1` and `boot_counter=0` to `grubenv`, and disarms the watchdog timer (if hardware or softdog watchdog is active and verified).
3. **P1/P2 Graphical Session Ready:** In milestones featuring graphical desktops (P1+), session readiness additionally asserts:
   - DRM scanout is driving the physical display without GPU reset events.
   - Smithay `nebu-compositor` has acquired DRM Master and bound `/run/user/$UID/wayland-0`.
   - `nebu-shell` layer-shell surfaces are presented, cross-fade is completed, and user input is unblocked.

> [!IMPORTANT]
> A successful kernel boot or reaching `multi-user.target` does **NOT** constitute a healthy deployment. If critical services fail or the compositor crashes post-boot, the deployment is marked **FAILED**, and rollback orchestration is triggered.

---

### 5.6 Boot Counter & Rollback State Machine

```
              [ New OS Deployment Staged ]
                           │
                           ▼
                 [ boot_counter = 3 ]
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
   [ Normal Startup ]           [ User Selects Menu ]
            │                             │
            ▼                             ▼
[ Decrement: counter = counter - 1 ]      │
            │                             │
            ├─────────────────────────────┘
            ▼
    [ Systemd Boot ]
            │
    ┌───────┴─────────────────────────────┐
    │ Crash / Watchdog Timeout?           │
    ├──────────────────┬──────────────────┤
    │ YES              │ NO               │
    ▼                  ▼                  ▼
[ Reboot ]    [ Health Check Pass? ]  [ counter <= 0? ]
    │                  │                  │
    │ (Loops back)     ├── YES            ├── YES: Trigger Automated Rollback
    │                  │   ▼              │   (Boots Deployment B)
    │                  │ [ Reset counter ]│
    │                  │ [ boot_success=1]└── NO: Try Next Boot Attempt
    ▼                  │ [ Commit Image ]
[ boot_counter ]       └──────────────────
```

#### State Machine & Rollback Ownership Invariants:
1. **Boot Counter is Orchestration Only:** `boot_counter` serves strictly as an orchestration mechanism for health verification and rollback triggering. NebuOS does **NOT** build a custom deployment engine, custom package manager, or custom update engine; deployment management and rollbacks rely natively on `bootc` and GRUB BLS bootloader capabilities.
2. **Staging Initialization:** When a new OS deployment is staged via the native `bootc` staging flow (following the actual CLI/API provided by `bootc` in Fedora 44, e.g. `bootc upgrade` staging), the update orchestration initializes `boot_counter=3` and `boot_success=0` in `grubenv`.
3. **Decrement on Boot:** The GRUB bootloader script decrements `boot_counter` by 1 before jumping to `vmlinuz`.
4. **Automated Rollback Trigger:** If `boot_counter <= 0` is reached without `boot_success=1`, GRUB automatically bypasses the staged deployment and boots the previous verified deployment (`deployment.0`) via standard BLS bootloader entries.
5. **Deterministic Health Check:** In P0, `nebu-boot-check.service` executes as a deterministic oneshot test within 45 seconds of boot completion. Upon passing all minimal health gate checks, it resets `boot_counter=0`, sets `boot_success=1`, and disarms the watchdog timer (if hardware watchdog is present and verified).
6. **Infinite Reboot Loop Prevention:** If repeated boot failures exhaust the counter and no prior verified rollback deployment exists (e.g. fresh installation or broken initial image), the system automatically halts auto-rebooting and drops to an interactive GRUB recovery menu (`systemd.unit=rescue.target`), ensuring a recovery path is always available.
7. **Zero GUI Dependency:** The entire rollback state machine executes inside GRUB2 and systemd, guaranteeing 100% headless operation in Milestone P0.

---

### 5.7 Recovery Architecture Hierarchy

When recovering from failures, NebuOS enforces a strict four-tier hierarchy:

1. **Tier 1: Primary Recovery (Automated Rollback):**  
   Reverts instantly to the previous known-good deployment using native `bootc` / GRUB BLS mechanisms. Completely preserves `/home`, `/var`, and user application data. Avoids custom logic duplicating native bootc functionality.
2. **Tier 2: Secondary Recovery (Emergency / Rescue Target):**  
   If rollback is unavailable or manual maintenance is chosen, systemd targets `rescue.target` or `emergency.target`, mounting root read-only and unblanking TTY1.
3. **Tier 3: Diagnostic Fallback (Unblanked Console):**  
   Triggered via the `Escape` key or Diagnostic BLS entry; provides live verbose kernel dmesg and systemd unit logs (`loglevel=7 console=tty1`).
4. **Tier 4: Hardware / Display Fallback (Firmware Framebuffer):**  
   If native GPU KMS drivers fail, the display pipeline drops gracefully to Linux SimpleDRM or basic EFI GOP framebuffer, avoiding screen freezes.

---

### 5.8 Phase Ownership Boundaries

| Milestone Phase | Primary Focus | In-Scope Responsibilities | Strict Anti-Scope ("DO NOT DO") |
|---|---|---|---|
| **Milestone P0** | Foundation OS | UEFI GOP handover, GRUB2 BLS entries (Normal & Diagnostic), silent kernel parameters (`quiet splash loglevel=3 ...`), Dracut initramfs without Plymouth (`omit_dracutmodules+=" plymouth "`), Btrfs root mount orchestration, systemd multi-user target, bootc rollback counter tracking, serial/TTY diagnostics. | **ZERO GUI, ZERO Plymouth, ZERO Wayland, ZERO Slint, ZERO compositor.** P0 is 100% headless. |
| **Milestone P1** | Compositor & Display | Linux DRM/KMS device probe, scanout plane inheritance from SimpleDRM, atomic modesetting handover without unnecessary modesets, Smithay-based `nebu-compositor` display server, Wayland protocol server. | **NO desktop shell widgets, NO application launchers, NO system tray menus in compositor.** |
| **Milestone P2** | Desktop Shell & Boot Splash | Graphical boot splash branding presentation, binding to `nebu-design-tokens`, 200ms smooth cross-fade from splash to `nebu-shell`, post-rollback recovery notification card in shell. | **NO secondary/competing design system, NO custom bootloader, NO blocking boot transitions.** |
| **Milestones P3+** | Runtime, Compat, Apps | Retain existing phase ownership; zero modifications to boot lifecycle or handoff ownership. | **NO boot ownership changes.** |

---

### 5.9 UI Design System Integration & Theme/Branding Boundary

NebuOS enforces a strict three-way conceptual separation:

```
+─────────────────────────────────────────────────────────────────────────────+
|                             SYSTEM BOUNDARIES                               |
+─────────────────────────────────────────────────────────────────────────────+
|  [ BOOT INFRASTRUCTURE ] (Milestone P0)                                     |
|  UEFI / GRUB2 BLS / Linux Kernel / Dracut / systemd                         |
|  - Headless, robust, resilient, silent parameters, rollback counters        |
+─────────────────────────────────────────────────────────────────────────────+
|  [ BOOT VISUAL PRESENTATION ] (Milestone P2)                                |
|  OEM Logo preservation, dark canvas (#0D1117), accent spinner (#388BFD)     |
|  - Consumes tokens from nebu-design-tokens; zero separate design system     |
+─────────────────────────────────────────────────────────────────────────────+
|  [ DESKTOP USER INTERFACE ] (Milestone P2)                                  |
|  NebuShell / Slint widgets / Taskbar / Dock / Settings / Launcher           |
|  - Interactive desktop surfaces; coordinates 200ms cross-fade               |
+─────────────────────────────────────────────────────────────────────────────+
```

- **Visual Tokens:** Canvas background binds to `Color.Background (#0D1117)`; progress elements bind to `Color.Accent (#388BFD)`; error states bind to `Color.StatusError (#F85149)`.
- **Reduced Motion Compliance:** If the user profile specifies `reduced_motion = true`, the 200ms cross-fade transition evaluates to `0ms` (instant cut).
- **Non-Blocking Rule:** Visual splash animations or transitions must **NEVER** delay desktop session readiness. The shell must present immediately when the compositor is ready.

---

### 5.10 Security & Trust Boundaries

```
[ UEFI Secure Boot: Microsoft CA / Fedora Shim ]
                     │ Cryptographic Signature
                     v
       [ GRUB2 BLS Bootloader (Signed) ]
                     │ Kernel & Initramfs Digest Verification
                     v
    [ Linux Kernel 6.14+ (Immutable Sysroot / dm-verity) ]
                     │ Dracut initramfs Integrity (Signed OSTree Tree)
                     v
         [ systemd PID 1 (sysroot) ]
                     │ Sandboxed IPC / Policy Restrictions
                     v
    [ NebuCompositor (UID 1000 / Privileged DRM Master) ]
                     │ Wayland Protocol Isolation
                     v
        [ NebuShell (Unprivileged Client) ]
```

1. **Information Leakage Prevention:** Silent boot suppresses kernel memory addresses, disk UUIDs, local IP leases, and MAC addresses from the display to protect against shoulder-surfing in public environments.
2. **Diagnostic Mode Security:** Console logs unblanked via `Escape` or Diagnostic Mode sanitize credentials and sensitive tokens.
3. **Boot Counter Tamper Resistance:** The `grubenv` file is stored on the unencrypted boot partition but writes are restricted to root during runtime; integrity is verified by the bootloader.
4. **Recovery Trust Boundary:** In production enterprise configurations, entering emergency rescue shells requires root password authentication.
5. **P0 Signing Separation:** Production cryptographic signing infrastructure (`cosign` / Sigstore) belongs to Milestone P8; Milestone P0 relies on upstream Fedora Secure Boot shim signatures without building a bespoke signing infrastructure.

---

### 5.11 Boot Performance Engineering Targets & Measurement Methodology

All duration figures are **Reference Engineering Targets**, not hard real-time guarantees, and do **NOT** constitute an automatic P0 failure gate before hardware benchmarks and empirical measurement methodologies are formally calibrated:

| Stage Range | Subsystem Description | Target Duration (NVMe SSD) | Target Duration (SATA SSD) | Measurement Source |
|---|---|---|---|---|
| **Stage 1–2** | Firmware & UEFI Initialization | < 1500 ms | < 2500 ms | ACPI FPDT (Firmware Performance Data Table) |
| **Stage 3** | GRUB2 BLS Parsing & Handover | < 250 ms | < 500 ms | `systemd-analyze` loader timestamp |
| **Stage 4–5** | Kernel Decompress & Dracut Initramfs | < 1300 ms | < 2200 ms | `systemd-analyze` kernel & initrd timestamps |
| **Stage 6** | systemd PID 1 to multi-user.target | < 900 ms | < 1500 ms | `systemd-analyze blame`, critical-chain |
| **Stage 7–8** | KMS Handover & NebuCompositor Start | < 450 ms | < 700 ms | Compositor internal timestamp to first commit |
| **Stage 9–10** | NebuShell Draw to Interactive Desktop | < 200 ms | < 400 ms | Layer-shell commit timestamp |
| **Total** | **Power-On to Interactive Desktop** | **< 4600 ms** | **< 7700 ms** | **End-to-End Stop-Watch / Frame Timing** |
| **P0 Baseline**| **QEMU Headless P0 to Login Prompt** | **<= 3500 ms** | **<= 3500 ms** | **systemd-analyze total / QEMU serial timestamp** |

> [!NOTE]
> **Performance Target Classification:**
> - NVMe $\le 4600\text{ ms}$ is a reference engineering target.
> - SATA $\le 7700\text{ ms}$ is a reference engineering target.
> - QEMU headless P0 $\le 3500\text{ ms}$ is an engineering target.
> 
> These metrics guide architectural sizing and design choices. They do NOT act as automatic failure gates in P0 automated tests until empirical hardware baselines are established across the target hardware matrix.

#### Measurement Methodology:
- **Reference Hardware Tiers:**
  - *Tier 1 (Budget / Minimal Baseline):* Intel Celeron N4020, 4GB RAM, SATA SSD (Crucial MX500).
  - *Tier 2 (Standard Performance):* Intel Core i5-1135G7, 8GB RAM, NVMe PCIe 3.0 SSD (Samsung 980).
- **Cold Boot vs. Warm Boot:** Benchmarks must report cold boots (full AC power cycle) separately from warm reboots.
- **Acceptable Variance:** $\pm 15\%$ variance is acceptable across runs due to DRAM training and SSD garbage collection.
- **Future Benchmark Phase:** Formal verification will be automated in the Compatibility Lab during Milestones P7 and P8.

---

## 6. Consequences and Trade-offs

### Positive Consequences
- **Consumer-Grade Polish:** Eliminates intimidating Linux text scrolls, matching macOS and Windows in visual elegance.
- **Milestone P0 Integrity:** Milestone P0 is rigorously preserved as a headless, verifiable base.
- **Display Continuity:** Avoids screen flickering and blanking by inheriting scanout planes properly.
- **Resilient Automated Recovery:** The 3-strike boot counter guarantees systems do not remain stuck in unbootable update states.
- **Unified Design Truth:** Eliminates visual drift by binding boot elements strictly to `nebu-design-tokens`.

### Negative Consequences / Trade-offs
- **Cross-Milestone Synchronization:** Boot experience requirements span P0 (silencing/rollback), P1 (DRM handoff), and P2 (visual splash).
- **Hardware Diversity:** Non-standard OEM panels may occasionally require modesetting; the architecture gracefully accepts this rather than asserting impossible zero-modeset guarantees.

---

## 7. Rejected Approaches

1. **Reject Embedding Slint in Dracut Initramfs:** Rejected due to excessive ramdisk size (>80MB) and high crash risk during early boot.
2. **Reject Disabling Kernel Logs Globally (`CONFIG_PRINTK=n`):** Rejected because it permanently blinds debugging; runtime silencing preserves full logs in `journalctl`.
3. **Reject Custom Bootloader:** Rejected because GRUB2 provides mature UEFI Secure Boot signing, BLS support, and upstream `bootc` compatibility.
4. **Reject Unbounded Reboot Loops:** Rejected; exactly 3 failed boot attempts strictly triggers automated rollback.
5. **Reject Locking Universal `ALLOW_MODESET=0`:** Rejected because some display hardware strictly requires a modeset; atomic modesetting is used without enforcing impossible universal invariants.

---

## 8. Risks and Mitigations

| Risk ID | Description | Severity | Mitigation Strategy | Owner Phase |
|---|---|---|---|---|
| **RSK-BOOT-01** | Display Modesetting Flicker During DRM/KMS Handover | MEDIUM | Preserve SimpleDRM scanout; bind atomic modesetting without unnecessary mode changes. | Milestone P1 |
| **RSK-BOOT-02** | Early Boot Silent Hang Obscuring Critical Diagnostic Information | HIGH | Emergency `Escape`/`F8` keypress unblanks screen immediately; dedicated Diagnostic BLS entry. | Milestone P0 |
| **RSK-BOOT-03** | Premature Splash Implementation in Headless Milestone P0 | HIGH | Section 24 in `AGENTS.md` strictly forbids GUI/Plymouth in P0; CI container linting blocks GUI packages. | Milestone P0 |
| **RSK-BOOT-04** | Boot Counter Corruption in `grubenv` Preventing Rollback | MEDIUM | Atomic writes to `grubenv`; interactive GRUB menu provides manual rollback fallback. | Milestone P0 |

---

## 9. Open Questions Resolution & Status

- **OQ-BOOT-01 (Plymouth vs. Native Splash in P2):** **RESOLVED.** Plymouth is omitted in P0 (`omit_dracutmodules+=" plymouth "`). In Milestone P2, Plymouth with a custom NebuTheme is evaluated as the baseline, with a native Rust splash daemon tracked as an optimization for Phase P8.
- **OQ-BOOT-02 (GRUB Menu Visibility):** **RESOLVED.** GRUB menu timeout is set to 0 by default for silent seamless boot; holding `Shift` or pressing `Escape` during firmware POST reveals the interactive GRUB menu.
- **OQ-BOOT-03 (Dynamic BGRT Geometry on Non-Standard Panels):** Open for implementation validation in Milestone P1 (tracked as `OQ-050`).
- **OQ-BOOT-04 (Diagnostic Boot Persistent Log Dump):** Open for implementation validation in Milestone P0 (tracked as `OQ-051`).

---

## 10. Related Specifications and Documents

- [docs/specification/01-boot-specification.md](../specification/01-boot-specification.md) — Technical Boot Specification
- [docs/desktop/01-nebucompositor-specification.md](../desktop/01-nebucompositor-specification.md) — NebuCompositor Specification
- [docs/desktop/02-nebushell-specification.md](../desktop/02-nebushell-specification.md) — NebuShell Specification
- [docs/design/00-design-system.md](../design/00-design-system.md) — Master Design System Specification
- [docs/updates/04-rollback-recovery.md](../updates/04-rollback-recovery.md) — Rollback & Recovery Specification
- [AGENTS.md](../../AGENTS.md) — Universal Agent Governance Contract
- [PROJECT_STATE.md](../../PROJECT_STATE.md) — Master Project State Snapshot
