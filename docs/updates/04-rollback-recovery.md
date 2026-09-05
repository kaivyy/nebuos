# Rollback and Recovery Specification — NebuOS

**Status:** APPROVED ARCHITECTURAL SPECIFICATION  
**Document ID:** NEBU-SPEC-ROL-001  
**Authority:** Principal OS Architect, bootc/Ostree Engineer, Security Architect  
**Purpose:** Specify the automated failure detection, boot-counter fallback, manual recovery triggers, filesystem rollback semantics, failure classification, and data preservation invariants for NebuOS.  

---

## 1. Status and Invariants

- **Status:** APPROVED — Mandatory resilience architecture across Milestones P0 through P8.
- **Architectural Invariants:**
  1. **Unconditional Survivability:** An operating system update must never leave a machine unbootable. If a newly booted image panics, deadlocks, or fails health checks, the host must fall back to the prior known-working deployment automatically without requiring user intervention.
  2. **Strict User Data Preservation:** Operating system rollbacks operate strictly on system binaries (`/usr`) and vendor configurations (`/etc`). Rollback **never** modifies, deletes, or reverts user documents in `/home`, system databases in `/var`, or application prefixes in `@nebu_apps`.
  3. **No Phantom Rollbacks:** Automated rollback is not assumed to occur through magic; it is governed by deterministic, verifiable mechanisms: the GRUB Boot Loader Specification (BLS) boot attempt counter, the hardware watchdog timer (`/dev/watchdog`), and `nebu-boot-check.service`.
  4. **Retention Floor:** The storage subsystem must preserve at least one verified, bootable rollback deployment at all times, protected from automatic garbage collection.

---

## 2. Rollback Architecture Overview

The rollback mechanism integrates the hardware watchdog, GRUB2 bootloader, OSTree sysroot, and systemd userspace:

```mermaid
graph TD
    subgraph Bootloader[GRUB2 Bootloader & grubenv]
        BLS[BLS Config: Default = deployment.1]
        COUNTER[grubenv: boot_counter=3]
        FALLBACK_ENTRY[Fallback Target: deployment.0]
    end

    subgraph KernelSpace[Kernel Initialization & Watchdog]
        KERNEL[Linux Kernel Boots]
        WDOG[Hardware / Softdog Watchdog Armed: 60s]
    end

    subgraph Userspace[systemd Userspace & Health Check]
        PID1[systemd PID 1 Reaches Target]
        CHECK[nebu-boot-check.service]
    end

    BLS -->|Boot Attempt| KERNEL
    COUNTER -->|Decrement Counter| KERNEL
    KERNEL --> WDOG
    KERNEL --> PID1
    PID1 --> CHECK

    alt Health Check Passes
        CHECK -->|Success: Disarm Watchdog| WDOG
        CHECK -->|Commit: boot_counter=0| COUNTER
    else Crash / Freeze / Health Check Timeout
        WDOG -.->|Hardware Reset on 60s Timeout| Bootloader
        FALLBACK_ENTRY -->|Counter == 0: Boot Fallback| KERNEL
    end
```

---

## 3. Automated Failure Detection & Boot Counting

### 3.1 The Boot Counting Sequence
1. **Pre-Boot Staging & Boot Counter Ownership:** When an update is staged via the native `bootc` staging flow (following the actual CLI/API provided by `bootc` in Fedora 44, e.g. `bootc upgrade` staging without custom package/deployment engines), the update orchestration writes `boot_counter=3` and `boot_success=0` into `/boot/grub2/grubenv`. The `boot_counter` is an orchestration mechanism; deployment storage and rollback remain 100% native to `bootc` and the bootloader.
2. **First Boot Attempt:**
   - GRUB loads, detects a staged deployment, reads `boot_counter=3`, decrements it to `boot_counter=2`, and writes the value back to `grubenv`.
   - GRUB passes execution to the newly staged kernel.
3. **Watchdog Arming (When Hardware/Softdog Verified):**
   - If a hardware watchdog (`/dev/watchdog`) or `softdog` driver is present and verified on the target platform, it is armed with a hardware timeout of 60 seconds.
   - If the kernel panics, the storage bus deadlocks, or userspace hangs before PID 1 completes initialization, the watchdog expires and forces a hardware reboot.
