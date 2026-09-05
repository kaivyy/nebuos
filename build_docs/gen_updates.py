#!/usr/bin/env python3
"""
Generate Updates Documentation for NebuOS (docs/updates/):
- 00-update-overview.md
- 01-image-build.md
- 02-release-channels.md
- 03-regression-gates.md
- 04-rollback.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs/updates"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_file(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: updates/{filename} ({len(content.splitlines())} lines)")

# 00-update-overview.md
write_file("00-update-overview.md", r"""# Update Architecture Overview — NebuOS

**Status:** REVIEW  
**Purpose:** Establish the transactional, atomic update model of NebuOS, ensuring immunity to mid-update power cuts and package dependency breakage.

---

## 1. Scope & Update Principles
NebuOS implements an image-based, immutable deployment model powered by `bootc` and `ostree`. The operating system treats the root filesystem (`/usr`) as a single, cryptographically signed, read-only OCI container image. Updates are applied transactionally in the background; a failed update never mutates the running system.

## 2. A/B Atomic Deployment Topology

```mermaid
graph TD
    UPSTREAM[Nebu OS Image Registry: registry.nebuos.org] -->|Pull New Image| AGENT[nebu-update-agent]
    
    subgraph SYSTEM_STORAGE [Host Drive - Btrfs Deployments]
        DEP_A["Deployment A (Active Running System) - Read-Only"]
        DEP_B["Deployment B (Staged New System) - Target of Update"]
        USER_DATA["Persistent Data: /var & /home - Untouched by OS Update"]
    end

    AGENT -->|Stage New Image| DEP_B
    DEP_B -->|Verify Signatures & Checksums| GRUB_UPDATE[Update GRUB Bootloader Spec]
    GRUB_UPDATE --> REBOOT[User Reboots at Convenience]
    REBOOT -->|Boot into| DEP_B
    DEP_B -.->|If Regression or Failure| ROLLBACK[Instant Rollback to Deployment A]
```

## 3. Related Documents
- [01-image-build.md](01-image-build.md)
- [02-release-channels.md](02-release-channels.md)
- [04-rollback.md](04-rollback.md)
""")

# 01-image-build.md
write_file("01-image-build.md", r"""# Image Build Pipeline Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define the automated CI/CD pipeline building, packaging, and signing NebuOS container-based operating system images.

---

## 1. Build Pipeline Architecture

```mermaid
sequenceDiagram
    autonumber
    participant Git as GitHub / GitLab Monorepo
    participant CI as CI Build Matrix (Podman / Buildah)
    participant QA as Automated Test Harness
    participant Reg as Nebu OCI Container Registry

    Git->>CI: Git Tag / Merge to main
    CI->>CI: Pull Fedora Atomic Base Container
    CI->>CI: Compile Nebu Components in Rust (Release + LTO)
    CI->>CI: Install Curated Upstream Wine & Mesa
    CI->>CI: Generate Base Image Layer via Containerfile
    CI->>QA: Boot Image in Headless Hardware Matrix
    QA->>QA: Run Tier 0 System Tests & Tier 1 App Tests
    alt Tests Pass (100% Clean)
        QA->>CI: Approve Promotion
        CI->>CI: Sign Image with Cosign / Sigstore (GPG)
        CI->>Reg: Push OCI Artifact to registry.nebuos.org
    else Tests Fail
        QA->>Git: Halt Pipeline & Alert Release Engineers
    end
```

## 2. Containerfile Build Layer Definition
The base image is defined declaratively using standard container syntax:
```dockerfile
FROM quay.io/fedora/fedora-bootc:40
# Base hardware, Mesa, PipeWire & systemd
RUN dnf install -y mesa-dri-drivers pipewire wireplumber networkmanager
# Bundled Wine & Proton Runtimes
COPY --from=wine-builder /opt/wine-staging /usr/lib/nebu/runtimes/wine/
# Compiled Nebu Rust Binaries
COPY target/release/nebu-compositor /usr/bin/nebu-compositor
COPY target/release/nebu-shell /usr/bin/nebu-shell
COPY target/release/nebu-runtime-daemon /usr/bin/nebu-runtime-daemon
COPY target/release/nebu /usr/bin/nebu
# Read-Only System Catalog
COPY data/compat.db /usr/share/nebu/compat.db
```

## 3. Related Documents
- [00-update-overview.md](00-update-overview.md)
- [03-regression-gates.md](03-regression-gates.md)
""")

# 02-release-channels.md
write_file("02-release-channels.md", r"""# Release Channels Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Establish release channel definitions, qualification criteria, and promotion policies.

---

## 1. Channel Definitions & Target Audiences

