# Universal Agent Operating Contract & Repository Governance — NebuOS

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
NebuOS is a lightweight, immutable, container-native Linux desktop operating system built on **Fedora Linux 44** using **Fedora Atomic / bootc** (`quay.io/fedora/fedora-bootc:44`) as the upstream foundation, with **Rust** as the primary system implementation language. It provides a native-feeling desktop experience capable of running native Linux and Windows user-space applications without requiring a Windows virtual machine.

### Baseline Platform Invariants
- **Upstream Foundation:** Fedora Linux 44 (`quay.io/fedora/fedora-bootc:44`).
- **Deployment Engine:** `bootc` 1.1+ with OSTree container storage backend.
- **Root Filesystem Immutability:** `/usr` is mounted strictly read-only (`ro,nodev`).
- **Storage Model:** Btrfs subvolumes (`@` root sysroot, `@home` user data, `@var` shared persistent state).
- **Service Supervision:** systemd v256+ with unified cgroups v2 hierarchy.
- **Production Image Identity:** Release builds must use immutable SHA-256 digest pinning (`quay.io/fedora/fedora-bootc:44@sha256:...`). Using `fedora:latest` or unversioned tags as production identity is strictly prohibited.

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
                      |    Fedora 44 Atomic / bootc Image Base   |
                      |        (Immutable /usr, Btrfs Pool)      |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |         Linux Kernel 6.14+ (Fedora 44)   |
                      +------------------------------------------+
```

*Important Architecture Note:* The diagram above represents the **target steady-state conceptual layering**. It does **NOT** imply that all layers exist in early milestones. Each roadmap milestone enforces a strict, isolated subsystem boundary.

---

## 3. Foundational Governance Principles

Every agent must internalize and obey these 16 principles:
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
15. **Prefer the Smallest Correct Change:** Always select the smallest, least intrusive change that fulfills requirements completely. Reuse existing code, utilities, and architectural patterns. Avoid duplicate code, unnecessary dependencies, speculative abstractions, premature optimizations, and unrelated refactoring.
16. **Milestone Isolation:** An agent assigned to Milestone P0 must NEVER write code for or pull in dependencies from P1, P2, P3, P4, P5, P6, or P7.

---

## 4. Agent Startup Protocol & Execution Lifecycle

### 4.1 Mandatory Behavior Sequence
Every task execution must strictly follow this sequential lifecycle:
```
  READ FIRST (AGENTS.md, PROJECT_STATE.md, Specs, ADRs)
        │
        ▼
      AUDIT (Inspect actual working tree, diff, blockers)
        │
        ▼
      PLAN (Enumerate allowed files, tests, constraints)
        │
        ▼
  IMPLEMENT ONLY REQUESTED SCOPE (Minimal correct change)
        │
        ▼
     VERIFY (Empirical execution: linters, tests, builds)
        │
        ▼
    DOCUMENT (Update specs, PROJECT_STATE.md, HANDOFF.md)
        │
        ▼
  FINAL REPORT (Factual summary with command outputs)
