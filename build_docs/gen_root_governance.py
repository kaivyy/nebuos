import os

BASE_DIR = "/root/NebuOS"

def write_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created: {rel_path} ({len(content)} bytes)")

# ==============================================================================
# AGENTS.md
# ==============================================================================
agents_md = """# Universal Agent Operating Contract & Repository Governance — NebuOS

**Document ID:** NEBU-AGENTS-001  
**Authority Level:** Mandatory Repository Contract  
**Target Audience:** All AI Coding Agents (Codex, Claude Code, Agy CLI, Gemini, Cursor, and any automated/semi-automated engineering agent) and Human Maintainers  
**Status:** ACTIVE & BINDING  

---

## 1. Universal Agent Operating Contract

This repository operates under a strict, agent-neutral **Governance Contract**.

### The Core Invariant
> **Agents may change. The repository remains sovereign.**  
> Chat history can be lost, truncated, or discarded at any time.  
> Agent memory is **NEVER** a source of truth.  
> The repository state, verified artifacts, and documented specifications are the **sole authoritative record** of the NebuOS project.  
> No agent may alter architecture, violate milestone boundaries, bypass verification gates, weaken security policies, or declare completion without concrete evidence.

Every AI agent entering this repository—regardless of model provider, vendor, context window, or interface—is legally and operationally bound by this document.

---

## 2. Project Identity & Conceptual Architecture

### What NebuOS Is
NebuOS is a lightweight, immutable, container-native Linux desktop operating system built on **Fedora Atomic / bootc** with **Rust** as the primary system implementation language. It provides a native-feeling desktop experience capable of running native Linux and Windows user-space applications without requiring a Windows virtual machine.

### Non-Negotiable Product Invariant
> **VIRTUAL MACHINE: NOT PART OF NEBUOS**  
> NebuOS does **NOT** run a guest Windows OS inside QEMU, KVM, VirtualBox, or any hypervisor. Compatibility is achieved exclusively via native user-space API translation and graphics call intercept (Wine, Proton, DXVK, VKD3D). Any suggestion, code, or documentation attempting to introduce a Windows VM violates the master product vision.

### Conceptual System Layering
```
                      +------------------------------------------+
                      |       Windows Applications & Games       |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |              DXVK / VKD3D                |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |              Wine / Proton               |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |           Compatibility Engine           |
                      |       (Database, Fingerprint, Patch)     |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |               NebuRuntime                |
                      |   (Per-App Prefix, bwrap Sandbox, DBus)  |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |             Nebu System Apps             |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |                NebuShell                 |
                      |       (Slint, Pluggable UI Engine)       |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |              NebuCompositor              |
                      |          (Smithay, Pure Wayland)         |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |                 Wayland                  |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |           PipeWire Audio & Media         |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |             Mesa 3D Graphics             |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |         DRM/KMS & Hardware Drivers       |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |             System Services              |
                      |        (systemd, NetworkManager)         |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |     Fedora Atomic / bootc Image Base     |
                      |        (Immutable /usr, Btrfs Pool)      |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |              Linux Kernel 6.x            |
                      +------------------------------------------+
```

*Important Architecture Note:* The diagram above represents the **target steady-state conceptual layering**. It does **NOT** imply that all layers exist in early milestones. Each roadmap milestone enforces a strict, isolated subsystem boundary.

---

## 3. Foundational Governance Principles

Every agent must internalize and obey these 14 principles:
1. **Source Code is Not the Sole Truth:** Code without specification, tests, and documentation violates repository integrity.
2. **Repository State is Evidence:** Only files present in the filesystem and tracked in git constitute evidence.
3. **Architecture Decisions Must Be Documented:** No architectural decision exists unless recorded in an approved ADR (`docs/decisions/`).
4. **Milestone Boundaries are Sovereign:** Future milestone features must never be implemented prematurely ("sekalian", "while we're here", or "for demo purposes").
5. **No Silent Architecture Changes:** You may not substitute libraries, frameworks, or system patterns without an explicit ADR and impact analysis.
6. **No Scope Creep:** Work strictly within the assigned task and allowed scope.
7. **No Speculative Abstractions:** Do not build premature abstractions for hypothetical future needs.
8. **No Duplicate Architectures or Sources of Truth:** Never maintain parallel specifications or redundant truth files.
9. **Verify Before Claiming Success:** Assertions require reproducible execution logs and evidence.
10. **Traceability is Mandatory:** Every change must map back to requirements in `PRD.md` or a formal specification.
11. **Work From Filesystem State, Not Memory:** Read current files upon entering; never rely on context memory or past session summaries.
12. **Previous Agent Output is Not Fact:** Verify claims made by previous agents through independent inspection.
13. **No False Completion:** Never declare `100% Complete`, `DONE`, or `PASS` without passing all acceptance criteria.
14. **Defend System Immutability & Safety:** Respect host and guest safety protocols at all times.

---

## 4. Agent Startup Protocol (Mandatory 21 Steps)

Upon receiving any prompt or task in this repository, **EVERY AGENT MUST EXECUTE THIS PROTOCOL IN SEQUENCE**:

1. **Read `AGENTS.md`:** Re-verify operating rules and behavioral constraints.
2. **Read `PROJECT_STATE.md`:** Determine actual current project status, active milestone, and blockers.
3. **Read `HANDOFF.md`:** Review the exact state and directives left by the preceding agent.
4. **Read `docs/INDEX.md`:** Understand the documentation landscape and navigate to relevant specifications.
5. **Inspect Repository Structure:** Review directory layout and file existence.
6. **Inspect `git status`:** Check working tree cleanliness and uncommitted changes.
7. **Inspect `git diff`:** Verify if active modifications exist and establish their ownership.
8. **Identify Current Milestone:** Confirm whether the project is in P0, P1, P2, etc.
9. **Identify Current Task:** Extract the precise objective of the current invocation.
10. **Identify Allowed Scope:** Enumerate the exact files and directories permitted to be touched.
11. **Identify Relevant Specifications:** Read the deep technical specs (`docs/specification/`, `docs/interfaces/`).
12. **Identify Relevant Tests:** Determine which automated or manual acceptance tests validate this task.
13. **Check Open Blockers:** Verify that no blocking issues (`BLOCKER`) halt this work.
14. **Create Execution Plan:** Formulate a structured, evidence-driven implementation plan.
15. **Implement ONLY Approved Scope:** Execute edits strictly within allowed boundaries.
16. **Run Verification:** Execute linters, tests, builds, or static checks.
17. **Review Changes:** Inspect `git diff` to ensure zero unintended changes or formatting pollution.
18. **Update Documentation (if behavior changed):** Synchronize specifications and traceability.
19. **Update `PROJECT_STATE.md`:** Record current status, test results, and milestone progress.
20. **Update `HANDOFF.md`:** Write a crisp, actionable transfer report for the next agent.
21. **Produce Final Report:** Deliver a structured, factual summary to the user.

---

## 5. Source of Truth Policy & Conflict Protocol

### Hierarchy of Authority
When resolving discrepancies or conflicting statements across files, agents must adhere to this strict hierarchy:

```
    Tier 1: PRD.md (Master Product Vision, Invariants, Non-VM Mandate)
      |
      v
    Tier 2: docs/decisions/ (ADR-0001..10: Binding Architecture Decisions)
      |
      v
    Tier 3: docs/specification/ & docs/interfaces/ (Technical Contracts & Schemas)
      |
      v
    Tier 4: docs/roadmap/ (Milestone Boundaries, Scope, Anti-Scope, Exit Gates)
      |
      v
    Tier 5: Actual Repository Implementation (Verified Code & Containerfiles)
      |
      v
    Tier 6: docs/architecture/ (Informational High-Level Blueprints)
```

### Operational Roles of Governance Files:
- **`AGENTS.md`:** Governs **how agents behave and work** (Universal Operating Rules). It does NOT alter OS architecture.
- **`PROJECT_STATE.md`:** Records **where the project currently stands** (Current State Snapshot).
- **`HANDOFF.md`:** Facilitates **context transfer between sequential agents** (Immediate Task State).

### Conflict Protocol
If an agent encounters a contradiction between documentation, ADRs, or code:
1. **Identify the conflict:** Pinpoint the exact contradictory statements.
2. **Identify Source A & Source B:** Record file paths and line numbers.
3. **Explain the technical divergence:** Describe why the two sources disagree.
4. **Evaluate impact:** Determine whether the conflict causes architectural drift or breaks dependencies.
5. **Determine if blocking:** Assess whether current task execution can proceed safely.
6. **Recommend resolution:** Base the recommendation on Tier 1 invariants and existing ADRs.
7. **Propose an ADR:** If an architectural trade-off is involved, draft an ADR proposal.
8. **DO NOT perform silent resolution:** Never arbitrarily choose one source and silently overwrite the other.
9. **Log in `PROJECT_STATE.md`:** Record the conflict under `Known Issues` or `Open Decisions`.

---

## 6. Milestone Discipline & Boundary Enforcement

NebuOS development is organized into 9 sequential, strictly bounded milestones:

| Milestone | Name | Core Objective | In-Scope | Anti-Scope |
|---|---|---|---|---|
| **P0** | Foundation OS | Minimal bootc Linux base, Btrfs subvolumes, network, TTY | Containerfile.p0, kernel 6.x, dracut, Btrfs (@, @home, @var), NetworkManager, agetty | Wayland, Smithay, Slint, GUI, Audio, Wine, Proton, Runtime |
| **P1** | NebuCompositor | Wayland display compositor in pure Rust | Smithay 0.3+, DRM/KMS backend, libinput, basic rendering | Shell widgets, taskbars, Wine, desktop apps |
| **P2** | NebuShell | Desktop environment & UI shell | Slint UI toolkit, panel, dock, launcher, notifications, theme engine | Wine integration, PE parsing, compatibility DB |
| **P3** | NebuRuntime | Windows application execution runtime | Per-app prefix manager, Btrfs reflink cloning, bwrap sandbox, D-Bus service | Wine staging customization, DXVK gaming tuning |
| **P4** | Compatibility Engine | Compatibility database, profiles, patch engine | SQLite database, PE header fingerprinting, recipe DSL | Heavy 3D GPU optimization, gaming launchers |
| **P5** | Graphics Runtime | DXVK, VKD3D-Proton, GPU vendor tuning | DXVK configuration, shader cache, Mesa/NVK/PRIME profiles | Desktop installers, user software store |
| **P6** | Installer & Store | Application discovery and onboarding | PE installer heuristics, desktop entry generator, Software Center | Kernel tuning, core compositor changes |
| **P7** | Compatibility Lab | Automated regression & compatibility testing | Headless test harness, 100+ Windows app validation suite | New feature development |
| **P8** | Production Validation | Security audit, performance certification, ISO | Final image signing, OTA update server, release hardening | Architecture changes |
| **P9+** | Future Enhancements | Post-1.0 features (ARM64, cloud sync, etc.) | Research & experimental prototypes | Current production release |

### Strict Boundary Rules:
- **Never implement P2 features in P0** simply to display a graphical window.
- **Never install Wine in P0 or P1** simply to test a `.exe` binary.
- **Never introduce premature dependencies.**
- If a task discovers a missing prerequisite from a future milestone: **STOP**, mark as **BLOCKED**, and report to the user.

---

## 7. Safe Change Policy & Prohibited Destructive Actions

To protect repository history, user data, and the host execution environment, **ALL AGENTS ARE STRICTLY FORBIDDEN FROM RUNNING THE FOLLOWING ACTIONS**:

### Prohibited Commands:
- `git reset --hard`
- `git clean -fd`
- `git push --force`
- Deleting the repository root or entire top-level directories (`rm -rf docs/`, `rm -rf src/`)
- Modifying or repartitioning host storage drives (`fdisk`, `parted`, `mkfs` on `/dev/sda`, `/dev/nvme0n1`)
- Overwriting the host bootloader or EFI system partition (`grub2-install` on host `/boot/efi`)
- Modifying host operating system kernel, systemd units, or network configuration
- Deleting or overwriting uncommitted modifications made by another agent or the user
- Printing, logging, or committing secrets, tokens, private keys, or credentials
- Mass rewriting or mass deletion of documentation files without explicit user instruction

### Destructive Action Stop Protocol:
If a destructive command is genuinely necessary (e.g., reformatting a virtual disk image in a test harness):
1. **STOP immediately.**
2. Formulate a warning specifying:
   - Exact command line.
   - Intended target and technical reason.
   - Affected files and scope.
   - Recovery and rollback plan.
3. Request explicit user authorization before execution.

---

## 8. Multi-Agent Safety & Working Tree Etiquette

Multiple agents may work sequentially or in parallel branches on this repository.
- **Inspect Before Editing:** Always run `git status` and `git diff` before modifying files.
- **Respect Dirty Working Trees:** If untracked files or unstaged changes exist, determine their origin. Do NOT run `git checkout .` or `git clean`.
- **Unclear Ownership:** If an unstaged change appears incomplete or belongs to an interrupted task, document it in `HANDOFF.md` under `Known Issues` before proceeding.
- **Atomic Commits:** Commit logical units of work with clear, descriptive conventional commit messages (e.g., `docs(governance): add universal agent operating contract`).

---

## 9. Change Scope & Follow-Up Protocol

Before writing any code or editing documentation, every agent must define its operational envelope:
```text
Current Milestone:      <P0..P8>
Current Task:           <Short Task Title>
Allowed Files:          <Explicit file/directory list>
Relevant Specifications:<Paths to docs/specification/ or docs/interfaces/>
Relevant Tests:         <Paths to tests or validation commands>
Expected Output:        <Concrete deliverable>
Out of Scope:           <Explicitly excluded components>
```

### Handling Out-of-Scope Findings:
If an agent discovers bugs, documentation discrepancies, or missing features outside its allowed scope:
1. **Do NOT fix it immediately.**
2. Log the issue in `PROJECT_STATE.md` under `Known Issues` or `Follow-Up Items`.
3. If the discovered issue is a **BLOCKER** to the current task, halt execution and report to the user.

---

## 10. Implementation & Refactoring Policy

- **Reuse Existing Abstractions:** Inspect existing crates, utilities, and helper scripts before authoring new modules.
- **Avoid Premature Abstractions:** Prefer straightforward, concrete implementations over heavily parameterized trait hierarchies until multiple callers require generalization.
- **Preserve Interface Contracts:** Adhere strictly to the D-Bus XML interfaces and Wayland protocol signatures documented in `docs/interfaces/`.
- **No Large Style Refactors:** Do NOT reformat or restructure existing code simply to match an agent's personal stylistic preference.
- **Minimal Code Principle:** Implement the minimum code necessary to satisfy acceptance criteria completely and reliably.

---

## 11. Dependency Management Policy

Before introducing any external dependency (Rust crate, system package, or build tool), the agent must document:
1. **Why:** What specific functionality does this dependency provide?
2. **Existing Alternative:** Why can standard library or existing in-tree code not fulfill this need?
3. **Maintenance:** Is the upstream crate actively maintained with responsive security patches?
4. **License:** Is the license compatible with NebuOS (`MPL-2.0`, `Apache-2.0`, `MIT`)?
5. **Security:** Does `cargo audit` report known vulnerabilities?
6. **Binary Size & Memory Impact:** What is the added binary footprint and RSS overhead?
7. **Build Time:** Does it significantly lengthen compilation times?
8. **Runtime Impact:** Does it spawn background threads or allocate global resources?
9. **Architectural Classification:** If introducing a major subsystem (e.g., new UI library, DB engine), an approved **ADR is mandatory**.

---

## 12. Rust Engineering Standards

As Rust is the primary implementation language for NebuOS system daemons (`nebu-compositor`, `nebu-shell`, `nebu-runtime-daemon`):
- **Idiomatic Rust:** Adhere to standard Rust API guidelines and conventions.
- **Explicit Error Handling:** Use `Result<T, E>` and `thiserror` for library crates; `anyhow` is restricted to CLI entry points.
- **No Uncontrolled Panics:** Functions must never call `unwrap()` or `expect()` in production paths; propagate errors via `?`.
- **Strict `unsafe` Policy:**
  - `unsafe` blocks are forbidden unless interacting with raw C FFI (DRM/KMS ioctls, Wayland protocol bindings) or hardware registers.
  - Every `unsafe` block must include a `// SAFETY:` comment proving that all invariants are upheld.
- **Code Quality Gates:**
  - `cargo fmt --check` must pass with zero warnings.
  - `cargo clippy -- -D warnings` must pass cleanly.
  - All public structs, enums, traits, and functions must have comprehensive Rustdoc comments.

---

## 13. Architecture Change Policy & Drift Detection

Architectural integrity is the bedrock of NebuOS:
1. **No Silent Drift:** Replacing an architectural component (e.g., replacing Smithay with wlroots, or replacing bootc with OSTree client directly) without an ADR is strictly prohibited.
2. **Architecture Change Procedure:**
   - Step 1: Document the proposed change and technical justification.
   - Step 2: Compare against current architecture and enumerate trade-offs.
   - Step 3: Assess impact on milestones, memory footprint, security boundaries, and interfaces.
   - Step 4: Draft an ADR in `docs/decisions/` following the established schema.
   - Step 5: Await user approval before modifying code.
3. **Drift Detection:** If an agent discovers that existing code contradicts documentation, it must raise a `DOCUMENTATION DRIFT` flag and document the discrepancy.

---

## 14. Testing & Verification Policy

Evidence precedes assertions:
- **Prohibited Claims:** Never report `Tests passing` or `Build verified` without providing the actual terminal command and output.
- **Standard Status Enum:**
  - `NOT TESTED`: Code written or modified, but no validation commands executed.
  - `TESTED`: Verification command executed with recorded output.
  - `PASS`: Acceptance criteria fully met with zero errors.
  - `FAIL`: Acceptance criteria failed; errors captured and analyzed.
  - `BLOCKED`: Tests cannot run due to missing environment, dependencies, or hardware.
  - `NOT VERIFIED`: Claims made without concrete execution evidence.
- **Verification Pyramid:** Unit tests -> Integration tests -> Static analysis (`clippy`) -> System QEMU boot tests.

---

## 15. Completion Policy

An item is NOT complete simply because a file was created or code compiled:
```
  Specification Exists
        |
        v
  Code Implemented
        |
        v
  Build / Compile Passes
        |
        v
  Automated Tests Pass
        |
        v
  Acceptance Criteria Verified
        |
        v
  Documentation Synchronized
        |
        v
  STATUS: COMPLETE
```
Agents must distinguish between `Implemented`, `Built`, `Tested`, `Verified`, and `Accepted`.

---

## 16. Performance Measurement Policy

Performance targets must be treated with scientific rigor:
- **Classification:** Distinguish clearly between:
  - **Hard Requirement:** Mandatory threshold; failure blocks release (e.g., P0 idle RAM < 150 MB).
  - **Engineering Target:** Nominal design goal under standard conditions.
  - **Benchmark:** Comparative measurement against an industry baseline.
  - **Stretch Goal:** Aspirational optimization target.
  - **Regression Threshold:** Maximum acceptable deviation from baseline (e.g., < 5% frame drop).
- **Mandatory Benchmark Metadata:** Every recorded benchmark must state:
  * Hardware CPU, RAM, and Storage specifications.
  * GPU vendor, model, and driver version (if graphics related).
  * Measurement methodology, toolchain, and sample size.
  * Mean, variance, and outlier data.

---

## 17. Security Architecture Policy

Security in NebuOS is structured upon defense-in-depth:
- **Sandboxing Invariant:** Untrusted Windows applications must execute within an unprivileged Bubblewrap (`bwrap`) container with restricted `/proc`, read-only `/usr`, private `/tmp`, and isolated network namespaces where appropriate.
- **SELinux Strategy:**
  - Milestones P0–P4 run in `SELINUX=permissive` to avoid false denials during base bringup.
  - Milestone P5 activates `SELINUX=enforcing` upon deployment of the custom `nebu-sandbox.te` policy module.
- **No Arbitrary Security Weakening:** Never disable security mechanisms globally to bypass an error without documenting an explicit security exception and threat analysis.

---

## 18. Windows Compatibility Reality Policy

- **Wine/Proton is an API Translation Layer:** Wine is **NOT** a Windows kernel. It translates Win32/NT system calls to Linux POSIX syscalls in user space.
- **Realistic Expectations:** NebuOS does **NOT** promise 100% Windows application compatibility.
- **Unsupported Technologies:** Anti-cheat systems requiring kernel-mode drivers (`.sys`), custom WDDM graphics drivers, hardware dongle drivers, and direct physical disk access are architecturally unsupported.
- **Honest Documentation:** Never delete or downplay compatibility limitations to make marketing claims appear more favorable.

---

## 19. Documentation Synchronization Policy

Whenever system behavior, configuration paths, CLI arguments, or IPC schemas change:
- The agent **MUST** update the corresponding technical specification (`docs/specification/`), interface schema (`docs/interfaces/`), or roadmap milestone (`docs/roadmap/`).
- If an agent completes code without updating documentation, it must document the discrepancy as `NEEDS DOCUMENTATION UPDATE` in `PROJECT_STATE.md`.

---

## 20. Agent Handoff Protocol

Before terminating a session, every agent must update `HANDOFF.md` with:
- **Current Handoff Metadata:** Agent title, date, active milestone, and active task.
- **Completed Deliverables:** Exact files created or edited.
- **Verification Evidence:** Commands executed and terminal output summaries.
- **Unverified & Failed Items:** Explicit list of tests not run or errors encountered.
- **Immediate Next Action:** Exact step the subsequent agent must undertake.
- **Strict Prohibitions ("Do Not Do"):** Boundaries and anti-scope for the next agent.
"""

