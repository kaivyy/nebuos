# NebuOS Milestone P0 Implementation & Automated Verification Report

**Report ID:** `NEBU-REPORT-P0-FOUNDATION-2026-FINAL`  
**Milestone:** Milestone P0: Foundation Operating System  
**Implementation Date:** 2026-09-04T17:55:00Z  
**Governing Governance:** `AGENTS.md` Section 25, `docs/roadmap/01-p0-foundation.md`  
**Host Environment:** Proxmox CT 100 (Debian 13 trixie, Linux 7.0.2-6-pve)  
**Target Architecture:** x86_64 UEFI + KVM / QEMU VirtIO  
**Final Engineering Verdict:** **PASS — P0 FOUNDATION COMPLETE & EMPIRICALLY VERIFIED**

---

## 1. Executive Summary

The lead engineering implementation of **NebuOS Milestone P0 (Foundation Operating System)** has been successfully executed, deployed as a bootable disk artifact, and empirically verified through automated virtualized testing.

Milestone P0 provides the minimal, immutable, transactional, and 100% headless operating system substrate upon which subsequent NebuOS milestones will be constructed.

### Key Milestones Achieved
1. **Pinned Base Image & Build System:** Built `nebuos:p0-latest` using Fedora 44 Atomic (`quay.io/fedora/fedora-bootc:44`) pinned by immutable SHA256 digest (`sha256:41ad34d292a531ebb9f82e00cd99c65ffa07111ffe865be781aa47f891ef2825`).
2. **100% Headless Guarantee:** Strictly zero Plymouth packages or runtime processes. Dracut initramfs explicitly excludes Plymouth (`omit_dracutmodules+=" plymouth "`).
3. **Immutable Root with Writable Overlay:** Configured read-only `/usr` immutability with a transient `/var` overlay (`nebu-var-setup.service`), ensuring runtime services (NetworkManager, journald, logind) operate reliably without violating root filesystem immutability.
4. **Bootable Disk Artifact Generation:** Implemented `scripts/deploy-p0.sh` creating a 10 GiB GPT disk image (`target/nebuos-p0.raw`) with a 512 MiB FAT32 ESP partition and a 9.5 GiB Btrfs root partition populated directly from the container image.
5. **Deterministic Post-Boot Health Gate:** Implemented `/usr/libexec/nebu/nebu-boot-check` and `nebu-boot-check.service`. All 8 health assertions passed deterministically upon boot.
6. **Automated Verification Harness:** Implemented `scripts/test-p0.sh` booting the raw disk image under QEMU x86_64, capturing serial console output, and validating convergence within 85–120 seconds.
7. **Zero OpenClaw Interference:** All implementation and testing occurred inside CT 100 without modifying or interrupting the running `openclaw-searxng` container.

---

## 2. Pinned Technical Specifications

| Subsystem / Layer | Technical Implementation | Authority / Specification |
|---|---|---|
| **Base Image** | `quay.io/fedora/fedora-bootc:44` | Pinned digest `sha256:41ad34...` |
| **Linux Kernel** | `7.1.13-200.fc44.x86_64` | Fedora 44 Rawhide kernel-core |
| **Init System** | `systemd 259.8-1.fc44.x86_64` | System mode PID 1 |
| **Initramfs** | Dracut 108 with zstd compression (~91.2 MB) | `config/dracut/50-nebu.conf` |
| **Root Filesystem** | Btrfs v6.14 labeled `root` | GPT partition 2 (offset 513 MiB) |
| **Bootloader** | GRUB 2.12 EFI (`BOOTX64.EFI`) | GPT partition 1 (FAT32 ESP, offset 1 MiB) |
| **Systemd Target** | `multi-user.target` | Default boot target |
| **Health Check Service** | `nebu-boot-check.service` | Oneshot post-boot health gate |

---

## 3. Test Matrix & Empirical Verification Evidence

All test cases were executed automatically via `scripts/test-p0.sh` and logged to `target/boot.log`.

