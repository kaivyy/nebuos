# NebuOS Milestone P0 Testing & Verification Guide

**Status:** APPROVED  
**Target Milestone:** Milestone P0: Foundation Operating System  
**Authority:** QA / Testing Lead, Principal OS Architect  

---

## 1. Overview
This document defines the automated testing matrix and verification procedures for NebuOS Milestone P0.

Milestone P0 is certified **PASS** if and only if:
1. Container image builds cleanly.
2. In-container package and configuration validation passes.
3. Bootable UEFI disk artifact is produced without errors.
4. QEMU UEFI boot sequence reaches serial login prompt (`login:`).
5. Deterministic health gate `nebu-boot-check.service` completes with exit code 0 and commits `boot_success=1`.

## 2. Test Execution Environment
- **Local Container (CT 100):** Uses QEMU in TCG (Tiny Code Generator) mode when `/dev/kvm` is absent.
  > [!NOTE]
  > TCG is used exclusively for functional and state-machine verification. TCG boot durations are not comparable to hardware benchmarks and do NOT represent native performance.
- **Proxmox VM (Production Test Target):** Configured with full KVM hardware virtualization and OVMF UEFI firmware.

## 3. Automated Test Execution
Run the automated test harness:

```bash
# Execute end-to-end CI pipeline:
./scripts/p0-ci.sh

# Or run QEMU test harness directly:
./scripts/test-p0.sh target/nebuos-p0.raw
```

## 4. Test Matrix & Acceptance Criteria

| Test ID | Test Category | Assertion Criteria | Failure Condition |
|---|---|---|---|
| `TC-P0-001` | Image Build | Container build exits code 0 | Non-zero exit code or dependency conflict |
| `TC-P0-002` | Scope Isolation | Zero GUI, Plymouth, Wayland, Slint, Wine packages | Forbidden package detected in rpm list |
| `TC-P0-003` | Dracut Config | `omit_dracutmodules+=" plymouth "` present in initramfs | Plymouth module found in initramfs |
| `TC-P0-004` | Artifact Generation | Valid GPT with ESP (FAT32) and Btrfs root | Partition creation or filesystem mount failure |
| `TC-P0-005` | UEFI Handover | OVMF executes GRUB2 EFI binary cleanly | Firmware hang or unbootable image |
| `TC-P0-006` | Kernel & Initramfs | Linux 6.14+ decompresses and mounts Btrfs root `@` | Kernel panic or missing storage driver |
| `TC-P0-007` | systemd Multi-User | systemd reaches `multi-user.target` | Target dependency failure or PID 1 hang |
| `TC-P0-008` | Immutability Gate | `/usr` is mounted strictly read-only (`ro,nodev`) | Write to `/usr` succeeds |
| `TC-P0-009` | Health Gate | `nebu-boot-check.service` passes all assertions within 45s | Service fails or times out |
| `TC-P0-010` | Boot Success Commit | `boot_success=1` written to `grubenv` | `boot_success` absent or 0 |
| `TC-P0-011` | TTY Availability | `agetty` prompt displayed on `ttyS0` / `tty1` | Login prompt not reached within timeout |
| `TC-P0-012` | Rollback Resiliency | Repeated boot failures decrement counter to rollback | Infinite reboot loop or hang |

## 5. Failure Diagnosis & Log Collection
All test logs are persisted in `target/boot.log`. To inspect failures:
```bash
# View full boot serial transcript:
cat target/boot.log

# Check health check execution output:
grep -A 10 "nebu-boot-check" target/boot.log
```
