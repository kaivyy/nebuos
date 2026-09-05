# NebuOS Milestone P0 Artifact Specification

**Status:** APPROVED  
**Target Milestone:** Milestone P0: Foundation Operating System  
**Authority:** OS Storage Architect, Release Engineer  

---

## 1. Overview
This document specifies the disk image structure, partition schema, Btrfs subvolume layout, and bootloader configuration files for NebuOS Milestone P0 bootable artifacts.

## 2. Disk Artifact Format
- **Filename:** `target/nebuos-p0.raw` (Raw GPT disk image, sparse format).
- **Target Size:** 10 GB sparse (allocates only ~2.5 GB physical disk space).
- **Partition Table:** GUID Partition Table (GPT).

## 3. Partition Table Layout

```text
+-----------------------------------------------------------------------------------+
| Partition 1: EFI System Partition (ESP)                                            |
| - Size: 512 MB                                                                    |
| - Type GUID: c12a7328-f81f-11d2-ba4b-00a0c93ec93b (EFI System)                   |
| - Format: FAT32                                                                   |
| - Mount Point: /boot/efi                                                          |
| - Contents: /EFI/fedora/grubx64.efi, /EFI/fedora/shimx64.efi, /EFI/fedora/grub.cfg|
+-----------------------------------------------------------------------------------+
| Partition 2: NebuOS Root Filesystem                                               |
| - Size: Remaining disk (~9.5 GB)                                                  |
| - Type GUID: 4f68bce3-e8cd-4db1-96e7-fbcaf984b709 (Linux Root x86-64)            |
| - Format: Btrfs                                                                   |
| - Mount Options: compress=zstd:1,space_cache=v2,noatime                           |
+-----------------------------------------------------------------------------------+
```

## 4. Btrfs Subvolume Topology

NebuOS implements three distinct Btrfs subvolumes on Partition 2:

| Subvolume Name | Mount Path | Mount Flags | Purpose |
|---|---|---|---|
| `@` | `/` (and `/sysroot`) | `rw,noatime,compress=zstd:1` | Operating system root sysroot. Contains immutable `/usr` mount. |
| `@home` | `/var/home` (symlinked from `/home`) | `rw,noatime,compress=zstd:1` | User personal data, documents, desktop configs. Untouched by updates or rollbacks. |
| `@var` | `/var` | `rw,noatime,compress=zstd:1` | Shared persistent operating system state, container storage, and systemd journal logs. |

## 5. Bootloader Specification (BLS) Entries
BLS entries are stored in `/boot/loader/entries/`:

1. **Normal Silent Boot Entry (`ostree-1-nebuos.conf`):**
   ```conf
   title NebuOS 0.1.0-p0 (Foundation)
   version 6.14.0-nebuos
   linux /boot/vmlinuz-...
   initrd /boot/initramfs-...img
   options root=LABEL=nebuos-root rootflags=subvol=@ quiet splash loglevel=3 rd.systemd.show_status=false systemd.show_status=false vt.global_cursor_default=0 udev.log_level=3
   ```

2. **Diagnostic Boot Entry (`ostree-1-nebuos-diag.conf`):**
   ```conf
   title NebuOS 0.1.0-p0 (Diagnostic Mode)
   version 6.14.0-nebuos
   linux /boot/vmlinuz-...
   initrd /boot/initramfs-...img
   options root=LABEL=nebuos-root rootflags=subvol=@ debug systemd.show_status=true rd.systemd.show_status=true loglevel=7 console=tty1 console=ttyS0
   ```

## 6. GRUB Environment State (`grubenv`)
Stored at `/boot/grub2/grubenv` (or `/boot/efi/EFI/fedora/grubenv`):
- `boot_counter`: Countdown integer (3 to 0).
- `boot_success`: Binary commit flag (`0` uncommitted, `1` healthy).
- `default`: Target BLS boot entry index (`0` active deployment, `1` rollback fallback).