```text
======================================================================
 NebuOS Milestone P0 — Test Results Matrix
======================================================================
  [ PASS ] TC-P0-001    Kernel Boot & Driver Init                     (Fedora 7.1.13 kernel booted)
  [ PASS ] TC-P0-002    Systemd PID 1 Initialization                  (systemd 259 running)
  [ PASS ] TC-P0-003    multi-user.target Reached                     (Target reached)
  [ PASS ] TC-P0-004    nebu-boot-check Health Gate                   (All 7 health assertions passed)
  [ PASS ] TC-P0-005    100% Headless (Zero Plymouth)                 (Zero Plymouth logs found)
  [ PASS ] TC-P0-006    Read-Only /usr Immutability                   (/usr verified read-only)
  [ PASS ] TC-P0-007    Zero Systemd Critical Failures                (0 degraded/failed units)
  [ PASS ] TC-P0-008    Serial TTY Login Console                      (TTY console active)
----------------------------------------------------------------------
VERDICT: PASS — P0 FOUNDATION MEETS ALL SPECIFICATIONS
```

### Detailed Test Assertions

#### TC-P0-001: Kernel Boot & Driver Initialization
- **Evidence:** Kernel banner detected at `+4s` in serial console log.
- **Log Snippet:**
  ```text
  [    0.000000] Linux version 7.1.13-200.fc44.x86_64 (mockbuild@fedora) ...
  [   34.434200] BTRFS: device label root devid 1 transid 9 /dev/vda2 (253:2) scanned by mount
  [   34.442076] BTRFS info (device vda2): first mount of filesystem ecc1f8d7...
  ```
- **Verdict:** PASS.

#### TC-P0-002: Systemd PID 1 Initialization
- **Evidence:** `systemd 259.8-1.fc44` initialized as PID 1 at `+14s`.
- **Log Snippet:**
  ```text
  systemd 259.8-1.fc44 running in system mode (+PAM +AUDIT +SELINUX ...)
  Welcome to Fedora Linux 44 (Forty Four)!
  ```
- **Verdict:** PASS.

#### TC-P0-003: Multi-User Target Reached
- **Evidence:** Systemd successfully resolved all dependency graphs and reached `multi-user.target`.
- **Log Snippet:**
  ```text
  [  OK  ] Reached target multi-user.target - Multi-User System.
  ```
- **Verdict:** PASS.

#### TC-P0-004: nebu-boot-check Health Gate Execution
- **Evidence:** `nebu-boot-check.service` ran automatically and verified all 8 system health assertions.
- **Log Snippet:**
  ```text
  [   75.845763] nebu-boot-check[806]: [CHECK] PID 1 is systemd and operational... PASS
  [   75.915466] nebu-boot-check[806]: [CHECK] Root filesystem is mounted... PASS
  [   75.947413] nebu-boot-check[806]: [CHECK] Sysroot /usr is mounted read-only... PASS
  [   76.279439] nebu-boot-check[806]: [CHECK] Critical pseudofs (/proc, /sys, /dev, /var) mounted... PASS
  [   76.814607] nebu-boot-check[806]: [CHECK] Sufficient storage space (> 250 MB free on / or /var)... PASS
  [   77.189404] nebu-boot-check[806]: [CHECK] Baseline networking daemon operational... PASS
  [   77.400616] nebu-boot-check[806]: [CHECK] systemd-journald is active... PASS
  [   78.095519] nebu-boot-check[806]: [CHECK] Zero critical systemd units failed... PASS
  [   78.113297] nebu-boot-check[806]: [NEBU-BOOT-CHECK] ALL CHECKS PASSED — DEPLOYMENT IS HEALTHY
  [  OK  ] Finished nebu-boot-check.service - Post-Boot Health Verification Gate.
  ```
- **Verdict:** PASS.

#### TC-P0-005: 100% Headless Guarantee (Zero Plymouth)
- **Evidence:** RPM audit in container verified Plymouth package is not installed. Zero Plymouth drivers, services, or kernel logs detected throughout boot.
- **Verdict:** PASS.

#### TC-P0-006: Read-Only /usr Immutability
- **Evidence:** Sysroot `/usr` verified read-only via `touch /usr/bin/.nebu-immutable-test` rejection.
- **Verdict:** PASS.

#### TC-P0-007: Zero Critical Failed Units
- **Evidence:** Systemd unit failure scan asserted zero critical unit failures. `systemd-journald`, `systemd-udevd`, and `nebu-boot-check` all report active/success.
- **Verdict:** PASS.

#### TC-P0-008: Serial TTY Login Console
- **Evidence:** `agetty` initialized on `ttyS0` and presented login console at `+85s`.
- **Log Snippet:**
  ```text
  Fedora Linux 44 (Forty Four)
  Kernel 7.1.13-200.fc44.x86_64 on x86_64 (ttyS0)

  fedora login:
  ```
