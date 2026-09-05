# ADR-0007: Absolute Prohibition of Virtual Machines for Windows Compatibility

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Product Lead  
**Consulted:** PRD §1, §3, §80, §81, §93  

---

## 1. Context and Problem Statement
When running Windows applications on Linux, many projects take the easy path of launching a hidden Windows virtual machine (KVM, QEMU, VirtualBox). While this guarantees high compatibility, it introduces fatal product flaws: massive memory consumption (2–4 GB minimum), slow VM boot times (15–30s), dual operating system maintenance, Windows licensing requirements, poor GPU virtualization, and lack of seamless desktop window integration. The NebuOS PRD establishes a non-negotiable core vision: NebuOS is a lightweight OS that does NOT use virtual machines.

## 2. Decision Drivers
- **Product Vision Invariant:** PRD §1, §3 explicitly state: "Virtual Machine: NOT PART OF NEBUOS."
- **Hardware Inclusivity:** NebuOS must run on 4GB RAM low-end PCs; running a Windows VM would instantly exhaust all physical memory.
- **Instant Launch Latency:** Applications must launch within 1.5–2.5 seconds, not the 20+ seconds required to boot a Windows hypervisor instance.
- **Zero Windows Licensing:** Users must not be required to purchase, activate, or maintain a proprietary Microsoft Windows OS license.
- **Native Window Ergonomics:** Application windows must be first-class Wayland surfaces with native shadows, snapping, and Alt+Tab integration.

## 3. Considered Options
- **Option 1: Pure API Translation (Wine/Proton/DXVK) with Sandbox Isolation [SELECTED]**
- **Option 2: Micro-VM Fallback for Incompatible Applications (e.g. Firecracker/KVM)**
- **Option 3: Full Windows Virtual Machine (KVM/QEMU with GPU Passthrough)**

## 4. Decision Outcome
**Chosen Option: Option 1 — Pure API Translation Layer (Zero Virtual Machines).**

NebuOS strictly prohibits the inclusion, packaging, or runtime fallback to virtual machines for Windows application execution. All Windows executables run as native Linux processes in isolated user namespaces via Wine and Proton. Applications that require Windows kernel drivers or ring-0 virtualization are marked as unsupported and rejected cleanly.

### Positive Consequences
- True lightweight performance: steady-state system idle memory < 800 MB RAM.
- Application cold launch latency <= 2.5s; warm launch <= 800ms.
- Windows application windows are native Wayland surfaces composited directly on the desktop.
- 100% legal independence: zero Microsoft Windows ISO or license requirements.

### Negative Consequences
- Applications requiring proprietary Windows kernel-mode drivers (`.sys`), hardware dongle drivers, or ring-0 anti-cheat cannot run.

## 5. Pros and Cons of Alternatives

### Option 2 & 3: Micro-VMs or Full Virtual Machines
- *Pros:* Runs software requiring Windows kernel drivers.
- *Cons:* Violates PRD core principle; requires 2–4 GB RAM overhead; requires Windows license; introduces slow boot cycles; destroys the value proposition of NebuOS.

## 6. Confirmation and Validation
- Architectural audit confirming zero hypervisor dependencies (`qemu`, `libvirt`, `kvm`) in base image manifests.
