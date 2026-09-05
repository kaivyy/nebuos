# ADR-0001: Standard LTS Linux Kernel as Hardware and Operating System Foundation

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Linux OS Engineer  
**Consulted:** PRD §1, §5, §60  

---

## 1. Context and Problem Statement
NebuOS is designed to deliver a modern, high-performance desktop operating system capable of running native Linux applications and Windows binaries seamlessly on standard x86_64 hardware. Developing a custom operating system kernel from scratch would require decades of engineering effort, introduce severe hardware driver deficits, and lack mature graphics and containerization stacks. We must choose the underlying kernel foundation that delivers maximum hardware compatibility, advanced memory management, low latency, and robust container isolation.

## 2. Decision Drivers
- **Broad Hardware Ecosystem:** Out-of-the-box support for thousands of x86_64 motherboards, CPUs, Wi-Fi chipsets, and peripheral devices.
- **Direct Rendering Infrastructure (DRM/KMS):** Native integration with Mesa and modern GPU hardware drivers (Intel, AMD, NVIDIA).
- **Advanced Concurrency and Synchronization Primitives:** In-kernel `futex2` (`futex_waitv`), `io_uring`, and `epoll` essential for high-performance Windows API emulation.
- **Resource Control and Isolation:** Linux cgroups v2, user namespaces, and seccomp BPF filters required for per-application Bubblewrap sandboxing.
- **Long-Term Maintainability:** Regular upstream security patches and stable Long-Term Support (LTS) maintenance cycles.

## 3. Considered Options
- **Option 1: Upstream Long-Term Support (LTS) Linux Kernel (6.6+ or Fedora Stable 6.10+) [SELECTED]**
- **Option 2: Custom In-House Microkernel (e.g. seL4 or custom Rust kernel)**
- **Option 3: BSD Kernel Foundation (FreeBSD / OpenBSD)**
- **Option 4: Windows NT Emulation Kernel (ReactOS approach)**

## 4. Decision Outcome
**Chosen Option: Option 1 — Upstream Long-Term Support (LTS) Linux Kernel.**

We select the standard Linux kernel (6.6 LTS / 6.10+ from Fedora base) with specific sysctl tunables (`vm.max_map_count=2147483642`, `split_lock_mitigate=0`, `fs.file-max=2097152`).

### Positive Consequences
- Immediate zero-day support for modern PC hardware, NVMe drives, USB4/Thunderbolt, and Wi-Fi 6E/7.
- First-class support for `futex_waitv` (syscall 449), enabling Proton/Wine Fsync to match native Windows thread synchronization performance.
- Native integration with standard container engines (`bootc`, `bwrap`, `podman`).
- Zero kernel development or maintenance overhead for the NebuOS engineering team.

### Negative Consequences
- Susceptible to occasional upstream kernel regressions (mitigated via atomic image rollback).
- Proprietary NVIDIA out-of-tree kernel modules require pre-compiled kmod layering.

## 5. Pros and Cons of Alternatives

### Option 2: Custom Microkernel
- *Pros:* Strict formal verification, minimal attack surface.
- *Cons:* Zero device driver support for consumer GPUs, Wi-Fi, or audio; years of development before reaching a bootable desktop; completely unfeasible within project scope.

### Option 3: BSD Kernel
- *Pros:* Permissive licensing, clean monolithic architecture.
- *Cons:* Significantly lagging GPU driver support (Mesa Vulkan, DRM/KMS); lack of modern gaming optimizations (`futex_waitv`); smaller hardware compatibility footprint.

### Option 4: ReactOS Approach (NT Kernel Clone)
- *Pros:* Native NT architecture and driver model.
- *Cons:* Decades of incomplete reverse engineering; severe instability with modern 64-bit software; lack of support for modern web browsers, CAD suites, and DirectX 12.

## 6. Confirmation and Validation
- Automated boot tests on physical hardware (Intel Gen9 through Core Ultra, AMD Ryzen 3000-8000 series).
- Sysctl verification asserting `vm.max_map_count` and `fsync` support at boot.