```

### 4.2 Strict Behavioral Prohibitions
An agent entering this repository must **NEVER**:
- Start writing code before thoroughly reading and auditing relevant architectural specifications.
- Treat `TODO` comments or draft stubs as implicit permission to implement out-of-scope features.
- Expand milestone scope beyond the current prompt's explicit boundary.
- Add external frameworks, crates, or libraries simply because they are convenient or familiar.
- Create speculative abstractions or redundant wrapper types without multiple active call-sites.
- Unilaterally replace architectural dependencies without an approved ADR.
- Delete, overwrite, or deprecate existing architecture documentation without concrete evidence.

### 4.3 Mandatory 21-Step Startup Protocol
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
| **P0** | Foundation OS | Minimal bootc Linux base, Btrfs subvolumes, network, TTY | Containerfile.p0 (`quay.io/fedora/fedora-bootc:44`), Linux kernel 6.14+, dracut v102+ initramfs, UEFI, Btrfs (@, @home, @var), systemd v256+, networking foundation (NetworkManager), TTY/login (agetty), SELinux permissive baseline, QEMU verification | Wayland, Smithay, NebuCompositor, NebuShell, Slint/Iced, GUI, Audio (PipeWire), Wine, Proton, DXVK, VKD3D, installers, Software Center, Compatibility Lab |
| **P1** | NebuCompositor | Wayland display compositor in pure Rust | Smithay 0.3+, DRM/KMS backend, libinput, basic rendering | Shell widgets, taskbars, Wine, desktop apps |
| **P2** | NebuShell | Desktop environment & UI shell | Slint UI toolkit, panel, dock, launcher, notifications, theme engine | Wine integration, PE parsing, compatibility DB |
| **P3** | NebuRuntime | Windows application execution runtime | Per-app prefix manager, Btrfs reflink cloning, bwrap sandbox, D-Bus service | Wine staging customization, DXVK gaming tuning |
| **P4** | Compatibility Engine | Compatibility database, profiles, patch engine | SQLite database, PE header fingerprinting, recipe DSL | Heavy 3D GPU optimization, gaming launchers |
| **P5** | Graphics Runtime | DXVK, VKD3D-Proton, GPU vendor tuning | DXVK configuration, shader cache, Mesa/NVK/PRIME profiles | Desktop installers, user software store |
| **P6** | Application Platform & Marketplace | Application discovery, management, sandboxing, and developer platform | Subphases P6.0–P6.4: Nebu App Manager daemon, Flatpak/Flathub integration, Fedora repos, Windows recipe installer, Slint Marketplace UI, permission inspection, developer platform | Custom package managers, forking Flathub, direct package manager access from UI, Electron/Chromium, payment backends |
| **P7** | Compatibility Lab | Automated regression & compatibility testing | Headless test harness, 100+ Windows app validation suite | New feature development |
| **P8** | Production Validation | Security audit, performance certification, ISO | Final image signing, OTA update server, release hardening | Architecture changes |
| **P9+** | Future Enhancements | Post-1.0 features (ARM64, cloud sync, etc.) | Research & experimental prototypes | Current production release |

### Strict Boundary Rules:
- **Milestone Isolation:** An agent assigned to Milestone P0 must NEVER write code for or pull in dependencies from P1 through P7.
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

### Core Security & Safety Invariants:
- **No Hardcoded Secrets:** Never hardcode, commit, or log credentials, tokens, private keys, or API tokens.
- **No Unsafe Shell Execution:** Never pass unescaped variables or user input into shell commands; avoid raw subshells where direct APIs exist.
- **No Arbitrary Filesystem Access:** Validate all target paths; ensure file writes remain strictly inside the repository or designated container scratch mount.
- **Least Privilege:** Run all scripts, containers, and test harnesses with the minimum necessary Linux capabilities.
- **SELinux Awareness:** Respect SELinux policies; do not disable security controls globally to bypass errors.
- **Secure Defaults:** All configuration files, systemd units, and scripts must ship with hardened, secure defaults.

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
- **VERIFY_REQUIRED Policy:** Any item or assumption tagged as `VERIFY_REQUIRED` must be empirically proven via test execution, not assumed, estimated, or declared complete through static inspection.
- **Runtime Testing Rule:** A `PASS` status cannot be granted based on static code inspection alone if the acceptance criteria require runtime testing (e.g., boot execution, service startup, network handshake).
- **Standard Status Enum:**
  - `NOT TESTED`: Code written or modified, but no validation commands executed.
  - `TESTED`: Verification command executed with recorded output.
  - `PASS`: Acceptance criteria fully met with zero errors.
  - `FAIL`: Acceptance criteria failed; errors captured and analyzed.
  - `BLOCKED`: Tests cannot run due to missing environment, dependencies, or hardware.
  - `VERIFY_REQUIRED`: Empirical verification required before release gate sign-off.
  - `NOT VERIFIED`: Claims made without concrete execution evidence.
- **Verification Pyramid:** Unit tests -> Integration tests -> Static analysis (`clippy`) -> System QEMU boot tests.

---

## 15. Completion Policy & P0 Verification Expectations

An item is NOT complete simply because a file was created or code compiled:
```
  Specification Exists
        │
        ▼
  Code Implemented
        │
        ▼
  Build / Compile Passes
        │
        ▼
  Automated Tests Pass
        │
        ▼
  Acceptance Criteria Verified
        │
        ▼
  Documentation Synchronized
        │
        ▼
  STATUS: COMPLETE