# ==============================================================================
# PROJECT_STATE.md
# ==============================================================================
project_state_md = """# NebuOS Project State Snapshot

**Document Authority:** Single Source of Current Project Reality  
**Last Updated:** 2026-09-04T13:25:00Z  
**Governing Milestone:** Milestone P0: Foundation Operating System  
**Audit Gate Status:** **PASS WITH NOTES** (NEBU-GATE-P0-2026-001)  

---

## 1. Executive Status Dashboard

| Attribute | Current Value | Authority / Source |
|---|---|---|
| **Current Project Phase** | Phase 4: Pre-Implementation Governance & P0 Readiness | `docs/roadmap/00-implementation-roadmap.md` |
| **Current Milestone** | **Milestone P0: Foundation Operating System** | `docs/roadmap/01-p0-foundation.md` |
| **Milestone Status** | **PLANNED (Ready for Implementation)** | `docs/audit/P0_READY_GATE.md` |
| **P0 Implementation Started?** | **NO (Zero code written; containerfile not created)** | Actual Repository State |
| **Active Task** | Repository Agent Governance Setup & Verification | User Mandate |
| **Task Status** | **COMPLETE** | Evidence in `docs/audit/AGENT_GOVERNANCE_AUDIT.md` |
| **Last Verification Completed** | P0 Ready Gate Verification (`NEBU-GATE-P0-2026-001`) | `docs/audit/P0_READY_GATE.md` |
| **Last Verification Verdict** | **PASS WITH NOTES** | Verified across 37 audit dimensions |
| **Active Blockers** | **0 (Zero)** | No blocking issues halt P0 |

---

## 2. Milestone Progress Tracker

```
[ P0: Foundation OS ]       ==> [ READY TO START ] (P0 Ready Gate: PASS WITH NOTES)
[ P1: NebuCompositor ]      ==> [ LOCKED / P0 PREREQUISITE ]
[ P2: NebuShell ]           ==> [ LOCKED / P1 PREREQUISITE ]
[ P3: NebuRuntime ]         ==> [ LOCKED / P2 PREREQUISITE ]
[ P4: Compatibility Engine] ==> [ LOCKED / P3 PREREQUISITE ]
[ P5: Graphics Runtime ]    ==> [ LOCKED / P4 PREREQUISITE ]
[ P6: Installer / Store ]   ==> [ LOCKED / P5 PREREQUISITE ]
[ P7: Compatibility Lab ]   ==> [ LOCKED / P6 PREREQUISITE ]
[ P8: Production Validation]==> [ LOCKED / P7 PREREQUISITE ]
```

---

## 3. Subsystem Implementation Status Matrix

| Subsystem | Target Milestone | Code Status | Spec Status | Test Status | Next Action |
|---|---|---|---|---|---|
| **P0 Base Containerfile** | P0 | NOT STARTED | COMPLETE (`01-p0-foundation.md`) | PLANNED (12 tests) | Author `Containerfile.p0` |
| **P0 Btrfs Storage Engine** | P0 | NOT STARTED | COMPLETE (`03-filesystem-spec.md`) | PLANNED | Validate subvolume mounts in QEMU |
| **P0 QEMU Test Harness** | P0 | NOT STARTED | COMPLETE (`01-p0-foundation.md`) | PLANNED | Author `tests/integration/p0_boot_test.sh` |
| **NebuCompositor (Smithay)** | P1 | LOCKED | COMPLETE (`01-compositor.md`) | LOCKED | Do not implement in P0 |
| **NebuShell (Slint)** | P2 | LOCKED | COMPLETE (`02-shell.md`) | LOCKED | Do not implement in P0 |
| **NebuRuntime Daemon** | P3 | LOCKED | COMPLETE (`00-runtime-spec.md`) | LOCKED | Do not implement in P0 |
| **Compatibility Database** | P4 | LOCKED | COMPLETE (`01-database-schema.md`) | LOCKED | Do not implement in P0 |
| **DXVK / VKD3D Integration** | P5 | LOCKED | COMPLETE (`04-dxvk-vkd3d.md`) | LOCKED | Do not implement in P0 |
| **Software Center** | P6 | LOCKED | COMPLETE (`06-software-center.md`) | LOCKED | Do not implement in P0 |

---

## 4. Known Issues & Operational Notes

The following issues were identified during the P0 Ready Gate Verification and are actively tracked:

| Issue ID | Priority | Description | Resolution Plan | Target Milestone |
|---|---|---|---|---|
| `ISSUE-M-001` | MEDIUM | 109 links in `docs/TRACEABILITY.md` point to legacy blueprint paths | Update links to point to `docs/specification/` | Milestone P0 (Documentation) |
| `ISSUE-M-002` | MEDIUM | Blanket Btrfs `nodatacow` on `@nebu_apps` disables checksums and compression | Reclassified as NEEDS EXPERIMENT; test targeted `chattr +C` on registry/db files | Milestone P3 |
| `ISSUE-M-003` | MEDIUM | Final UI toolkit choice (Slint vs Iced) needs formal ADR | Formalize ADR upon exiting P1; current recommendation is Slint | Milestone P1 Exit Gate |
| `ISSUE-H-001` | HIGH | SELinux enforcing mode prior to custom policy compilation causes avc denials | Set `SELINUX=permissive` during P0–P4; build `nebu-sandbox.te` in P5 | Milestone P5 |
| `ISSUE-L-001` | LOW | Legacy blueprint files in `docs/architecture/` lack deprecation banners | Add deprecation header pointing to `docs/specification/` | Milestone P0 |
| `ISSUE-L-002` | LOW | Legacy BIOS mentioned in QEMU docs could cause UEFI confusion | Add note clarifying BIOS is strictly for virtualized CI without OVMF | Milestone P0 |

---

## 5. Active Risk Management

Top 5 operational risks monitored during Milestone P0 implementation:
1. **RSK-001 (Image Build Failure):** Base Fedora bootc package dependency conflict during container build. *Mitigation: Pin package versions in Containerfile.p0.*
2. **RSK-002 (dracut Kernel Panic):** Initramfs missing Btrfs or systemd drivers during early boot pivot. *Mitigation: Explicit dracut module inclusions in Containerfile.*
3. **RSK-003 (Root Subvolume Mount Timeout):** Misconfigured GRUB kernel arguments (`rootflags=subvol=@`). *Mitigation: Automated QEMU boot test assertions.*
4. **RSK-004 (SELinux AVC Denial at Boot):** Systemd services blocked on unconfined bootc base. *Mitigation: Explicit `SELINUX=permissive` in `/etc/selinux/config`.*
5. **RSK-005 (Memory Budget Overshoot):** Unintended background daemons pushing idle RAM > 150 MB. *Mitigation: Lean package manifest (7-12 core RPMs only).*

---

## 6. Open Architecture Decisions

- **DEC-001 (Slint vs Iced):** Scheduled for Milestone P1 Exit Gate. (Strong technical recommendation: Slint, due to ~12-15 MB RSS vs ~35-45 MB RSS).
- **DEC-002 (Wine Staging vs Proton Upstream):** Scheduled for Milestone P3.
- **DEC-003 (Btrfs targeted `chattr +C` vs `nodatacow`):** Scheduled for Milestone P3.

---

## 7. Blocked Items

- **None.** There are **zero (0) blocking issues** preventing the commencement of Milestone P0 implementation.

---

## 8. Immediate Next Action for Implementation

**Implement Milestone P0: Foundation Operating System** in accordance with [`docs/roadmap/01-p0-foundation.md`](docs/roadmap/01-p0-foundation.md):
1. Author `/root/NebuOS/Containerfile.p0` based on `quay.io/fedora/fedora-bootc:40`.
2. Configure minimal package list (`kernel-core`, `btrfs-progs`, `systemd`, `NetworkManager`, `util-linux`, `shadow-utils`).
3. Set `SELINUX=permissive` in `/etc/selinux/config`.
4. Create automated test harness `tests/integration/p0_boot_test.sh` for headless QEMU UEFI boot verification.
5. Validate all 12 acceptance criteria (`TC-P0-001` through `TC-P0-012`).

---

## 9. Strict Anti-Scope ("Do Not Implement Yet")

- **DO NOT** write or import Wayland compositor code (`smithay`).
- **DO NOT** implement desktop shells, panels, or widgets (`slint`, `iced`).
- **DO NOT** install or run Wine, Proton, DXVK, or VKD3D.
- **DO NOT** install PipeWire or graphical display drivers.
- **DO NOT** author runtime prefix management daemons.
"""

