# ADR-0005: Upstream Wine as Core Windows Application Compatibility Engine

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Compatibility Engineer  
**Consulted:** PRD §16, §20, §70, §71  

---

## 1. Context and Problem Statement
NebuOS aims to provide seamless execution of Windows applications on Linux without running a Windows virtual machine. The Windows Win32/NT API is massive, encompassing thousands of undocumented system calls, registry semantics, OLE/COM interfaces, and userland DLLs. Re-implementing this API from scratch is impossible. We must decide how NebuOS integrates Wine to achieve maximum application compatibility while maintaining engineering sustainability.

## 2. Decision Drivers
- **Engineering Viability:** Wine represents over 30 years of continuous engineering by hundreds of systems developers.
- **Maintenance Sustainability:** Forking Wine would create an unsustainable maintenance burden and disconnect NebuOS from upstream fixes.
- **Modularity:** Ability to run decoupled Wine release trees (Stable, Staging) per application prefix.
- **Integration Potential:** Deep control over environment variables, DLL overrides, registry hives, and sandboxing without modifying Wine internals.

## 3. Considered Options
- **Option 1: Upstream Wine Integration via Dynamic Prefixes and Declarative Patching [SELECTED]**
- **Option 2: Hard Fork of Wine (NebuWine)**
- **Option 3: Binary Translation / Emulation (Box64 / QEMU User Space)**
- **Option 4: Windows Virtual Machine Fallback (Explicitly Rejected by PRD)**

## 4. Decision Outcome
**Chosen Option: Option 1 — Upstream Wine Integration Layer.**

NebuOS treats Wine as an external, immutable dependency. NebuOS packages official upstream Wine Stable and Wine Staging release builds in `/usr/lib/nebu/runtimes/wine/`. Compatibility adjustments are applied externally via declarative compatibility profiles, registry injection, DLL overrides, and environment configuration rather than source code modifications.

### Positive Consequences
- Zero source-code maintenance overhead for the Win32 emulation engine.
- Instant access to upstream Wine releases (e.g. Wine 9.0+ Wayland driver support).
- Clean separation of concerns: NebuOS focuses on orchestration, isolation, UI, and patching.
- Complete licensing compliance (LGPL-2.1).

### Negative Consequences
- Inability to fix internal Wine bugs immediately without upstream submission.
- Dependence on upstream Wine release cadence.

## 5. Pros and Cons of Alternatives

### Option 2: Hard Fork of Wine
- *Pros:* Ability to hack temporary workarounds directly into DLL source code.
- *Cons:* Disconnects from upstream improvements; rebasing becomes an insurmountable engineering nightmare; project failure mode observed in numerous dead Linux distributions.

### Option 3: Binary Translation (Box64/QEMU)
- *Pros:* Enables running x86_64 binaries on ARM64 hardware.
- *Cons:* Massive performance penalty (30–60% slowdown); unnecessary on native x86_64 hardware.

### Option 4: Virtual Machine Fallback
- *Pros:* High compatibility.
- *Cons:* Direct violation of PRD §1, §3; massive RAM overhead (2–4 GB); slow boot; Windows licensing requirements; completely rejected.

## 6. Confirmation and Validation
- Application compatibility lab executing 50 Windows applications against upstream Wine staging builds with automated verification.
