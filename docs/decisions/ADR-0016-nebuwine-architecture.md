# ADR-0016: NebuWine Downstream Distribution Architecture and Upstream-First Lifecycle

**Status:** APPROVED  
**Date:** 2026-09-05  
**Authors:** Principal OS Architect, Linux Compatibility Architect, Wine Compatibility Engineer, Git/Upstream Integration Engineer  
**Deciders:** NebuOS Core Architecture Group  
**Supercedes:** Reconciles and supersedes the semantic ambiguity in ADR-0005 Option 2  
**Related ADRs:** ADR-0005 (Wine Integration), ADR-0006 (Proton/DXVK), ADR-0010 (Hardware Compatibility), ADR-0015 (Compatibility Lab), ADR-0017 (Decoupled Runtime Storage), ADR-0018 (Gaming Runtime)  
**Consulted:** PRD §16, §20, §27, §28, §29, §30, §70, §71, §72, §93  

---

## 1. Context and Problem Statement

ADR-0005 previously selected "Option 1: Upstream Wine Integration Layer" and rejected "Option 2: Hard Fork of Wine (NebuWine)" to avoid the historical Linux pitfall of an unmaintainable, diverged Wine fork. However, this created a critical architectural ambiguity:
1. Pure upstream Wine frequently lags by months or years in addressing specific enterprise CAD/BIM stubs, niche font rendering quirks, and Wayland window-management behaviors.
2. Conversely, a disconnected hard fork invariably leads to rebase bankruptcy, security neglect, and abandonment.
3. System specifications ambiguously referenced "NebuWine" without defining whether it was an external distribution, a fork, or an in-tree module.

NebuOS requires a crystal-clear, sustainable architectural model that delivers rapid application fixes without severing ties with upstream WineHQ.

---

## 2. Core Architectural Principle

NebuOS formally adopts the **Upstream-First Downstream Distribution Model**:

$$\text{Upstream First} \longrightarrow \text{Local When Necessary} \longrightarrow \text{Upstream Again When Possible}$$

$$\text{NebuWine} = \text{Upstream Wine} + \text{Minimal Maintained Delta}$$

NebuWine is **NOT** a permanent hard fork. NebuWine is an official **downstream Wine distribution** built directly upon pristine upstream WineHQ git tags, carrying a strictly governed, rebaseable, transparent patchset.

---

## 3. Decision Drivers

- **Continuous Upstream Synchronization:** NebuWine must cleanly track WineHQ releases (Wine 10, 11, 12, 13, 14, 15, 16+) without requiring NebuOS architectural redesigns or manual codebase overhauls.
- **Minimal Delta Discipline:** Every line of downstream code represents technical debt. The downstream patchset must remain small, measurable, and actively driven toward upstream acceptance.
- **Traceability and Provenance:** Every downstream commit or patch must document its exact purpose, author, upstream review link, target applications, and test verification.
- **Architectural Separation:** Wine source patching must never be conflated with prefix configuration or user-space compatibility workarounds.

---

## 4. Architectural Domain Separation

NebuOS strictly bifurcates compatibility remediation into two distinct domains:

```
+-------------------------------------------------------------------------------+
|                    NebuOS Two-Domain Compatibility Architecture               |
+-------------------------------------------------------------------------------+
                                        |
       +--------------------------------+-------------------------------+
       |                                                                |
       v                                                                v
+-------------------------------+                     +-------------------------------+
| Domain A: Wine Source Patching|                     | Domain B: Prefix Remediation  |
| (Governed by ADR-0016 / 07-WP)|                     | (Governed by 03-patch-engine) |
+-------------------------------+                     +-------------------------------+
| - Target: wine.git source code|                     | - Target: WINEPREFIX state    |
| - Scope: Win32/NT API bugs,   |                     | - Scope: DLL overrides, registry|
|   Wayland driver integration, |                       keys, font substitution,      |
|   wineserver IPC, ntdll stubs |                       bwrap sandbox rules, env vars |
| - Build-time artifact         |                     | - Run-time dynamic injection  |
| - Upstream submission required|                     | - Managed by nebu-patcher     |
+-------------------------------+                     +-------------------------------+
```

1. **Domain A: Wine Source Patching (`wine.git`):**
   - Applies solely to C/assembly source code within the Wine source tree.
   - Purpose: Win32 API implementation, WineHQ bug fixes, kernel driver glue (e.g. NTSYNC), and Wayland driver enhancements.
   - Detailed governance, lifecycle, and provenance are codified in `docs/compatibility/07-wine-patch-governance.md`.