```
Agents must distinguish between `Implemented`, `Built`, `Tested`, `Verified`, and `Accepted`.

### Milestone P0 Verification Expectations
When Milestone P0 implementation is undertaken, the agent must empirically verify and provide execution output logs for:
1. **Base Image Build:** Image builds cleanly from `quay.io/fedora/fedora-bootc:44`.
2. **bootc Lint:** `bootc container lint` exits with code 0.
3. **Initramfs & Storage:** dracut initramfs embeds core drivers (`nvme`, `ahci`, `virtio_blk`, `virtio_scsi`, `btrfs`).
4. **Btrfs Layout:** Subvolumes `@` (`/sysroot`), `@home` (`/var/home`), and `@var` (`/var`) mount correctly.
5. **Sysroot Immutability:** `/usr` is mounted strictly read-only (`ro,nodev`).
6. **Init & Services:** systemd reaches `multi-user.target` with `systemctl --failed` reporting 0 units.
7. **Console Access:** Serial console (`ttyS0`) and virtual console (`tty1`) provide working `agetty` login prompts.
8. **Networking:** NetworkManager acquires DHCP lease.
9. **SELinux Baseline:** Permissive mode boots with zero critical AVC denials.
10. **UEFI QEMU Boot:** Headless QEMU script completes boot cycle in <= 3.5 seconds.
11. **Anti-Scope Scan:** Dependency scan proves zero Wayland, Smithay, Slint, Wine, Proton, audio, or GUI packages.
12. **Empirical Values Only:** Values like initramfs byte size or image digests must originate from actual build/test commands, never invented.

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

---

## 21. Reproducibility & Image Build Governance Policy

To guarantee deterministic, verifiable system software delivery:
- **Upstream Baseline:** Milestone P0 and subsequent base builds must derive from `quay.io/fedora/fedora-bootc:44`.
- **Immutable Digest Pinning:** Production and release builds must pin the exact image SHA-256 digest (`quay.io/fedora/fedora-bootc:44@sha256:<digest>`).
- **Prohibited Tags:** The `:latest` tag is unversioned and non-deterministic; using `fedora:latest` or `fedora-bootc:latest` as production identity is strictly prohibited.
- **Deterministic Build Environment:** Container builds must set `SOURCE_DATE_EPOCH` to commit timestamp and avoid non-deterministic file timestamps or ordering.
- **Scientific Honesty:** Do not claim 100% bit-for-bit reproducibility until cryptographically proven through independent multi-node builds.

---

## 22. Application Platform & Nebu Marketplace Governance Policy

To govern the application distribution, packaging, and management architecture:
- **Milestone Allocation:** Application Platform and Nebu Marketplace belong strictly to **Milestone P6** (with subphases P6.0 through P6.4) and Phase P8 for production readiness.
- **Milestone Isolation Lockout:** Agents working on Milestones P0, P1, P2, P3, P4, or P5 are **STRICTLY PROHIBITED** from implementing Marketplace UI, backend services, Flatpak integrations, App Manager daemons, or publisher portals unless the user task explicitly requests architecture documentation.
- **No Custom Package Managers:** NebuOS will **NOT** create a package manager or bespoke package archive format from scratch.
- **Ecosystem Leverage:** Flatpak is the primary desktop application packaging and sandboxing foundation. Flathub is an upstream discovery/source ecosystem.
- **No Upstream Forks:** NebuOS will **NOT** fork Flatpak or Flathub, and will **NOT** host complete Flathub mirrors during early phases.
- **No Custom Package Format Without ADR:** Any deviation from standard Flatpak, OCI, and RPM formats requires an approved ADR.
- **Nebu App Manager Abstraction Invariant:** The Marketplace UI and NebuShell launcher must **NEVER** execute package managers (`flatpak`, `dnf`, `rpm`) or runtime daemons (`wine`, `wineserver`) directly. All interactions must route through the `Nebu App Manager` abstraction daemon (`org.nebu.AppManager1`).
- **Separation of Windows Applications:** Windows applications are managed through the Nebu Compatibility Engine in isolated Btrfs prefixes; they are **NEVER** packaged as Flatpaks.
- **Mandatory Security Verification:** Cryptographic signatures and SHA-256 checksums must be validated before staging any package or recipe. Permissions must be disclosed to the user prior to installation.
- **Update Lifecycle Independence:** Application updates must operate live in userspace via Flatpak / App Manager and must **NEVER** trigger, depend on, or conflate with base OS updates (`bootc`), compatibility DB updates, or firmware updates (`fwupd`).
- **No Webview / Heavy Frameworks:** The Marketplace UI must be implemented in native Rust (Slint). Electron, Chromium, and heavy webviews are strictly banned.
- **No Premature Monetization:** Payment processing and commercial monetization backends are strictly out of scope for initial P6.

---

## 23. UI/UX, Design System & Iconography Governance Policy

To guarantee an uncompromising, cohesive visual language, prevent architectural bloat, and protect milestone boundaries:
- **Phase Ownership Allocation:**
  - **Milestone P0:** Strictly headless foundation. Zero graphical UI, Wayland, Slint, icons, docks, or settings code.
  - **Milestone P1 (NebuCompositor):** Smithay-based Wayland compositor, KMS presentation, surface stacking, input routing, and layer-shell protocol server. Provides Server-Side Decoration (SSD) surfaces, but **NEVER** draws application launchers, system tray menus, or widget UI design.
  - **Milestone P2 (NebuShell):** The sole primary home of the desktop UI, design system, token engine (`nebu-design-tokens`), abstract iconography engine (`nebu-icon`), theme & layout engines, launcher, dock, taskbar, notifications, settings, and SSD button sync.
  - **Milestones P3–P5:** Non-visual runtime, compatibility, and graphics subsystems. Zero visual UI.
  - **Milestone P6:** Application Platform & Marketplace UI (`crates/nebu-marketplace-ui/`) consuming tokens and components from P2.
  - **Milestones P7–P8:** Visual regression testing, accessibility audits, and final dedicated Nebu Icon Set commissioning.
- **Strict Prohibition of Webviews / Electron:** Electron, Chromium, CEF, Node.js, and heavy webviews are **CATEGORICALLY PROHIBITED** across all desktop components. All user interfaces must be implemented in native compiled Rust with Slint (`nebu-shell` idle RSS <= 45 MB, `nebu-marketplace-ui` idle RSS <= 35 MB).
- **Abstract Icon Access Invariant (`NebuIcon`):** Application code and Slint markup must **NEVER** bind directly to external SVG file paths or third-party library glyph names. All icons must be requested via the strongly typed `NebuIcon` abstraction layer (`docs/design/01-iconography.md`).
- **Dual-Phase Icon Lifecycle:** An open-source candidate library (Lucide or Material Symbols) is used strictly for prototyping and development under verified SPDX licensing, with a seamless, zero-refactor transition to a custom, dedicated **Nebu Icon Set** in production.
- **Untrusted Icon Sanitization:** Third-party application icons (from Flathub or extracted Windows PE `.ico` files) are treated as untrusted data and must be parsed in an unprivileged Bubblewrap sandbox before rasterization.
- **Tripartite Desktop Architecture (ADR-0009 / ADR-0013):** A single `nebu-shell` binary dynamically coordinates Theme (visual styling), Layout (spatial geometry), and Behavior (interactions). Creating separate shell binaries for Windows-like vs. macOS-like paradigms is strictly prohibited.
- **Accessibility & Contrast Invariants:** All UI implementations must satisfy WCAG 2.1 AA luminance contrast (>= 4.5:1 for body copy, >= 3.0:1 for large headers/icons), provide full keyboard navigation with a 2px solid focus ring, and clamp animations to 0ms when `reduced_motion = true`.
- **SPDX Asset Licensing:** Every external asset (font, icon, wallpaper) must declare an approved SPDX open-source license (`OFL-1.1`, `ISC`, `Apache-2.0`, `MIT`) in `assets/LICENSES.md` and maintain attribution in `assets/ATTRIBUTION.md`.

---

## 24. Boot Experience Architecture & Phase Governance Policy

To guarantee a modern, silent, flicker-free boot experience without violating architectural milestone boundaries:
- **Governing Architecture:** All boot-related design and implementation is strictly governed by [ADR-0014: NebuOS Boot Experience Architecture and Graphical Handoff](docs/decisions/ADR-0014-boot-experience-and-graphical-handoff.md) and [01-boot-specification.md](docs/specification/01-boot-specification.md).
- **Milestone Ownership & Strict Boundaries:**
  - **Milestone P0 (Headless Foundation):** P0 is **100% HEADLESS**. Scope is strictly confined to UEFI firmware handover, GRUB2 BLS bootloader configuration, silent kernel command-line parameters (`quiet splash loglevel=3 rd.systemd.show_status=false systemd.show_status=false vt.global_cursor_default=0 udev.log_level=3`), Dracut initramfs modules (explicitly omitting Plymouth: `omit_dracutmodules+=" plymouth "`), Btrfs mount orchestration, systemd multi-user target initialization, and `bootc` transactional rollback boot counter tracking. Coding agents in P0 are **CATEGORICALLY PROHIBITED** from introducing Plymouth splash screens, Slint, Wayland, or any graphical frameworks into the P0 build.
  - **Milestone P1 (NebuCompositor):** Provides Stage 7 (GRAPHICAL_HANDOFF) and Stage 8 (NEBUCOMPOSITOR). The Smithay-based compositor takes over the DRM/KMS scanout plane from Linux SimpleDRM / EFI framebuffer (guided by ACPI BGRT metadata) using atomic modesetting under the scanout preservation principle (avoiding unnecessary modeset when compatible, while permitting clean atomic modeset if hardware requires link retraining), guaranteeing flicker-free display transition.
  - **Milestone P2 (NebuShell & Graphical Boot Experience):** The exclusive milestone for user-facing graphical boot splash components (if evaluated/enabled), visual branding, splash-to-shell smooth cross-fade (< 200ms) conforming to master motion tokens, and post-rollback user notification cards.
- **Ten-Stage Boot Lifecycle Invariant:** Every boot implementation must conform to the formal 10-stage lifecycle: `POWER_ON → UEFI → BOOTLOADER → KERNEL → INITRAMFS → SYSTEMD → GRAPHICAL_HANDOFF → NEBUCOMPOSITOR → NEBUSHELL → READY`. Screen ownership at each stage must be strictly respected.
- **Boot Counter Ownership & Native Engine Rule:** `boot_counter` serves strictly as an orchestration mechanism for health verification and rollback triggering. Coding agents must **NEVER** build a custom deployment engine, custom package manager, or custom update daemon. Deployment staging, switching, and rollback rely strictly on native `bootc` CLI/APIs and GRUB BLS mechanisms.
- **Decoupled Health Verification Invariant:** Agents must explicitly distinguish: `P0 Boot Completed` $\neq$ `P0 Deployment Healthy` $\neq$ `P1/P2 Graphical Session Ready`. In P0, `nebu-boot-check` is a minimal deterministic oneshot service (timeout 45s, not a complex daemon) that commits `boot_success=1` only after verifying PID 1 health, root and critical mounts, basic networking (if in baseline), active headless baseline services, and zero failed critical units. Hardware watchdog is disarmed only if verified and active on the platform.
- **Performance Targets as Reference Targets:** Boot performance targets (NVMe $\le 4600\text{ ms}$, SATA $\le 7700\text{ ms}$, QEMU headless P0 $\le 3500\text{ ms}$) are Reference Engineering Targets, **NOT** hard real-time guarantees or automatic P0 build/test failure gates before empirical calibration across target hardware tiers.
- **Three Boot Modes Invariant:**
  1. *Normal Boot:* Silent, OEM/Nebu branded, zero console log spam.
  2. *Diagnostic Boot:* Triggered via user escape key (`Escape` or `F8`) or explicit BLS entry (`ostree-1-nebuos-diag.conf`); unblanks screen and exposes full live verbose console logging (`loglevel=7 debug console=tty1`).
  3. *Recovery / Rollback Boot:* Automatically triggered when GRUB boot counter reaches 0 or selected manually from GRUB menu; boots silently into the previous verified deployment and triggers a post-boot diagnostic notification card in NebuShell.
- **Display Handover & Anti-Flicker Invariant:** All graphical display transitions must preserve the scanout framebuffer across the physical transport flow: UEFI GOP $\rightarrow$ EFI framebuffer $\rightarrow$ Linux SimpleDRM $\rightarrow$ Native GPU DRM/KMS $\rightarrow$ NebuCompositor (with ACPI BGRT providing logo metadata, not physical buffer transport), without VT toggling or display resolution switching.
- **Design System Invariance:** Visual styling for early system boot components must bind strictly to `nebu-design-tokens` (`Color.Background #0D1117`, `Color.Accent #388BFD`, `Typography.FontFamilySans Inter`). Creating a second, disparate, or competing design system for the bootloader or splash is strictly forbidden.

