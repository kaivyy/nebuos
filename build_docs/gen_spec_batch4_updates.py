#!/usr/bin/env python3
"""
Generator for Batch 4: Updates subsystem specifications:
- updates/00-update-specification.md
- updates/01-image-build.md
- updates/02-release-channels.md
- updates/03-regression-gates.md
- updates/04-rollback-recovery.md
"""

import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {path} ({len(content.splitlines())} lines)")

# 00-update-specification.md
u0 = r"""# Update Subsystem Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Define the atomic OS image update architecture, ostree/bootc deployment model, A/B partition lifecycle, and automated rollback triggers in NebuOS.

---

## 1. Status
DRAFT — Master implementation specification for the NebuOS update and lifecycle subsystem.

## 2. Purpose
Traditional Linux desktop distributions suffer from package state fragmentation, broken dependencies, and incomplete upgrades. NebuOS eliminates these issues by treating the base operating system as an immutable, cryptographically signed OCI container image managed via `bootc` and `rpm-ostree`. This specification defines how updates are staged, verified, and activated.

## 3. Scope
- Master update architecture based on Fedora Atomic and `bootc`.
- Staged deployment model with zero runtime interruption of active user processes.
- Cryptographic image signature verification (Sigstore / cosign).
- Automated health checks and automated reboot fallback.
- User notification, scheduling, and power state policies.

## 4. Non-goals
- Package-by-package delta upgrades (base OS upgraded strictly as complete atomic images).
- Live kernel hot-patching without reboot (reboot required to activate new base kernel).
- Modifying `/usr` at runtime.

## 5. Requirements
1. **R-UPD-01:** Deploy all OS updates as immutable atomic image trees via `bootc` container images.
2. **R-UPD-02:** Never overwrite active running system files; updates staged to inactive boot deployment.
3. **R-UPD-03:** Verify cryptographic Ed25519 / Sigstore signatures before applying any update image.
4. **R-UPD-04:** Provide zero-touch automated rollback if a newly booted image fails system health checks within 120s.
5. **R-UPD-05:** Preserve all user data in `/var` and `/home` across image upgrades without data loss.

## 6. Architecture
The update subsystem operates across the local update agent, OSTree deployment manager, and GRUB bootloader:

```mermaid
graph TD
    subgraph Registry[Remote Image Registry]
        OCI[quay.io/nebuos/base:latest]
        SIG[Cosign Signature & Provenance]
    end

    subgraph HostAgent[NebuOS Update Agent]
        TIMER[systemd nebu-update.timer]
        AGENT[nebu-update-agent Daemon]
        VERIFIER[Signature & Health Validator]
    end

    subgraph Sysroot[Local Btrfs Sysroot]
        BOOTC[bootc / rpm-ostree Engine]
        DEP_A[Deployment A: Active Boot]
        DEP_B[Deployment B: Staged Update]
        GRUB[GRUB2 BLS Bootloader Menu]
    end

    TIMER --> AGENT
    AGENT -->|Check New Digest| OCI
    OCI --> VERIFIER
    SIG --> VERIFIER
    VERIFIER -->|Deploy| BOOTC
    BOOTC --> DEP_B
    DEP_B --> GRUB
    GRUB -.->|Next Boot Default| DEP_B
```

## 7. Components
1. **Update Agent (`nebu-update-agent`):** Background user/system daemon checking registry for new image digests.
2. **`bootc` CLI & Daemon:** Standard tool managing transactional container deployments to disk.
3. **Health Monitor (`nebu-boot-check.service`):** Runs immediately after boot to confirm display server and core daemons reach `READY=1`.
4. **GRUB Boot Counter:** Hardware-agnostic GRUB2 boot-counting script tracking boot attempts.

## 8. Data Flow
1. `nebu-update.timer` triggers daily check on metered/unmetered connection.
2. Agent queries `quay.io/nebuos/base:1.0-stable` manifest.
3. If new SHA-256 digest found:
   - Downloads image layers into local container storage.
   - Verifies Cosign signature using NebuOS public root key.
   - Invokes `bootc switch` to create new OSTree deployment.
   - Prepares GRUB boot entry with boot counter `boot_counter=3`.
4. Agent emits D-Bus notification: *"NebuOS update installed. Restart to apply."*
5. User restarts system; GRUB boots new deployment.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant Timer as Update Timer
    participant Agent as Update Agent
    participant Bootc as bootc engine
    participant Grub as GRUB2
    participant Check as nebu-boot-check

    Timer->>Agent: CheckForUpdates()
    Agent->>Bootc: bootc upgrade --apply=false
    Bootc-->>Agent: New Deployment Staged: deployment.1
    Agent->>Grub: SetNextBoot(deployment.1, counter=3)
    Note over Agent,Grub: User reboots system
    Grub->>Check: Boot deployment.1 (counter decrements to 2)
    Check->>Check: Validate systemd units & DRM scanout
    alt Health Check Passes
        Check->>Grub: SetBootSuccessful(counter=0)
    else Health Check Fails or Kernel Panics
        Grub->>Grub: Counter exhausted -> Boot deployment.0 (Rollback)
    end
```

## 10. Interfaces
- **D-Bus Update Interface:** `org.nebu.Update1`
  - `CheckForUpdate() -> UpdateStatus`
  - `ApplyStagedUpdate() -> Boolean`
  - `GetActiveDeployment() -> DeploymentInfo`
  - `GetRollbackDeployment() -> DeploymentInfo`
- **CLI Management Command:** `nebu update check`, `nebu update apply`, `nebu rollback`

## 11. Dependencies
- `bootc` >= 0.1.14.
- `rpm-ostree` >= 2024.1.
- `cosign` / Sigstore verification libraries.
- GRUB2 with Boot Loader Specification (BLS) support.

## 12. Security
- System images signed via Ed25519 signing keys; unsigned or mismatched images rejected before writing to disk.
- Update agent runs with isolated system credentials (`ProtectHome=true`, `ProtectKernelTunables=true`).
- Base root filesystem mounted strictly read-only (`ro,nodev`).

## 13. Resource Requirements
- Idle memory overhead of update timer: 0 MB (systemd timer-activated).
- Active upgrade staging memory: <= 85 MB RSS.
- Staging disk requirement: ~1.5–3.0 GB temporary layer cache during download.

## 14. Failure Modes
1. **Network Interruption During Layer Download:** Incomplete container pull.
2. **Signature Verification Failure:** Compromised or uncertified image registry digest.
3. **Display Server Black Screen on Boot:** New graphics driver fails to initialize DRM plane.

## 15. Recovery Behavior
- Incomplete downloads resume automatically using HTTP range requests and container chunk deduplication.
- Signature failures abort the operation immediately, leave running system completely untouched, and log security alert.
- Boot failure triggers GRUB counter fallback to prior working deployment in < 10 seconds.

## 16. Testing Requirements
- Automated CI test building base image, staging update, booting in QEMU, and verifying health check.
- Intentional crash injection test asserting that watchdog triggers automatic GRUB rollback.
- Data integrity test asserting user files in `/home` remain bit-identical across 10 OS upgrades.

## 17. Performance Requirements
- Background update staging I/O: Throttled to < 20 MB/s to prevent disk starvation during user desktop tasks.
- Boot time increase during first boot of new image: <= 1.5s (SELinux label validation only).
- Rollback execution time: <= 10s (standard reboot duration).

## 18. Compatibility Considerations
- User application prefixes (`~/.nebu/apps/`) are fully decoupled from OS image and remain untouched across updates.

## 19. Open Questions
- **OQ-UPD-01:** Should updates be applied automatically on shutdown or strictly when initiated by the user?
- **OQ-UPD-02:** Should compatibility database updates be shipped out-of-band via SQLite delta updates or strictly bundled with OS images?

## 20. Related Documents
- [01-image-build.md](01-image-build.md)
- [02-release-channels.md](02-release-channels.md)
- [03-regression-gates.md](03-regression-gates.md)
- [04-rollback-recovery.md](04-rollback-recovery.md)
"""