4. **Subsequent Boot Attempts (If Crashed):**
   - GRUB reads `boot_counter=2` (or `boot_counter=1`), decrements it, and attempts to boot again.
5. **Counter Exhaustion & Automated Rollback:**
   - If the system fails repeatedly, GRUB detects `boot_counter=0` with `boot_success=0`.
   - **Rollback Deployment Available:** GRUB overrides the default entry, skips the failed deployment, and automatically boots `deployment.0` (the previous verified working deployment) via standard BLS boot entries. The host arrives cleanly at the desktop session in reference engineering target < 15 seconds.
   - **No Known-Good Deployment Available (Edge Case / Fresh Install):** To prevent an infinite boot-reboot loop, GRUB stops auto-rebooting, clears timeout, and presents an interactive recovery menu displaying entry `NebuOS Recovery Mode (systemd.unit=rescue.target)` along with an on-screen diagnostic notice, ensuring a recovery path is always accessible.

### 3.2 Health Check Disarm & Commit (`nebu-boot-check.service`)
Health verification is strictly decoupled between operating system milestones:
$$\text{P0 Boot Completed} \neq \text{P0 Deployment Healthy} \neq \text{P1/P2 Graphical Session Ready}$$

- **Milestone P0 (Headless Foundation):** `nebu-boot-check.service` is a minimal, deterministic oneshot service (`Type=oneshot`, `TimeoutSec=45`, NOT a complex daemon). It executes after `multi-user.target` and asserts the minimal deterministic health gate:
  1. PID 1 / systemd is operational (`systemctl is-system-running` is `running` or `degraded` without critical service loss).
  2. Root filesystem is correctly mounted with `/usr` strictly read-only.
  3. Critical filesystem mounts are active (`/var`, `/var/home` or `/home`, `/boot`, `/proc`, `/sys`, `/dev`) with adequate free space.
  4. Basic networking is ready (NetworkManager active or link carrier verified, if networking is part of P0 baseline).
  5. Core headless baseline services are active.
  6. Zero critical systemd units have failed (`systemctl --failed` reports 0 failed critical units).
  7. Upon assertion pass: writes `boot_counter=0` and `boot_success=1` to `grubenv`, and disarms `/dev/watchdog` (if verified and active).
- **Milestone P1+ (Graphical Desktop):** `nebu-boot-check.service` executes after `graphical.target`. It additionally asserts that `nebu-compositor` has successfully acquired DRM master, rendered the initial desktop frame, and established Wayland IPC socket readiness.

```ini
# /usr/lib/systemd/system/nebu-boot-check.service
[Unit]
Description=NebuOS Post-Update Health Verification
DefaultDependencies=no
After=multi-user.target
Before=graphical.target

[Service]
Type=oneshot
ExecStart=/usr/libexec/nebu/nebu-boot-check
RemainAfterExit=yes
TimeoutSec=45

[Install]
WantedBy=multi-user.target
```

When `/usr/libexec/nebu/nebu-boot-check` confirms system health:
1. Writes `boot_counter=0` and `boot_success=1` to `grubenv`.
2. Closes the watchdog file descriptor with the magic character `'V'` (if hardware/softdog watchdog is active) to safely disarm the watchdog timer.
3. Broadcasts D-Bus signal `org.nebu.Update1.UpdateCommitted` (in milestones with D-Bus update daemon active).

---

## 4. Manual Rollback Triggers

In addition to automated watchdog recovery, users and administrators have full manual rollback control:

### 4.1 Interactive Bootloader Recovery
If a user experiences an issue not caught by automated health checks (e.g. specific application glitches):
1. During boot, press `ESC` or `Shift` to display the GRUB boot menu.
2. Select the secondary BLS entry: `NebuOS (Previous Deployment - Rollback)`.
3. System boots instantly into the previous working deployment.

### 4.2 CLI Rollback Command
From a running desktop session or root terminal:
```bash
# Query rollback availability:
nebu rollback status

# Execute immediate rollback:
nebu rollback --reboot
```
Under the hood, `NebuUpdateService` executes `bootc rollback`, which swaps the primary and secondary bootloader entries in the sysroot, and initiates a clean reboot.