---

## 25. Milestone P0 Foundation Implementation & Verification Mandates

When executing Milestone P0 (Foundation Operating System), every engineering agent is strictly bound by these implementation contracts:

1. **Absolute Headless Scope Boundary:** Milestone P0 delivers ONLY the bootable, headless base OS:
   - Base image: Fedora Linux 44 Atomic (`quay.io/fedora/fedora-bootc:44`).
   - Kernel 6.14+, Dracut initramfs without Plymouth (`omit_dracutmodules+=" plymouth "`).
   - UEFI GOP + GRUB2 BLS bootloader (silent normal boot and verbose diagnostic boot entries).
   - Btrfs filesystem subvolumes: `@` (`/sysroot`), `@home` (`/var/home`), `@var` (`/var`).
   - Immutable `/usr` mounted strictly read-only (`ro,nodev`).
   - systemd `multi-user.target` with `agetty` on `tty1` and `ttyS0`.
   - Basic networking via NetworkManager.
   - **STRICT ANTI-SCOPE:** Under NO circumstances may a P0 task introduce: Wayland, Smithay, `nebu-compositor`, `nebu-shell`, Slint, Iced, Plymouth, audio stacks (PipeWire/PulseAudio), Wine, Proton, DXVK, VKD3D, or Marketplace components.
