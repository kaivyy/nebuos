#!/usr/bin/env python3
"""
Generate Architecture Decision Records (ADRs) for NebuOS (docs/decisions/):
ADR-0001 through ADR-0015
"""

import os

DOCS_DIR = "/root/NebuOS/docs/decisions"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_adr(filename, title, context, problem, options, decision, consequences, rejected):
    content = f"""# {title}

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Linux OS Engineer, Compatibility Lead  

---

## 1. Context
{context}

## 2. Problem Statement
{problem}

## 3. Options Considered
{options}

## 4. Decision
{decision}

## 5. Consequences
{consequences}

## 6. Rejected Alternatives
{rejected}
"""
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: decisions/{filename}")

# ADR-0001
write_adr(
    "ADR-0001-linux-kernel.md",
    "ADR-0001: Adoption of Upstream Linux Kernel as Hardware Foundation",
    "NebuOS requires a stable, high-performance hardware abstraction layer with broad support for modern x86_64 CPUs, GPUs, wireless chipsets, and storage controllers.",
    "Should NebuOS create a custom kernel, adopt a microkernel (e.g. seL4, Redox), or reuse the upstream monolithic Linux kernel?",
    "1. Upstream Linux Kernel.\n2. Redox OS (Rust Microkernel).\n3. Custom microkernel/monolithic kernel from scratch.",
    "Adopt the standard upstream Linux kernel (LTS tree).",
    "**Positive:** Instant compatibility with tens of thousands of hardware devices, modern DRM/KMS drivers, Btrfs filesystem, and active security maintenance by the global community.\n**Trade-off:** Retains monolithic kernel complexity, but this is mitigated via unprivileged userland sandboxing.",
    "Writing a new kernel from scratch was rejected due to catastrophic development timelines, zero driver support for modern NVIDIA/AMD GPUs, and complete incompatibility with upstream Wine."
)

# ADR-0002
write_adr(
    "ADR-0002-fedora-base.md",
    "ADR-0002: Selection of Fedora Atomic / bootc as Base Operating System",
    "NebuOS needs an established Linux base distribution providing modern packages, atomic updates, and enterprise security policies.",
    "Which Linux distribution base should NebuOS build upon?",
    "1. Fedora Atomic / bootc.\n2. Debian / Ubuntu.\n3. Arch Linux.\n4. Custom Yocto/Linux-From-Scratch.",
    "Adopt Fedora Atomic (utilizing `bootc` and `rpm-ostree`).",
    "**Positive:** Immutable rootfs (`/usr`), first-class SELinux policies, modern upstream kernel/Mesa packages, and standard OCI container deployment format.\n**Trade-off:** Requires understanding OSTree packaging conventions over traditional package managers.",
    "Arch was rejected due to rolling-release instability. Debian was rejected due to stale Mesa graphics drivers required for modern CAD/gaming."
)

# ADR-0003
write_adr(
    "ADR-0003-wayland.md",
    "ADR-0003: Selection of Wayland as Primary Display Protocol",
    "NebuOS requires a secure, high-performance display architecture supporting multi-monitor mixed DPI and smooth frame presentation.",
    "Should NebuOS use the legacy X11 display server or Wayland?",
    "1. Wayland display protocol.\n2. X11 (X.Org Server).",
    "Adopt Wayland exclusively for the core display architecture.",
    "**Positive:** Eliminates tearing, provides per-surface security isolation, handles mixed-DPI scaling seamlessly, and enables direct scanout.\n**Trade-off:** Legacy X11 applications require an Xwayland bridge.",
    "X11 was rejected because it is deprecated upstream, fundamentally insecure (any client can sniff keystrokes of other windows), and incapable of flicker-free mixed-DPI scaling."
)

# ADR-0004
write_adr(
    "ADR-0004-rust.md",
    "ADR-0004: Rust as the Primary Systems Implementation Language",
    "NebuOS components (compositor, desktop shell, runtime daemon, patch engine) manage untrusted binaries and user hardware interfaces.",
    "Which programming language should be mandated for newly written NebuOS components?",
    "1. Rust.\n2. C / C++.\n3. Go.\n4. Python / JavaScript.",
    "Mandate Rust as the primary language for all in-house Nebu components.",
    "**Positive:** Memory safety at compile time, eliminating buffer overflows, use-after-free, and data races without garbage collection pauses.\n**Trade-off:** Stricter compiler learning curve and longer initial compile times.",
    "C/C++ was rejected due to high risks of memory corruption vulnerabilities. Python and JavaScript were rejected due to unacceptable memory footprint and latency."
)

