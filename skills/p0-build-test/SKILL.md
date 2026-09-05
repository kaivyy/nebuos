# P0 Build & Boot Verification Skill — NebuOS

## 1. Purpose
Governs the end-to-end implementation, container image building, disk artifact generation, and automated UEFI boot testing for **Milestone P0: Foundation Operating System**.

## 2. Scope
Applies strictly to Milestone P0 engineering tasks. Enforces that no agent claims success without verifiable empirical logs.

## 3. Relevant Documentation
- `docs/roadmap/01-p0-foundation.md`: Milestone P0 execution roadmap.
- `docs/specification/00-system-specification.md`: Base system packages and tunables.
- `docs/specification/01-boot-specification.md`: UEFI GOP, Dracut, GRUB BLS, and health gate.
- `docs/decisions/ADR-0002-fedora-base.md`: Fedora 44 and bootc foundation.
- `docs/decisions/ADR-0014-boot-experience-and-graphical-handoff.md`: Boot experience and decoupled health criteria.
- `docs/p0/P0_BUILD.md`: Build instructions.
- `docs/p0/P0_TESTING.md`: Test harness execution.
- `docs/p0/P0_ARTIFACT.md`: Disk image layout and partition specifications.
- `docs/operations/PROXMOX_TEST_ENV.md`: Proxmox VM & CT 100 specifications.

## 4. Complete Agent Workflow
Every agent working on P0 implementation must follow this deterministic 13-stage workflow:

```
inspect ──> implement ──> build ──> validate ──> generate bootable artifact
   │                                                    │
   ▼                                                    ▼
report <── retest <── fix <── diagnose <── collect logs <── health gate <── boot <── deploy/test
```

1. **Inspect:** Examine existing repository state, environment constraints (Docker/Podman, QEMU, OVMF, `/dev/kvm`), and task dependencies.
2. **Implement:** Write minimal, surgical configuration files, systemd units, and scripts. Do NOT introduce bloated dependencies or premature milestone code.
3. **Build:** Execute container build (`scripts/build-p0.sh`) using pinned base image `quay.io/fedora/fedora-bootc:44@sha256:...`.
4. **Validate:** Perform in-container validation (verify package manifest, dracut initramfs existence, permissions, and systemd enabled units).
5. **Generate Bootable Artifact:** Run `scripts/deploy-p0.sh` to produce a bootable raw disk image (`target/nebuos-p0.raw`) with GPT, FAT32 ESP, and Btrfs subvolumes (`@`, `@home`, `@var`).
6. **Deploy / Test:** Launch `scripts/test-p0.sh` to boot the artifact under QEMU with OVMF UEFI firmware.
7. **Boot:** Monitor kernel boot, Dracut initramfs pivot, root filesystem mount, and systemd `multi-user.target` reach.
8. **Health Gate:** Assert that `nebu-boot-check.service` executes deterministically within 45s, passes all assertions, and commits `boot_success=1` to `grubenv`.
9. **Collect Logs:** Extract serial console output, systemd journal excerpt, and test exit codes to `target/boot.log`.
10. **Diagnose:** If boot or health check fails, analyze failure root cause (e.g. missing driver in dracut, SELinux denial, mount failure).
11. **Fix:** Apply surgical correction to Containerfile, dracut config, or health check script.
12. **Retest:** Rerun build and test harness from Step 3 until all assertions pass.
13. **Report:** Compile final report with empirical evidence, log snippets, and exact metrics.

## 5. Allowed Changes
- Creating and modifying `Containerfile.p0`, `Containerfile`.
- Authoring configuration files under `config/` (dracut, sysctl, systemd units, selinux).
- Authoring and maintaining automation scripts under `scripts/` (`build-p0.sh`, `deploy-p0.sh`, `test-p0.sh`, `p0-ci.sh`).
- Updating P0 documentation under `docs/p0/` and `docs/operations/`.

## 6. Forbidden Changes (Strict Anti-Scope)
- **NO GUI IN P0:** Never install Wayland, Smithay, Slint, Iced, Plymouth, X11, or Weston. P0 is 100% headless.
- **NO AUDIO IN P0:** Never install PipeWire, PulseAudio, or ALSA sound servers.
- **NO COMPATIBILITY LAYERS IN P0:** Never install Wine, Proton, DXVK, or VKD3D.
- **NO CUSTOM DEPLOYMENT ENGINE:** Never write custom package managers, custom update daemons, or custom deployment engines. Rely 100% on native `bootc` and GRUB BLS.
- **NO FABRICATION OF TEST RESULTS:** Never claim "PASS" without actual QEMU or VM execution logs.

## 7. Architecture Constraints
- Base Platform: Fedora Linux 44 (`quay.io/fedora/fedora-bootc:44`).
- Kernel: Linux 6.14+ standard.
- Initramfs: Dracut with `omit_dracutmodules+=" plymouth "` and storage drivers (`nvme`, `ahci`, `virtio_blk`, `virtio_scsi`, `btrfs`).
- Storage: Btrfs subvolumes (`@` on `/sysroot`, `@home` on `/var/home`, `@var` on `/var`).
- Sysroot Immutability: `/usr` mounted strictly read-only (`ro,nodev`).
- Health Gate: `nebu-boot-check.service` (oneshot, timeout 45s).
- Console: Serial console `ttyS0` and virtual terminal `tty1` via `agetty`.

## 8. Verification Invariants
- `podman build` or `docker build` succeeds with exit code 0.
- Raw disk image `nebuos-p0.raw` has valid GPT partition table and Btrfs subvolumes.
- QEMU UEFI boot reaches `login:` prompt on serial console.
- `nebu-boot-check` emits `STATUS: PASS` and writes `boot_success=1`.
- Immutability check confirms `/usr` cannot be modified by root.

## 9. Common Failure Modes & Diagnostics
- **Dracut Missing Storage Modules:** Kernel boots but cannot mount root subvolume `@`. Fix: Ensure `drivers+=" virtio_blk virtio_scsi btrfs "` in `config/dracut/50-nebu.conf`.
- **Read-Only Test False Positive:** Testing write on `/tmp` or `/var` instead of `/usr`. Fix: Test strictly on `/usr/bin/testfile`.
- **Health Gate Timeout:** `nebu-boot-check.service` hangs waiting for network or non-existent daemon. Fix: Verify timeout is 45s and checks are non-blocking.
