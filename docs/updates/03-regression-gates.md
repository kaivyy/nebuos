# Regression Gates and Release Promotion Specification — NebuOS

**Status:** APPROVED ARCHITECTURAL SPECIFICATION  
**Document ID:** NEBU-SPEC-GAT-001  
**Authority:** QA / Compatibility Lab Lead, OS Update/Release Engineer, Principal OS Architect  
**Purpose:** Specify the automated quality gates, subsystem update policies (Kernel, Mesa, Wine), hardware lab matrices, and promotion barriers required before any OS image enters the Stable channel.  

---

## 1. Status and Invariants

- **Status:** APPROVED — Mandatory release qualification standard across Milestones P0 through P8.
- **Architectural Invariants:**
  1. **Zero Unqualified Stable Deployments:** No OS image or compatibility database update may be tagged or promoted to the `stable` channel without passing 100% of mandatory blocking gates.
  2. **Release-Gate vs. Per-Device Invariant:** Hardware certification and compatibility test suites are executed **exclusively in the centralized NebuOS Compatibility Lab** as a release qualification gate. Individual user devices never execute heavy compatibility benchmarks as a prerequisite for applying an update.
  3. **Decoupled Subsystem Policies:** Specific regression suites govern Kernel, Mesa, and Wine updates independently to prevent silent component regressions.
  4. **Automated Enforcement:** Quality gates are implemented as automated CI/CD pipeline assertions; manual human sign-off exists solely as a secondary audit barrier.

---

## 2. Multi-Tiered Gating Pipeline Architecture

Promotion from an unverified container build to the production `stable` channel requires sequential traversal through five discrete quality gates:

```mermaid
graph TD
    subgraph Pipeline[Automated Gating Sequence]
        CANDIDATE[Release Candidate Digest: sha256:...]
        GATE1[Gate 1: Static Code, Lint & CVE Security Scan]
        GATE2[Gate 2: Headless Virtual Boot & P0 Core Tests]
        GATE3[Gate 3: Subsystem Policies (Kernel, Mesa, Wine)]
        GATE4[Gate 4: Hardware Compatibility Lab Matrix]
        GATE5[Gate 5: Performance SLAs & Architecture Sign-off]
    end

    subgraph Outcome[Release Outcome]
        STABLE_TAG[Promote to Stable Channel]
        REJECT[Block Promotion & Open P0 Blocker Bug]
    end

    CANDIDATE --> GATE1
    GATE1 -->|Pass| GATE2
    GATE2 -->|Pass| GATE3
    GATE3 -->|Pass| GATE4
    GATE4 -->|Pass| GATE5
    GATE5 -->|Approved| STABLE_TAG

    GATE1 -->|Fail| REJECT
    GATE2 -->|Fail| REJECT
    GATE3 -->|Fail| REJECT
    GATE4 -->|Fail| REJECT
    GATE5 -->|Fail| REJECT
```

---

## 3. Gate Definitions and Acceptance Thresholds

### 3.1 Gate 1: Static Analysis & Supply Chain Security
- **Execution Environment:** GitHub Actions / GitLab CI cloud runners.
- **Test Suites:**
  * `cargo clippy --workspace --all-targets -- -D warnings`: Zero warnings permitted.
  * `cargo audit`: Zero unmitigated High or Critical advisories in Rust crates.
  * `trivy image --severity HIGH,CRITICAL quay.io/nebu-ci/base:rc`: Zero Critical CVEs; all High CVEs must have documented risk acceptances.
  * `bootc container lint`: Asserts standard container structure, systemd integration, and absence of mutable `/usr` hooks.
- **Blocking Threshold:** 100% Pass. Any failure halts the pipeline immediately.

### 3.2 Gate 2: Headless Virtual Boot & P0 Verification
- **Execution Environment:** Headless QEMU/KVM virtual machine with OVMF UEFI firmware.
- **Test Suites:**
  * Automated installation test: `bootc install to-disk /dev/vda`.
  * Clean boot assertion: Reaches `multi-user.target` in <= 5.0 seconds.
  * Systemd health check: `systemctl --failed` reports 0 failed units.
  * Btrfs subvolume layout verification: Confirms `@`, `@home`, `@var`, and `@nebu_apps` mounted with correct flags (`compress=zstd:1`).
  * Transactional upgrade test: Invokes `bootc upgrade`, boots new deployment, and validates successful pivot.
- **Blocking Threshold:** 100% Pass.

### 3.3 Gate 3: Subsystem-Specific Update Policies
Subsystems with tight system integration must pass dedicated regression test suites:

#### A. Kernel Update Policy (PRD §75)
Every new Linux kernel version or minor patch must pass automated tests verifying:
- **Core Boot & Storage:** NVMe APST, SATA AHCI, Btrfs filesystem integrity, zram swap compression.
- **I/O & Peripherals:** USB 2.0/3.x/4 host controllers, Thunderbolt 3/4 bus discovery.
- **Graphics Core:** DRM/KMS modesetting initialization, page-flipping, buffer allocation.
- **Networking:** Wi-Fi link association, Ethernet GbE/2.5GbE negotiation, Bluetooth HCI interface.
- **Audio:** ALSA audio card registration, SOF DSP firmware loading.
- **Power Lifecycle:** 25x consecutive S0ix suspend/resume stress cycles with zero driver hangs or resume kernel panics.