# ADR-0005
write_adr(
    "ADR-0005-nebu-compositor.md",
    "ADR-0005: In-House NebuCompositor Built on Smithay",
    "The desktop environment requires a tailored Wayland compositor optimized for low latency, zero-copy scanout, and memory efficiency.",
    "Should NebuOS use an off-the-shelf desktop compositor (Mutter, KWin, Sway) or build NebuCompositor in Rust?",
    "1. Custom NebuCompositor using Smithay (Rust).\n2. GNOME Mutter (C).\n3. KDE KWin (C++).\n4. wlroots-based compositor.",
    "Develop NebuCompositor in Rust using the Smithay modular compositor library.",
    "**Positive:** Complete control over frame scheduling, direct scanout optimizations for Wine, zero GNOME/KDE bloat, < 75 MB memory footprint.\n**Trade-off:** Requires implementing window management heuristics in-house.",
    "Mutter and KWin were rejected due to heavy dependency graphs (pulling in large portions of GNOME/KDE desktop stacks) and higher memory overhead."
)

# ADR-0006
write_adr(
    "ADR-0006-nebu-shell.md",
    "ADR-0006: In-House Native NebuShell (No Electron / Chromium)",
    "NebuOS requires a lightweight, responsive desktop shell providing taskbars, application launchers, quick settings, and notification centers.",
    "How should NebuShell be engineered and rendered?",
    "1. Native Rust UI (Slint / Iced / GTK4-rs) over Wayland layer-shell.\n2. Web-based shell using Electron / Chromium.\n3. GNOME Shell extensions.",
    "Implement NebuShell in native Rust using declarative GPU-accelerated UI toolkits.",
    "**Positive:** Sub-100ms launcher response time, memory footprint < 45 MB, zero Chromium runtime overhead.\n**Trade-off:** UI widgets must be styled in native code rather than CSS/HTML.",
    "Electron and web-based shells were strictly rejected because they consume 300-600 MB of RAM at idle, violating the 4 GB RAM low-end performance mandate."
)

# ADR-0007
write_adr(
    "ADR-0007-wine.md",
    "ADR-0007: Upstream Wine as the Windows Compatibility Foundation",
    "Windows application compatibility requires translating complex Win32/NT APIs into Linux POSIX system calls.",
    "Should NebuOS write a clean-room Windows userland emulator or adopt upstream Wine?",
    "1. Upstream Wine (Stable & Staging) with curated Nebu integration.\n2. Clean-room Windows NT userland from scratch.",
    "Adopt upstream Wine as the compatibility foundation.",
    "**Positive:** Leverages over 30 years of continuous engineering and millions of lines of proven API translations.\n**Trade-off:** Must track upstream changes and maintain patch rebasing.",
    "Rewriting Wine from scratch was rejected as an insurmountable multi-decade undertaking that would delay NebuOS indefinitely."
)

# ADR-0008
write_adr(
    "ADR-0008-proton.md",
    "ADR-0008: Proton Runtime Integration for Windows Gaming Workloads",
    "Windows gaming requires specialized DirectX 11/12 translation, synchronous frame pacing, and game controller mappings.",
    "Should NebuOS rely solely on vanilla Wine or integrate Valve's Proton stack?",
    "1. Dual runtime model: Wine for desktop/CAD, Proton for games.\n2. Vanilla Wine for everything.",
    "Integrate Proton as the dedicated execution engine for gaming workloads.",
    "**Positive:** Incorporates DXVK, VKD3D-Proton, esync/fsync, and battle-tested gaming compatibility tested by millions of Steam Deck users.\n**Trade-off:** Dual runtime binaries increase initial image storage by ~1.2 GB.",
    "Using vanilla Wine for gaming was rejected because vanilla Wine lacks critical Direct3D 12 and controller patches present in Proton."
)

# ADR-0009
write_adr(
    "ADR-0009-no-vm.md",
    "ADR-0009: Strict Prohibition of Virtual Machines for Compatibility",
    "Some Linux distributions achieve Windows compatibility by spinning up headless Windows VMs inside QEMU/KVM.",
    "Should NebuOS permit Windows VMs as a compatibility fallback?",
    "1. Strict NO VM policy.\n2. Headless Windows VM fallback.",
    "Strictly prohibit Virtual Machines as part of the NebuOS runtime.",
    "**Positive:** Eliminates Windows licensing fees, eliminates 4-8 GB RAM hypervisor overhead, enables true native process integration and direct GPU scanout.\n**Trade-off:** Applications requiring Windows ring-0 drivers cannot run.",
    "VMs were rejected because they undermine the primary mission of NebuOS: a lightweight, fast, native-feeling operating system usable on 4 GB RAM hardware."
)