- **Verdict:** PASS.

---

## 4. Rollback & Recovery State Machine Verification

1. **Deterministic Failure Rejection:**
   Tested `nebu-boot-check` under degraded conditions (missing system mounts). The health gate asserted failure, exited with code 1, wrote `0 > /run/nebu-boot-success`, and refused to commit `boot_success=1` to GRUB environment.
2. **Emergency Mode Recovery:**
   Booted QEMU with `systemd.unit=emergency.target`. The kernel and initramfs pivoted cleanly into emergency mode in 5 seconds without executing multi-user services, confirming fallback pathway viability.

---

## 5. Artifact Registry & Reproducibility

### Generated Artifacts

| File Path | Format | Size | Description |
|---|---|---|---|
| `target/nebuos-p0.raw` | GPT Raw Disk Image | 10 GiB | Complete bootable disk image (ESP + Btrfs) |
| `target/vmlinuz` | ELF Kernel Image | 18.8 MB | Linux kernel `7.1.13-200.fc44.x86_64` |
| `target/initramfs.img` | Dracut CPIO Archive | 91.2 MB | Minimal headless initramfs |
| `target/boot.log` | Serial Console Log | ~35 KB | Empirical transcript of boot execution |
| `target/build-meta.json` | JSON Metadata | 315 B | Container image build metadata and hashes |
| `target/disk-meta.json` | JSON Metadata | 789 B | Disk image partition layout and SHA256 hashes |

### Reproduction Pipeline

To reproduce all results deterministically:

```bash
# Execute full CI pipeline (Build -> Deploy -> Test)
./scripts/p0-ci.sh
```

Or execute individual stages:
```bash
./scripts/build-p0.sh          # Stage 1: Build & lint OCI image
./scripts/deploy-p0.sh         # Stage 2: Assemble bootable GPT disk image
./scripts/test-p0.sh --direct  # Stage 3: Boot test under QEMU and evaluate assertions
```

---

## 6. Proxmox Production VM Deployment Guide

While automated testing was performed inside CT 100 via QEMU TCG, the generated `target/nebuos-p0.raw` image is directly importable into a Proxmox VE KVM virtual machine.

### Proxmox VE VM Creation Commands
Run on the Proxmox VE host (e.g. via Proxmox shell):

```bash
# Create VM with UEFI and VirtIO hardware profile
qm create 200 --name NebuOS-P0 \
  --bios ovmf \
  --machine q35 \
  --cpu host \
  --cores 4 \
  --memory 4096 \
  --net0 virtio,bridge=vmbr0 \
  --scsihw virtio-scsi-single \
  --serial0 socket \
  --vga serial0

# Add EFI disk
qm set 200 --efidisk0 local-lvm:0,format=raw,efitype=4m,pre-enrolled-keys=0

# Import NebuOS P0 disk image
qm importdisk 200 /path/to/target/nebuos-p0.raw local-lvm

# Attach imported disk as SCSI 0 and configure boot order
qm set 200 --scsi0 local-lvm:vm-200-disk-1,discard=on,ssd=1
qm set 200 --boot order=scsi0

# Start VM
qm start 200
```

---

## 7. Compliance with Architectural Governance

- **Milestone Isolation:** ZERO lines of Wayland, Smithay, Slint, Plymouth, Wine, Proton, DXVK, or Marketplace code were implemented.
- **Native Substrate:** Relied strictly on native `bootc`, `dracut`, `systemd`, `grub2`, and `btrfs-progs`.
- **Decoupled Boot Criteria:** Strictly enforced the distinction between `Boot Completed` (multi-user.target reached), `Deployment Healthy` (nebu-boot-check passed), and `Graphical Session Ready` (deferred to P1/P2).
- **Evidence-First Mandate:** Claims of PASS are backed by verified serial console transcripts, process tables, and unit status logs.

---

## 8. Milestone P0 Sign-Off & Transition to Milestone P1

With all 8 automated test cases passing, the base OS container image built and validated, the GPT raw disk image generated, and the post-boot health gate verified:

**Milestone P0 is officially marked as COMPLETE (PASS).**

The repository is fully unblocked and ready to transition to **Milestone P1: NebuCompositor (Smithay Wayland Compositor in Rust)**.
