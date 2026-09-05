# NebuOS Architecture Navigation Map

**Document ID:** NEBU-ARCH-MAP-001  
**Authority:** Architectural Index & Navigation Guide  
**Status:** ACTIVE  

---

## 1. System Vision & Invariants

NebuOS is an immutable, container-native Linux desktop operating system based on **Fedora Atomic / bootc** designed to run native Linux and Windows applications with native performance and appearance.

### The Three Master Invariants:
1. **Virtual Machine: NOT PART OF NEBUOS:** NebuOS does **NOT** run Windows in a virtual machine. Compatibility is achieved exclusively through user-space API translation and graphics intercept (Wine, Proton, DXVK, VKD3D).
2. **Immutable Base Operating System:** The root filesystem (`/usr`) is read-only and deployed as atomic OCI container images via `bootc`. System state is strictly confined to `/var` and `/etc`.
3. **Rust as Primary Language:** Custom NebuOS system daemons (`nebu-compositor`, `nebu-shell`, `nebu-runtime-daemon`) are developed in pure, idiomatic Rust.

---

## 2. Conceptual Layer Topology

```
+-------------------------------------------------------------------------------+
|                         Windows Applications & Games                          |
+-------------------------------------------------------------------------------+
|                      DXVK (D3D9..11) / VKD3D-Proton (D3D12)                   |
+-------------------------------------------------------------------------------+
|                       Wine 9.x Staging / Valve Proton                         |
+-------------------------------------------------------------------------------+
|             Compatibility Engine (SQLite Database, Patch Engine DSL)          |
+-------------------------------------------------------------------------------+
|          NebuRuntime Daemon (Per-App Prefix, Bubblewrap Sandbox, D-Bus)       |
+-------------------------------------------------------------------------------+
|                      NebuShell (Slint UI Toolkit, Theme Engine)               |
+-------------------------------------------------------------------------------+
|                  NebuCompositor (Smithay 0.3+, Pure Wayland Display)          |
+-------------------------------------------------------------------------------+
|                             Wayland Protocol Core                             |
+-------------------------------------------------------------------------------+
|                     PipeWire Audio & Media Processing Engine                  |
+-------------------------------------------------------------------------------+
|                       Mesa 3D Graphics (RadeonSI, NVK, Iris)                  |
+-------------------------------------------------------------------------------+
|                       DRM/KMS Linux Display Drivers & libinput                |
+-------------------------------------------------------------------------------+
|                  systemd Init, NetworkManager, D-Bus Broker                   |
+-------------------------------------------------------------------------------+
|             Fedora Atomic / bootc Base Image (Btrfs Subvolumes)               |
+-------------------------------------------------------------------------------+
|                             Linux Kernel 6.x                                  |
+-------------------------------------------------------------------------------+
|                          x86_64 UEFI Physical Hardware                        |
+-------------------------------------------------------------------------------+
```

---

## 3. Subsystem Directory Navigation

For deep technical specifications, schemas, and contracts, refer to the authoritative specification documents:

### Core System Specifications (`docs/specification/`)
- [`00-system-specification.md`](docs/specification/00-system-specification.md): Base OS component ownership, package list, process tree.
- [`01-boot-specification.md`](docs/specification/01-boot-specification.md): UEFI, GRUB2 BLS, dracut initramfs, timing budgets.
- [`02-process-ipc-specification.md`](docs/specification/02-process-ipc-specification.md): Process hierarchy, cgroups v2 slices, D-Bus bus topology.
- [`03-filesystem-specification.md`](docs/specification/03-filesystem-specification.md): Partitioning, Btrfs subvolumes (`@`, `@home`, `@var`), mount flags.
- [`04-security-specification.md`](docs/specification/04-security-specification.md): Bubblewrap sandbox, SELinux policy, seccomp BPF filters.
- [`05-hardware-specification.md`](docs/specification/05-hardware-specification.md): GPU detection, kernel modules, power states.
- [`06-resource-management.md`](docs/specification/06-resource-management.md): Memory budgets, systemd-oomd, zram configuration.