### 4.3 Post-Rollback User Notification Experience (ADR-0014)
When the system reboots into a previous deployment due to automated boot counter exhaustion or manual recovery:
1. **Silent Fallback Boot:** The bootloader and kernel execute silently under Recovery/Rollback boot mode (`loglevel=3 quiet splash`).
2. **Desktop Session Initialization:** Once `nebu-compositor` and `nebu-shell` reach interactive desktop readiness, the system queries rollback status via `nebu rollback status` / D-Bus.
3. **Rollback Notification Card:** `nebu-shell` presents an informative, non-modal notification banner styled strictly via `nebu-design-tokens` (`Color.Warning / Accent`):
   > **System Update Rolled Back**  
   > NebuOS could not complete startup with the latest update. Your previous working version has been safely restored. All personal files, apps, and settings remain completely intact.  
   > `[ View Diagnostics ]` `[ Dismiss ]`
4. **Actionable Diagnostics:** Clicking "View Diagnostics" displays a sanitised excerpt from `/var/log/nebu-boot-check.log` and `/var/log/journal`, offering an option to submit an anonymous diagnostic report to the release engineering portal.

---

## 5. Filesystem Semantics & Rollback Safety

A major source of user anxiety is misunderstanding what an operating system rollback affects. NebuOS documentation explicitly dispels the myth that "rollback restores the entire computer to an earlier date":

```
+-----------------------------------------------------------------------------------+
| WHAT ROLLBACK RESTORES (SYSTEM LAYER)                                             |
| - Reverts all OS binaries, libraries, kernel modules in /usr                     |
| - Reverts vendor configuration templates in /etc                                  |
| - Restores previous bootloader kernel arguments and initramfs                     |
+-----------------------------------------------------------------------------------+
                                        ≠
+-----------------------------------------------------------------------------------+
| WHAT ROLLBACK PRESERVES UNTOUCHED (USER & STATE LAYER)                            |
| - Personal documents, desktop files, downloads in /home (NEVER touched)          |
| - Browser history, bookmarks, and user application configurations                 |
| - System logs, Flatpak runtimes, container images in /var                         |
| - Windows application prefixes, saves, and registry data in @nebu_apps            |
+-----------------------------------------------------------------------------------+
```

### 5.1 Deep Semantics Across Subvolumes
1. **`/usr` (Read-Only Image Tree):** Completely replaced by the previous deployment's image tree. Bit-for-bit identical to the prior state.
2. **`/etc` (OSTree 3-Way Merge):**
   - Reverts configuration files to the snapshot taken when the previous deployment was active.
   - Any local configuration files created by the administrator while booted into the broken deployment are preserved in `/etc` with an `.ostree-save` extension, preventing accidental data loss.
3. **`/var` (Shared Persistent State):**
   - `/var` is physically mounted from the `@var` Btrfs subvolume and shared across all deployments.
   - Rollback **does not** revert `/var`. System logs (`/var/log/journal`) remain accessible, allowing engineers to analyze why the new deployment failed!
4. **`/home` (User Personal Space):**
   - `/home` is physically mounted from the `@home` Btrfs subvolume.
   - Upgrades and rollbacks **never execute any write, delete, or revert operations** on `/home`.

---

## 6. Failure Classification & Recovery Matrix

NebuOS formalizes 10 discrete failure classes that can occur during the update lifecycle:

