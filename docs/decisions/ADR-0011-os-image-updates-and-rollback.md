# ADR-0011: Operating System Image Updates, bootc Transactional Deployments, and Automated Rollback Architecture

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal OS Architect, OS Update/Release Engineer, bootc/Ostree Engineer, Security Architect, DevOps/Infrastructure Engineer  
**Consulted:** PRD §9 (Atomic Update Model), §10 (Release Channels), §72 (Update Safety), §73–75 (Component Policies); ADR-0002 (Fedora Base); ADR-0008 (Btrfs Subvolumes & Atomic Deployments); ADR-0010 (Hardware Compatibility)  

---

## 1. Context and Problem Statement

Traditional package-based Linux desktop distributions (utilizing `dnf`, `apt`, or `pacman`) mutate running filesystems in-place. If a system update is interrupted by power loss, network partition, or disk saturation, the host is left in an inconsistent intermediate state with mismatched shared libraries, broken symbolic links, or unconfigured kernel modules. Furthermore, desktop software and gaming compatibility layers (Wine, Proton, DXVK, Mesa, and proprietary GPU drivers) possess tight kernel ABI couplings. A minor upstream package drift can silently break 3D acceleration or application launch without offering an instant, zero-touch fallback to the previous known-working system.

NebuOS requires an operating system update architecture that guarantees:
1. **Transactionality:** Updates are atomic; an image is deployed completely or not at all. Active running processes are never mutated.
2. **Deterministic Reproducibility:** Every deployment corresponds to an immutable, cryptographically signed OCI container image identified by a SHA-256 digest.
3. **Automated Recovery:** Boot failures, kernel panics, or broken display environments trigger automatic, hands-off rollback to the prior working deployment.
4. **User Data Invariance:** User documents, personal files, and persistent state (`/home`, `/var`) are physically isolated from OS binaries and remain 100% intact across updates and rollbacks.
5. **Clear Separation of Concerns:** OS updates, native Linux application updates, Windows application prefix lifecycles, compatibility database updates, and peripheral firmware updates must operate via independent, dedicated mechanisms rather than being conflated into a monolithic payload.

---

## 2. Decision Drivers

- **Zero Runtime Disruption:** Background update staging must execute without restarting daemons, killing user applications, or locking filesystems.
- **Upstream Standards Leverage:** Utilize established, enterprise-grade Linux container-boot primitives (`bootc`, `ostree`, `containers/storage`) rather than maintaining a bespoke distribution package manager or custom A/B partition daemon.
- **Security & Provenance:** Cryptographic verification (Sigstore/Cosign with Ed25519 root keys) must validate image integrity before byte staging to disk.
- **Rollback Predictability:** Rollback must be deterministic, rapid (< 15 seconds), and bounded by quantifiable health check assertions.
- **Architectural Boundary Invariance:** The user desktop shell (`nebu-shell`) must act strictly as an unprivileged presentation client over D-Bus; all deployment operations belong to privileged system daemons (`bootc` coordinated by `NebuUpdateService`).
- **Milestone P0 Independence:** The base bootable OS (Milestone P0) must establish the container/bootc deployment substrate without depending on graphical compositors, desktop shells, or Wine runtimes.

---

## 3. Considered Options

### Option 1: `bootc` Native OCI Image Deployment Engine with OSTree Transactional Rootfs [SELECTED]
NebuOS base operating system images are authored as standard OCI container images (built via `Containerfile`), distributed via standard OCI container registries, and deployed directly to disk using `bootc`. `bootc` manages bootable OSTree deployments backed by Btrfs subvolumes, creating an inactive staging deployment during upgrades and swapping GRUB BLS boot targets upon completion. NebuOS builds an unprivileged D-Bus coordination service (`NebuUpdateService`), health checks, release policies, and UI contracts on top of `bootc`.

### Option 2: Classic `rpm-ostree` with Client-Side Package Layering
Use traditional `rpm-ostree` client-side composition where the base OS tracks an OSTree commit and users/system can layer RPM packages dynamically on top of the immutable base.
- *Trade-offs:* Allows dynamic RPM installation but introduces client-side package drift, non-deterministic image states across devices, slow compose times on client hardware, and complex dependency solver bugs during upgrades.