write_file("/root/NebuOS/docs/updates/00-update-specification.md", u0)

# 01-image-build.md
u1 = r"""# Image Build Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the Containerfile definitions, build pipelines, multi-stage layering, package pruning, and reproducibility standards for NebuOS base images.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P0 and P8 image build pipeline.

## 2. Purpose
NebuOS is distributed as a bootable OCI container image. This specification defines the exact structure of the `Containerfile`, build stages, package manifests, stripping rules, and container optimization strategies necessary to achieve a clean, secure, and minimal base OS image.

## 3. Scope
- Base container configuration derived from Fedora Atomic (`quay.io/fedora/fedora-bootc:40`).
- Multi-stage build process compiling NebuOS Rust binaries (`nebu-compositor`, `nebu-shell`, `nebu-runtime-daemon`).
- Dependency package manifest and package minimization rules.
- Stripping debugging symbols, manpages, and non-essential documentation.
- OCI container layer optimization to keep total uncompressed image <= 3.2 GB.

## 4. Non-goals
- Compiling custom Linux kernel forks (uses standard Fedora kernel).
- Embedding proprietary graphics drivers directly in public open-source base layer.
- Hosting private container registries outside GitHub Packages / Quay.io.

## 5. Requirements
1. **R-BLD-01:** Build the complete bootable OS image using standard Containerfile and Podman/Buildah tools.
2. **R-BLD-02:** Incorporate multi-stage builds ensuring zero Rust compiler tooling or build caches pollute the production image.
3. **R-BLD-03:** Enforce reproducible builds: identical commit tags produce bit-identical container manifests.
4. **R-BLD-04:** Strip all binaries in `/usr/bin` and `/usr/libexec/nebu/` of unneeded symbols.
5. **R-BLD-05:** Resulting base image download footprint must be <= 1.2 GB compressed (<= 3.2 GB uncompressed).

## 6. Architecture
The image build operates via multi-stage container compilation:

```mermaid
graph TD
    subgraph Stage1[Stage 1: Rust Builder Container]
        CARGO_SRC[Rust Workspaces Source]
        RUST_TOOLCHAIN[Rust 1.80+ / Cargo]
        BUILD_OUT[Compiled Binaries: nebu-*, lib*]
    end

    subgraph Stage2[Stage 2: Base OS Composition]
        FEDORA_BASE[Fedora bootc Base Image]
        RPM_INSTALL[DNF / RPM Package Manifest]
        SYS_CONFIG[/etc, /usr/lib/systemd, sysctl]
    end

    subgraph FinalImage[Production Image Assembly]
        COPY_BIN[Copy Binaries from Stage 1]
        STRIP_STEP[Symbol Stripping & Cleanup]
        PRESEED[Preseeded Compat DB & Wine Staging]
        OCI_EXPORT[quay.io/nebuos/base:1.0]
    end

    CARGO_SRC --> RUST_TOOLCHAIN
    RUST_TOOLCHAIN --> BUILD_OUT
    FEDORA_BASE --> RPM_INSTALL
    RPM_INSTALL --> SYS_CONFIG
    BUILD_OUT --> COPY_BIN
    SYS_CONFIG --> COPY_BIN
    COPY_BIN --> STRIP_STEP
    STRIP_STEP --> PRESEED
    PRESEED --> OCI_EXPORT
```

## 7. Components
1. **`Containerfile.p0`:** Minimal bootable base containing kernel, systemd, and terminal.
2. **`Containerfile.release`:** Production image containing desktop, compositor, shell, and compatibility layers.
3. **Layer Pruner Script:** Removes `/usr/share/doc`, `/usr/share/man`, and locale files not matching target languages.
4. **Image Signer:** Integrates with GitHub Actions to sign images using Cosign and GitHub OIDC tokens.

## 8. Data Flow
1. Developer pushes tag `v1.0.0` to repository.
2. CI runner spins up builder container:
   - `cargo build --release --locked` builds all workspace crates.
3. Second stage starts from `quay.io/fedora/fedora-bootc:40`:
   - Installs RPMs: `kernel`, `mesa-dri-drivers`, `pipewire`, `wine`, `bwrap`, `sqlite`.
   - Copies compiled binaries into `/usr/bin/`.
   - Copies systemd units into `/usr/lib/systemd/system/` and `/usr/lib/systemd/user/`.
4. Prunes non-essential files and executes `ostree container commit`.
5. Pushes signed image to container registry.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant CI as GitHub Actions Runner
    participant Buildah as Buildah Engine
    participant Registry as Quay.io Registry
    participant Cosign as Cosign Signer

    CI->>Buildah: buildah bud -f Containerfile -t nebuos/base:1.0
    Buildah->>Buildah: Stage 1: Build Rust Crates (nebu-compositor, nebu-shell)
    Buildah->>Buildah: Stage 2: Install RPM dependencies & configure sysroot
    Buildah->>Buildah: Copy binaries & apply SELinux file contexts
    Buildah-->>CI: Image Built (SHA-256 Digest: abc123def456)
    CI->>Registry: push nebuos/base:1.0
    CI->>Cosign: cosign sign --key env:COSIGN_KEY nebuos/base:1.0
    Cosign-->>Registry: Signature Uploaded
```

## 10. Interfaces
- **Base Containerfile Excerpt:**
  ```dockerfile
  FROM rust:1.80-bookworm AS builder
  WORKDIR /build
  COPY . .
  RUN cargo build --release --locked --workspace

  FROM quay.io/fedora/fedora-bootc:40
  RUN dnf install -y \
      kernel \
      systemd \
      mesa-vulkan-drivers \
      bubblewrap \
      pipewire \
      wine-core \
      && dnf clean all
  COPY --from=builder /build/target/release/nebu-compositor /usr/bin/
  COPY --from=builder /build/target/release/nebu-shell /usr/bin/
  COPY --from=builder /build/target/release/nebu-runtime-daemon /usr/bin/
  RUN bootc container lint
  ```

## 11. Dependencies
- Podman / Buildah / Docker container runtime.
- `bootc` container verification utilities.
- Upstream Fedora Atomic base packages.

## 12. Security
- Multi-stage builds prevent compiler toolchains (`gcc`, `cargo`, header files) from residing in production images.
- Base images scanned for CVEs via Trivy / Grype before publishing.
- Provenance attested via in-toto metadata in GitHub Actions.

## 13. Resource Requirements
- Build environment RAM: >= 8 GB (for compiling large Rust dependencies).
- Build environment disk: >= 30 GB scratch space.
- CI pipeline execution time: <= 18 minutes on 8-core runner.

## 14. Failure Modes
1. **Dependency Package Checksum Mismatch:** Corrupted RPM mirror.
2. **SELinux Relabeling Failure:** New binary lacks proper file context.
3. **Image Size Exceeded:** Base image exceeds 3.2 GB limit.

## 15. Recovery Behavior
- DNF configured with multiple fallback mirror lists.
- Automated `restorecon -Rv /usr` executed during container build stage.
- Build fails with diagnostic alert if image exceeds budget.

## 16. Testing Requirements
- Automated smoke test launching newly built container in QEMU via `bootc install to-disk`.
- Vulnerability scanning gate rejecting builds with High/Critical CVEs.

## 17. Performance Requirements
- Final compressed image size: <= 1.2 GB.
- Uncompressed rootfs disk usage: <= 3.2 GB.

## 18. Compatibility Considerations
- Base image maintains standard POSIX filesystem layout compatible with Fedora OStree tooling.

## 19. Open Questions
- **OQ-BLD-01:** Should proprietary NVIDIA drivers be packaged as an optional container image tag (`base:1.0-nvidia`) or dynamic kmod layer?
- **OQ-BLD-02:** Should the build pipeline support automated AArch64 (ARM64) builds in future phases?

## 20. Related Documents
- [00-update-specification.md](00-update-specification.md)
- [02-release-channels.md](02-release-channels.md)
- [03-regression-gates.md](03-regression-gates.md)
"""

