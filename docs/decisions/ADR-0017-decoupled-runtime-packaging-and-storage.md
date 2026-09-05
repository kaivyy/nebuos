# ADR-0017: Decoupled Compatibility Runtime Packaging and Storage Strategy

**Status:** APPROVED  
**Date:** 2026-09-05  
**Authors:** Principal OS Architect, Runtime Architect, Security Architect, Storage Engineer  
**Deciders:** NebuOS Core Architecture Group  
**Supercedes:** Supersedes the `/usr/lib/nebu/runtimes/` storage path specified in ADR-0005 and ADR-0008  
**Related ADRs:** ADR-0002 (Fedora Base), ADR-0005 (Wine Integration), ADR-0008 (Atomic Updates), ADR-0016 (NebuWine Architecture), ADR-0018 (Gaming Runtime)  
**Consulted:** PRD §16, §20, §70, §71, §80, §81, §82, §83  

---

## 1. Context and Problem Statement

NebuOS utilizes an immutable, container-based OS image architecture managed via `bootc` and `ostree` (ADR-0002, ADR-0008). In this architecture, `/usr` is mounted strictly read-only (`ro`) and can only be modified by deploying a new base OS container image followed by a system reboot.

Previous documentation (e.g. ADR-0005, early runtime specs) designated `/usr/lib/nebu/runtimes/` as the installation directory for Wine, Proton, DXVK, and VKD3D-Proton. This design introduced severe architectural contradictions:
1. **Coupled Update Cadence:** Updating a Wine candidate or issuing a hotfix for a broken application required building, signing, distributing, and rebooting the entire 3.5 GB NebuOS base operating system.
2. **Multi-Version Coexistence Bloat:** Shipping multiple concurrent Wine versions (Stable, Candidate, Gaming, Legacy) inside the base container inflated the base OS image size from ~2.5 GB to > 8 GB.
3. **Rollback Friction:** Rolling back a broken Wine runtime required rolling back the entire operating system deployment, risking loss of unrelated kernel/security updates.
4. **Offline and Low-Bandwidth Penalty:** Users on metered connections could not receive a 150 MB Wine runtime update without downloading a multi-gigabyte OS delta.

We must decide on a decoupled packaging, storage, and execution model for NebuWine and companion runtimes that preserves base image immutability, SELinux enforcement, and atomic rollback while granting independent update lifecycles.

---

## 2. Decision Drivers

- **Independent Lifecycle:** Wine and graphics translation runtimes must update, roll back, and install without rebooting the host OS.
- **Base OS Immutability:** The base OS rootfs (`/usr`, `/`) must remain strictly immutable, cryptographically signed, and verifiably pure.
- **Atomic Operations:** Runtime updates must be atomic; a crashed or aborted download must never leave a partially installed or corrupted runtime.
- **Multi-Version Coexistence:** Applications must be able to pin specific runtime versions (e.g., App X on NebuWine 11.4, App Y on NebuWine 12.0) side-by-side.
- **SELinux & Sandboxing Integrity:** Runtimes must execute under strict SELinux labels (`nebu_runtime_t` or container domains) and bubblewrap sandboxing without weakening host protection.
- **Storage Efficiency:** Golden runtime templates and shared libraries must leverage Btrfs reflink deduplication to minimize disk footprint.

---

## 3. Considered Alternatives

### Option A: Packaged Inside Base OS Container (`/usr/lib/nebu/runtimes/`)
- Ship all Wine versions directly in the `bootc` Containerfile.
- *Pros:* Trivially simple filesystem layout; guaranteed single-vendor QA.
- *Cons:* Huge image bloat (> 8 GB); requires full OS reboot for a 1-line Wine patch; completely rejected.

### Option B: Pure Flatpak Runtime Extensions (`org.winehq.Wine` / `com.valvesoftware.Steam.CompatibilityTool`)
- Distribute all runtimes strictly as Flatpak OCI bundles into `/var/lib/flatpak/`.
- *Pros:* Well-understood desktop standard; isolated runtimes.
- *Cons:* Heavy Flatpak sandbox layers conflict with NebuOS's fine-grained bubblewrap orchestration (`nebu-runtime-daemon`); rigid permissions hinder deep Wayland compositor integration and system-level performance profiling.

### Option C: Systemd System Extensions (`systemd-sysext`)
- Package runtimes as squashfs/erofs images mounted over `/usr` at boot.
- *Pros:* Merges cleanly into `/usr` hierarchy.
- *Cons:* Complex dynamic overlayfs management across atomic reboots; unpredictable SELinux label inheritance; fragile when merging multiple overlapping runtime extensions.

### Option D: Decoupled Btrfs Storage Subvolume at `/var/lib/nebu/runtimes/` with Read-Only Bind Execution (CHOSEN)
- Host runtimes in a dedicated stateful subvolume: `@runtimes` mounted at `/var/lib/nebu/runtimes/`.
- Runtimes are packaged as signed, compressed OCI artifacts or squashfs archives deployed atomically into versioned directories (e.g., `/var/lib/nebu/runtimes/nebuwine-11.4.0/`).
- At runtime launch, `nebu-runtime-daemon` mounts the target runtime directory **read-only (`ro`)** inside the application's bubblewrap container at `/usr/lib/nebu/runtime/`.
- *Pros:* Independent lifecycle; zero OS reboot required; atomic deployment via Btrfs snapshots; 100% read-only enforcement during execution; flawless SELinux labeling; native Btrfs reflink deduplication.
- *Cons:* Requires managing stateful directory updates in `/var`.