### Option 3: Dual-Partition Raw Disk A/B Mirroring (Systemd-Sysupdate / Android-Style)
Divide physical storage into fixed active/inactive root partitions (`root-a`, `root-b`). Updates stream raw block-level filesystem diffs into the inactive partition.
- *Trade-offs:* Guarantees bit-exact partitions but wastes massive disk space (requires reserving two full root partitions of 15–30 GB each, severely penalizing 64GB/128GB budget laptops), lacks file-level shared extents, and makes multi-deployment retention (e.g. pinned fallback) prohibitively expensive.

### Option 4: Full Package Distribution with Transactional DNF (`dnf5` with Btrfs Snapshots)
Retain standard Fedora RPM packages, but wrap updates in automated Btrfs pre/post snapshots via snapper.
- *Trade-offs:* Fails to guarantee image immutability; packages can fail mid-install; files in `/usr` remain mutable; package dependency combinations explode across user base, destroying predictability in the Compatibility Lab.

---

## 4. Decision Outcome

**Chosen Option: Option 1 — `bootc` Native OCI Image Deployment Engine with OSTree Transactional Rootfs.**

### 4.1 Architectural Role of `bootc`
`bootc` is established as the sole operating system deployment engine for NebuOS. NebuOS will **not** build a custom OS package manager or deployment daemon. `bootc` executes the transactional primitives:
- `bootc upgrade` (staging flow): Checks registry, downloads layer deltas, verifies signatures, and stages an inactive boot deployment (using the actual available staging CLI options of `bootc` 1.x in Fedora 44).
- `bootc switch <image>`: Re-targets the host to a new release channel or specific immutable digest.
- `bootc rollback`: Re-points the default bootloader entry to the prior working deployment.
- `bootc status --format=json`: Queries current active, staged, rollback, and pinned deployment states.

NebuOS constructs the orchestration layer above `bootc`:
```
+-------------------------------------------------------------------------+
|                  NebuShell (Unprivileged Desktop Client)                |
|  - Settings -> System -> Software Update (Presentation Only)            |
+-------------------------------------------------------------------------+
                                    │
                                    │ org.nebu.Update1 (D-Bus / Polkit)
                                    ▼
+-------------------------------------------------------------------------+
|                    NebuUpdateService (System Daemon)                    |
|  - Policy evaluation (Power, Network, Metered status)                   |
|  - Release metadata fetching & release notes formatting                 |
|  - Staging orchestration & D-Bus status broadcasts                      |
|  - Post-boot health check supervision & rollback coordination           |
+-------------------------------------------------------------------------+
                                    │
                                    │ Privileged Process Execution
                                    ▼
+-------------------------------------------------------------------------+
|                       bootc Engine (System Layer)                       |
|  - OCI Layer Pull -> Sigstore Verification -> OSTree Sysroot Staging    |
+-------------------------------------------------------------------------+
                                    │
                                    │ Filesystem & Bootloader
                                    ▼
+-------------------------------------------------------------------------+
|                       Btrfs Subvolumes & GRUB BLS                       |
|  - /sysroot (ostree/deploy), @home, @var, @nebu_apps                    |
|  - BLS Entries (deployment.0, deployment.1) + Boot Counting Watchdog    |
+-------------------------------------------------------------------------+
```

### 4.2 Update Model & Storage Semantics
- **Base OS Image (`/usr`):** Strictly read-only (`ro,nodev`). Completely replaced atomically across upgrades.
- **System Configuration (`/etc`):** Managed via OSTree 3-way merge (`/usr/etc` default vendor template vs previous active `/etc` vs new vendor template). Local admin customizations are preserved.
- **System State (`/var`):** Shared persistent state across all deployments (`/sysroot/ostree/deploy/nebu/var`). System logs, container storage (`/var/lib/containers`), and databases persist undisturbed.
- **User Data (`/home`):** Dedicated Btrfs subvolume (`@home` mounted at `/var/home`). OS updates and rollbacks **never** modify, delete, or revert user files.
- **Windows Application Prefixes (`@nebu_apps`):** Stored under user space (`~/.nebu/apps/` or dedicated Btrfs subvolume) and completely isolated from the OS image lifecycle.

### 4.3 Release Channels & Versioning
- **Channels:**
  * `stable`: Default channel for general users, office workstations, and gaming desktops. Promoted after rigorous regression testing.
  * `testing`: Opt-in channel for enthusiasts and hardware testers. Receives bi-weekly release candidates.
  * `development`: Daily builds reflecting latest `main` trunk for internal developers and automated CI smoke testing.
