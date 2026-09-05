# NebuOS Milestone P0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the finalized NebuOS Milestone P0 architecture and documentation into a real, bootable, immutable, transactional Linux OS based on Fedora 44 Atomic and bootc that can be automatically built and verified.

**Architecture:** Extend `quay.io/fedora/fedora-bootc:44` via `Containerfile.p0` with minimal headless packages, headless Dracut initramfs (Plymouth omitted), UEFI GRUB2 BLS bootloader, Btrfs subvolumes (`@`, `@home`, `@var`), immutable read-only `/usr`, deterministic oneshot health gate (`nebu-boot-check.service`), and automated QEMU UEFI boot verification.

**Tech Stack:** Fedora Linux 44, bootc 1.x, Linux Kernel 6.14+, systemd 256+, Dracut, Btrfs, GRUB2 BLS, Docker / Podman, QEMU / OVMF.

## Global Constraints

- **Milestone P0 is 100% HEADLESS:** Zero GUI, zero Wayland, zero Smithay, zero Slint, zero Plymouth, zero audio, zero Wine/Proton, zero Marketplace.
- **Strict Anti-Scope:** No custom deployment engine, no custom package manager, no custom update daemon; rely natively on `bootc` and bootloader BLS entries.
- **Base OS:** Fedora 44 Atomic (`quay.io/fedora/fedora-bootc:44@sha256:41ad34d292a531ebb9f82e00cd99c65ffa07111ffe865be781aa47f891ef2825`).
- **Filesystem & Mounts:** `/usr` mounted strictly read-only (`ro,nodev`); Btrfs subvolumes `@` (`/sysroot`), `@home` (`/var/home`), `@var` (`/var`).
- **Health Gate:** `nebu-boot-check.service` is a minimal deterministic oneshot service with `TimeoutSec=45`.
- **Decoupled Boot States:** `P0 Boot Completed` $\neq$ `P0 Deployment Healthy` $\neq$ `P1/P2 Graphical Session Ready`.
- **Environment Isolation:** Development in Proxmox CT 100 (Debian 13 trixie); preserve OpenClaw operations; QEMU TCG for local functional verification, document Proxmox VM UEFI/KVM.
- **Evidence Over Assertion:** Never claim PASS without verifiable logs from actual build, validation, and boot execution.

---

### Task 1: Environment & Tooling Validation

**Files:**
- Test: Environment binaries and kernel/virtualization features.

**Interfaces:**
- Consumes: Host Debian 13 environment inside CT 100.
- Produces: Installed virtualization/storage packages (`qemu-system-x86`, `ovmf`, `qemu-utils`, `btrfs-progs`), verified Docker engine.

- [ ] **Step 1: Install required virtualization and disk tools in CT 100**
Install packages with minimal footprint:
```bash
apt-get update && apt-get install -y --no-install-recommends qemu-system-x86 ovmf qemu-utils btrfs-progs
```

- [ ] **Step 2: Verify installed binaries and firmware paths**
Verify:
```bash
which qemu-system-x86_64 qemu-img mkfs.btrfs docker
ls -la /usr/share/OVMF/OVMF_CODE.fd || ls -la /usr/share/ovmf/OVMF.fd
```
Expected: All binaries exist, OVMF firmware available.

- [ ] **Step 3: Verify Docker daemon and OpenClaw container non-interference**
```bash
docker ps
```
Expected: Docker operational, existing `openclaw-searxng` container healthy and uninterrupted.

---

### Task 2: Engineering Governance & Agent Contract Update (`AGENTS.md`)

**Files:**
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: Milestone P0 finalized architecture.
- Produces: Binding instructions for coding agents regarding P0 execution, boundaries, and validation criteria.

- [ ] **Step 1: Update AGENTS.md with P0 execution directives**
Ensure Sections 1, 2, and 24 specify:
1. P0 is 100% headless with zero GUI / Wayland / Slint / Plymouth / Wine / Audio.
2. Build success is not boot success; boot success is not deployment health.
3. Minimal deterministic health gate assertions.
4. Native bootc and BLS usage; prohibition of custom deployment/update engines.
5. P0 PASS requires empirical test evidence.

- [ ] **Step 2: Verify AGENTS.md consistency**
Check that AGENTS.md contains no references allowing premature P1/P2 packages in P0.

