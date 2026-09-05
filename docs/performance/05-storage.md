# Storage Performance & Quota Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify Btrfs compression tuning, prefix disk quota management, and shader cache garbage collection.

---

## 1. Filesystem Compression Tuning
- **Compression Algorithm:** Transparent `zstd:1` compression enabled on root (`@`) and home (`@home`) subvolumes.
- **Benefits:**
  - Reduces operating system install footprint from ~18 GB to **< 9 GB**.
  - Doubles effective SATA SSD read bandwidth by compressing data before bus transfer.

## 2. Automated Storage Quota & Garbage Collection
- **Shader Cache Pruning:** `~/.nebu/cache/shaders/` is capped at 5 GB system-wide. An LRU daemon prunes caches older than 90 days.
- **Prefix Snapshots:** Point-in-time prefix snapshots are automatically rotated; older snapshots are removed after 14 days unless pinned by the user.

## 3. Related Documents
- [00-performance-goals.md](00-performance-goals.md)
- [../architecture/04-filesystem.md](../architecture/04-filesystem.md)