write_file("/root/NebuOS/docs/updates/01-image-build.md", u1)

# 02-release-channels.md
u2 = r"""# Release Channels Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the release channel topology (Stable, Beta, Nightly), promotion criteria, update cadences, and channel switching mechanisms in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P8 release engineering.

## 2. Purpose
NebuOS serves diverse user profiles ranging from mission-critical desktop productivity users to gaming enthusiasts seeking the latest graphics drivers. This specification establishes the three distinct release channels, their stability guarantees, update frequencies, and channel switching mechanisms.

## 3. Scope
- Definition of Stable, Beta, and Nightly channels.
- Image tagging and container registry naming taxonomy.
- Channel promotion gates and automated validation requirements.
- Dynamic channel switching via `bootc switch` without data loss.
- Out-of-band security emergency releases (Hotfix channel).

## 4. Non-goals
- Maintaining independent channel forks (all channels derive from main development trunk).
- Supporting unsupported custom third-party channel repositories.

## 5. Requirements
1. **R-CHN-01:** Maintain three primary release channels: `stable`, `beta`, and `nightly`.
2. **R-CHN-02:** Ensure user can switch between channels via a single GUI dropdown or CLI command.
3. **R-CHN-03:** Enforce strict regression gating before any image is promoted from Beta to Stable.
4. **R-CHN-04:** Provide dedicated Hotfix cadence for zero-day security vulnerabilities.
5. **R-CHN-05:** Preserve user data, application prefixes, and settings seamlessly when moving between channels.

## 6. Architecture
Release channels are represented as distinct OCI container tags in the central container registry:

```mermaid
graph LR
    subgraph Development[Trunk Development]
        MAIN[Git Main Branch]
    end

    subgraph Channels[Release Channels]
        NIGHTLY[Nightly Channel: base:nightly]
        BETA[Beta Channel: base:beta]
        STABLE[Stable Channel: base:stable / base:1.0.X]
        HOTFIX[Hotfix Channel: base:1.0.X-sec]
    end

    MAIN -->|Automated Nightly CI| NIGHTLY
    NIGHTLY -->|Weekly Stability Gate| BETA
    BETA -->|Monthly Regression Gate| STABLE
    STABLE -.->|Emergency Patch| HOTFIX
```

## 7. Components
1. **Stable Channel:** Intended for general users, office environments, and production workstations. Updated monthly or for critical security fixes.
2. **Beta Channel:** Intended for power users and enthusiasts. Updated bi-weekly with new compatibility profiles, kernel updates, and Wine staging releases.
3. **Nightly Channel:** Automated daily builds reflecting the latest commits on `main`. Intended strictly for developers and QA automation.
4. **Channel Switcher (`nebu channel`):** CLI and D-Bus utility re-pointing `bootc` remote tracking references.

## 8. Data Flow
1. User opens Software Center Settings -> Release Channel.
2. Selects "Beta Channel".
3. D-Bus invokes `nebu-update-agent.SwitchChannel("beta")`.
4. Agent executes:
   `bootc switch quay.io/nebuos/base:beta`.
5. Staged deployment prepared in background.
6. Notification alerts user: *"Switched to Beta Channel. Restart to boot into Beta."*

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Shell as Desktop Settings
    participant Agent as nebu-update-agent
    participant Bootc as bootc engine

    User->>Shell: Select "Beta" in Channel Dropdown
    Shell->>Agent: SetReleaseChannel("beta")
    Agent->>Bootc: bootc switch quay.io/nebuos/base:beta
    Bootc->>Bootc: Pull delta layers & prepare boot deployment
    Bootc-->>Agent: Deployment staged successfully
    Agent-->>Shell: ChannelSwitched(restart_required=true)
    Shell-->>User: Display restart banner
```

## 10. Interfaces
- **Channel Registry Tags:**
  - `quay.io/nebuos/base:stable` (points to current GA release, e.g. `1.0.2`)
  - `quay.io/nebuos/base:beta` (points to release candidates)
  - `quay.io/nebuos/base:nightly` (points to daily build `YYYYMMDD`)
- **CLI Commands:**
  - `nebu channel get`
  - `nebu channel set <stable|beta|nightly>`

## 11. Dependencies
- OCI container registry supporting multi-tag image deployments.
- `bootc` switch capability.

## 12. Security
- All channel images must be cryptographically signed by official NebuOS release keys.
- Switching to Nightly warns user about bleeding-edge stability risks.

## 13. Resource Requirements
- Channel switching download overhead: proportional to layer diffs between channels (typically 200–600 MB).
- Disk overhead: two parallel deployments stored on Btrfs subvolumes (~500 MB shared extent delta).

## 14. Failure Modes
1. **Channel Downgrade Failure:** Switching from Beta to Stable where schema or config formats are incompatible.
2. **Registry Tag Missing:** Network timeout or tag deletion during switch.

## 15. Recovery Behavior
- When switching from newer to older channel, agent validates compatibility database backward-compatibility before committing.
- In network failure, original active deployment remains running untouched.

## 16. Testing Requirements
- Automated CI pipeline testing transition `stable -> beta -> stable` with automated verification of desktop state.
- Nightly build generation test verifying zero broken dependencies.

## 17. Performance Requirements
- Channel switch execution time (excluding download time): <= 45s.
- Reboot time into new channel: <= 8.0s.

## 18. Compatibility Considerations
- User application prefixes are forward and backward compatible across adjacent channels.

## 19. Open Questions
- **OQ-CHN-01:** Should enterprise deployments be able to lock users to the Stable channel via policy configuration?
- **OQ-CHN-02:** Should the Nightly channel retain automated telemetry crash reporting enabled by default?

## 20. Related Documents
- [00-update-specification.md](00-update-specification.md)
- [01-image-build.md](01-image-build.md)
- [03-regression-gates.md](03-regression-gates.md)
- [04-rollback-recovery.md](04-rollback-recovery.md)
"""

