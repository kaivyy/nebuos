# ADR-0005: Upstream Wine as Core Windows Application Compatibility Engine

**Status:** APPROVED (Clarified & Reconciled by ADR-0016 and ADR-0017)  
**Date:** 2026-09-04 (Updated 2026-09-05)  
**Deciders:** Principal Systems Architect, Compatibility Engineer  
**Consulted:** PRD §16, §20, §70, §71  
**Related ADRs:** ADR-0006 (Proton/DXVK), ADR-0016 (NebuWine Downstream Distribution), ADR-0017 (Decoupled Runtime Storage), ADR-0018 (Gaming Runtime)  

---

> [!NOTE]
> **Architectural Reconciliation (ADR-0016 & ADR-0017):**
> 1. **Downstream Distribution vs. Hard Fork:** The rejection of Option 2 ("Hard Fork of Wine") in this document specifically rejected an unmaintainable, isolated hard fork that severs upstream WineHQ ties. [ADR-0016](file:///root/NebuOS/docs/decisions/ADR-0016-nebuwine-architecture.md) formalizes **NebuWine** as an *Upstream-First Downstream Distribution* ($\text{NebuWine} = \text{Upstream Wine} + \text{Minimal Maintained Delta}$) tracking pristine WineHQ releases (Wine 11..16+) with strict patch governance.
> 2. **Runtime Storage Decoupling:** The initial storage location `/usr/lib/nebu/runtimes/wine/` in Section 4 has been superseded by [ADR-0017](file:///root/NebuOS/docs/decisions/ADR-0017-decoupled-runtime-packaging-and-storage.md) to `/var/lib/nebu/runtimes/` to resolve coupling with the immutable `/usr` filesystem in `bootc`.

## 1. Context and Problem Statement
NebuOS aims to provide seamless execution of Windows applications on Linux without running a Windows virtual machine. The Windows Win32/NT API is massive, encompassing thousands of undocumented system calls, registry semantics, OLE/COM interfaces, and userland DLLs. Re-implementing this API from scratch is impossible. We must decide how NebuOS integrates Wine to achieve maximum application compatibility while maintaining engineering sustainability.

## 2. Decision Drivers
- **Engineering Viability:** Wine represents over 30 years of continuous engineering by hundreds of systems developers.
- **Maintenance Sustainability:** Forking Wine would create an unsustainable maintenance burden and disconnect NebuOS from upstream fixes.
- **Modularity:** Ability to run decoupled Wine release trees (Stable, Staging) per application prefix.
- **Integration Potential:** Deep control over environment variables, DLL overrides, registry hives, and sandboxing without modifying Wine internals.

## 3. Considered Options
- **Option 1: Upstream Wine Integration via Dynamic Prefixes and Declarative Patching [SELECTED]**
- **Option 2: Hard Fork of Wine (NebuWine) [REJECTED — Reconciled by ADR-0016 as Upstream-First Downstream Distribution]**
- **Option 3: Binary Translation / Emulation (Box64 / QEMU User Space)**
- **Option 4: Windows Virtual Machine Fallback (Explicitly Rejected by PRD)**

## 4. Decision Outcome
**Chosen Option: Option 1 — Upstream Wine Integration Layer.**

NebuOS treats Wine as an external, upstream-aligned dependency. As refined by [ADR-0016](file:///root/NebuOS/docs/decisions/ADR-0016-nebuwine-architecture.md) and [ADR-0017](file:///root/NebuOS/docs/decisions/ADR-0017-decoupled-runtime-packaging-and-storage.md), NebuOS packages upstream-tracking NebuWine release builds in `/var/lib/nebu/runtimes/` (formerly `/usr/lib/nebu/runtimes/wine/`). Compatibility adjustments are applied via two separate tiers: (A) strictly governed upstream-candidate source patches for Wine itself ([docs/compatibility/07-wine-patch-governance.md](file:///root/NebuOS/docs/compatibility/07-wine-patch-governance.md)), and (B) prefix-level declarative compatibility profiles, registry injection, DLL overrides, and sandboxing managed dynamically by `nebu-patcher` ([docs/compatibility/03-patch-engine.md](file:///root/NebuOS/docs/compatibility/03-patch-engine.md)).

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
- *Cons:* Disconnects from upstream improvements; rebasing becomes an insurmountable engineering nightmare; project failure mode observed in numerous dead Linux distributions. *(Note: Superseded by the structured downstream model in ADR-0016).*

### Option 3: Binary Translation (Box64/QEMU)
- *Pros:* Enables running x86_64 binaries on ARM64 hardware.
- *Cons:* Massive performance penalty (30–60% slowdown); unnecessary on native x86_64 hardware.

### Option 4: Virtual Machine Fallback
- *Pros:* High compatibility.
- *Cons:* Direct violation of PRD §1, §3; massive RAM overhead (2–4 GB); slow boot; Windows licensing requirements; completely rejected.

## 6. Confirmation and Validation
- Application compatibility lab executing 50 Windows applications against upstream Wine staging builds with automated verification.
