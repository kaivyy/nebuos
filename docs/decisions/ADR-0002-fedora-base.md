# ADR-0002: Fedora Linux 44 Atomic / Image-Based Base Operating System

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Linux OS Engineer  
**Consulted:** PRD §7, §8, §9, §10, §72; docs/specification/00-system-specification.md  

---

## 1. Context and Problem Statement
Traditional package-based Linux distributions (Debian, Arch, standard Fedora Workstation) allow runtime package mutation. Over time, user-installed packages, aborted upgrades, and conflicting library dependencies cause system state drift, broken environments, and unbootable states. NebuOS requires an immutable, verifiable, and atomic base operating system that guarantees reproducibility, seamless atomic upgrades, and instant rollback.

Furthermore, NebuOS must establish a concrete, validated upstream distribution baseline for Milestone P0 (Foundation). Choosing an unversioned floating baseline (`fedora:latest`) introduces non-deterministic builds, while tracking an outdated baseline (e.g., Fedora 40/41) creates technical debt and deprives the OS of modern kernel, systemd, dracut, and bootc capabilities.

## 2. Decision Drivers
- **Immutability:** System root (`/usr`) must be mounted read-only to prevent tampering, configuration drift, and corruption.
- **Atomic Image Upgrades:** OS updates must apply as a single atomic transaction without intermediate broken states.
- **OCI Container Integration (`bootc`):** Ability to build, layer, test, and distribute the base OS using standard Containerfile and OCI registry workflows (`bootc` 1.1+).
- **Modern Package & Kernel Stack (Fedora 44):** Native access to modern Linux kernel (6.14+), systemd (v256+), dracut (v102+), Btrfs progs (6.8+), Mesa drivers, PipeWire audio, and Wayland libraries.
- **Predictable Upstream Cadence:** Backed by an established, active upstream enterprise Linux community with a stable release cycle, avoiding both rolling-release instability and LTS obsolescence.
- **Strict P0 Scope Protection:** Base OS must provide a minimal headless container suitable for bringing up boot, Btrfs subvolumes, systemd multi-user target, and TTY login without dragging in desktop, display server, or Wine dependencies.

## 3. Considered Options
- **Option 1: Fedora Linux 44 Atomic Base with `bootc` (`quay.io/fedora/fedora-bootc:44`) [SELECTED]**
- **Option 2: Older Fedora Atomic Releases (Fedora 40 / 41 / 42 / 43) [REJECTED]**
- **Option 3: Fedora Rawhide / Floating Rolling Base [REJECTED]**
- **Option 4: Traditional Mutable Distribution (Ubuntu LTS / Debian Stable) [REJECTED]**
- **Option 5: Custom Scratch / Yocto Distribution [REJECTED]**
- **Option 6: Arch Linux Base with Btrfs Snapshots [REJECTED]**

## 4. Decision Outcome
**Chosen Option: Option 1 — Fedora Linux 44 Atomic Base with `bootc` (`quay.io/fedora/fedora-bootc:44`).**

NebuOS establishes **Fedora Linux 44** as the official upstream foundation baseline for Milestone P0. The base system is constructed via a multi-stage `Containerfile` extending `quay.io/fedora/fedora-bootc:44` and deployed immutably to target systems.

### 4.1 Technical Baseline Architecture
- **Upstream Base Image:** `quay.io/fedora/fedora-bootc:44`
- **Linux Kernel:** Linux 6.14+ (Fedora 44 standard kernel packages `kernel-core`, `kernel-modules`)
- **Init & Service Supervision:** systemd v256+
- **Initramfs Generator:** dracut v102+
- **Root Filesystem & Layout:** Btrfs subvolumes (`@` mounted at `/`, `@home` at `/var/home`, `@var` at `/var`)
- **Security Baseline:** SELinux enforcing mode using Fedora 44 targeted policy (`selinux-policy-targeted`)
- **Container Deployment Mechanism:** `bootc` 1.1+ with ostree container storage backend
- **Packaging Format for Output:** OCI standard image (`application/vnd.oci.image.manifest.v1+json`)

