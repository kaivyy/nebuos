# ADR-0008: Atomic Image Deployments and Btrfs Subvolume Topology

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Storage Engineer  
**Consulted:** PRD §7, §9, §15, §43, §44  

---

## 1. Context and Problem Statement
Operating system updates and storage management must be resilient against power loss, filesystem corruption, and storage bloat. Windows application prefixes create thousands of small files and duplicate runtime DLLs. Furthermore, updates must never corrupt the active operating system. We must choose the underlying storage architecture and atomic deployment engine that provides copy-on-write snapshots, instant reflink prefix provisioning, and atomic OS deployments.

## 2. Decision Drivers
- **Atomic OS Updates:** Transactional container-based image upgrades via `bootc` and OSTree.
- **Fast Prefix Provisioning:** Ability to clone a 500 MB clean Wine prefix template in < 200ms without duplicating disk blocks.
- **Filesystem Compression:** Transparent data compression to reduce disk consumption on budget devices.
- **Data Safety:** Copy-on-Write (CoW) metadata guarantees protecting against power-loss corruption.

## 3. Considered Options
- **Option 1: Btrfs Subvolume Topology with `bootc` Atomic Deployments [SELECTED]**
- **Option 2: Ext4 Filesystem with Traditional LVM Snapshots**
- **Option 3: ZFS on Linux**
- **Option 4: OverlayFS on Read-Only SquashFS**

## 4. Decision Outcome
**Chosen Option: Option 1 — Btrfs Subvolumes with `bootc` Atomic Deployments.**

NebuOS formats storage using Btrfs with dedicated subvolumes:
- `@`: Root sysroot deployment mount (`/sysroot`)
- `@home`: User persistent personal files (`/home`)
- `@var`: System persistent state (`/var`)
- `@nebu_apps`: Windows application prefixes (`nodatacow` enabled to eliminate registry fragmentation).
OS images are managed immutably via `bootc`. Application prefixes are cloned instantly from templates using Btrfs reflink ioctl (`FICLONE`).

### Positive Consequences
- Zero-copy prefix provisioning: creating a new prefix takes < 150ms and consumes 0 bytes of disk space initially.
- Automated instant rollback: reverting an application or OS update takes < 500ms via Btrfs snapshots.
- Transparent `zstd:1` compression reduces OS and application footprint by 35–45%.

### Negative Consequences
- Btrfs Copy-on-Write can cause fragmentation on random-write files (mitigated by setting `nodatacow` on `@nebu_apps`).
- Btrfs free space reporting requires user-facing documentation.

## 5. Pros and Cons of Alternatives

### Option 2: Ext4 with LVM
- *Pros:* Simple, mature.
- *Cons:* Lacks file-level reflink cloning; creating a prefix requires copying 500 MB of data (taking 5–15 seconds); snapshots are coarse-grained at the volume level.

### Option 3: ZFS
- *Pros:* Enterprise snapshot features.
- *Cons:* Out-of-tree kernel module license conflict (CDDL vs GPLv2); heavy memory footprint incompatible with 4GB RAM budget.

### Option 4: OverlayFS on SquashFS
- *Pros:* Minimal read-only image.
- *Cons:* Poor random-write performance; lacks subvolume snapshotting and reflink capabilities.

## 6. Confirmation and Validation
- Btrfs FICLONE benchmark validating prefix clone latency < 200ms.
- Atomic image update and rollback test confirming data persistence in `/home` and `/var`.
