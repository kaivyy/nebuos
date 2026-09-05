import os

BASE_DIR = "/root/NebuOS"

def write_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created/Updated: {rel_path} ({len(content)} bytes)")

# ==============================================================================
# ADR-0010: Hardware Compatibility, Laptop-First Platform, & Power Architecture
# ==============================================================================
adr_0010 = """# ADR-0010: Real-World Hardware Compatibility, Laptop-First Validation, and Power Management Architecture

**Status:** APPROVED  
**Date:** 2026-09-04  
**Authors:** Principal OS Architect, Linux Hardware Compatibility Engineer, Power Management Engineer  
**Deciders:** NebuOS Core Architecture Group  
**Supercedes:** None  
**Related ADRs:** ADR-0001 (Linux Kernel Base), ADR-0003 (Smithay Wayland), ADR-0005 (Wine Integration), ADR-0009 (NebuShell Architecture)  

---

## 1. Context and Problem Statement

NebuOS aims to be a lightweight, rock-solid desktop operating system capable of running native Linux and Windows applications without a virtual machine. However, software compatibility is meaningless if the operating system fails to reliably initialize hardware, drain laptop batteries excessively during sleep, crash on external display hotplugging, stutter during hybrid graphics offloading, or fail to wake from suspend.

Real-world personal computing hardware is intensely fragmented across:
1. **Diverse CPU Architectures & Topologies:** Intel hybrid P/E-core architectures (Alder Lake, Raptor Lake, Meteor Lake), AMD Zen chiplets (Zen 3/4/5), asymmetric thread scheduling, thermal throttling, and frequency scaling.
2. **GPU & Display Topologies:** Intel iGPUs, AMD Radeon GPUs, NVIDIA GeForce/RTX GPUs, hybrid graphics (PRIME offload), mixed-DPI multi-monitors, high refresh rate panels, USB-C DisplayPort Alternate Mode, and Thunderbolt docks.
3. **Power Management & ACPI:** Modern Standby (ACPI S0ix / `s2idle`) vs traditional S3 suspend-to-RAM (`deep`), aggressive battery optimization, charging thresholds, and thermal regulation.
4. **Input & Peripherals:** Precision touchpads, multi-touch gestures, touchscreens, active styluses, audio routing over PipeWire/WirePlumber, Wi-Fi 5/6/6E/7, and Bluetooth LE audio.

Previous architectural documentation treated hardware primarily through the narrow lens of GPU enumeration for Wine/Proton. NebuOS requires an authoritative architectural framework governing how hardware is abstracted, how power states are preserved, how laptops are validated, and how hardware diagnostics are presented to users.

---

## 2. Decision Drivers

- **Laptop-First Reality:** Over 70% of modern desktop Linux installations run on laptops. A desktop OS that cannot sleep properly or drains 20% battery overnight will be immediately abandoned.
- **Deterministic Suspend/Resume:** Windows applications running under Wine/Proton maintain complex graphical and threading states. Suspend and resume must freeze and restore these processes without memory corruption or Xwayland crashes.
- **Hardware Abstraction Decoupling:** The desktop shell (`nebu-shell`) and user-facing applications must NEVER interact directly with raw kernel device nodes or require root privileges to adjust display brightness, toggle Wi-Fi, or switch power profiles.
- **Privacy-Preserving Compatibility:** Hardware detection and fingerprinting must be performed locally using SQLite to configure quirks and driver parameters without transmitting invasive user telemetry.
- **Anti-Overpromising Engineering:** NebuOS must explicitly disclaim "100% hardware compatibility" and instead adopt formal, testable Hardware Certification Tiers (H0 through H5).

---

## 3. Considered Alternatives

### Option A: Direct Hardware Coupling in Shell (Monolithic Model)
- Let `nebu-shell` execute raw system commands (`rfkill`, `xrandr`/wlr-randr, `brightnessctl`, direct `/sys` writes).
- *Rejected:* Violates privilege separation, creates security vulnerabilities, and couples the UI toolkit directly to platform quirks.

### Option B: Rely Entirely on Upstream Distro Defaults without Platform Policy
- Accept default Fedora/upstream power and suspend policies without dedicated hardware qualification or Wine process freezing.
- *Rejected:* Causes high S0ix sleep drain, broken resume in Wine/Proton gaming sessions, and silent display failures on hybrid GPU laptops.

### Option C: Layered Hardware Abstraction with Laptop Compatibility Program (CHOSEN)
- Enforce strict hierarchical abstraction: `Hardware` -> `Linux Kernel` -> `Standard System Services` -> `Nebu System D-Bus APIs` -> `NebuCompositor / NebuShell`.
- Implement a dedicated **NebuOS Laptop Compatibility Program** with rigorous, multi-iteration suspend/resume test gates.
- Support dynamic ACPI sleep mode selection (`s2idle` vs `deep`) with automatic firmware quirk detection.
- Integrate hardware profiles into the central SQLite compatibility database (`compat.db`).

---

## 4. Decision Outcome

### Chosen Solution: Option C (Layered Hardware Abstraction with Laptop-First Compatibility Program)

NebuOS formally adopts a six-tier hardware abstraction hierarchy, a dual-pillar compatibility framework, and an explicit power management architecture.

### 4.1 Strict Layered Hardware Abstraction

```
+-------------------------------------------------------------------------------+
|                      NebuShell (Slint UI / System Settings)                   |
+-------------------------------------------------------------------------------+
                                       |
                   D-Bus IPC (org.freedesktop.*, org.nebu.*)
                                       v
+-------------------------------------------------------------------------------+
|                        Nebu System Hardware APIs / Daemons                    |
|             (power-profiles-daemon, upowerd, geoclue, nebu-hw-probe)          |
+-------------------------------------------------------------------------------+
                                       |
                   Standard System Services & Display Compositor
                                       v
+-------------------------------------------------------------------------------+
|       NebuCompositor       |    NetworkManager    |    PipeWire / WirePlumber |
|  (Wayland, DRM/KMS, Mesa)  |   (Wi-Fi, Eth, VPN)  |   (Audio, BT, Cam Portal) |
+-------------------------------------------------------------------------------+
                                       |
                            Linux Subsystems & Drivers
                                       v
+-------------------------------------------------------------------------------+
|    DRM / KMS    |    cfg80211 / nl80211    |    ALSA / HDA    |    libinput   |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                                Linux Kernel 6.x                               |
|              (ACPI Subsystem, S0ix/S3 Sleep Engine, cgroups v2)               |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                               Physical Hardware                               |
|         (Intel/AMD/NVIDIA, Displays, USB-C/Thunderbolt Docks, Battery)        |
+-------------------------------------------------------------------------------+
```

### 4.2 Modern Standby (S0ix) and ACPI S3 Strategy
1. **Dynamic Detection:** The system probes `/sys/power/mem_sleep`. On platforms supporting Low Power S0 Idle (`s2idle`), NebuOS defaults to `s2idle` while validating SoC low-power states via the Linux kernel `intel_pmc_core` / `amd_pmc` drivers.
2. **Fallback to Deep S3:** If a platform experiences unmitigated S0ix battery drain (> 2.5% per hour in sleep) due to broken OEM ACPI tables, NebuOS provides an automatic or user-selectable fallback to `deep` S3.
3. **Deterministic Wine Freeze Hook:** Prior to system sleep, `systemd-sleep` triggers `/usr/lib/systemd/system-sleep/nebu-wine-freeze.sh`, utilizing cgroups v2 `cgroup.freeze` to halt all Wine/Proton threads before GPU context power-down, preventing driver deadlocks on resume.

### 4.3 Desktop Environment Reference Integration
NebuOS explicitly audits and incorporates proven design patterns from established Linux desktop environments without adopting them as runtime dependencies:
- **From GNOME:** UPower integration, `power-profiles-daemon` D-Bus integration, Mutter's fractional scaling architecture, and PipeWire camera portal sandboxing.
- **From KDE Plasma:** Advanced KScreen multi-monitor layout persistence, per-output refresh rate and VRR (Variable Refresh Rate / Adaptive Sync) configuration, and detailed battery health management (charge limits).
- **From Sway / wlroots:** High-efficiency, zero-overhead Wayland damage tracking, direct DRM scanout optimization, and lightweight input gesture configuration via `libinput`.
- **From Budgie:** Modular applet architecture and clean panel/dock isolation.

### 4.4 Dual-Pillar Compatibility Program
The NebuOS Compatibility Program is officially bifurcated into two mutually supportive pillars:
```
NebuOS Compatibility Program
  |
  +-- Pillar 1: Hardware Compatibility Program
  |     +-- CPU Topology & Thermal Management
  |     +-- Hybrid Graphics (PRIME Offload & dGPU D3cold)
  |     +-- Display & Mixed-DPI Multi-Monitor
  |     +-- Power & S0ix/S3 Suspend/Resume
  |     +-- Network (Wi-Fi 5/6/6E/7, Bluetooth LE Audio)
  |     +-- Audio Routing (PipeWire/WirePlumber)
  |     +-- Peripherals, Docking, & USB-C DP Alt Mode
  |
  +-- Pillar 2: Application Compatibility Program
        +-- Linux Native Applications (Flatpak / OCI)
        +-- Windows Productivity Applications (Wine 9.x Staging)
        +-- Windows High-End 3D Gaming (Valve Proton / DXVK / VKD3D)
        +-- Declarative Patch Engine & Community Profiles
```

### 4.5 Hardware Certification Tiers (H0 through H5)
NebuOS establishes formal, verifiable tiers of hardware compliance:
- **Tier H0 (Boot Compatibility):** Kernel boots to TTY console via UEFI; basic storage and input functional.
- **Tier H1 (Basic Hardware Functionality):** DRM display output operational; keyboard, mouse, and wired Ethernet functional.
- **Tier H2 (Desktop Hardware Functionality):** Hardware-accelerated Wayland compositor active; audio playback, Wi-Fi, and precision touchpad gestures functional.
- **Tier H3 (Power Management):** S0ix / S3 sleep and resume pass 10 consecutive cycles with zero system hangs; battery state and thermal controls active.
- **Tier H4 (Advanced Hardware Features):** Hybrid GPU offload, multi-monitor mixed-DPI hotplugging, USB-C docking stations, Bluetooth LE, and webcam operational.
- **Tier H5 (Production Certified):** System passes 50 consecutive suspend/resume cycles, overnight sleep (< 1.5% battery drain/hour), long idle, thermal stress testing, and receives official certification.

---

## 5. Consequences

### Positive Consequences
- Guarantees that laptops running NebuOS achieve competitive battery life and instant-on resume reliability.
- Shields high-level desktop UI code from low-level Linux kernel and hardware driver complexities.
- Establishes reproducible hardware testing criteria for the QA Hardware Lab (Milestone P7).
- Prevents game and workstation application crashes during laptop lid open/close transitions.

### Negative / Trade-Off Consequences
- Requires developing and maintaining hardware probe tools (`nebu-hw-probe`) and sleep hooks.
- Demands extensive physical hardware testing across Intel, AMD, and NVIDIA laptop platforms in the Compatibility Lab.
- Requires handling edge-case firmware bugs in OEM ACPI tables.

---

## 6. Traceability and Mapping

- **PRD Section 4:** Hardware Targets (x86_64, UEFI, 4GB RAM minimum, GPU tiers) -> Satisfied.
- **PRD Section 6:** Desktop Experience -> Satisfied via power profiles and multi-monitor management.
- **Roadmap:** Milestone P0 (Base Bootability), Milestone P1 (Display/Input), Milestone P2 (Power/Desktop Integration), Milestone P5 (Hybrid Graphics), Milestone P7 (Hardware Compatibility Lab).
"""

write_file("docs/decisions/ADR-0010-hardware-compatibility-and-power-management.md", adr_0010)