2. **Native bootc & Zero Custom Deployment Engine:**
   - Operating system deployment, packaging, layer caching, and rollback rely 100% natively on `bootc` and GRUB BLS bootloader entries.
   - Agents are **FORBIDDEN** from implementing custom deployment engines, custom package managers, or custom update daemons.
   - The `boot_counter` in `grubenv` is purely orchestration state for health verification and rollback triggering.
3. **Reproducible & Pinned Build Principles:**
   - Production and release container builds MUST use immutable digest pinning (`quay.io/fedora/fedora-bootc:44@sha256:...`).
   - Floating tags (e.g. `:44`) are permitted only during early local prototyping.
   - Package manifests must be minimal and explicitly pinned to avoid dependency bloat.
4. **Deterministic Health Gate (`nebu-boot-check`):**
   - Must be implemented as a deterministic systemd oneshot service (`Type=oneshot`, `TimeoutSec=45`), NOT a complex daemon.
   - Executes after `multi-user.target`.
   - Minimum assertions: PID 1 operational, Btrfs root mounted, `/usr` read-only, critical mounts active (`/var`, `/proc`, `/sys`, `/dev`), sufficient storage free, baseline network link ready, core headless services active, zero critical systemd unit failures.
   - Writes `boot_success=1` and `boot_counter=0` only upon all assertions passing.
   - Disarms hardware watchdog (`/dev/watchdog`) only if verified and active on the platform.