### 4.2 Upstream Tracking & Stability vs Freshness Policy
- NebuOS tracks Fedora stable releases rather than Rawhide or unversioned tags.
- Within the Fedora 44 lifecycle:
  * Minor upstream package updates (kernel point releases, security errata, systemd patches) are ingested via scheduled weekly CI rebuilds.
  * Ingested images must pass automated CI validation (`bootc container lint`, headless QEMU boot test, systemd-analyze verification) before staging into the `testing` channel.
- Major Upstream Fedora Upgrades (e.g. Fedora 44 → Fedora 45):
  * Upgrades to subsequent Fedora major releases are treated as major release engineering events.
  * They require a dedicated release branch, ABI verification of all native Rust components, a mandatory 30-day soak period in the `development`/`testing` channels, and passing the full automated test suite before promotion to `stable`.

### 4.3 Version Pinning Policy
- **Development Builds:** May track `quay.io/fedora/fedora-bootc:44` floating tag during active milestone integration.
- **Production & Release Builds:** Must pin exact OCI image digest (e.g., `quay.io/fedora/fedora-bootc:44@sha256:<digest>`) to guarantee bit-for-bit build reproducibility.
- NebuOS product semantic versioning (e.g., `0.1.0` for P0, `1.0.0` for GA) is strictly decoupled from the underlying Fedora 44 baseline version.

### 4.4 Positive Consequences
- Root filesystem `/usr` is mounted strictly read-only (`ro,nodev`), preventing accidental deletion or unauthorized tampering.
- Updates are staged in the background as complete OCI container layers; activation occurs cleanly and atomically upon reboot.
- Native integration with modern kernel 6.14+ and systemd v256+ provides first-class support for cgroups v2, modern ACPI states, and fast boot times.
- Automated rollback via GRUB boot-counting and bootc ensures self-healing if a staged image fails post-boot health checks.
- Developers build, layer, test, and audit NebuOS base images using standard Podman and OCI container tooling.

### 4.5 Negative Consequences
- Users cannot execute ad-hoc `dnf install` commands on a running system (native applications must be deployed via Flatpak, user containers, or NebuRuntime).
- Modifying host-level system dependencies requires an image rebuild and staging through the release pipeline.

## 5. Pros and Cons of Alternatives

### Option 2: Older Fedora Atomic Releases (Fedora 40 / 41 / 42 / 43)
- *Pros:* Known past stability.
- *Cons:* Deprecated upstream support lifecycle; older kernel and systemd versions lacking modern hardware compatibility and cgroups optimizations; premature technical debt requiring immediate migration.

### Option 3: Fedora Rawhide / Floating Base
- *Pros:* Absolute latest packages.
- *Cons:* Extreme instability, frequent ABI breaks, unannounced package drops, non-reproducible CI builds; unsuitable for stable OS foundation.

### Option 4: Traditional Mutable Ubuntu / Debian
- *Pros:* Familiar package management for end-users.
- *Cons:* Susceptible to broken dependencies ("dependency hell"); no native atomic rollback; mutable system files easily corrupted.

### Option 5: Custom Yocto / LFS Distribution
- *Pros:* Extreme minimalism, zero upstream bloat.
- *Cons:* Massive maintenance burden; compiling every package from source in CI; lagging security updates for thousands of packages.

### Option 6: Arch Linux Base
- *Pros:* Rolling release, latest upstream software.
- *Cons:* Inherent instability and frequent manual intervention required; lack of native immutable image deployment architecture.

## 6. Confirmation and Validation
- Base image build verified with `podman build` targeting `quay.io/fedora/fedora-bootc:44`.
- Image integrity validated via `bootc container lint`.
- Automated QEMU boot test verifying:
  1. Successful boot into systemd multi-user.target in < 5 seconds.
  2. Btrfs root layout mounted read-only on `/usr`.
  3. SELinux enforcing mode enabled without fatal denials during boot.
  4. Working TTY login prompt with root credential access.