| Failure Class | Root Cause | Detection Mechanism | User-Visible Status in UI | Automated Recovery Action | Log Location |
|---|---|---|---|---|---|
| **F-01: Network Interruption** | Wi-Fi drop or timeout during layer pull | HTTP 5xx / TCP reset in `bootc` | "Download paused. Reconnecting..." | Automatically resumes layer transfer using HTTP range requests; active system untouched. | `journalctl -u nebu-update` |
| **F-02: Registry Outage** | Remote registry 503 / DNS resolution failure | DNS / TLS handshake timeout | "Update server temporarily unavailable." | Backs off exponentially (15m, 1h, 4h); leaves active system running. | `journalctl -u nebu-update` |
| **F-03: Signature Failure** | Image digest tampered or signature invalid | Cosign Ed25519 verification returns non-zero | "Security verification failed. Update blocked." | Operation aborted immediately; downloaded layers purged; security alert logged. | `/var/log/nebu-security.log` |
| **F-04: Disk Space Low** | Free space on `/sysroot` < 2.5 GB | Pre-staging disk space probe | "Insufficient disk space for update." | Staging blocked before write; triggers `bootc prune`; prompts user to clean disk. | `journalctl -u nebu-update` |
| **F-05: Staging Write Error** | I/O error or Btrfs filesystem corruption | `bootc` exit code non-zero | "Failed to stage update. Storage error." | Staging tree cleaned up; active system continues running undisturbed. | `dmesg`, `journalctl -k` |
| **F-06: Boot Panic** | Broken kernel module / ACPI deadlock | Watchdog timeout (60s) triggers hardware reset | Black screen during reboot (transient) | Watchdog resets machine; GRUB boot counter decrements; boots previous deployment. | `/var/log/journal` (Prior boot) |
| **F-07: Display Hang** | DRM/KMS failure or GPU driver crash | `nebu-boot-check` fails DRM scanout assertion | Display freeze / black screen | Watchdog expires; boots previous deployment; displays "Restored prior version" notification. | `/var/log/nebu-boot-check.log` |
| **F-08: Service Loop** | Core systemd service crashes continuously | `systemctl --failed` returns non-empty in check | Long boot splash screen | Health check fails; triggers reboot; boots previous deployment. | `journalctl -b -1` |
| **F-09: Health Timeout** | System fails to reach target within 45s | Systemd unit timer expires | Splash screen reaches timeout | Service invokes `bootc rollback` and triggers immediate reboot into fallback. | `/var/log/nebu-boot-check.log` |
| **F-10: Power Loss During Update** | Battery dies while downloading or staging | System suddenly powers off | Power turns off | Transactional nature of OSTree guarantees that incomplete deployment is ignored on reboot. | `dmesg` |

---

## 7. Storage Management, Quotas, & Retention Policy

Maintaining two parallel bootable deployments requires disciplined disk capacity rules:

```
+-------------------------------------------------------------------------+
|                    DEPLOYMENT RETENTION TOPOLOGY                        |
+-------------------------------------------------------------------------+
|                                                                         |
|  [DEPLOYMENT 1: Active System]    ─── Immutable Read-Only Rootfs        |
|                                                                         |
|  [DEPLOYMENT 0: Rollback System]  ─── Prior Working Deployment          |
|                                       (Protected from automatic prune)  |
|                                                                         |
|  [OPTIONAL: Pinned Deployment]    ─── Admin-pinned deployment           |
|                                       via: bootc pin <id>               |
|                                                                         |
|  [HISTORICAL DEPLOYMENTS]         ─── Automatically pruned via:         |
|                                       bootc prune                       |
|                                                                         |
+-------------------------------------------------------------------------+
```

### 7.1 Free Space Policy & Thresholds
- **Optimal Headroom:** >= 5.0 GB free space on `/sysroot`.
- **Soft Warning Threshold (5.0 GB to 3.5 GB):** NebuShell Settings notifies user that storage is getting low.
- **Hard Blocking Threshold (< 2.5 GB):** `NebuUpdateService` strictly refuses to stage new deployments until the user frees space.
- **Extent Sharing Benefit:** Because NebuOS uses Btrfs, the previous deployment shares identical data extents with the new deployment. Dual deployments consume only **500 MB to 1.5 GB of delta disk space**, not the full 3.2 GB image size.

---

## 8. Power Safety Invariants

- **Staging Power Gate:** `NebuUpdateService` will not pull container layers if battery charge is < 25% on an un-plugged laptop.
- **Reboot Power Gate:** If the user initiates "Restart Now" with a staged update, but the laptop battery is < 40% and AC power is disconnected, NebuShell presents a mandatory warning dialog:
  > *"Warning: Battery level is below 40%. Please connect your charger before applying the update to prevent unexpected shutdown during startup."*

---

## 9. Related Specifications
- [00-update-specification.md](00-update-specification.md) — Master update specification.
- [01-image-build.md](01-image-build.md) — Containerfile specification and build pipeline.
- [02-release-channels.md](02-release-channels.md) — Release channels and versioning.
- [03-regression-gates.md](03-regression-gates.md) — Automated regression gates.
- [../decisions/ADR-0011-os-image-updates-and-rollback.md](../decisions/ADR-0011-os-image-updates-and-rollback.md) — Binding architectural decision record.
- [../decisions/ADR-0014-boot-experience-and-graphical-handoff.md](../decisions/ADR-0014-boot-experience-and-graphical-handoff.md) — Boot experience and graphical handoff.