5. **Rollback & Resilience Hierarchy:**
   - A staged deployment starts with `boot_counter=3` and `boot_success=0`.
   - GRUB decrements `boot_counter` on each boot attempt.
   - Upon counter exhaustion (`boot_counter <= 0`):
     - If a previous deployment exists $\rightarrow$ automatically boots `deployment.0`.
     - If NO previous deployment exists (broken initial installation) $\rightarrow$ halts auto-reboot and drops to the interactive GRUB Recovery Menu (`rescue.target`), preventing infinite boot loops.
6. **Decoupled Lifecycle Hierarchy:**
   $$\text{Build Success} \neq \text{Boot Success} \neq \text{Deployment Healthy}$$
   - A successful container build does NOT mean P0 has succeeded.
   - A successful kernel boot does NOT mean the deployment is healthy.
   - P0 is certified **PASS** if and only if the built image successfully boots under UEFI and passes the deterministic health gate.
7. **Empirical Evidence Requirement:**
   - No agent may claim "PASS", "complete", or "verified" without providing actual execution logs from the build and boot harness.
   - If KVM acceleration is unavailable in the execution container (e.g. CT 100 without `/dev/kvm`), QEMU TCG must be used for functional verification, while Proxmox VM UEFI/KVM deployment is documented. Never fabricate benchmark numbers or hardware test outputs.