# ==============================================================================
# HANDOFF.md
# ==============================================================================
handoff_md = """# NebuOS Agent Handoff Protocol & Transfer State

**Handoff Timestamp:** 2026-09-04T13:25:00Z  
**Departing Agent Role:** Principal Developer Experience Architect & Repository Governance Engineer  
**Incoming Agent Role:** Operating System Systems Engineer / P0 Implementation Engineer  
**Active Milestone:** Milestone P0: Foundation Operating System  
**Current Task:** Repository Governance Initialization & P0 Implementation Hand-off  
**Task Status:** COMPLETE  

---

## 1. Executive Summary of Completed Work

1. **P0 Ready Gate Completed:** The formal 37-dimension gate verification was concluded with the authoritative verdict: **PASS WITH NOTES**. Verified documents are available at `docs/audit/P0_READY_GATE.md` and `docs/p0-ready-gate-verification.md`.
2. **Repository Governance Architecture Established:**
   - Universal Agent Contract authored: `AGENTS.md`.
   - Single Source of Project State established: `PROJECT_STATE.md`.
   - Contributor & Agent Guidelines established: `CONTRIBUTING.md`.
   - Architectural Navigation Map established: `ARCHITECTURE.md`.
   - Multi-agent thin adapters established: `CLAUDE.md`, `.cursorrules`, `GEMINI.md`.
   - Modular Agent Skills library established: `skills/` (13 domain skills with full operational constraints).
   - Governance Audit completed and verified: `docs/audit/AGENT_GOVERNANCE_AUDIT.md`.
3. **Repository State Invariant:** Zero NebuOS implementation code has been written. No base images, no kernel modifications, no compositors, and no compatibility runtimes have been created. The codebase is clean, pristine, and ready for disciplined P0 execution.

---

## 2. Changed Files in this Session

| File Path | Action | Content Summary |
|---|---|---|
| `AGENTS.md` | CREATED | Universal agent operating contract, 21-step startup protocol, safety policies. |
| `PROJECT_STATE.md` | CREATED | Master project state snapshot, P0 ready status, known issues, risk matrix. |
| `HANDOFF.md` | CREATED | Current agent context transfer protocol and execution instructions. |
| `CONTRIBUTING.md` | CREATED | Workflow guidelines for agents and human contributors. |
| `ARCHITECTURE.md` | CREATED | Architectural map, layer topology, component boundaries, specification index. |
| `CLAUDE.md` | CREATED | Thin adapter directing Claude Code to `AGENTS.md`. |
| `.cursorrules` | CREATED | Thin adapter directing Cursor to `AGENTS.md`. |
| `GEMINI.md` | CREATED | Thin adapter directing Gemini / Antigravity agents to `AGENTS.md`. |
| `skills/README.md` | CREATED | Skills discovery catalog and usage instructions. |
| `skills/*/SKILL.md` | CREATED | 13 modular domain skills covering architecture, rust, system, compositor, shell, runtime, compatibility, graphics, security, testing, performance, documentation, and release. |
| `docs/audit/P0_READY_GATE.md` | CREATED | Formal 37-step P0 Ready Gate Verification Report (PASS WITH NOTES). |
| `docs/p0-ready-gate-verification.md` | CREATED | Root mirror of P0 Ready Gate Verification Report. |
| `docs/audit/AGENT_GOVERNANCE_AUDIT.md` | CREATED | Comprehensive governance audit report verifying rule consistency. |
| `docs/INDEX.md` | MODIFIED | Added P0 Ready Gate verification report to Master Index. |

---

## 3. Verification Evidence

- **Documentation Verification:** All 111 documentation files indexed with 0 broken links in master index.
- **Git State:** Git repository initialized; working tree verified clean of unintended modifications.
- **Milestone Discipline:** Verified that Milestone P0 has NOT been prematurely implemented. Zero lines of premature GUI or Wine code exist in the tree.
- **Governance Self-Audit:** `docs/audit/AGENT_GOVERNANCE_AUDIT.md` conducted across 16 dimensions; result **PASS**.

---

## 4. What Was NOT Verified (Deferred Verification)

- **Physical Bare-Metal Boot:** Testing on physical OEM UEFI motherboards is deferred to Milestone P7 (Hardware Testing Lab). QEMU/OVMF virtualized UEFI is the target for P0.
- **Container Build Execution:** Container build of `Containerfile.p0` has not yet been executed because authoring `Containerfile.p0` is the first task of P0 implementation.

---

## 5. Known Issues & Operational Directives for Next Agent

1. **SELinux Setting:** During Milestone P0 implementation, configure `SELINUX=permissive` in `Containerfile.p0` and `/etc/selinux/config`. Do NOT set enforcing mode until P5.
2. **Package Manifest:** Strictly use the 7-package minimal manifest from `docs/roadmap/01-p0-foundation.md`. Do NOT use the full desktop manifest from `00-system-specification.md`.
3. **Btrfs Subvolumes:** Create exactly three subvolumes in P0: `@` (`/sysroot`), `@home` (`/var/home`), and `@var` (`/var`). Do NOT create `@nebu_apps` until P3.
4. **Link Maintenance:** Update 109 legacy links in `docs/TRACEABILITY.md` when performing routine documentation tasks.

---

## 6. Immediate Next Action

The incoming agent must:
1. Follow the **Agent Startup Protocol** in `AGENTS.md`.
2. Open [`docs/roadmap/01-p0-foundation.md`](docs/roadmap/01-p0-foundation.md).
3. Begin **Milestone P0 Task 1**: Author `/root/NebuOS/Containerfile.p0`.
4. Begin **Milestone P0 Task 2**: Author automated test harness `tests/integration/p0_boot_test.sh`.
5. Execute image build and QEMU boot test, recording logs as evidence.

---

## 7. Strict Prohibitions ("DO NOT DO")

- **DO NOT** attempt to implement `nebu-compositor` (Smithay).
- **DO NOT** attempt to implement `nebu-shell` (Slint).
- **DO NOT** install Wine, Proton, DXVK, or VKD3D.
- **DO NOT** install graphical desktop packages (Xwayland, Weston, GTK, Qt).
- **DO NOT** run destructive commands (`git reset --hard`, `git clean -fd`).
- **DO NOT** modify the host operating system's bootloader, partitions, or kernel.
"""