---

### Task 3: P0 Build & Test Agent Skill (`skills/p0-build-test/SKILL.md`)

**Files:**
- Create: `skills/p0-build-test/SKILL.md`

**Interfaces:**
- Consumes: P0 workflow requirements.
- Produces: Reusable skill manual defining the complete agent workflow: `inspect -> implement -> build -> validate -> generate bootable artifact -> deploy/test -> boot -> health gate -> collect logs -> diagnose -> fix -> retest -> report`.

- [ ] **Step 1: Author skills/p0-build-test/SKILL.md**
Define:
- Purpose, Scope, Allowed changes, Forbidden changes.
- Architecture constraints (Fedora 44, bootc, headless, Btrfs subvolumes).
- Step-by-step verification pipeline.
- Common failure modes and diagnostics.
- Strict rule: Never claim PASS without evidence.

- [ ] **Step 2: Update skills/README.md to register p0-build-test skill**
Add `p0-build-test` to the skills catalog table in `skills/README.md`.

---

### Task 4: P0 Architecture & Operations Documentation

**Files:**
- Create: `docs/p0/P0_BUILD.md`
- Create: `docs/p0/P0_TESTING.md`
- Create: `docs/p0/P0_ARTIFACT.md`
- Create: `docs/operations/PROXMOX_TEST_ENV.md`

**Interfaces:**
- Consumes: ADR-0002, ADR-0008, ADR-0011, ADR-0014, System & Boot specifications.
- Produces: Comprehensive operator and developer manuals for P0 build, test, artifacts, and Proxmox deployment.

- [ ] **Step 1: Create docs/p0/P0_BUILD.md**
Document:
- Build prerequisites (Docker / Podman, disk space, network).
- Containerfile layer structure and cache optimization.
- Image digest pinning vs floating development tags.
- Build commands and error troubleshooting.

- [ ] **Step 2: Create docs/p0/P0_TESTING.md**
Document:
- Automated test matrix (build, validation, QEMU boot, health gate).
- QEMU TCG functional testing vs KVM hardware acceleration.
- Test failure diagnosis and log extraction.

- [ ] **Step 3: Create docs/p0/P0_ARTIFACT.md**
Document:
- OCI image artifact structure.
- GPT partition layout (ESP FAT32 at `/boot/efi`, Btrfs root at `/sysroot`).
- Btrfs subvolume layout (`@`, `@home`, `@var`).
- BLS configuration files and grubenv layout.

- [ ] **Step 4: Create docs/operations/PROXMOX_TEST_ENV.md**
Document:
- CT 100 development container characteristics (Debian 13 trixie, Docker, non-KVM).
- Proxmox VM configuration for target testing (machine `q35`, BIOS `OVMF`, SCSI controller `virtio-scsi-single`, disk discard/ssd emulation, CPU `host`).
- LXC-to-Proxmox VM testing workflow.

---

### Task 5: Base OS Configuration Files & Kernel Tunables

**Files:**
- Create: `config/dracut/50-nebu.conf`
- Create: `config/sysctl/99-nebuos-p0.conf`
- Create: `config/systemd/nebu-base.target`
- Create: `config/selinux/config`

**Interfaces:**
- Consumes: 00-system-specification.md, 01-boot-specification.md.
- Produces: System configuration assets copied into `Containerfile.p0`.

- [ ] **Step 1: Create config/dracut/50-nebu.conf**
```conf
# NebuOS Dracut Initramfs Configuration (Milestone P0)
# Enforce minimal storage drivers and explicitly omit Plymouth
add_dracutmodules+=" btrfs systemd systemd-initrd "
omit_dracutmodules+=" plymouth "
drivers+=" nvme ahci virtio_blk virtio_scsi btrfs "
compress="zstd"
```

- [ ] **Step 2: Create config/sysctl/99-nebuos-p0.conf**
```conf
# NebuOS P0 Kernel Tunables
vm.swappiness=10
vm.dirty_ratio=15
vm.dirty_background_ratio=5
fs.inotify.max_user_watches=524288
```

- [ ] **Step 3: Create config/systemd/nebu-base.target**
Define `nebu-base.target` for headless baseline synchronization.