#### B. Mesa & Graphics Update Policy (PRD §74)
Every Mesa driver update must be tested across Intel, AMD, and NVIDIA hardware:
- **Vulkan & OpenGL:** Vulkan conformance test suites (VK-GL-CTS subset).
- **Translation Layers:** DXVK 2.x and VKD3D-Proton regression suites.
- **CAD & Productivity:** Wireframe rendering and 3D viewports in Autodesk AutoCAD 2024 and Dassault SolidWorks (eDrawings).
- **Gaming Benchmarks:** Stable frame pacing, zero shader compiler crashes, and zero rendering artifacts in designated benchmark titles.

#### C. Wine & Runtime Update Policy (PRD §73)
Wine/Proton staging updates must execute the 11-stage compatibility test invariant:
$$\text{INSTALL} \rightarrow \text{LAUNCH} \rightarrow \text{OPEN} \rightarrow \text{EDIT} \rightarrow \text{SAVE} \rightarrow \text{EXPORT} \rightarrow \text{PRINT} \rightarrow \text{GPU} \rightarrow \text{PLUGIN} \rightarrow \text{STRESS} \rightarrow \text{CLOSE}$$
- **Tier 1 Certified Suites:** Microsoft Office 2024 (Word, Excel, PowerPoint), AutoCAD 2024, Adobe Photoshop 2023, Notepad++.
- **Pass Threshold:** 100% functional pass rate across Tier 1 applications. Any regression in saving, printing, or GPU acceleration blocks the release.

### 3.4 Gate 4: Hardware Compatibility Lab Matrix
- **Execution Environment:** Bare-metal physical test rigs in the dedicated Compatibility Lab.
- **Hardware Coverage Matrix:**
  1. *Tier H1 (Budget Laptop):* Intel Celeron N4020 / N100, 4GB RAM, Intel UHD Graphics, eMMC/SATA SSD.
  2. *Tier H2 (Mainstream Ultrabook):* Intel Core i5 (12th/13th Gen), 16GB RAM, Iris Xe, NVMe SSD, Wi-Fi 6 AX201.
  3. *Tier H3 (AMD Mobile Workstation):* AMD Ryzen 7 7840U / 8840HS, 32GB RAM, Radeon 780M, Wi-Fi 6E MT7922.
  4. *Tier H4 (Discrete Gaming Desktop):* AMD Ryzen 5 7600X + NVIDIA GeForce RTX 4070 (Proprietary Driver Layer).
  5. *Tier H5 (Enterprise Docked Setup):* Lenovo ThinkPad T14 connected to Thunderbolt 4 Dual-4K Dock.
- **Test Scenarios:** Full suspend/resume, clamshell lid-close, multi-monitor mixed-DPI display hotplug, touchpad precision gestures, and audio jack detection.

### 3.5 Gate 5: Performance SLAs & Executive Sign-off
- **Idle Memory Budget:** System RAM at idle desktop <= 800 MB on 4GB hardware baseline (Milestone P2+).
- **Cold Boot Timing:** Power-on to interactive login screen <= 8.0 seconds on NVMe reference hardware.
- **Application Launch Latency:** Warm start for certified productivity apps <= 1.5 seconds.
- **Human Sign-off:** Release Engineer and Lead Systems Architect verify that all risks in `RISK_REGISTER.md` are accounted for and no open P0 blocker bugs remain.

---

## 4. Decoupled Subsystem Update Lifecycle

To prevent monolithic release bottlenecks, updates across different system layers operate on decoupled schedules:

| Subsystem Layer | Update Vehicle | Promotion Cadence | Gating Requirement |
|---|---|---|---|
| **Base OS Image** | `bootc upgrade` | Monthly / As Needed | Gates 1 through 5 (Full Pipeline) |
| **Linux Apps** | Flatpak | Continuous | Application developer CI + Flathub automated checks |
| **Windows Runtime** | `nebu-runtime` runners | Bi-weekly / Monthly | Gate 3C (Wine Suite) + Gate 4 (App Matrix) |
| **Compatibility DB** | Signed SQLite drop-in | Weekly / On-Demand | Gate 3C (Non-destructive DDL and query validation) |
| **Hardware Firmware** | `fwupd` / LVFS | OEM Dependent | LVFS cryptographic signature + Device Power Gating |

---

## 5. Failure Handling and Triage Protocol

If a release candidate fails any gate:
1. **Automated Halt:** The CI pipeline cancels remaining stages and prevents image promotion.
2. **Blocker Issue Creation:** An automated issue labeled `release-blocker` is filed in the repository with:
   - Offending commit SHA and container digest.
   - Exact failure logs, hardware rig ID, and crash dump / systemd journal extract.
   - Designated subsystem owner (Kernel, Graphics, Runtime, or Infrastructure Lead).
3. **Remediation:** The failure is resolved on `main`, generating a new release candidate digest (`v1.0.1-rc2`) which must re-run the entire gating pipeline from Gate 1.

---

## 6. Related Specifications
- [00-update-specification.md](00-update-specification.md) — Master update specification.
- [01-image-build.md](01-image-build.md) — Containerfile specification and build pipeline.
- [02-release-channels.md](02-release-channels.md) — Release channels and versioning.
- [04-rollback-recovery.md](04-rollback-recovery.md) — Rollback recovery mechanics.
- [../testing/07-hardware-testing.md](../testing/07-hardware-testing.md) — Hardware test matrix.