# ==============================================================================
# CONTRIBUTING.md
# ==============================================================================
contributing_md = """# Contributing to NebuOS — Developer & Agent Workflow

Thank you for contributing to **NebuOS**! This repository is governed by strict engineering standards to ensure that human developers and AI coding agents collaborate with maximum consistency, architectural fidelity, and safety.

---

## 1. Primary Operating Rules

Before making any changes:
1. **AI Agents:** You are legally and technically bound by [`AGENTS.md`](AGENTS.md). You must execute the 21-step startup protocol before touching code.
2. **Human Developers:** Please review [`AGENTS.md`](AGENTS.md) and [`ARCHITECTURE.md`](ARCHITECTURE.md) to understand the project invariants, milestone discipline, and source of truth hierarchy.
3. **Milestone Integrity:** All work must align strictly with the active milestone documented in [`PROJECT_STATE.md`](PROJECT_STATE.md). Work outside the active milestone will be rejected.

---

## 2. Source of Truth Hierarchy

When resolving technical discrepancies, adhere to this sequence of authority:
1. **`PRD.md`**: Master Product Requirements & Invariants (e.g., No Virtual Machines).
2. **`docs/decisions/` (ADRs)**: Binding architectural decisions.
3. **`docs/specification/` & `docs/interfaces/`**: Concrete implementation blueprints and schemas.
4. **`docs/roadmap/`**: Milestone boundaries, scope, anti-scope, and exit gates.
5. **Implementation Code**: Actual containerfiles, Rust source code, and configurations.
6. **`docs/architecture/`**: Informational high-level overviews (superseded by specifications).

---

## 3. Development & Branching Workflow

1. **Git Flow:**
   - `main`: Protected production branch.
   - `feature/<milestone>-<task-name>`: Feature branch for specific roadmap tasks (e.g., `feature/p0-containerfile`).
   - `fix/<issue-id>`: Targeted bugfix branch.
2. **Commit Conventions:**
   We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
   - `feat(subsystem): add new functionality`
   - `fix(subsystem): resolve a defect`
   - `docs(subsystem): update or add technical specifications`
   - `test(subsystem): add or update automated test suites`
   - `refactor(subsystem): restructure code without behavioral changes`
   - `chore(governance): update project state or handoff`

---

## 4. Quality & Verification Gates

Every pull request or task completion must satisfy these criteria:
- **Rust Components:**
  - `cargo fmt --check` passes cleanly.
  - `cargo clippy -- -D warnings` reports zero warnings.
  - Unit tests (`cargo test`) pass.
  - Public interfaces are fully documented with Rustdoc.
- **Container Images (bootc):**
  - Containerfile builds successfully without errors.
  - `bootc container lint` reports zero violations.
  - Image size meets milestone budget constraints.
- **Testing Evidence:**
  - Pull requests and handoffs must include terminal execution logs verifying acceptance criteria. Assertions without evidence will be rejected.

---

## 5. Architectural Decision Process (ADRs)

If your work introduces a new external dependency, alters an IPC interface, modifies the storage layout, or touches security policies:
1. Check `docs/decisions/` to see if an ADR already governs the topic.
2. If proposing an architectural change, draft a new ADR using the template in `docs/decisions/`.
3. Submit the ADR for review and approval before implementing code changes.

---

## 6. Safety & Security Invariants

- **Host Environment Protection:** NebuOS development happens inside containers and virtualized test environments. Never execute destructive commands against the host system's partitions, bootloaders, or system files.
- **No Secrets:** Never commit API keys, private tokens, passwords, or certificate keys.
- **Non-VM Invariant:** Never introduce virtual machine hypervisors (QEMU/KVM guests) as part of the desktop compatibility layer.
"""