- [ ] **Step 4: Create config/selinux/config**
Set `SELINUX=permissive` and `SELINUXTYPE=targeted` for P0 audit baseline.

---

### Task 6: Deterministic Health Gate (`nebu-boot-check`)

**Files:**
- Create: `config/scripts/nebu-boot-check`
- Create: `config/systemd/nebu-boot-check.service`

**Interfaces:**
- Consumes: ADR-0014 Section 5.5, 01-boot-specification.md Section 8.2.
- Produces: Oneshot deterministic health check service asserting all 7 P0 criteria and writing `boot_success=1` to `grubenv`.

- [ ] **Step 1: Author config/scripts/nebu-boot-check**
Implement deterministic script checking:
1. PID 1 / systemd is operational (`systemctl is-system-running` is `running` or `degraded`).
2. Root filesystem is mounted (`findmnt /`).
3. Critical mounts are active (`/var`, `/proc`, `/sys`, `/dev`).
4. Read-only `/usr` check (`touch /usr/bin/.test` must fail).
5. Sufficient disk space ($\ge 500$ MB free on `/`).
6. Baseline network link active or loopback up.
7. Critical headless units active (`systemd-journald`, `dbus`).
8. Zero critical unit failures (filter non-critical units).
9. Write `boot_success=1` and `boot_counter=0` to `grubenv` (if grubenv path exists).
10. Safely disarm watchdog (`echo -n V > /dev/watchdog` if `/dev/watchdog` exists).

- [ ] **Step 2: Author config/systemd/nebu-boot-check.service**
```ini
[Unit]
Description=NebuOS P0 Deterministic Post-Boot Health Verification
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

---

### Task 7: P0 Containerfile (`Containerfile.p0` & `Containerfile`)

**Files:**
- Create: `Containerfile.p0`
- Create: `Containerfile` (symlink or copy pointing to `Containerfile.p0`)

**Interfaces:**
- Consumes: Fedora 44 bootc base image, config files from Task 5 and Task 6.
- Produces: Valid OCI container image representing NebuOS Milestone P0 Foundation OS.

- [ ] **Step 1: Author Containerfile.p0**
```dockerfile
FROM quay.io/fedora/fedora-bootc:44@sha256:41ad34d292a531ebb9f82e00cd99c65ffa07111ffe865be781aa47f891ef2825

LABEL org.nebu.os.name="NebuOS" \
      org.nebu.os.version="0.1.0-p0" \
      org.nebu.os.milestone="P0" \
      org.nebu.os.headless="true"

# Install minimal headless P0 package set
RUN dnf -y install --setopt=install_weak_deps=False \
    kernel-core \
    kernel-modules \
    btrfs-progs \
    systemd \
    NetworkManager \
    util-linux \
    shadow-utils \
    iproute \
    dracut \
    grub2-efi-x64 \
    grub2-tools \
    efibootmgr \
    && dnf clean all

# Copy system configurations
COPY config/dracut/50-nebu.conf /etc/dracut.conf.d/50-nebu.conf
COPY config/sysctl/99-nebuos-p0.conf /etc/sysctl.d/99-nebuos-p0.conf
COPY config/systemd/nebu-base.target /usr/lib/systemd/system/nebu-base.target
COPY config/systemd/nebu-boot-check.service /usr/lib/systemd/system/nebu-boot-check.service
COPY config/scripts/nebu-boot-check /usr/libexec/nebu/nebu-boot-check
COPY config/selinux/config /etc/selinux/config

# Permissions and systemd enablement
RUN chmod 755 /usr/libexec/nebu/nebu-boot-check && \
    systemctl enable nebu-boot-check.service && \
    systemctl enable NetworkManager.service && \
    systemctl set-default multi-user.target

# Regenerate Dracut initramfs without Plymouth
RUN KERNEL_VER=$(rpm -q --qf "%{VERSION}-%{RELEASE}.%{ARCH}\n" kernel-core | head -n 1) && \
    dracut -f --kver "${KERNEL_VER}" /usr/lib/modules/"${KERNEL_VER}"/initramfs.img
