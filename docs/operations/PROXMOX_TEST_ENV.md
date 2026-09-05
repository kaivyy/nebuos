# Proxmox Virtual Environment Testing Architecture — NebuOS

**Status:** APPROVED  
**Target Architecture:** Proxmox VE 8.x / 7.x KVM Hypervisor & LXC Container  
**Authority:** Infrastructure & DevOps Engineer  

---

## 1. Overview
NebuOS development and testing utilizes a hybrid architecture within Proxmox Virtual Environment (PVE):
- **Development Environment (CT 100):** An unprivileged/nested LXC container running Debian 13 (OpenClaw stack, Docker engine, build toolchain, QEMU TCG for local unit/smoke testing).
- **Target Verification Environment (VM):** A dedicated full Proxmox KVM Virtual Machine configured for UEFI hardware testing, PCIe passthrough, and native benchmark verification.

> [!IMPORTANT]
> **CT 100 Non-Interference:**
> Development of NebuOS takes place directly inside CT 100 without disrupting other background services (e.g. `openclaw-searxng`). CT 100 is NOT converted into a VM.

## 2. Proxmox VM Hardware Configuration
When provisioning the test VM on Proxmox VE for NebuOS P0 validation, use the following hardware profile:

| Setting | Recommended Value | Rationale |
|---|---|---|
| **OS Type** | Linux (Kernel 6.x - 2.6) | Ensures modern ACPI and virtio driver profile. |
| **Machine Type** | `q35` | Modern PCIe topology; required for UEFI GOP and PCIe bridge assignment. |
| **BIOS Firmware** | `OVMF (UEFI)` | Mandatory. NebuOS strictly targets UEFI x86_64; legacy SeaBIOS is unsupported. |
| **EFI Storage** | 4 MB EFI Disk (`OVMF_VARS.fd`) | Holds persistent NVMe/GRUB boot variables. |
| **vCPU** | 4 Cores (`host` CPU type) | Passes through hardware virtualization flags (SSE4.2, AVX2, AES-NI). |
| **Memory** | 4096 MB (4 GB) | Standard reference memory budget for NebuOS. |
| **SCSI Controller** | `VirtIO SCSI Single` (IOThread enabled) | High-performance asynchronous disk I/O. |
| **Hard Disk** | VirtIO SCSI Disk (16 GB, SSD emulation, Discard=on) | Matches Btrfs TRIM and NVMe fast I/O assumptions. |
| **Network Device** | `VirtIO (paravirtualized)` | High-throughput baseline networking for NetworkManager verification. |
| **Display Device** | `VirtIO-GPU` (or Serial Terminal) | P0 is headless; serial console `ttyS0` displays boot logs. |

## 3. LXC-to-Proxmox VM Deployment Workflow
To transfer a built disk artifact from CT 100 to the Proxmox VM for bare-metal/KVM testing:

1. **Build Raw Artifact in CT 100:**
   ```bash
   ./scripts/p0-ci.sh
   # Produces target/nebuos-p0.raw
   ```

2. **Transfer to Proxmox PVE Host Storage:**
   ```bash
   # From PVE hypervisor host, import disk directly into target VM (e.g. VMID 105):
   qm disk import 105 /var/lib/vz/dump/nebuos-p0.raw local-zfs --format raw
   ```

3. **Attach Disk to VM:**
   ```bash
   qm set 105 --scsihw virtio-scsi-single --scsi0 local-zfs:vm-105-disk-0,discard=on,ssd=1
   qm set 105 --boot order=scsi0
   ```

4. **Launch VM and Monitor Serial Console:**
   ```bash
   qm start 105
   qm terminal 105
   ```