---

## 4. Decision Outcome

**Chosen Option: Option D — Dedicated Decoupled Subvolume at `/var/lib/nebu/runtimes/` with Read-Only Execution.**

NebuOS formally relocates all compatibility runtime binaries, libraries, and tools from `/usr/lib/nebu/runtimes/` to `/var/lib/nebu/runtimes/`.

```
/var/lib/nebu/runtimes/
├── active/                               # Symlinks or metadata for active defaults
│   ├── default -> ../stores/nebuwine-11.4.0/
│   ├── gaming  -> ../stores/nebuwine-gaming-11.4.0-dxvk2.4/
│   └── legacy  -> ../stores/nebuwine-10.2.1/
├── stores/                               # Content-addressed or version-tagged stores (ro)
│   ├── nebuwine-10.2.1/
│   │   ├── bin/ (wine, wine64, wineserver)
│   │   ├── lib/ & lib64/
│   │   └── share/
│   ├── nebuwine-11.4.0/
│   └── nebuwine-gaming-11.4.0-dxvk2.4/
│       ├── dxvk/
│       ├── vkd3d-proton/
│       └── wine/
└── templates/                            # Clean Btrfs golden prefix templates
    ├── win64-clean/
    └── win32-clean/
```

### 4.1 Execution Sandboxing Contract
When `nebu-runtime-daemon` initiates an application sandbox via bubblewrap:
```bash
bwrap \
  --ro-bind /usr /usr \
  --ro-bind /var/lib/nebu/runtimes/stores/nebuwine-11.4.0 /usr/lib/nebu/runtime \
  --symlink /usr/lib/nebu/runtime/bin/wine64 /usr/bin/wine \
  --bind /var/home/$USER/.local/share/nebu/prefixes/myapp /wineprefix \
  ...
```
The runtime is mapped as **read-only** inside the sandbox container. Neither the Windows executable nor the Wine process can modify its own runtime binaries or libraries.

### 4.2 Evaluation Comparison Matrix

| Evaluation Criterion | Option A (/usr in Base) | Option B (Flatpak Ext) | Option C (sysext) | Option D (/var/lib/nebu/runtimes) |
|---|---|---|---|---|
| **Base Immutability** | Preserved | Preserved | Preserved | **Preserved (Host `/usr` untouched)** |
| **Independent Updates**| FAILED (Requires OS build) | PASSED | PASSED | **PASSED (Sub-minute update)** |
| **No Reboot Required** | FAILED (Reboot needed) | PASSED | FAILED (Reload needed) | **PASSED (Immediate hot-swap)** |
| **Atomic Deployment**  | PASSED (ostree) | PASSED (ostree) | PARTIAL | **PASSED (Btrfs atomic swap)** |
| **Multi-Version Pin**  | FAILED (Bloats OS) | PASSED | FAILED (Complex overlay)| **PASSED (Side-by-side folders)**|
| **SELinux Compatibility| Native | Flatpak-specific | Fragile | **Native (`nebu_runtime_t`)** |
| **Reflink Deduplication| N/A | Partial | No | **Full native Btrfs support** |
| **Offline Recovery**   | Full OS rollback | Flatpak rollback | Manual disable | **Instant symlink rollback** |

---

## 5. Storage Topology and Btrfs Layout

During initial disk formatting, the NebuOS partition installer provisions the `@runtimes` subvolume:
- Mount Point: `/var/lib/nebu/runtimes`
- Subvolume: `@runtimes`
- Mount Options: `defaults,subvol=@runtimes,compress=zstd:3,noatime,nodev`
- Permissions: `0755 root:root`
- SELinux Context: `system_u:object_r:nebu_runtime_store_t:s0`

---

## 6. Consequences

### Positive Consequences
- Base operating system image remains compact (~2.5 GB), clean, and fast to download.
- Runtime releases can occur on independent cycles (e.g. weekly or bi-weekly sync with WineHQ).
- Zero host reboots required to upgrade or patch Wine.
- Multiple Wine and DXVK versions coexist peacefully with negligible storage overhead via Zstandard compression and Btrfs reflink deduplication.
- Instant, deterministic rollback to known-good runtime versions if an application regresses.

### Negative Consequences
- Runtime updates must be orchestrated by a local daemon (`nebu-runtime-daemon`) or package updater rather than relying solely on `bootc update`.
- Storage consumption in `/var` must be monitored to evict abandoned legacy runtimes.

---

## 7. Verification and Acceptance Criteria

- [x] Documented in ADR-0017; cross-referenced in ADR-0005, ADR-0008, and `docs/runtime/08-nebuwine-specification.md`.
- [x] Bubblewrap mount model validated against security architecture in `docs/runtime/07-runtime-security.md`.
- [x] Filesystem subvolume specification aligned with `docs/specification/03-filesystem-specification.md`.
