# Base OS & System Services Skill — NebuOS

## 1. Purpose
Governs the creation, configuration, and maintenance of the Fedora Linux 44 Atomic / bootc base operating system, Btrfs subvolumes, systemd services, dracut initramfs, and bootloader integration.

## 2. Scope
Applies primarily to Milestone P0 (Foundation OS) and Milestone P8 (Production Hardening).

## 3. Relevant Documentation
- `docs/roadmap/01-p0-foundation.md`: Milestone P0 execution plan.
- `docs/specification/00-system-specification.md`: Base image package manifests.
- `docs/specification/01-boot-specification.md`: dracut, GRUB2, and BLS sequence.
- `docs/specification/03-filesystem-specification.md`: Btrfs subvolumes and mount table.
- `docs/decisions/ADR-0002-fedora-base.md`: Fedora Linux 44 base OS and bootc.
- `docs/decisions/ADR-0008-atomic-updates.md`: Atomic deployments and Btrfs subvolumes.
- `docs/decisions/ADR-0011-os-image-updates-and-rollback.md`: OS updates, image model, and rollback.
- `docs/decisions/ADR-0014-boot-experience-and-graphical-handoff.md`: Boot experience and graphical handoff.

## 4. Allowed Changes
- Authoring and updating `Containerfile.p0` and future container build layers.
- Configuring dracut configuration files in `/etc/dracut.conf.d/`.
- Creating systemd unit files and presets in `/usr/lib/systemd/system/`.
- Authoring automated QEMU boot test scripts in `tests/integration/`.

## 5. Forbidden Changes
- **ZERO GUI PACKAGES IN P0:** Never add Wayland, Smithay, Slint, Weston, X11, or Mesa 3D packages to the P0 container manifest.
- **ZERO PLYMOUTH IN P0:** Never install Plymouth or graphical splash packages in P0. Dracut must explicitly omit Plymouth (`omit_dracutmodules+=" plymouth "`) in accordance with ADR-0014. P0 is 100% headless.
- **ZERO WINE IN P0:** Never install Wine or Proton packages in the P0 container.
- **NO INSTALLERS IN P0:** Never add graphical installers, store frontends, or desktop setup wizards in P0.
- **NO PREMATURE MILESTONE IMPLEMENTATION:** Never implement P1–P7 components during P0 tasks.
- **NO HOST MODIFICATIONS:** Never execute partitioning or bootloader commands against the development host.

## 6. Architecture Constraints
- Base Platform: Fedora Linux 44 (`quay.io/fedora/fedora-bootc:44`).
- Kernel: Linux kernel 6.14+ (Fedora 44 standard).
- Initramfs: dracut v102+ with `nvme`, `ahci`, `virtio_blk`, `virtio_scsi`, `btrfs`, `systemd-initrd`, and `omit_dracutmodules+=" plymouth "`.
- Silent Boot Kernel Arguments (Normal Boot): `quiet splash loglevel=3 rd.systemd.show_status=false systemd.show_status=false vt.global_cursor_default=0 udev.log_level=3`.
- Diagnostic Boot Entry: BLS entry with `debug loglevel=7 console=tty1` for troubleshooting.
- Storage: Btrfs subvolumes (`@` root sysroot, `@home` at `/var/home`, `@var` at `/var`).
- Sysroot Immutability: `/usr` mounted strictly read-only (`ro,nodev`).
- Init & Supervision: systemd v256+ with multi-user target and unified cgroups v2.
- Deterministic P0 Health Gate (ADR-0014): `nebu-boot-check` executes as a minimal deterministic oneshot service (timeout 45s) verifying PID 1 health, root and critical mounts, network readiness, headless services, and 0 failed critical units before committing `boot_success=1`. Disarms watchdog only if verified and active.
- Boot Counter Ownership: `boot_counter` in `grubenv` is strictly orchestration state for rollback triggering; coding agents must never build custom deployment or package engines, but rely natively on `bootc` and BLS boot entries.
- Security Baseline: SELinux permissive mode in P0 to audit boot denials; enforcing mode deferred to P5.
- Target Architecture: x86_64 UEFI with Boot Loader Specification (BLS Type 1).
- Console: TTY login on `tty1` and `ttyS0` via `agetty`.

## 7. Implementation Guidance
- Base image: Extend `quay.io/fedora/fedora-bootc:44`.
- Digest Pinning: Production and release builds must use immutable SHA-256 digest pinning (`quay.io/fedora/fedora-bootc:44@sha256:...`). Using `fedora:latest` or unversioned tags as production identity is strictly prohibited.
- In P0, configure `SELINUX=permissive` in `/etc/selinux/config` to prevent false boot denials.
- Keep package manifest minimal: use the core headless packages specified in `01-p0-foundation.md`.

## 8. Verification
- `podman build -t nebu-os:p0 -f Containerfile.p0 .` builds cleanly.
- `bootc container lint` reports 0 errors.
- dracut initramfs includes core storage drivers (`nvme`, `ahci`, `virtio_blk`, `virtio_scsi`, `btrfs`).
- Automated QEMU boot test boots to `agetty` login prompt (reference engineering target <= 3.5s, non-hard failure gate) with idle RAM < 150 MB RSS.
- `systemctl --failed` reports 0 failed units.
- Dependency scan confirms zero forbidden packages (Wayland, Smithay, Slint, Wine, Proton, audio, GUI).
- Empirical Values: Actual image size and initramfs byte size must be captured from execution output, never fabricated.

## 9. Common Failure Modes
- dracut omitting Btrfs module, causing root subvolume mount timeout and emergency shell drop.
- Forgetting `rootflags=subvol=@` in kernel parameters.
- Accidental inclusion of GUI or Wine dependencies violating P0 anti-scope.

## 10. Handoff Requirements
- Record QEMU boot log and `systemd-analyze` timing report in `HANDOFF.md`.
- Report total container image size, exact digest hash, and idle memory RSS.