write_file("/root/NebuOS/docs/updates/02-release-channels.md", u2)

# 03-regression-gates.md
u3 = r"""# Regression Gates Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the automated quality gates, compatibility lab test suites, performance thresholds, and sign-off criteria required for release promotion in NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P7 and P8 automated release gating.

## 2. Purpose
To ensure zero regressions across OS upgrades, NebuOS implements a strict, multi-tiered quality gating pipeline. No base OS image or compatibility database update may be promoted to the Stable channel without passing automated functional, graphics, security, and compatibility regression gates.

## 3. Scope
- Definition of automated test suites gating release promotion.
- Performance SLA thresholds (RAM, boot time, launch latency).
- Compatibility Lab test matrix (Office, CAD, Adobe, Games).
- Security audit and vulnerability scanning gates.
- Manual architectural sign-off requirements.

## 4. Non-goals
- Manual testing of every minor nightly build (nightly testing is 100% automated).
- Testing proprietary applications without automated reproducible test scripts.

## 5. Requirements
1. **R-GAT-01:** Enforce automated CI gating on all pull requests and nightly builds.
2. **R-GAT-02:** Require 100% pass rate on the Core System Suite (boot, systemd targets, Wayland initialization).
3. **R-GAT-03:** Require 100% pass rate on the Tier 1 Windows Compatibility Suite (Office 2024, AutoCAD 2024, Notepad++).
4. **R-GAT-04:** Enforce performance gate: idle RAM must not exceed 800 MB on 4GB hardware baseline.
5. **R-GAT-05:** Block release promotion if any High or Critical CVE is present in base packages.

## 6. Architecture
The regression gating pipeline operates within GitHub Actions and the dedicated NebuOS Compatibility Lab:

```mermaid
graph TD
    subgraph Pipeline[Gating Pipeline Execution]
        CANDIDATE[Release Candidate Image]
        GATE1[Gate 1: Static Analysis & Security]
        GATE2[Gate 2: Headless Virtual Boot]
        GATE3[Gate 3: Hardware Compatibility Lab]
        GATE4[Gate 4: Performance SLA Verification]
        GATE5[Gate 5: Architectural Sign-off]
    end

    subgraph Decision[Promotion Decision]
        PROMOTE[Promote to Stable Channel]
        REJECT[Reject & Open Blocker Issue]
    end

    CANDIDATE --> GATE1
    GATE1 -->|Pass| GATE2
    GATE2 -->|Pass| GATE3
    GATE3 -->|Pass| GATE4
    GATE4 -->|Pass| GATE5
    GATE5 -->|Approved| PROMOTE
    GATE1 -->|Fail| REJECT
    GATE2 -->|Fail| REJECT
    GATE3 -->|Fail| REJECT
    GATE4 -->|Fail| REJECT
```

## 7. Components
1. **Gate 1 (Security & Lint):** Scans container layers via Trivy, validates SELinux policy contexts, runs `cargo clippy` and `cargo audit`.
2. **Gate 2 (Virtual Boot):** Boots image in headless QEMU/KVM, asserts all systemd units reach `active (running)`, verifies Wayland socket emergence.
3. **Gate 3 (Compatibility Lab):** Runs automated test scripts executing top 50 Windows applications on physical test rigs (Intel, AMD, NVIDIA).
4. **Gate 4 (Performance SLAs):** Measures cold boot time (< 8s), idle RAM (< 800 MB), and 60 FPS compositor frame pacing.
5. **Gate 5 (Human Sign-off):** Principal Systems Architect manual verification of release notes and risk register.

## 8. Data Flow
1. Release candidate tag `v1.0.0-rc1` triggered.
2. CI deploys image to Compatibility Lab test farm via PXE/iPXE bootc provisioner.
3. Test harness executes 11-stage compatibility test invariant:
   `INSTALL -> LAUNCH -> OPEN -> EDIT -> SAVE -> EXPORT -> PRINT -> GPU -> PLUGIN -> STRESS -> CLOSE`.
4. Test results aggregated into structured JSON report.
5. If all gate scores >= 95.0%, pipeline issues promotion approval token.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant CI as Release Pipeline
    participant Lab as Compatibility Lab
    participant Gate as Quality Gate Controller
    participant Rel as Registry

    CI->>Lab: Deploy Image to Hardware Matrix
    Lab->>Lab: Run Automated Windows App Suite
    Lab->>Lab: Measure Idle RAM and Boot Timings
    Lab-->>Gate: Submit Test Metrics Report
    Gate->>Gate: Evaluate Thresholds (Pass Rate: 100%, RAM: 580MB)
    alt All Metrics Within Budget
        Gate->>Rel: Tag Image as 'stable'
        Gate-->>CI: Release Gate PASSED
    else Any Regression Detected
        Gate-->>CI: Release Gate BLOCKED (File Blocker Bug)
    end
```

## 10. Interfaces
- **Test Results Schema (JSON):**
  ```json
  {
    "candidate_digest": "sha256:7f83b165...",
    "gate_results": {
      "security_scan": {"status": "PASSED", "cve_critical": 0, "cve_high": 0},
      "boot_test": {"status": "PASSED", "boot_time_s": 5.4},
      "idle_ram_mb": {"status": "PASSED", "value": 540.2, "limit": 800.0},
      "compat_suite_tier1": {"status": "PASSED", "passed": 50, "failed": 0}
    },
    "overall_verdict": "PROMOTABLE"
  }
  ```

## 11. Dependencies
- Compatibility Lab physical test farm.
- Trivy / Grype vulnerability scanners.
- Automated UI interaction harness (`ydotool`, Wayland frame capture).

## 12. Security
- Test harnesses run on isolated test VLANs to prevent rogue network traffic.
- Gating approval tokens signed via KMS HSM.

## 13. Resource Requirements
- Full regression gate execution time: <= 2.5 hours across physical hardware matrix.
- Test lab hardware: 3 dedicated test machines (Low-end Celeron/Intel UHD, Mid-tier AMD Ryzen, High-end NVIDIA dGPU).

## 14. Failure Modes
1. **Intermittent Flaky Test:** Network timeout during test app download.
2. **Performance Budget Breach:** Memory leak increases idle RAM to 850 MB.
3. **Hardware-Specific Graphic Glitch:** Vulkan artifact appearing exclusively on Intel Iris Xe.

## 15. Recovery Behavior
- Flaky tests rerun automatically up to 2 times; persistent failures block the gate.
- Performance regressions bisected automatically against commit history to identify offending PR.

## 16. Testing Requirements
- Meta-testing: Automated tests asserting that the gating harness accurately detects injected bugs and performance regressions.

## 17. Performance Requirements
- Gate evaluation decision latency: <= 30 seconds after test data collection.

## 18. Compatibility Considerations
- Tests validate both legacy Win32 (MFC, GDI) and modern Direct3D 11/12 software suites.

## 19. Open Questions
- **OQ-GAT-01:** Should community test results contribute to Beta promotion gates?
- **OQ-GAT-02:** What is the maximum acceptable frame pacing jitter threshold for gaming certification?

## 20. Related Documents
- [00-update-specification.md](00-update-specification.md)
- [01-image-build.md](01-image-build.md)
- [02-release-channels.md](02-release-channels.md)
- [04-rollback-recovery.md](04-rollback-recovery.md)
- [../testing/00-test-strategy.md](../testing/00-test-strategy.md)
"""