```

- [ ] **Step 2: Link Containerfile to Containerfile.p0**
```bash
ln -sf Containerfile.p0 Containerfile
```

---

### Task 8: Automation Scripts

**Files:**
- Create: `scripts/build-p0.sh`
- Create: `scripts/deploy-p0.sh`
- Create: `scripts/test-p0.sh`
- Create: `scripts/p0-ci.sh`

**Interfaces:**
- Consumes: Docker engine, QEMU, OVMF, `Containerfile.p0`.
- Produces: Executable, idempotent automation scripts for building, deploying to raw disk, testing under QEMU, and running full CI.

- [ ] **Step 1: Create scripts/build-p0.sh**
Builds the container image tagged as `nebuos:p0-latest`. Idempotent, checks Docker/Podman, logs build time and image size.

- [ ] **Step 2: Create scripts/deploy-p0.sh**
Generates a bootable raw disk image (`target/nebuos-p0.raw`) with GPT, FAT32 ESP, and Btrfs root containing `@` subvolume populated from the container image.

- [ ] **Step 3: Create scripts/test-p0.sh**
Executes QEMU with UEFI (OVMF), serial console logging to `target/boot.log`, timeout handling (120s for TCG), and parses the serial output for:
- Kernel boot & Dracut pivot
- Btrfs root mount
- systemd reaching `multi-user.target`
- `nebu-boot-check` PASS
- TTY login prompt

- [ ] **Step 4: Create scripts/p0-ci.sh**
Chains: `build-p0.sh` -> image validation -> `deploy-p0.sh` -> `test-p0.sh` -> generates test report summary.

- [ ] **Step 5: Make all scripts executable**
```bash
chmod +x scripts/*.sh
```

---

### Task 9: Execution — Image Build & Container Validation

**Files:**
- Execute: `scripts/build-p0.sh`
- Output: `target/build.log`, container image `nebuos:p0-latest`

- [ ] **Step 1: Execute build-p0.sh**
Run: `scripts/build-p0.sh`
Expected: Build succeeds with code 0.

- [ ] **Step 2: Validate container filesystem and packages**
Run validation checks inside the built container:
- Confirm no GUI/Wayland/Slint/Plymouth packages installed.
- Confirm `/usr/libexec/nebu/nebu-boot-check` exists and is executable.
- Confirm `nebu-boot-check.service` is enabled in `multi-user.target`.
- Confirm dracut initramfs was generated.

---

### Task 10: Execution — Disk Artifact Generation & Automated Boot Verification

**Files:**
- Execute: `scripts/deploy-p0.sh`
- Execute: `scripts/test-p0.sh`
- Output: `target/nebuos-p0.raw`, `target/boot.log`, `target/test-results.json`

- [ ] **Step 1: Generate bootable raw disk artifact**
Run: `scripts/deploy-p0.sh`
Expected: `target/nebuos-p0.raw` created with valid GPT, ESP, and Btrfs partitions.

- [ ] **Step 2: Run automated QEMU boot verification**
Run: `scripts/test-p0.sh`
Expected: QEMU boots image via OVMF UEFI, serial log captures boot sequence, `nebu-boot-check` runs, login prompt appears, test exits code 0.

---

### Task 11: Rollback & Recovery Verification

**Files:**
- Test: Rollback state machine and boot counter logic in `target/boot.log` and script assertions.

- [ ] **Step 1: Verify boot counter decrement and failure recovery handling**
Assert that:
- Fresh deployment has `boot_counter` initialized.
- `nebu-boot-check` resets `boot_counter=0` and writes `boot_success=1`.
- Simulated health failure does not cause infinite loop; triggers fallback or recovery target.

---

### Task 12: Project State Update, Knowledge Graph, & Implementation Report

**Files:**
- Modify: `PROJECT_STATE.md`
- Modify: `HANDOFF.md`
- Create: `docs/p0/P0_IMPLEMENTATION_REPORT.md`
- Run: `graphify update .`

- [ ] **Step 1: Update PROJECT_STATE.md**
Update milestone status to reflect P0 Implementation completed with test evidence.

- [ ] **Step 2: Update HANDOFF.md**
Document implemented files, build results, test results, and transfer state.

- [ ] **Step 3: Run graphify update .**
Keep knowledge graph current.

- [ ] **Step 4: Author docs/p0/P0_IMPLEMENTATION_REPORT.md**
Compile comprehensive final report with build metrics, test logs, validation results, and PASS status.