2. **Domain B: Prefix / Application Remediation (`nebu-patcher`):**
   - Applies at runtime to user prefixes without touching Wine binaries.
   - Governed by the 9-Tier Patch Hierarchy defined in `docs/compatibility/03-patch-engine.md` (Tier 1 Env Vars through Tier 9 Binary Hooking).

---

## 5. Downstream Patch Metadata Standard

Every downstream patch maintained in NebuWine must contain the following mandatory header schema:

```yaml
# --- NEBUWINE PATCH METADATA ---
Patch-ID: NW-PATCH-2026-0042
Category: UPSTREAM-CANDIDATE | APPLICATION-COMPATIBILITY | NEBUOS | PERFORMANCE | SECURITY-SENSITIVE | EXPERIMENTAL
Purpose: "Implement NtQueryInformationProcess ProcessMitigationPolicy stub for Autodesk Licensing"
Owner: "NebuOS Compatibility Group <compat@nebuos.org>"
Affected-Subsystem: ntdll / process
Affected-Applications: "Autodesk AutoCAD 2024, Revit 2025"
Introduced-Baseline: "wine-11.2"
Last-Verified-Baseline: "wine-11.8"
Upstream-Issue-URL: "https://bugs.winehq.org/show_bug.cgi?id=XXXXX"
Upstream-MR-URL: "https://gitlab.winehq.org/wine/wine/-/merge_requests/XXXX"
Upstream-Status: SUBMITTED | UNDER-REVIEW | REJECTED | NOT-SUBMITTED
Regression-Test: "tests/ntdll/test_mitigation_policy.c"
Security-Impact: "NONE (Stubs read-only mitigation flags; returns STATUS_SUCCESS)"
Performance-Impact: "NEGLIGIBLE (< 2ns CPU overhead on query)"
Lifecycle-Status: PROPOSED | TESTING | UPSTREAM-CANDIDATE | SUBMITTED | ACCEPTED | UPSTREAMED | REMOVE | LOCAL | OBSOLETE | SECURITY-HOLD
# --- END METADATA ---
```

---

## 6. Multi-Generation Wine Progression Model

NebuWine is designed to span across Wine generations (Wine 11 through Wine 16+) via a formal state machine:

```
[ New WineHQ Tag ]
        |
        v
[ Applicability & Delta Analysis ]
        |
        +---> Clean Rebase? ---> YES ---> [ Automated Build ]
        |                                          |
        NO                                         v
        |                                  [ WineHQ C-Tests ]
        v                                          |
[ Merge Conflict / Equivalence Triage ]            v
        |                                  [ NebuOS Headless Tests ]
        v                                          |
[ Rebase & Update Metadata ]                       v
        |                                  [ L0-L7 App & Game Workflows ]
        +----------------------------------------> |
                                                   v
                                          [ Compatibility Lab Gate ]
                                                   |
                        +--------------------------+--------------------------+
                        |                                                     |
                        v                                                     v
                 [ PASS Tier 0-3 ]                                    [ FAIL Any Gate ]
                        |                                                     |
                        v                                                     v
             [ Promote to CANDIDATE ]                              [ Retain STABLE Baseline ]
                        |                                                     |
                        v (2 weeks burn-in)                                   v
             [ Promote to STABLE ]                                 [ Demote / Quarantine ]
```

### 6.1 Version Support Classifications
- **SUPPORTED (STABLE):** The production-default runtime provided to standard users. Thoroughly validated against L0-L7 workflows.
- **CANDIDATE:** Next-generation build undergoing Compatibility Lab verification and community opt-in testing.
- **LEGACY:** Retained previous-generation runtimes preserved in `/var/lib/nebu/runtimes/` for applications requiring pinned environments.
- **UNSUPPORTED:** Retired or non-reproducible historical builds.

---

## 7. Consequences

### Positive Consequences
- Formally resolves the contradiction between ADR-0005 and PRD requirements for targeted Wine improvements.
- Establishes a disciplined, audit-compliant process where no rogue, undocumented patches can enter the OS.
- Positions NebuOS as an active, constructive contributor to upstream WineHQ rather than a parasitic fork.
- Future-proofs the operating system for Wine 11, 12, 13, 14, 15, and 16+.

### Negative Consequences
- Requires engineering discipline to rebase downstream patches against upstream Wine bi-weekly development tags.
- Upstream submission overhead: patches must be written according to WineHQ coding guidelines and test conventions.

---

## 8. Verification and Acceptance Criteria

- [x] Formally documented in ADR-0016; cross-referenced in ADR-0005.
- [x] Full technical implementation specification authored in `docs/runtime/08-nebuwine-specification.md`.
- [x] Wine source patch governance standard authored in `docs/compatibility/07-wine-patch-governance.md`.
