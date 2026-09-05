import os

BASE_DIR = "/root/NebuOS"

def write_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Hardened: {rel_path} ({len(content)} bytes)")

# ==============================================================================
# 1. HARDEN ADR-0010
# ==============================================================================
adr_0010_hardened = """# ADR-0010: Real-World Hardware Compatibility, Laptop-First Platform, and Power Management Architecture

**Status:** APPROVED (Hardened)  
**Date:** 2026-09-04  
**Authors:** Principal OS Architect, Linux Hardware Compatibility Engineer, Power Management Engineer  
**Deciders:** NebuOS Core Architecture Group  
**Supercedes:** None  
**Related ADRs:** ADR-0001 (Linux Kernel Base), ADR-0003 (Smithay Wayland), ADR-0005 (Wine Integration), ADR-0009 (NebuShell Architecture)  

---

## 1. Context and Problem Statement

NebuOS aims to be a lightweight, rock-solid desktop operating system capable of running native Linux and Windows applications without a virtual machine. However, software translation layers (Wine/Proton/DXVK) are useless if the underlying operating system fails to reliably initialize hardware, drains laptop batteries excessively during sleep, crashes on external display hotplugging, stutters during hybrid graphics offloading, or fails to wake from sleep.

Real-world personal computing hardware is intensely fragmented across:
1. **CPU Architectures & Hybrid Topologies:** Intel hybrid P/E-core architectures (Alder Lake through Arrow Lake), AMD Zen chiplets (Zen 3 through Zen 5), asymmetric thread scheduling, thermal regulation, and dynamic frequency scaling.
2. **GPU & Display Topologies:** Intel integrated graphics (i915 vs xe), AMD Radeon GPUs, NVIDIA GeForce/RTX GPUs, hybrid graphics (PRIME offload), mixed-DPI multi-monitors, high refresh rate panels, USB-C DisplayPort Alternate Mode, and Thunderbolt docks.
3. **Power Management & ACPI:** Modern Standby (ACPI S0ix / `s2idle`) versus traditional S3 suspend-to-RAM (`deep`), aggressive device runtime power management (Runtime PM), charging thresholds, and thermal regulation.
4. **Input & Peripherals:** Precision touchpads, multi-touch gestures, touchscreens, active styluses, audio routing over PipeWire/WirePlumber, Wi-Fi 5/6/6E/7, and Bluetooth LE Audio.

Previous documentation contained overly absolute statements (e.g. universal "0W" in D3cold, universal S3 fallback, universal 80% charge limits, universal 4096 pen pressure). This hardened ADR establishes realistic, evidence-driven architectural boundaries for hardware abstraction, power state management, laptop testing, and diagnostics.

---

## 2. Decision Drivers

- **Laptop-First Reality:** Over 70% of modern client Linux installations run on laptops. A desktop operating system that cannot sleep reliably or drains battery excessively will fail in the marketplace.
- **Feasible Hardware Abstraction:** The desktop shell (`nebu-shell`) and user applications must NEVER interact directly with raw kernel device nodes, require root privileges, or execute privileged sysfs writes.
- **Realistic Power States:** D3cold and ACPI sleep states are **platform- and capability-dependent**. NebuOS must probe capabilities and handle hardware where deep sleep or S3 is unavailable.
- **Deterministic Wine Process Preservation:** Windows applications running under Wine/Proton maintain complex graphical and threading states. Suspend and resume must freeze and restore these processes via cgroups v2 without memory corruption or Xwayland crashes.
- **Privacy-Preserving Local Matching:** Hardware detection and fingerprinting must be performed locally using SQLite to configure quirks and driver parameters without transmitting telemetry.
- **Honest Engineering Terminology:** NebuOS explicitly rejects "universal compatibility" claims. The system defines verifiable Hardware Certification Tiers (H0 through H5).

---

## 3. Considered Alternatives

### Option A: Monolithic Hardware Coupling in Shell
- Let `nebu-shell` execute raw system commands (`rfkill`, `xrandr`/wlr-randr, `brightnessctl`, direct `/sys` writes).
- *Rejected:* Violates privilege separation, creates security vulnerabilities, and couples the UI toolkit directly to platform quirks.

### Option B: Rely Entirely on Upstream Distro Defaults without Platform Policy
- Accept default Fedora/upstream power and suspend policies without dedicated hardware qualification or Wine process freezing.
- *Rejected:* Causes high S0ix sleep drain, broken resume in Wine/Proton gaming sessions, and silent display failures on hybrid GPU laptops.

### Option C: Layered Hardware Abstraction with Laptop Compatibility Program (CHOSEN & HARDENED)
- Enforce strict hierarchical abstraction: `Hardware` -> `Linux Kernel` -> `Standard System Services` -> `Nebu System D-Bus APIs` -> `NebuCompositor / NebuShell`.
- Implement a dedicated **NebuOS Laptop Compatibility Program** with rigorous, multi-iteration suspend/resume test gates.
- Support dynamic ACPI sleep mode selection (`s2idle` vs `deep`) with capability detection and OEM firmware quirk handling.
- Integrate hardware profiles into the central SQLite compatibility database (`compat.db`).

---

## 4. Decision Outcome

### Chosen Solution: Option C (Layered Hardware Abstraction with Laptop-First Compatibility Program)

### 4.1 Strict Layered Hardware Abstraction

```
+-------------------------------------------------------------------------------+
|                      NebuShell (Slint UI / System Settings)                   |
+-------------------------------------------------------------------------------+
                                       |
                   Standard User Session D-Bus (org.freedesktop.*)
                                       v
+-------------------------------------------------------------------------------+
|                    Nebu System Hardware APIs / Daemons                        |
|       (power-profiles-daemon, upowerd, geoclue, nebu-hw-probe, udisks2)       |
+-------------------------------------------------------------------------------+
                                       |
                   System Bus / Session Compositor IPC Protocol
                                       v
+-------------------------------------------------------------------------------+
|       NebuCompositor       |    NetworkManager    |    PipeWire / WirePlumber |
|  (Wayland, DRM/KMS, Mesa)  |   (Wi-Fi, Eth, VPN)  |   (Audio, BT, Cam Portal) |
+-------------------------------------------------------------------------------+
                                       |
                   Kernel System Call / ioctl / nl80211 Interface
                                       v
+-------------------------------------------------------------------------------+
|    DRM / KMS    |    cfg80211 / nl80211    |    ALSA / HDA    |    libinput   |
|   ACPI Subsystem|    cgroups v2 Freezer    |    v4l2 / Media  |    Btrfs/crypto|
+-------------------------------------------------------------------------------+
                                       |
                            Device Drivers & Module Binding
                                       v
+-------------------------------------------------------------------------------+
|   i915 / xe     |      amdgpu          |   nouveau / nvidia  |  iwlwifi/ath11k|
|                               Linux Firmware Blobs                            |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                               Physical Hardware                               |
|        (x86_64 CPUs, GPUs, Panels, Touchpads, Batteries, USB-C/TB Docks)      |
+-------------------------------------------------------------------------------+
```

### 4.2 Power Management & Realistic Sleep State Policy

1. **ACPI Sleep State Capability Enumeration:**
   - The system probes `/sys/power/mem_sleep` to determine platform-supported states (`s2idle`, `deep`).
   - On modern platforms supporting Low Power S0 Idle (`s2idle`), NebuOS defaults to `s2idle` while tracking SoC low-power states via `intel_pmc_core` / `amd_pmc`.
   - **Non-Universal S3 Clarification:** On modern laptops (Intel Tiger Lake+, Meteor Lake, AMD Phoenix/Hawk Point), OEM ACPI tables frequently omit S3 support entirely. **NebuOS does NOT assume S3 is universally available.** If S3 (`deep`) is missing, fallback to `deep` is disabled; the system instead utilizes SoC PMC debugging to identify uncooperative PCIe/USB devices blocking sleep, or offers user-initiated hibernation.
   - If both `s2idle` and `deep` are supported and `s2idle` exhibits excessive battery drain, NebuOS permits configuration of `mem_sleep_default=deep`.

2. **Standardized Sleep Drain Benchmarking:**
   - **Engineering Target:** Sleep power draw $\le 750\text{ mW}$ ($\le 1.5\%$ battery drain per hour on a standardized 50Wh battery at 100% health, Wi-Fi associated and idle, no external peripherals).
   - **Warning Threshold:** Drain $> 1200\text{ mW}$ ($> 2.0\%$/hr on 50Wh battery) triggers a diagnostic notification in NebuShell.
   - **Failure Threshold:** Drain $> 1800\text{ mW}$ ($> 3.0\%$/hr on 50Wh battery) blocks H5 Production Certification.

3. **Hybrid Graphics & D3cold Realism:**
   - The integrated GPU (iGPU) drives compositor scanout.
   - The discrete GPU (dGPU) is requested to enter its deepest supported runtime power state (runtime `D3cold` or `D3hot`).
   - **Technical Reality:** Achieving D3cold depends on platform ACPI `_PR3` power resource support, PCIe root port capabilities, active render/compute contexts, and display wiring. If an external display is physically wired to the dGPU (common on gaming laptops), the dGPU cannot enter D3cold while the display is connected. **NebuOS does not claim universal "0W" GPU powerdown.**

4. **Deterministic Wine Process Freeze:**
   - Prior to system sleep, `systemd-sleep` triggers `/usr/lib/systemd/system-sleep/nebu-wine-freeze.sh`.
   - All Wine/Proton threads inside `app-nebu-*.scope` are frozen via cgroups v2 (`cgroup.freeze = 1`) before display and GPU context powerdown, preventing driver deadlocks upon resume.

### 4.3 Desktop Environment Reference Audit

NebuOS explicitly audits reference desktop environments for design patterns while maintaining zero runtime dependencies on their desktop stacks:

| Desktop Environment | Inspired By / Design Pattern Reused | Upstream Components Reused | Not Used / Rejected | Architectural Rationale |
|---|---|---|---|---|
| **GNOME** | Seamless `power-profiles-daemon` integration, UPower battery daemon, PipeWire camera portal sandboxing, fractional scaling viewport downsampling. | `power-profiles-daemon`, `upowerd`, `xdg-desktop-portal`. | GNOME Shell, Mutter, JavaScript extension engine, GDM. | Extensions create memory leaks and instability; NebuOS mandates a Rust-native compositor (`nebu-compositor`). |
| **KDE Plasma** | KScreen multi-monitor layout persistence, per-output VRR settings, battery charge limit controls. | Multi-monitor config schema concepts and sysfs charge limit patterns. | KWin, KDE Plasma desktop, Qt/KConfig frameworks, SDDM. | High memory footprint violates the NebuOS low-resource invariant (< 450 MB desktop RAM). |
| **Sway / wlroots** | Lightweight damage tracking, direct DRM scanout optimization, zero-overhead input gesture dispatch. | Wayland protocol idioms and `libinput` configuration logic. | Sway window manager, wlroots library, manual tiling model. | NebuOS uses Smithay (Rust) and targets mainstream users requiring a floating, intuitive desktop. |
| **Budgie** | Modular panel and applet architecture, clean separation of status tray from notifications. | Desktop applet lifecycle patterns. | Budgie Desktop, legacy GNOME/GTK3 stack libraries. | NebuOS uses a unified Slint/Rust UI shell (ADR-0009). |

### 4.4 Hardware Certification Tiers (H0 through H5)

1. **Tier H0 (Boot Compatibility):** Kernel boots to TTY console via 64-bit UEFI; storage and serial/virtual TTY functional. (Milestone P0).
2. **Tier H1 (Basic Hardware Functionality):** DRM display output operational; keyboard, mouse, wired Ethernet functional. (Milestone P0/P1).
3. **Tier H2 (Desktop Hardware Functionality):** Hardware-accelerated Wayland active; audio playback, Wi-Fi, and precision touchpad gestures functional. (Milestone P1/P2).
4. **Tier H3 (Power Management Validated):** 10 consecutive sleep/wake cycles pass; lid close/open transitions verified; battery health active; idle power within target. (Milestone P2).
5. **Tier H4 (Advanced Hardware Features):** Hybrid GPU offload, multi-monitor mixed-DPI hotplug, USB-C docks, Bluetooth LE Audio active. (Milestone P5).
6. **Tier H5 (Production Certified):** 50 consecutive sleep/wake cycles pass; overnight sleep drain within threshold; long thermal stress verified; HCL entry published. (Milestone P7/P8).

---

## 5. Consequences

### Positive Consequences
- Guarantees realistic, attainable hardware standards without overpromising universal compatibility.
- Decouples high-level desktop UI code from low-level Linux kernel and hardware driver complexities.
- Establishes reproducible hardware testing criteria for the QA Hardware Lab (Milestone P7).
- Prevents game and workstation application crashes during laptop sleep/wake transitions.

### Negative / Trade-Off Consequences
- Requires ongoing maintenance of hardware probe tools (`nebu-hw-probe`) and quirk databases.
- Demands testing across diverse physical hardware in the Compatibility Lab (Milestone P7).
- Acknowledges that certain hardware configurations (e.g. broken OEM ACPI tables) will require documented limitations rather than magic software fixes.

---

## 6. Traceability and Mapping

- **PRD Section 4:** Hardware Targets (x86_64, UEFI, 4GB RAM minimum, GPU tiers) -> Satisfied.
- **PRD Section 6:** Desktop Operating Experience -> Satisfied via power profiles and multi-monitor management.
- **Milestones:** P0 (Base Bootability), P1 (Display/Input), P2 (Power/Desktop Integration), P3 (Wine Freeze), P5 (Hybrid Graphics), P7 (Hardware Compatibility Lab).
"""

write_file("docs/decisions/ADR-0010-hardware-compatibility-and-power-management.md", adr_0010_hardened)