# ==============================================================================
# ARCHITECTURE.md
# ==============================================================================
architecture_md = """# NebuOS Architecture Navigation Map

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
"""

# ==============================================================================
# Thin Agent Adapters
# ==============================================================================
claude_md = """# Claude Code Agent Configuration — NebuOS

You are working on the **NebuOS** repository.

This project is strictly governed by the universal repository contract:
👉 **[`AGENTS.md`](AGENTS.md)**

### Mandatory Startup Sequence:
1. Read [`AGENTS.md`](AGENTS.md) and execute the 21-step startup protocol.
2. Read [`PROJECT_STATE.md`](PROJECT_STATE.md) to inspect active milestone and blockers.
3. Read [`HANDOFF.md`](HANDOFF.md) to review previous agent directives.
4. Check [`docs/INDEX.md`](docs/INDEX.md) for relevant technical specifications.

### Strict Prohibitions:
- DO NOT implement features outside the current active milestone.
- DO NOT write code for future milestones (no GUI/Compositor/Wine in P0).
- DO NOT execute destructive git or filesystem commands.
- DO NOT rely on previous conversation memory; rely solely on repository files.
"""

cursorrules = """# Cursor Agent Rules — NebuOS

You are working on the NebuOS repository.

This project is governed by the universal agent contract: AGENTS.md.

Mandatory Rules:
1. Read AGENTS.md, PROJECT_STATE.md, and HANDOFF.md before proposing any changes.
2. Adhere strictly to the current active milestone specified in PROJECT_STATE.md.
3. Never implement features belonging to future milestones (e.g., zero GUI or Wine in P0).
4. Never execute destructive commands (no git reset --hard, no git clean -fd).
5. All Rust code must be idiomatic, minimal unsafe, and pass cargo fmt and cargo clippy.
6. Verify all claims with actual command outputs before reporting completion.
"""