write_file("/root/NebuOS/docs/updates/03-regression-gates.md", u3)

# 04-rollback-recovery.md
u4 = r"""# Rollback and Recovery Specification — NebuOS

**Status:** DRAFT  
**Purpose:** Specify the automated failure detection, boot-counter fallback, manual recovery triggers, and data preservation invariants for NebuOS.

---

## 1. Status
DRAFT — Technical implementation specification for Phase P0 and P8 rollback mechanisms.

## 2. Purpose
An operating system must never leave a user with an unbootable machine after an update. NebuOS guarantees that even in catastrophic scenarios—such as kernel panics, broken display drivers, or power loss during an upgrade—the system detects the failure automatically and falls back to the previous working deployment in under 10 seconds.

## 3. Scope
- Boot failure detection mechanisms (GRUB boot counter, watchdog timers).
- Automated rollback triggering without requiring user intervention.
- Manual rollback invocation via GRUB boot menu and CLI.
- User data preservation invariants (`/home`, `/var`, application prefixes).
- Disaster recovery via live USB installer environment.

## 4. Non-goals
- Reverting user personal documents or files in `~/Documents` when rolling back OS image.
- Dual-boot recovery orchestration with third-party operating systems (Windows, macOS).

## 5. Requirements
1. **R-ROL-01:** Ensure system can always boot the previous known-good deployment from the GRUB boot menu.
2. **R-ROL-02:** Automatically decrement GRUB boot counter upon boot; if counter reaches zero without health check success, reboot into fallback deployment.
3. **R-ROL-03:** Guarantee 100% data preservation of user directories (`/home`, `/var`) during rollback.
4. **R-ROL-04:** Provide CLI command `nebu rollback` allowing instant return to prior image.
5. **R-ROL-05:** Maintain at least two complete bootable deployment entries in GRUB BLS at all times.

## 6. Architecture
Rollback operates through the integration of the GRUB2 environment, the OSTree deployment directory, and the systemd health checker:

```mermaid
graph TD
    subgraph Bootloader[GRUB2 Bootloader]
        BLS[Boot Loader Specification Entries]
        ENV[grubenv: boot_counter=3]
        FALLBACK[Fallback Entry: Deployment 0]
    end

    subgraph HealthCheck[Early Boot Health Verification]
        INIT[initramfs & systemd PID 1]
        CHECK[nebu-boot-check.service]
        WATCHDOG[Hardware Watchdog /dev/watchdog]
    end

    subgraph Deployments[Btrfs Deployments]
        DEP_NEW[Deployment 1: New Image]
        DEP_OLD[Deployment 0: Previous Working Image]
    end

    BLS -->|Default| DEP_NEW
    ENV -->|Counter Decrement| INIT
    INIT --> CHECK
    WATCHDOG -.->|Hardware Reset on Hang| Bootloader
    CHECK -->|Success: counter=0| ENV
    CHECK -->|Timeout / Panic| FALLBACK
    FALLBACK --> DEP_OLD
```

## 7. Components
1. **GRUB Boot Counter Script (`/boot/grub2/grubenv`):** Tracks remaining boot attempts before forced fallback.
2. **Boot Health Daemon (`nebu-boot-check.service`):** Systemd service running after `graphical-session.target`; writes `boot_counter=0` upon verifying:
   - Compositor running.
   - Display scanned out.
   - Root filesystem mounted cleanly.
3. **Watchdog Timer Integration:** Arms hardware/softdog watchdog at boot (timeout: 60s); disarms only when health check succeeds.
4. **Rollback CLI Agent:** Interacts with `bootc rollback` to permanently promote fallback deployment.

## 8. Data Flow
1. User applies OS update and restarts machine.
2. GRUB reads `grubenv`: `boot_counter=2`, `next_entry=nebuos-1.0.1`.
3. System boots into `nebuos-1.0.1`:
   - Decrements counter: `boot_counter=1`.
4. Kernel boots, but graphics driver panics or freezes display.
5. Health check fails to run within 60s.
6. Hardware watchdog resets computer.
7. GRUB restarts, reads `boot_counter=1`: decrements to 0.
8. Counter exhausted -> GRUB skips `nebuos-1.0.1` and boots `nebuos-1.0.0` (previous working image).
9. User arrives at working login screen in < 15 seconds.

## 9. Control Flow
```mermaid
sequenceDiagram
    autonumber
    participant Grub as GRUB2 Bootloader
    participant Kernel as Linux Kernel
    participant Systemd as systemd PID 1
    participant Check as nebu-boot-check
    participant User as Desktop User

    Grub->>Kernel: Boot New Deployment (counter=2 -> 1)
    Kernel->>Systemd: Initialize userspace
    alt Normal Boot (Success)
        Systemd->>Check: Start nebu-boot-check.service
        Check->>Grub: Set boot_counter=0 (Commit Deployment)
        Systemd->>User: Display Login Screen
    else Fatal Boot Failure (Crash / Freeze)
        Note over Kernel,Systemd: System deadlocks or kernel panics
        Grub->>Kernel: Hardware Watchdog Triggers Reboot
        Grub->>Grub: Counter exhausted (0) -> Select Prior Working Deployment
        Grub->>Kernel: Boot Prior Working Deployment
        Kernel->>User: Display Login Screen (Rollback Notice)
    end
```

## 10. Interfaces
- **GRUB Environment Variables:**
  - `boot_counter`: Integer (3 to 0).
  - `boot_success`: Boolean flag.
- **CLI Rollback Command:**
  - `nebu rollback` (marks current deployment invalid and sets prior deployment as default).
  - `nebu rollback status`

## 11. Dependencies
- `grub2-tools` and `grub2-efi`.
- Linux kernel watchdog driver (`softdog` or hardware ACPI WDAT).
- `bootc` rollback primitives.

## 12. Security
- Rollback mechanism cannot be hijacked by unprivileged applications; `grubenv` write permissions restricted to root (UID 0).
- Fallback deployments are immutable and signed; prevents rolling back to an unauthorized or tampered image.

## 13. Resource Requirements
- Boot counter execution latency in GRUB: < 10ms.
- Health check verification execution time: <= 500ms after desktop target reached.
- Disk storage for prior deployment: shared extents via Btrfs (~400 MB to 1.2 GB unique data).

## 14. Failure Modes
1. **Both Deployments Corrupted:** Disk hardware failure damages filesystem metadata.
2. **grubenv Write Failure:** Read-only boot partition prevents counter update.

## 15. Recovery Behavior
- If both deployments fail, GRUB displays rescue shell with instructions to boot from NebuOS Live USB.
- In `grubenv` failure, GRUB defaults to interactive menu prompt allowing manual selection of older entries.

## 16. Testing Requirements
- Automated test simulating kernel panic on boot and asserting automated fallback to previous image.
- Watchdog timeout simulation test.
- Manual rollback CLI verification test.

## 17. Performance Requirements
- Total recovery reboot duration: <= 12 seconds from reset to desktop login.
- Zero loss of user document files or open browser tabs preserved in `/home`.

## 18. Compatibility Considerations
- Works seamlessly across UEFI 2.4+ and legacy BIOS configurations.

## 19. Open Questions
- **OQ-ROL-01:** Should NebuOS display an interactive notification explaining why the system rolled back after an automated recovery event?
- **OQ-ROL-02:** Should the failed deployment be pinned for debugging or purged immediately to save disk space?

## 20. Related Documents
- [00-update-specification.md](00-update-specification.md)
- [01-image-build.md](01-image-build.md)
- [02-release-channels.md](02-release-channels.md)
- [03-regression-gates.md](03-regression-gates.md)
"""

write_file("/root/NebuOS/docs/updates/04-rollback-recovery.md", u4)