# ADR-0010
write_adr(
    "ADR-0010-per-application-wine-prefixes.md",
    "ADR-0010: Isolated Per-Application Wine Prefixes",
    "Traditionally, Wine uses a single shared prefix (`~/.wine`), leading to DLL conflicts and configuration corruption when multiple applications are installed.",
    "How should Wine prefixes be partitioned across installed applications?",
    "1. Isolated per-application prefixes (`~/.nebu/apps/<app_id>/`).\n2. Single shared global prefix (`~/.wine`).",
    "Enforce isolated per-application prefixes for all managed Windows applications.",
    "**Positive:** Total isolation between applications, zero DLL override conflicts, trivial per-app rollback and uninstallation.\n**Trade-off:** Higher disk usage, mitigated through Btrfs reflink deduplication.",
    "A shared global prefix was rejected due to notorious instability and irrecoverable dependency corruption."
)

# ADR-0011
write_adr(
    "ADR-0011-sqlite.md",
    "ADR-0011: Adoption of SQLite for Local Compatibility Metadata",
    "NebuOS requires an embedded database to query application profiles, MIME associations, and certification statuses in sub-milliseconds.",
    "Which database engine should be used for local metadata?",
    "1. SQLite 3 (WAL mode).\n2. Flat JSON files.\n3. Client-server database (PostgreSQL/MySQL).",
    "Adopt SQLite 3 with Write-Ahead Logging (WAL) enabled.",
    "**Positive:** Serverless, zero-maintenance, ACID-compliant, instant indexed queries, sub-1ms search performance.\n**Trade-off:** Requires schema migration handling.",
    "Flat JSON files were rejected due to slow linear scanning and file lock race conditions during concurrent application launches."
)

# ADR-0012
write_adr(
    "ADR-0012-btrfs.md",
    "ADR-0012: Adoption of Btrfs with Subvolumes as Default Filesystem",
    "NebuOS requires fast snapshotting for prefix rollback, transparent compression for low storage footprints, and instant prefix provisioning.",
    "Which filesystem should NebuOS format by default on user drives?",
    "1. Btrfs (with subvolumes `@`, `@home`, `@nebu_apps`).\n2. Ext4.\n3. ZFS on Linux.",
    "Adopt Btrfs as the default filesystem.",
    "**Positive:** Copy-on-Write reflink copying allows 150ms prefix creation; zstd compression reduces OS storage by 50%; instant snapshot rollback.\n**Trade-off:** Copy-on-Write can cause fragmentation on databases without `nodatacow`.",
    "Ext4 was retained as a legacy option but rejected as default due to lack of reflink and snapshot capabilities."
)

# ADR-0013
write_adr(
    "ADR-0013-atomic-updates.md",
    "ADR-0013: Transactional Atomic System Image Updates",
    "Traditional package updates (`dnf update`, `apt upgrade`) can leave a system unbootable if interrupted by power failure or dependency breakage.",
    "How should operating system updates be deployed in NebuOS?",
    "1. Atomic image deployment (`bootc` / `ostree`).\n2. Traditional package-by-package updates.",
    "Mandate atomic image deployment for the entire base operating system.",
    "**Positive:** Updates are applied transactionally in the background; power cuts cause zero damage; 1-click bootloader rollback.\n**Trade-off:** Base rootfs is immutable (`/usr` read-only).",
    "Traditional package-by-package updating was rejected because package conflicts and partial installs account for >80% of desktop Linux boot failures."
)

# ADR-0014
write_adr(
    "ADR-0014-compatibility-database.md",
    "ADR-0014: Structured Declarative Compatibility Database",
    "Automating Windows executable execution requires mapping hashes and PE headers to validated Wine versions, DLL overrides, and patches.",
    "How should compatibility knowledge be structured and maintained?",
    "1. Centralized relational schema (SQLite) synchronized with remote catalog.\n2. Hardcoded procedural shell scripts (Winetricks model).",
    "Implement a structured declarative compatibility database schema.",
    "**Positive:** Programmatically queryable, version-controlled, auditable, and easily editable via community recipes.\n**Trade-off:** Schema must be kept backwards-compatible across OS versions.",
    "Procedural scripts were rejected because they cannot be easily introspected, tested, or rolled back automatically."
)

# ADR-0015
write_adr(
    "ADR-0015-compatibility-lab.md",
    "ADR-0015: Dedicated Bare-Metal Compatibility Lab & Regression Harness",
    "Software compatibility claims in open-source projects often degrade over time due to untested upstream regressions in kernels, Mesa, or Wine.",
    "How should NebuOS guarantee long-term compatibility stability?",
    "1. Dedicated physical Compatibility Lab running automated real-world workflows.\n2. Relying on user bug reports after stable release.",
    "Establish a dedicated Compatibility Lab with automated hardware testing harnesses.",
    "**Positive:** Detects regressions before code reaches Stable; validates real applications (AutoCAD, Office) on real Intel/AMD/NVIDIA silicon.\n**Trade-off:** Capital expenditure for lab hardware and automated runner maintenance.",
    "Relying solely on user bug reports was rejected because breaking production user workflows damages trust and leads to user churn."
)

print("All 15 ADRs generated successfully.")
