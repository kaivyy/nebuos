# Phase P0: Foundation Specification — NebuOS

**Status:** APPROVED  
**Phase:** P0  
**Target Duration:** Sprint 1–2  

---

## 1. Objective
Establish the absolute minimal, verifiable bootable base operating system for NebuOS. P0 proves that the Fedora Atomic container image builds reproducibly in CI, deploys to disk via `bootc`, boots on physical/virtual x86_64 hardware to a serial/virtual terminal (`agetty`), initializes systemd PID 1 cleanly, establishes Btrfs subvolume mounts, brings up basic networking, and provides core diagnostic tools.

P0 is intentionally kept extremely small and focused.

## 2. Scope (What's IN)
- Minimal `Containerfile.p0` based on `quay.io/fedora/fedora-bootc:44`.
- Standard upstream Linux kernel 6.14+ (Fedora 44 standard).
- Btrfs subvolume filesystem topology (`@`, `@home`, `@var`).
- Read-only `/usr` sysroot mount validation.
- Minimal package set: `systemd`, `util-linux`, `NetworkManager`, `iproute`, `btrfs-progs`, `dracut`.
- Boot to text console / TTY (`multi-user.target`).
- Virtual terminal diagnostics: `journalctl`, `systemd-analyze blame`, `dmesg`.
- Local QEMU test automation script (`scripts/test-p0-boot.sh`).

## 3. Anti-Scope (What's NOT IN)
- NO graphical display server (`nebu-compositor` or Wayland).
- NO desktop shell (`nebu-shell`).
- NO Mesa GPU acceleration or DRM modesetting validation.
- NO Wine, Proton, DXVK, or Windows compatibility layers.
- NO PipeWire audio server or Bluetooth.
- NO custom Rust application daemons (`nebu-runtime-daemon`).
- NO graphical installers or software stores.

## 4. Dependencies
- Container build toolchain (`podman` / `buildah`).
- `bootc` >= 1.1.0.
- Upstream Fedora 44 package repositories.
- QEMU / KVM for virtual verification.

## 5. Deliverables
- `Containerfile.p0` located at repository root.
- System configuration files:
  - `/etc/sysctl.d/99-nebuos-p0.conf`
  - `/etc/dracut.conf.d/50-nebu.conf`
- Build script `scripts/build-p0-image.sh`.
- Test harness `scripts/test-p0-boot.sh`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P0-01 (Build Reproducibility):** `podman build -f Containerfile.p0` completes with exit code 0 in under 5 minutes on CI runner.
2. **EC-P0-02 (Boot Verification):** QEMU boots `Containerfile.p0` to login prompt (`login:`) in <= 3.0 seconds (kernel + userspace).
3. **EC-P0-03 (Immutability Gate):** Attempting `touch /usr/bin/testfile` fails with `Read-only file system` error.
4. **EC-P0-04 (Network Readiness):** `NetworkManager` starts and acquires DHCP IPv4 address within 2.0s of boot.
5. **EC-P0-05 (Zero Failed Services):** `systemctl --failed` outputs `0 loaded units listed`.

## 7. Known Risks & Mitigations
- **Risk:** Missing kernel modules in dracut initramfs causes boot hang on non-standard storage controllers.
  - *Mitigation:* Include standard storage driver bundle (`nvme`, `ahci`, `virtio_blk`, `virtio_scsi`) in `dracut.conf`.