- **Versioning Policy:**
  NebuOS uses semantic product versioning (`MAJOR.MINOR.PATCH`, e.g. `NebuOS 1.0.1`) distinct from underlying upstream components:
  * NebuOS Product Version: `1.0.1`
  * Base Distribution: `Fedora 44 (bootc)`
  * Kernel Version: `Linux 6.14.x-nebu`
  * Mesa Version: `Mesa 25.0.x`
  * Immutable Image Digest: `sha256:7f83b165...`
  * Unique Release ID: `nebu-20260904.1`

### 4.4 Image Registry & Trust Model
- **Registry Topology:** Public production images are hosted on a highly available OCI registry (`quay.io/nebuos/base` or `registry.nebuos.org/base`). CI test builds and ephemeral artifacts reside in separate internal repositories.
- **Cryptographic Signing:** Every published image is signed using Sigstore/Cosign with Ed25519 root keys. User devices verify the signature and transparency log before any layer bytes are written to disk. HTTPS alone is rejected as insufficient trust.

### 4.5 Staged Deployment & Reboot Policy
- **Download & Staging:** Executed in the background with I/O and network throttling. The active user session is completely undisturbed.
- **Activation:** NebuOS enforces a strict "No Surprise Reboot" policy. Automatic reboots are forbidden by default. Updates require a user-initiated reboot or schedule at next natural shutdown.
- **Reboot Classification:**
  * *Reboot Required:* Base OS kernel, systemd, libc, graphics stack, or compositor updates.
  * *Reboot Not Required:* Flatpak application updates, independent Compatibility DB updates, runtime user configuration.

### 4.6 Post-Boot Health Checks & Automated Rollback
- Upon rebooting into a staged deployment, GRUB initializes a boot attempt counter (`boot_counter=3`).
- `nebu-boot-check.service` executes after target reach:
  * P0 Health Check: Boot successful, systemd reached multi-user.target without failed units, rootfs mounted read-only, loopback/network baseline active, version matches staged release.
  * P2+ Health Check: Expands to verify compositor DRM master acquisition, display scanout, and desktop shell socket binding.
- If the system experiences a kernel panic, display freeze, or service failure causing watchdog expiration, GRUB decrements the counter. Once exhausted, GRUB automatically falls back to the previous deployment.

### 4.7 Subsystem Update Decoupling
To avoid monolithic bottlenecks, NebuOS strictly decouples update mechanisms:
1. **Operating System:** Transactional image update via `bootc`.
2. **Native Linux Applications:** Flatpak user-space runtimes via Flathub/NebuStore.
3. **Windows Application Runtime:** User-space prefixes via `nebu-runtime-daemon` and Btrfs reflink templates.
4. **Compatibility Database (`compat.db`):** Independently updateable signed SQLite database, distributed out-of-band without full OS rebuilds.
5. **Hardware Firmware:** Low-level UEFI/EC updates mediated strictly via `fwupd` / LVFS with AC power and battery safety gating.

---

## 5. Pros and Cons of the Chosen Architecture

### Positive Consequences
- Eliminates "broken upgrade" states entirely; power loss during update leaves host 100% operational on previous deployment.
- CI pipeline in the Compatibility Lab tests the exact bit-for-bit container image that runs on user machines.
- Btrfs extent sharing ensures dual bootable deployments require only 500 MB – 1.5 GB of delta storage, making it practical for budget SSDs.
- Clear D-Bus separation ensures NebuShell remains unprivileged and crash-isolated from the deployment engine.

### Negative Consequences / Trade-offs
- Base OS updates require a reboot to take effect (live kernel patching is out of scope).
- Storage consumption requires active monitoring: hosts must maintain >= 3.5 GB free space to safely stage a new deployment.
- Reverting an OS image does not revert user data or third-party database tables in `/var`, requiring clear user-facing documentation to prevent confusion.

---

## 6. Confirmation and Validation

- **Automated QEMU Transactional Test:** Build base image, stage update via `bootc switch`, reboot in QEMU, assert successful health check commit.
- **Fault-Injection Crash Test:** Induce kernel panic in staged deployment; assert hardware watchdog triggers reboot and GRUB successfully falls back to previous deployment.
- **Data Preservation Test:** Assert user files in `/home` and application data in `/var` remain bit-identical across upgrade and rollback cycles.

---
*Signed off by:*  
**Principal OS Architect & Lead Systems Engineer**  
*NebuOS Technical Steering Committee*