### Interface & Contract Specifications (`docs/interfaces/`)
- [`00-interface-overview.md`](docs/interfaces/00-interface-overview.md): System IPC boundary map and versioning policy.
- [`01-ipc-interfaces.md`](docs/interfaces/01-ipc-interfaces.md): D-Bus introspection XML (`org.nebu.Runtime1`, `org.nebu.Compositor1`).
- [`02-runtime-interfaces.md`](docs/interfaces/02-runtime-interfaces.md): Rust trait definitions for runtime engines.
- [`03-compositor-interfaces.md`](docs/interfaces/03-compositor-interfaces.md): Wayland protocol extensions.
- [`04-shell-interfaces.md`](docs/interfaces/04-shell-interfaces.md): Layer-shell surface contracts, theme engine traits.
- [`05-installer-interfaces.md`](docs/interfaces/05-installer-interfaces.md): PE binary analysis and desktop entry registration.
- [`06-database-interfaces.md`](docs/interfaces/06-database-interfaces.md): SQLite schema, migrations, connection pooling.

### Architectural Decision Records (`docs/decisions/`)
- [`ADR-0001`](docs/decisions/ADR-0001-base-os-architecture.md): Fedora Atomic and bootc Platform.
- [`ADR-0002`](docs/decisions/ADR-0002-btrfs-filesystem-layout.md): Btrfs Filesystem and Subvolume Layout.
- [`ADR-0003`](docs/decisions/ADR-0003-smithay-wayland-compositor.md): Smithay Rust Wayland Compositor.
- [`ADR-0004`](docs/decisions/ADR-0004-wine-proton-integration.md): Wine and Proton Dual Runtime Integration.
- [`ADR-0005`](docs/decisions/ADR-0005-nvidia-driver-strategy.md): NVIDIA Graphics Driver Strategy.
- [`ADR-0006`](docs/decisions/ADR-0006-btrfs-reflink-prefix-management.md): Btrfs Reflink Instant Prefix Creation.
- [`ADR-0007`](docs/decisions/ADR-0007-dual-licensing-strategy.md): Dual Licensing Strategy (MPL-2.0 / Apache-2.0).
- [`ADR-0008`](docs/decisions/ADR-0008-desktop-first-philosophy.md): Linux-First Desktop Paradigm.
- [`ADR-0009`](docs/decisions/ADR-0009-nebushell-ui-architecture.md): NebuShell Pluggable UI Architecture.
- [`ADR-0010`](docs/decisions/ADR-0010-bubblewrap-security-isolation.md): Bubblewrap Sandbox Security Architecture.

### Implementation Roadmap (`docs/roadmap/`)
- [`00-implementation-roadmap.md`](docs/roadmap/00-implementation-roadmap.md): Master roadmap and milestone dependency DAG.
- [`01-p0-foundation.md`](docs/roadmap/01-p0-foundation.md): Milestone P0 Foundation Operating System.
- [`02-p1-nebucompositor.md`](docs/roadmap/02-p1-nebucompositor.md): Milestone P1 Wayland Compositor.
- [`03-p2-nebushell.md`](docs/roadmap/03-p2-nebushell.md): Milestone P2 Desktop Shell.
- [`04-p3-neburuntime.md`](docs/roadmap/04-p3-neburuntime.md): Milestone P3 Windows Application Runtime.
- [`05-p4-compatibility-engine.md`](docs/roadmap/05-p4-compatibility-engine.md): Milestone P4 Compatibility Database & Patches.
- [`06-p5-graphics-runtime.md`](docs/roadmap/06-p5-graphics-runtime.md): Milestone P5 DXVK / VKD3D & GPU Acceleration.
- [`07-p6-applications.md`](docs/roadmap/07-p6-applications.md): Milestone P6 Installer & Software Center.
- [`08-p7-compatibility-lab.md`](docs/roadmap/08-p7-compatibility-lab.md): Milestone P7 Compatibility Testing Lab.
- [`09-p8-production-validation.md`](docs/roadmap/09-p8-production-validation.md): Milestone P8 Production Certification.