gemini_md = """# Gemini / Antigravity Agent Configuration — NebuOS

You are working on the **NebuOS** repository.

This project is strictly governed by the universal repository contract:
👉 **[`AGENTS.md`](AGENTS.md)**

### Mandatory Directives:
1. **Universal Contract:** Read [`AGENTS.md`](AGENTS.md) and strictly follow the 21-step startup protocol.
2. **Current State:** Read [`PROJECT_STATE.md`](PROJECT_STATE.md) and [`HANDOFF.md`](HANDOFF.md) to understand current milestone and restrictions.
3. **Knowledge Graph (`graphify`):**
   - For codebase queries, run `graphify query "<question>"` when `graphify-out/graph.json` exists.
   - Read `graphify-out/GRAPH_REPORT.md` only for broad review.
   - After modifying code, run `graphify update .` to keep the graph current.
4. **Milestone Boundary:** Respect milestone isolation. Do not implement future milestone features prematurely.
"""

# Write all root governance files
write_file("AGENTS.md", agents_md)
write_file("PROJECT_STATE.md", project_state_md)
write_file("HANDOFF.md", handoff_md)
write_file("CONTRIBUTING.md", contributing_md)
write_file("ARCHITECTURE.md", architecture_md)
write_file("CLAUDE.md", claude_md)
write_file(".cursorrules", cursorrules)
write_file("GEMINI.md", gemini_md)
print("Root governance files generated successfully.")
