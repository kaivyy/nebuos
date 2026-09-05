import os

target_file = "/root/NebuOS/docs/testing/07-hardware-testing.md"

content = """# Hardware Testing Specification & Certification Lab — NebuOS

**Document ID:** NEBU-TEST-0007  
**Status:** APPROVED  
**Author:** Principal QA Architect, Linux Hardware Compatibility Engineer, Systems Test Lead  
**Target Version:** 1.0 (Milestones P0–P8)  
**Last Updated:** 2026-09-04  
**Governing Documents:** NEBU-SPEC-0005 (Hardware Specification), ADR-0010 (Hardware & Power Architecture)  

---

## 1. Status

APPROVED. This specification defines the hardware testing architecture, bare-metal QA laboratory requirements, automated Hardware Compatibility List (HCL) generation, the **NebuOS Laptop Compatibility Program**, and the **H0–H5 Certification Pipeline**.

---

## 2. Purpose

To ensure that NebuOS achieves rock-solid real-world reliability on diverse desktop and laptop hardware, this document establishes:
1. The formal **Hardware Certification Tiers (H0 through H5)**.
2. The complete **Laptop-First Validation Pipeline** verifying critical mobile hardware subsystems.
3. The **Quantitative Suspend/Resume Stress Testing Suite** (single cycle, 10x iteration, 50x endurance, 8-hour overnight drain).
4. Physical hardware test lab topologies across 17 real-world computing classes.
5. The **Known Problem Classification Matrix** for rapid root-cause isolation across system layers.
6. Automated HCL database synchronization with `/usr/share/nebu/compat.db`.

---

## 3. Scope

This specification applies to:
- Physical bare-metal hardware testing in the NebuOS Hardware Compatibility Lab (Milestone P7).
- Virtualized and automated QEMU/KVM base hardware verification in Milestone P0.
- Laptop power management, Modern Standby (ACPI S0ix / `s2idle`), and traditional S3 (`deep`) validation.
- Peripheral hotplugging, multi-monitor display outputs, USB-C/Thunderbolt docking stations, and PipeWire audio stream handoff.

---

## 4. Non-Goals

- Testing non-x86_64 CPU architectures in the 1.0 release cycle.
- Physical destructive stress testing (chassis drops, connector cycle endurance).
- Testing legacy non-UEFI BIOS machines (64-bit UEFI firmware is strictly mandatory).
- Virtual machine hypervisor testing for Windows applications (strictly prohibited by master PRD).

---

## 5. Requirements

### 5.1 Functional Requirements

| Identifier | Description | Verification Method | Milestone |
|---|---|---|---|
| **REQ-TEST-HW-001** | The qualification tool `nebu-hw-probe` must inspect DMI/SMBIOS, sysfs, PCI, and USB buses to generate structured manifests. | Automated JSON schema test | P0 |
| **REQ-TEST-HW-002** | The test lab must support automated remote provisioning via IPMI/Redfish power cycling and PXE network booting. | Remote provisioning run | P7 |
| **REQ-TEST-HW-003** | Test nodes must execute automated S0ix and S3 sleep cycles with resume verification and battery drain measurement. | `tests/system/suspend_stress.sh` | P2 |
| **REQ-TEST-HW-004** | Display testing must validate multi-monitor mixed-DPI hotplugging and audio stream handoff over HDMI/DP via PipeWire. | Event and audio stream capture | P1 |
| **REQ-TEST-HW-005** | Touchpad testing must validate multi-touch gestures, palm rejection, and pointer acceleration curves via `libinput`. | Automated gesture input replay | P1 |
| **REQ-TEST-HW-006** | Hardware test outcomes must automatically update the central compatibility database with verified device IDs and quirk entries. | SQLite transaction verification | P4 |

### 5.2 Non-Functional Performance & Reliability Requirements

| Identifier | Target Threshold | Rationale |
|---|---|---|
| **NFR-TEST-HW-001** | Suspend-to-resume cycle validation must restore network and display outputs in $\le 1.2\text{ s}$. | Instant-on user expectation. |
| **NFR-TEST-HW-002** | Overnight sleep (8 hours) battery drain rate must not exceed $1.5\%$ per hour in S0ix ($0.8\%$ in S3). | Prevents laptop battery depletion. |
| **NFR-TEST-HW-003** | Endurance 50x suspend/resume loop must achieve $100\%$ success rate without kernel panic or session crash. | Enterprise reliability SLA. |
| **NFR-TEST-HW-004** | Cold bare-metal provisioning (PXE boot to bootc ostree deployment) must complete in $< 4\text{ minutes}$. | High-throughput QA lab automation. |

---

## 6. Architecture: Dual-Pillar Compatibility Program

NebuOS organizes all compatibility engineering into two distinct, parallel pillars under the master **NebuOS Compatibility Program**:

```
+-------------------------------------------------------------------------------+
|                         NebuOS Compatibility Program                          |
+-------------------------------------------------------------------------------+
                       |                                 |
                       v                                 v
+------------------------------------+   +------------------------------------+
|  Pillar 1: Hardware Compatibility  |   | Pillar 2: Application Compatibility|
+------------------------------------+   +------------------------------------+
| * CPU Hybrid P/E Core Scheduling   |   | * Linux Native Flatpak Apps        |
| * GPU & Hybrid PRIME Offloading    |   | * Windows Productivity (Wine 9.x)  |
| * Display Mixed-DPI & Hotplugging  |   | * Windows 3D Gaming (Valve Proton) |
| * Power Management (S0ix / S3)     |   | * DXVK (D3D9/10/11) & VKD3D-Proton |
| * Wi-Fi 5/6/7 & Bluetooth LE Audio |   | * SQLite Profile Database          |
| * Audio Stream Routing (PipeWire)  |   | * Declarative 9-Tier Patch Engine  |
| * USB-C / Thunderbolt Docking      |   | * Automated Application Test Matrix|
| * Hardware Test Lab (Milestone P7) |   | * Compatibility Lab (Milestone P7) |
+------------------------------------+   +------------------------------------+
```

---

## 7. Hardware Certification Tiers (H0 through H5)

Hardware platforms evaluated by the lab are classified into six rigorous certification tiers:

```
[ Tier H0: Boot Compatibility ]
  - Criteria: System boots to TTY console via 64-bit UEFI.
  - Verified: Linux Kernel 6.x, dracut initramfs, NVMe/SATA storage, serial/virtual TTY.
  - Target Milestone: P0 Foundation.

[ Tier H1: Basic Hardware Functionality ]
  - Criteria: Basic display scanout, keyboard, mouse, and wired Ethernet operational.
  - Verified: DRM/KMS basic driver, USB HID input, standard PCI network.
  - Target Milestone: P0/P1.

[ Tier H2: Desktop Hardware Functionality ]
  - Criteria: Hardware-accelerated Wayland desktop active with audio and wireless connectivity.
  - Verified: Mesa 3D driver, Smithay Wayland compositor, PipeWire audio playback, Wi-Fi association, precision touchpad gestures.
  - Target Milestone: P1/P2.

[ Tier H3: Power Management Validated ]
  - Criteria: System handles power transitions, sleep, wake, and thermal regulation safely.
  - Verified: 10x consecutive S0ix/S3 sleep cycles pass; lid open/close transitions verified; battery health and charge thresholds active; active idle power <= 4.5W.
  - Target Milestone: P2.

[ Tier H4: Advanced Hardware Features ]
  - Criteria: Complex graphics and docking peripherals fully integrated.
  - Verified: Hybrid GPU dynamic PRIME offloading, USB-C/Thunderbolt multi-monitor docking, mixed-DPI fractional scaling, Bluetooth LE Audio, webcam streaming.
  - Target Milestone: P5.

[ Tier H5: Production Certified ]
  - Criteria: Comprehensive qualification across the entire Laptop Compatibility Program.
  - Verified: 50x sleep/wake cycles pass; 8-hour overnight sleep battery drain < 1.5%/hr; long thermal stress verified; zero kernel warnings; official HCL entry published.
  - Target Milestone: P7 / P8.
```

---

## 8. NebuOS Laptop Compatibility Program

Laptops undergo an exhaustive 16-step sequential validation pipeline:

```mermaid
flowchart TD
    S1[1. UEFI Cold Boot < 3.5s] --> S2[2. GPU & Panel Modesetting]
    S2 --> S3[3. Wi-Fi Association & Speed Test]
    S3 --> S4[4. Bluetooth Pairing & LE Audio]
    S4 --> S5[5. PipeWire Audio Speaker/Mic Switch]
    S5 --> S6[6. Touchpad Multi-Touch & Palm Rejection]
    S6 --> S7[7. Keyboard Function & Brightness Keys]
    S7 --> S8[8. Webcam Capture & Privacy Shutter]
    S8 --> S9[9. Panel Backlight PWM 0%-100%]
    S9 --> S10[10. Battery Health & 80% Charge Limit]
    S10 --> S11[11. S0ix / S3 Sleep Transition < 250ms]
    S11 --> S12[12. System Resume to Interactive < 1.2s]
    S12 --> S13[13. Lid Close Clamshell & Open Resume]
    S13 --> S14[14. USB-C Dock & Dual Monitor Hotplug]
    S14 --> S15[15. 50x Repeated Sleep/Wake Loop]
    S15 --> S16[16. 8-Hour Overnight Sleep Drain < 1.5%/hr]
```

---

## 9. Suspend/Resume Validation Test Suite

Automated scripts in `tests/system/` execute standardized power transition tests:

### 9.1 Test Cases

| Test ID | Test Scenario | Execution Method | Pass Criteria |
|---|---|---|---|
| **TC-SR-001** | Single Sleep/Wake Cycle | `rtcwake -m mem -s 10` | Resume to interactive desktop $< 1.2\text{ s}$; display, Wi-Fi, audio restore. |
| **TC-SR-002** | 10x Sleep/Wake Loop | `tests/system/suspend_loop.sh 10` | 10/10 passes; zero kernel panics or driver deadlocks. |
| **TC-SR-003** | 50x Endurance Loop | `tests/system/suspend_loop.sh 50` | 50/50 passes; Wine gaming session thawed cleanly. |
| **TC-SR-004** | Overnight Battery Drain | 8-hour sleep on battery | Battery drain $< 1.5\%/\text{hr}$ (S0ix) or $< 0.8\%/\text{hr}$ (S3). |
| **TC-SR-005** | Docked Multi-Monitor Sleep | Suspend with dual displays on USB-C dock | Both monitors wake cleanly; window layouts preserved. |
| **TC-SR-006** | Peripheral Active Sleep | Suspend with Bluetooth audio and USB mouse | Bluetooth reconnects automatically; mouse operational instantly. |

---

## 10. Real-World Hardware Test Matrix (17 Hardware Classes)

The physical Hardware Test Lab maintains dedicated bare-metal nodes covering:
1. **Mainstream Desktop:** Intel Core i5-12400 / AMD Ryzen 5 5600 + Radeon RX 6600.
2. **Office Laptop:** Lenovo ThinkPad T14 Gen 4 (AMD Ryzen 7 PRO 7840U / Radeon 780M).
3. **Ultrabook:** Dell XPS 13 Plus (Intel Core i7-1360P / Iris Xe).
4. **Gaming Laptop:** ASUS ROG Zephyrus G14 (AMD Ryzen 9 + NVIDIA GeForce RTX 4060).
5. **Creator Laptop:** HP Envy 16 (Intel Core i9 + OLED 4K Touch + RTX 4070).
6. **Workstation:** Lenovo ThinkStation P620 (AMD Threadripper PRO 5955WX + RTX A4000).
7. **Mini PC:** Minisforum UM780 XTX (AMD Ryzen 7 7840HS).
8. **Low-End Baseline (Older PC):** Intel Celeron N4020 / AMD Athlon 3000G, 4 GB RAM, SATA SSD.
9. **Modern PC:** Intel Core Ultra 7 155H (Meteor Lake with NPU).
10. **AMD Pure Platform:** Framework Laptop 16 (Ryzen 7 7840HS + Radeon RX 7700S).
11. **Intel Pure Platform:** Intel NUC 12 Enthusiast (Core i7-12700H + Intel Arc A770M).
12. **NVIDIA Optimus Laptop:** Lenovo Legion 5 (Intel CPU + RTX 3070).
13. **Multi-Monitor Workstation:** 3x displays (4K 60Hz + 1440p 144Hz + 1080p).
14. **Touchscreen Convertible (2-in-1):** Lenovo Yoga 7i (Intel Core i7 + 360 hinge + Pen).
15. **USB-C Docking Node:** Dell WD22TB4 Thunderbolt 4 Dock setup.
16. **Legacy Wi-Fi/Audio Node:** Older Realtek RTL8723DE Wi-Fi and Conexant CX20724 audio.
17. **Modern Wi-Fi 7 Platform:** Intel BE200 Wi-Fi 7 + Bluetooth 5.4.

---

## 11. Known Problem Classification Matrix

When hardware defects or regressions occur, the lab classifies issues into explicit categories to direct resolution to the correct team:

| Classification | Responsible Layer | Resolution Action |
|---|---|---|
| **KERNEL ISSUE** | Linux Upstream Kernel | Report to kernel bugzilla; pin working kernel release. |
| **DRIVER ISSUE** | Proprietary Driver Stack | Apply driver parameter workarounds in `/etc/modprobe.d/`. |
| **FIRMWARE ISSUE** | OEM Vendor / `fwupd` | Notify user to upgrade BIOS via LVFS; apply ACPI DSDT override. |
| **ACPI ISSUE** | Kernel ACPI Subsystem | Switch between `s2idle` and `deep` via `mem_sleep_default`. |
| **MESA ISSUE** | Mesa Userspace Drivers | Report to freedesktop GitLab; pin stable Mesa build. |
| **COMPOSITOR ISSUE**| `nebu-compositor` | Fix Wayland output management or DRM scanout bug in Rust code. |
| **SYSTEM SERVICE** | NetworkManager / PipeWire | Adjust WirePlumber routing script or NetworkManager configuration. |
| **NebuShell ISSUE** | `nebu-shell` | Fix UI widget or D-Bus proxy call in Slint/Rust code. |
| **APPLICATION ISSUE**| User Application | Isolate in Wine prefix profile or Flatpak permission manifest. |
| **HARDWARE DEFECT** | Physical Hardware | Retire defective node; replace memory or peripheral cable. |
| **UPSTREAM LIMIT** | Linux Platform Architecture | Document known limitation in release notes and HCL. |

---

## 12. Diagnostics & Telemetry (`nebu-hw-probe`)

The automated diagnostic probe `nebu-hw-probe` generates complete hardware telemetry:
```bash
nebu-hw-probe --format=json --output=/run/nebu/hardware_topology.json
```
- Inspects PCI, USB, DMI, CPUID, sysfs, and ACPI tables.
- Cryptographically hashes device combinations to match local SQLite profiles.
- Zero external network transmission; privacy is mathematically guaranteed.

---

## 13. Related Documents

- [05-hardware-specification.md](../specification/05-hardware-specification.md)
- [00-system-specification.md](../specification/00-system-specification.md)
- [../decisions/ADR-0010-hardware-compatibility-and-power-management.md](../decisions/ADR-0010-hardware-compatibility-and-power-management.md)
- [../compatibility/01-database-schema.md](../compatibility/01-database-schema.md)
- [../roadmap/08-p7-compatibility-lab.md](../roadmap/08-p7-compatibility-lab.md)
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content.strip() + "\n")
print(f"Updated {target_file} with comprehensive hardware testing specification ({len(content)} bytes)")