| Channel Name | Update Frequency | Target Audience | Stability Profile | Promotion Gate |
|---|---|---|---|---|
| **Nightly** | Daily (Automated) | Internal Core Developers | Bleeding-edge. May contain experimental Wine builds and untested Mesa drivers. | Automated Tier 0 boot test pass. |
| **Beta** | Bi-weekly | Early Adopters & Community Testers | Relatively stable. Features feature-complete implementations undergoing testing. | 100% Tier 0 + Tier 1 test suite pass. |
| **Stable** | Monthly / Quarterly | Production Users & Enterprises | Enterprise rock-solid. Zero known regressions in certified CAD, Office, or core apps. | 100% Tier 0, 1, 2 pass + Compatibility Lab human QA signoff. |
| **LTS** | Annual (Long Term Support) | Mission-critical Workstations | High security, backported CVE fixes only. Zero feature churn. | Dedicated 60-day enterprise soaking period. |

## 2. Channel Switching
Users can switch release channels dynamically via Nebu Settings or CLI:
`nebu update channel set beta`
The update agent stages the new channel's latest verified container deployment without formatting `/home` or personal application data.

## 3. Related Documents
- [00-update-overview.md](00-update-overview.md)
- [03-regression-gates.md](03-regression-gates.md)
""")

# 03-regression-gates.md
write_file("03-regression-gates.md", r"""# Regression Gates Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define the automated regression testing barriers that block unstable component updates from reaching the Stable channel.

---

## 1. Component Update Trigger Matrix

```mermaid
graph TD
    KERNEL_UP[Kernel Update: e.g. 6.10 -> 6.11] --> GATE_SYS[System Gate: Boot, DRM, Suspend/Resume, USB]
    MESA_UP[Mesa Update: e.g. 24.1 -> 24.2] --> GATE_GFX[Graphics Gate: Vulkan CTS, DXVK, CAD 3D Viewport]
    WINE_UP[Wine Update: e.g. 9.2 -> 9.3] --> GATE_APP[App Gate: Office 2024 Macros, AutoCAD DWG, Maya Rigging]
    COMP_UP[NebuCompositor Update] --> GATE_DESK[Desktop Gate: Wayland Protocol CTS, Multi-Monitor]

    GATE_SYS --> AGGREGATOR{All Gates 100% PASS?}
    GATE_GFX --> AGGREGATOR
    GATE_APP --> AGGREGATOR
    GATE_DESK --> AGGREGATOR

    AGGREGATOR -->|YES| STABLE_PROMOTE[Promote Image to Stable Channel]
    AGGREGATOR -->|NO| REJECT[Reject Build & Generate Defect Report]
```

## 2. Zero-Tolerance Regression Policy
If any certified application (Microsoft Office 2021/2024, Autodesk AutoCAD 2024, Maya) suffers a regression in core functionality or performance:
1. The update is **immediately blocked** from promotion to Stable.
2. The compatibility defect is isolated to either upstream (Wine/Mesa) or Nebu layer.
3. If caused by an upstream regression, a targeted Nebu patch is applied to neutralize the defect before re-testing.

## 3. Related Documents
- [01-image-build.md](01-image-build.md)
- [02-release-channels.md](02-release-channels.md)
- [../testing/03-compatibility-testing.md](../testing/03-compatibility-testing.md)
""")

# 04-rollback.md
write_file("04-rollback.md", r"""# Rollback Architecture Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify the instant rollback mechanism, boot failure detection, and automatic recovery workflows.

---

## 1. Rollback Execution Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Watchdog
    participant GRUB as GRUB2 Bootloader
    participant OSTree as OSTree Sysroot Engine
    participant Recovery as Nebu Recovery Agent

    alt Manual Rollback via Desktop UI
        User->>Recovery: Click "Rollback to Previous OS Version"
        Recovery->>OSTree: Set default deployment index to 1 (Previous)
        Recovery->>User: Prompt to reboot
    else Automated Boot Failure Rollback
        GRUB->>GRUB: Increment boot_counter
        alt boot_counter > 3 (Repeated Hang / Crash)
            GRUB->>GRUB: Auto-select Deployment 1 (Known Good)
            GRUB->>Recovery: Boot into previous deployment with failure flag
            Recovery->>User: Display Notification: "System automatically rolled back due to startup failure"
        end
    end
```

## 2. Data Decoupling Invariant
System rollbacks exclusively revert the `/usr` OS container image. User files in `/home`, documents, browser sessions, and application prefixes in `~/.nebu/apps/` are **never** rolled back during an OS rollback, preventing any data loss.

## 3. Related Documents
- [00-update-overview.md](00-update-overview.md)
- [../architecture/02-boot-and-init.md](../architecture/02-boot-and-init.md)
""")

print("Updates documentation generated successfully.")
