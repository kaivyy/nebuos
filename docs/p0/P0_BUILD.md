# NebuOS Milestone P0 Build Guide

**Status:** APPROVED  
**Target Milestone:** Milestone P0: Foundation Operating System  
**Authority:** Principal OS Architect, bootc/Ostree Engineer  

---

## 1. Overview
This document specifies the container-based build procedure for NebuOS Milestone P0 Foundation Operating System. NebuOS extends Fedora Linux 44 Atomic using native `bootc` container image conventions.

## 2. Prerequisites
Building NebuOS P0 requires:
- **Host OS:** Linux x86_64 (Debian 13 trixie, Ubuntu 24.04, or Fedora 44).
- **Container Engine:** Docker Engine (>= 24.0) or Podman (>= 4.9).
- **Storage:** At least 20 GB free disk space in `/var/lib/docker` or `/var/lib/containers`.
- **Network:** Internet access to reach `quay.io/fedora/fedora-bootc:44` and Fedora package repositories.

## 3. Base Image & Digest Pinning
Production and release builds MUST use immutable digest pinning to guarantee bit-for-bit build reproducibility.

```dockerfile
# Pinned Base Image (Fedora 44 bootc x86_64)
FROM quay.io/fedora/fedora-bootc:44@sha256:41ad34d292a531ebb9f82e00cd99c65ffa07111ffe865be781aa47f891ef2825
```

For local development or experimental iteration, the floating tag `quay.io/fedora/fedora-bootc:44` may be used.

## 4. Minimal Headless Package Manifest
Milestone P0 is 100% headless. Only core headless packages are installed:
- `kernel-core`, `kernel-modules`: Linux 6.14+ base kernel and required hardware modules.
- `btrfs-progs`: Utilities for managing Btrfs filesystem subvolumes.
- `systemd`, `util-linux`, `shadow-utils`: Core userspace initialization and user management.
- `NetworkManager`, `iproute`: Baseline networking stack.
- `dracut`: Initramfs generation tool (configured to omit Plymouth).
- `grub2-efi-x64`, `grub2-tools`, `efibootmgr`: UEFI bootloader tooling.

## 5. Build Commands
The primary build script is `scripts/build-p0.sh`:

```bash
# Execute idempotent build:
./scripts/build-p0.sh

# Or invoke container engine directly:
docker build -t nebuos:p0-latest -f Containerfile.p0 .
```

## 6. Build Validation
After building, validate the container image before generating disk artifacts:
```bash
# 1. Verify image exists:
docker images nebuos:p0-latest

# 2. Check no GUI packages leaked:
docker run --rm nebuos:p0-latest rpm -qa | grep -iE "wayland|smithay|slint|plymouth|pipewire"
# Expected: Empty output (0 packages)

# 3. Verify health-check service is enabled:
docker run --rm nebuos:p0-latest systemctl is-enabled nebu-boot-check.service
# Expected: enabled
```
