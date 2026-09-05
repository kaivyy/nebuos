# Agents & Skills Architecture Alignment Audit Report — NebuOS

**Document ID:** NEBU-AUDIT-AGENTS-SKILLS-2026-001  
**Audit Date:** 2026-09-04  
**Auditor Roles:** Principal Developer Experience Architect, Agent Governance Engineer, Linux OS Architect, Security Architect, Release Gate Auditor  
**Audit Scope:** Full audit and synchronization of `AGENTS.md`, all 13 domain `SKILL.md` files, `skills/README.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `GEMINI.md`, and `.cursorrules` to establish complete alignment with the Fedora Linux 44 baseline, bootc substrate, immutable digest pinning, P0 headless boundary, milestone isolation, verification-first culture, and the minimal change principle.  
**Final Audit Status:** **PASS WITH NOTES**  

---

## 1. Executive Summary

This audit report evaluates and establishes the complete alignment of all developer and AI agent instruction files across the NebuOS repository. As NebuOS prepares for Milestone P0 implementation, human engineers and autonomous coding agents (Codex, Claude Code, Agy CLI, Gemini, Cursor, etc.) require unambiguous, synchronized, and enforceable operational directives.

Prior to this alignment, agent instructions suffered from architectural drift:
- Inconsistent base OS references across governance files (ambiguity regarding Fedora versions).
- Missing immutable SHA-256 digest pinning requirements for container base images.
- Broken ADR references in domain skill files (e.g., references to non-existent `ADR-0001` or `ADR-0002-btrfs-filesystem-layout.md`).
- Absence of explicit "Prefer the Smallest Correct Change" guidance, risking speculative abstractions and bloat.
- Lack of formalized empirical verification expectations and `VERIFY_REQUIRED` flagging for hardware-dependent milestones.

Through systematic audit and remediation:
1. **Fedora Linux 44** (`quay.io/fedora/fedora-bootc:44`) is established as the immutable upstream baseline across all agent files.
2. **bootc 1.1+** is codified as the atomic deployment substrate, with strict immutable digest pinning (`@sha256:...`) required for production releases.
3. **Milestone P0 Scope & Anti-Scope** are cemented: P0 is strictly a minimal headless foundation (kernel 6.14+, systemd v256+, dracut v102+, TTY login, Btrfs subvolumes, network, permissive SELinux, QEMU boot validation). All graphical, Wayland, shell, Wine, and desktop features are locked out.
4. **Milestone Isolation & Minimal Change Policies** are embedded into core governance, preventing premature implementations or speculative over-engineering.
5. **Verification-First Standards** are codified, preventing fabricated test claims and defining concrete empirical pass criteria.

The final verdict is **PASS WITH NOTES**. All governance, agent instructions, and skills are completely synchronized. The sole "note" reflects that live runtime execution and boot testing remain categorized as `VERIFY_REQUIRED` to be executed during Milestone P0 implementation.

---

## 2. Files Audited

Every agent configuration, governance contract, skill document, and contributor guide in the repository was inspected:

| File Path | Component / Role | Audit Status | Primary Findings & Remediation |
|---|---|---|---|
| [`AGENTS.md`](file:///root/NebuOS/AGENTS.md) | Universal Agent Contract | **UPDATED / PASS** | Added Fedora 44 baseline, digest pinning rule, Principle 15 (Smallest Correct Change), Principle 16 (Milestone Isolation), execution lifecycle (§4.1), behavioral prohibitions (§4.2), P0 empirical criteria (§15), and reproducibility policy (§21). |
| [`skills/architecture/SKILL.md`](file:///root/NebuOS/skills/architecture/SKILL.md) | Architecture Governance Skill | **UPDATED / PASS** | Aligned layer hierarchy to Fedora 44 bootc; embedded Minimal Change Principle and Milestone Isolation constraints. |
| [`skills/system/SKILL.md`](file:///root/NebuOS/skills/system/SKILL.md) | Base OS & Services Skill | **UPDATED / PASS** | Corrected broken ADR references to `ADR-0002`, `ADR-0008`, `ADR-0011`; codified Fedora 44 base image, digest pinning, and P0 scope/anti-scope. |
| [`skills/compositor/SKILL.md`](file:///root/NebuOS/skills/compositor/SKILL.md) | Wayland Compositor Skill | **AUDITED / PASS** | Contains explicit `DO NOT WORK IN P0` lockout. Target milestone correctly designated as P1. No edits needed. |
| [`skills/shell/SKILL.md`](file:///root/NebuOS/skills/shell/SKILL.md) | Desktop Shell Skill | **AUDITED / PASS** | Contains explicit `DO NOT WORK IN P0` lockout. Target milestone correctly designated as P2. No edits needed. |
| [`skills/runtime/SKILL.md`](file:///root/NebuOS/skills/runtime/SKILL.md) | Windows Runtime Skill | **AUDITED / PASS** | Contains explicit `DO NOT WORK IN P0` lockout. Target milestone correctly designated as P3. No edits needed. |
| [`skills/compatibility/SKILL.md`](file:///root/NebuOS/skills/compatibility/SKILL.md) | Compatibility Platform Skill | **AUDITED / PASS** | Contains explicit `DO NOT WORK IN P0` lockout. Target milestones correctly designated as P4/P7. No edits needed. |
| [`skills/graphics/SKILL.md`](file:///root/NebuOS/skills/graphics/SKILL.md) | 3D Graphics Skill | **AUDITED / PASS** | Contains explicit `DO NOT WORK IN P0` lockout. Target milestone correctly designated as P5. No edits needed. |
| [`skills/security/SKILL.md`](file:///root/NebuOS/skills/security/SKILL.md) | Security & Containment Skill | **UPDATED / PASS** | Added invariants: no hardcoded secrets, no unsafe shell execution, path validation, least privilege, and secure defaults. |
| [`skills/testing/SKILL.md`](file:///root/NebuOS/skills/testing/SKILL.md) | Verification & Testing Skill | **UPDATED / PASS** | Added `docs/audit/FEDORA_44_BASELINE_AUDIT.md` reference; formalized `VERIFY_REQUIRED` status and 9 empirical P0 test suites. |
| [`skills/performance/SKILL.md`](file:///root/NebuOS/skills/performance/SKILL.md) | Performance Engineering Skill | **AUDITED / PASS** | References performance budgets; adheres to core architecture. No edits needed. |
| [`skills/documentation/SKILL.md`](file:///root/NebuOS/skills/documentation/SKILL.md) | Documentation Sync Skill | **AUDITED / PASS** | Adheres to Source of Truth hierarchy and documentation drift standards. No edits needed. |
| [`skills/release/SKILL.md`](file:///root/NebuOS/skills/release/SKILL.md) | Release & Updates Skill | **UPDATED / PASS** | Added references to `ADR-0002` and `ADR-0011`; codified Fedora 44 base image, digest pinning, and background staging. |
| [`skills/rust/SKILL.md`](file:///root/NebuOS/skills/rust/SKILL.md) | Rust Systems Skill | **AUDITED / PASS** | Enforces idiomatic Rust, zero clippy warnings, minimal unsafe code. No edits needed. |
| [`skills/README.md`](file:///root/NebuOS/skills/README.md) | Skills Catalog Index | **UPDATED / PASS** | Updated `system/` row to explicitly reference `Fedora 44 Atomic / bootc`. |
| [`CONTRIBUTING.md`](file:///root/NebuOS/CONTRIBUTING.md) | Developer & Contributor Guide | **UPDATED / PASS** | Added Fedora 44 baseline, digest pinning rule, size budget, minimal change policy, and milestone discipline to quality gates. |
| [`CLAUDE.md`](file:///root/NebuOS/CLAUDE.md) | Claude Code Agent Config | **UPDATED / PASS** | Added Fedora 44 baseline, bootc 1.1+, minimal change guidance, and explicit P0 anti-scope prohibitions. |
| [`GEMINI.md`](file:///root/NebuOS/GEMINI.md) | Gemini/Antigravity Config | **UPDATED / PASS** | Added Fedora 44 baseline, bootc 1.1+, digest pinning, minimal change principle, and P0 headless boundary directives. |
| [`.cursorrules`](file:///root/NebuOS/.cursorrules) | Cursor IDE Rules | **UPDATED / PASS** | Added Fedora 44 baseline, bootc 1.1+, digest pinning, and smallest correct change rule. |

---

## 3. Fedora 44 Alignment

Across all agent instructions and skills, the upstream operating system baseline has been unified on **Fedora Linux 44**:
- **Official Container Base:** `quay.io/fedora/fedora-bootc:44`
- **Core Software Baseline:**
  - Linux Kernel: `6.14+`
  - systemd: `v256+`
  - dracut: `v102+`
  - Btrfs progs: `6.8+`
  - bootc: `1.1+`
- **Decoupled Product Semantic Versioning:** All agent documents clarify that NebuOS versioning (`0.1.0` for Milestone P0, `0.2.0` for P1, etc.) is completely decoupled from the upstream Fedora 44 release number.
- **Zero Stale References:** No active skill or agent instruction file contains references to deprecated baselines (Fedora 40, 41, 42, 43, Rawhide, or unversioned tags).

---

## 4. bootc Alignment

NebuOS utilizes an atomic, image-based deployment substrate powered by `bootc`:
- **Architecture Model:** An OSTree-backed transactional container deployment. The root filesystem (`/usr`) is mounted strictly read-only. Stateful directories (`/etc`, `/var`, `/home`) are preserved across updates.
- **Storage Topology:** Three dedicated Btrfs subvolumes:
  - `@` mounted at `/` (root filesystem, managed via OSTree deployments)
  - `@home` mounted at `/var/home` (persistent user data)
  - `@var` mounted at `/var` (persistent system state)
- **Update Workflow:** Atomic updates staged in background via `bootc upgrade --apply=false`, with seamless switchover upon next reboot.
- **Digest Pinning Mandate:**
  - Production and release container builds MUST pin immutable SHA-256 base image digests (`quay.io/fedora/fedora-bootc:44@sha256:...`).
  - The use of unpinned, floating tags (`:latest`, unadorned `:44`) is strictly prohibited in release configurations.

---

## 5. P0 Scope Alignment

Milestone P0 represents the bare-metal and virtualized foundation substrate. All agent instructions enforce that P0 is strictly limited to:
1. Upstream base image `quay.io/fedora/fedora-bootc:44`.
2. Minimal `Containerfile.p0` package manifest (kernel, dracut, systemd, btrfs-progs, NetworkManager, shadow-utils, util-linux).
3. Btrfs subvolume layout (`@`, `@home`, `@var`) with zstd:1 compression.
4. dracut initramfs configuration supporting systemd and Btrfs boot.
5. GRUB 2.06+ / Boot Loader Specification (BLS) compliant bootloader configuration.
6. systemd `multi-user.target` steady-state target.
7. TTY text-mode login prompt on virtual consoles (`tty1`–`tty6`) and serial console (`ttyS0`).
8. NetworkManager DHCP automatic network acquisition.
9. SELinux `permissive` baseline logging denials for future policy generation.
10. Bare-metal and QEMU boot validation.
11. Uncompressed container image size budget strictly below 1.8 GB.

---

## 6. P0 Anti-Scope Alignment

All agent skills and instructions explicitly lock out the following components during Milestone P0:
- **NO Graphical Display Server:** No Wayland compositor, no Smithay, no wlroots, no X11.
- **NO Desktop Shell:** No NebuShell, no Slint, no GTK, no Qt, no UI themes or layouts.
- **NO Windows Compatibility:** Zero Wine, Proton, DXVK, VKD3D-Proton, binfmt_misc, or wineserver.
- **NO Application Subsystems:** No Software Center, no Application Installer, no SQLite compatibility database.
- **NO Audio Subsystem:** No PipeWire or WirePlumber.
- **NO Non-Standard Drivers:** No proprietary GPU drivers (NVIDIA proprietary driver deferred to P5).

Any agent attempting to introduce code, dependencies, or unit files for anti-scope features during P0 will be immediately flagged for governance violation.

---

## 7. Milestone Isolation

Milestone isolation is codified as Principle 16 in `AGENTS.md` and enforced in `skills/architecture/SKILL.md`:
- Engineering tasks are strictly compartmentalized by roadmap phase (P0 Foundation -> P1 Compositor -> P2 Shell -> P3 Runtime -> P4 Compatibility -> P5 Graphics -> P6 Applications -> P7 Testing -> P8 Production).
- Agents executing tasks for milestone `P[n]` are prohibited from creating placeholder crates, speculative interfaces, stubs, or mock implementations for milestone `P[n+1]` or beyond.
- Progression between milestones requires meeting 100% of the preceding milestone's exit criteria, documented and approved through a formal Ready Gate.

---

## 8. Architecture Governance

The governance system ensures architectural stability regardless of the AI agent or developer involved:
- **Source of Truth Hierarchy:**
  1. `PRD.md` (Master Requirements & Non-Negotiable Invariants)
  2. `docs/decisions/` (Approved ADRs)
  3. `docs/specification/` & `docs/interfaces/` (Implementation Contracts)
  4. `docs/roadmap/` (Phase Boundaries & Exit Gates)
  5. Implementation Code
  6. Informational Overviews (`docs/architecture/`)
- **Strict Layer Hierarchy:**
  ```text
  Linux Kernel (6.14+)
    │
  Fedora 44 bootc Base (systemd v256+, dracut v102+)
    │
  System Services (NetworkManager, D-Bus, udev)
    │
  Wayland Core Protocols (wl_compositor, xdg_shell) [P1]
    │
  Smithay 0.3+ Compositor (nebu-compositor) [P1]
    │
  NebuShell UI (Slint toolkit) [P2]
    │
  NebuRuntime Daemon (bwrap sandbox, prefix manager) [P3]
    │
  Wine 9.x / Proton / DXVK / VKD3D-Proton [P3-P5]
    │
  Windows Applications [P3+]
  ```
- **Minimal Change Principle (Principle 15):** Agents must always prefer the smallest correct change. Every added abstraction, trait, dependency, or configuration file must be strictly justified by the immediate task requirements. Speculative generalizations and premature optimizations are rejected.

---

## 9. Verification Policy

NebuOS operates under a strict verification-first culture:
- **Evidence Over Assertion:** Agents cannot claim that a task is "complete", "working", or "fixed" without providing concrete, reproducible terminal command outputs.
- **`VERIFY_REQUIRED` Status:** Tests requiring execution on real hardware, hypervisors (QEMU), or container runtimes that cannot be executed in the current session are explicitly flagged as `VERIFY_REQUIRED`.
- **Three-Tier Verification Ladder:**
  - *Tested:* Automated unit or integration tests pass in a mock or container harness.
  - *Verified:* Tested on live target architecture (bare metal or QEMU) with execution logs captured.
  - *Accepted:* Verified and validated against all PRD requirements and non-functional SLAs.
- **Zero Tolerance for Hallucinated Results:** Simulating or guessing test outcomes is a critical governance breach.

---

## 10. Security Guidance

Security and containment guidelines have been unified across `AGENTS.md` and `skills/security/SKILL.md`:
1. **Zero Hardcoded Secrets:** No API keys, credentials, signing private keys, or passwords in code or containerfiles.
2. **Safe Subprocess Execution:** Raw shell invocations (`sh -c`, `bash -c`, or unescaped string formatting) are prohibited. All process spawning must use structured argument vectors (e.g., `std::process::Command::new`).
3. **Unprivileged Namespaces:** Containerization and application sandboxing must use unprivileged user namespaces (`bwrap`). Setuid root helper binaries are strictly prohibited.
4. **Strict Path Validation:** All filesystem paths passed to daemons or sandboxes must be canonicalized to prevent path traversal attacks (`..`, symlink escapes).
5. **Least Privilege:** Daemons and background services must run under dedicated unprivileged system accounts unless kernel/mount privileges are explicitly mandated.
6. **SELinux Baseline:** Permissive during P0–P4 to accumulate audit logs without blocking system startup; enforcing mode activated in P5 with dedicated policy modules (`nebu-sandbox.te`).
7. **Secure Defaults:** System defaults must fail closed. Access is denied unless explicitly authorized.

---

## 11. Reproducibility Guidance

To ensure deterministic, bit-reproducible OS image generation:
- Base images must be pinned to immutable SHA-256 digests in production build manifests:
  ```dockerfile
  FROM quay.io/fedora/fedora-bootc:44@sha256:44b6c...
  ```
- Package installation commands in containerfiles must lock repository states or specify explicit package versions where applicable.
- Ephemeral package caches must be purged within the same container layer (`dnf clean all && rm -rf /var/cache/dnf/*`).
- File timestamps, permissions, and build-time metadata must be normalized during image packaging.

---

## 12. Instruction Conflicts Found & Resolved

During the audit, four notable discrepancies and conflicts were identified and remediated:

1. **Broken ADR References in `skills/system/SKILL.md`:**
   - *Conflict:* Referenced `docs/decisions/ADR-0001-base-os-architecture.md` and `ADR-0002-btrfs-filesystem-layout.md`, neither of which existed.
   - *Resolution:* Corrected to canonical ADR files: `docs/decisions/ADR-0002-fedora-base.md`, `ADR-0008-atomic-updates.md`, and `ADR-0011-os-image-updates-and-rollback.md`.
2. **Missing Fedora Release Pinning in `AGENTS.md`:**
   - *Conflict:* `AGENTS.md` previously described Fedora Atomic/bootc generically without binding the baseline to Fedora Linux 44.
   - *Resolution:* Added explicit Fedora Linux 44 baseline, upstream image `quay.io/fedora/fedora-bootc:44`, bootc 1.1+, and digest pinning rules across Sections 2, 6, 15, and 21.
3. **Absence of Minimal Change Directive:**
   - *Conflict:* Prior governance lacked an explicit constraint against speculative over-engineering, leading to risks of bloated abstractions.
   - *Resolution:* Added Principle 15 ("Prefer the Smallest Correct Change") to `AGENTS.md`, and reinforced it in `skills/architecture/SKILL.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `GEMINI.md`, and `.cursorrules`.
4. **Discrepancy in P0 Verification Expectations:**
   - *Conflict:* Verification expectations for P0 were fragmented across different documents without a unified checklist of empirical values.
   - *Resolution:* Harmonized across `AGENTS.md` §15 and `skills/testing/SKILL.md` §8 into 9 concrete empirical tests with specific required metrics.

---

## 13. Changes Made (Detail per File)

The following edits were made across the repository:

### 1. `AGENTS.md`
- **Section 2 (Architectural Core):** Added Fedora Linux 44 baseline, `quay.io/fedora/fedora-bootc:44`, bootc 1.1+, digest pinning, prohibited `:latest`, and updated ASCII layer diagram to show Fedora 44 base and kernel 6.14+.
- **Section 3 (Core Invariants):** Added Principle 15 (Prefer the Smallest Correct Change) and Principle 16 (Milestone Isolation).
- **Section 4 (Agent Execution Protocol):** Added §4.1 (Execution Lifecycle: READ FIRST -> AUDIT -> PLAN -> IMPLEMENT ONLY REQUESTED SCOPE -> VERIFY -> DOCUMENT -> FINAL REPORT) and §4.2 (Strict Behavioral Prohibitions).
- **Section 6 (Milestone Boundaries):** Updated Milestone P0 row with complete in-scope/anti-scope and added explicit Milestone Isolation boundary rule.
- **Section 7 (System Invariants):** Added core security & safety rules (zero hardcoded secrets, no unsafe shell execution, least privilege, path validation).
- **Section 14 (Verification Ladder):** Added `VERIFY_REQUIRED` status definition and empirical testing requirements.
- **Section 15 (Acceptance Criteria):** Added 12 concrete P0 verification items requiring real numerical values and terminal logs.
- **Section 21 (Reproducibility & Build Governance):** Added comprehensive image build governance and digest pinning policy.

### 2. `skills/system/SKILL.md`
- Fixed broken ADR links to point to `ADR-0002-fedora-base.md`, `ADR-0008-atomic-updates.md`, and `ADR-0011-os-image-updates-and-rollback.md`.
- Codified base image `quay.io/fedora/fedora-bootc:44`, digest pinning for release, and prohibition of `fedora:latest`.
- Formulated complete P0 scope, anti-scope, and verification procedures.

### 3. `skills/release/SKILL.md`
- Added references to `ADR-0002` and `ADR-0011`.
- Codified Fedora 44 base image, immutable digest pinning, prohibition of `:latest`, and background staging via `bootc upgrade --apply=false`.

### 4. `skills/testing/SKILL.md`
- Added reference to `docs/audit/FEDORA_44_BASELINE_AUDIT.md`.
- Formally defined `VERIFY_REQUIRED` status and rules prohibiting false completion claims.
- Detailed 9 concrete empirical tests for Milestone P0.

### 5. `skills/architecture/SKILL.md`
- Updated layer hierarchy to: `Linux Kernel (6.14+) -> Fedora 44 bootc (quay.io/fedora/fedora-bootc:44) -> System Services -> Wayland -> Smithay -> NebuShell -> NebuRuntime -> Wine/Proton -> Windows Apps`.
- Added prohibition against speculative abstractions.
- Added Milestone Isolation and Minimal Change Principle constraints.

### 6. `skills/security/SKILL.md`
- Added prohibitions against hardcoded secrets, unsafe shell execution, and arbitrary filesystem access.
- Added architectural constraints for least privilege and unprivileged user namespaces (`bwrap`).
- Added implementation guidance for strict path canonicalization and secure defaults.

### 7. `skills/README.md`
- Updated `system/` row to explicitly reference `Fedora 44 Atomic / bootc`.

### 8. `CONTRIBUTING.md`
- Updated Container Images quality gate to mandate Fedora 44 (`quay.io/fedora/fedora-bootc:44`), immutable digest pinning for releases, and <1.8GB image size budget.
- Added Minimal Change & Milestone Discipline gate.

### 9. `CLAUDE.md`
- Added Baseline & Architecture Foundation section specifying Fedora 44, bootc 1.1+, and minimal change policy.
- Updated prohibitions to explicitly list Wayland, GUI, Compositor, and Wine.

### 10. `GEMINI.md`
- Added Architecture Baseline directive specifying Fedora 44, bootc 1.1+, Btrfs subvolumes, and digest pinning.
- Added Minimal Change Principle directive and clarified P0 headless boundary.

### 11. `.cursorrules`
- Added Architecture Baseline rule specifying Fedora 44 and bootc 1.1+.
- Added Smallest Correct Change rule.

---

## 14. Remaining Issues / Debt

1. **No Implementation Containerfile Yet:** In strict accordance with the pre-implementation audit mandate, `Containerfile.p0` has not yet been authored. It will be constructed as the first step of Milestone P0 implementation.
2. **Live Digest Hash Determination:** The exact SHA-256 digest hash for `quay.io/fedora/fedora-bootc:44` will be determined and pinned upon the initial container image pull during P0 execution.
3. **Automated Link Verification:** An automated markdown link checker script should be scheduled in CI during P0 to continuously monitor cross-reference integrity.

---

## 15. VERIFY_REQUIRED Status

The following verification activities are classified as **`VERIFY_REQUIRED`** and must be empirically executed and logged during Milestone P0 implementation:

1. **Base Image Pull:** Verify `quay.io/fedora/fedora-bootc:44` pulls cleanly and record its image ID and digest.
2. **Container Build:** Build `Containerfile.p0` using Podman; record build time, exit code, and layer log.
3. **bootc Lint:** Run `bootc container lint` on the built image; verify 0 errors and 0 warnings.
4. **Image Size Measurement:** Verify uncompressed image size is strictly below 1.8 GB.
5. **QEMU Virtualized Boot:** Boot disk image in QEMU; confirm bootloader menu, kernel initialization, and systemd multi-user target reach.
6. **Kernel & Userspace Version Check:** Confirm kernel is 6.14+, systemd is v256+, dracut is v102+, Btrfs progs is 6.8+.
7. **Read-Only `/usr` Verification:** Verify `/usr` is mounted `ro` and write attempts are rejected with `Read-only file system`.
8. **TTY Text Login Verification:** Confirm successful login on virtual console and serial console.
9. **SELinux Mode Verification:** Run `getenforce` to verify `Permissive` mode and inspect `/var/log/audit/audit.log` for AVC denial logging.

---

## 16. Final Verdict

**Verdict:** **PASS WITH NOTES**

**Evaluation:**
- All 19 agent instruction, governance, and skill documents are fully synchronized, coherent, and aligned with Fedora Linux 44, bootc 1.1+, Btrfs subvolumes, milestone isolation, security invariants, and verification standards.
- Zero premature implementation code was introduced.
- The repository governance is hardened, unambiguous, and fully ready for Milestone P0 implementation.
- The "NOTES" designation formally reflects that runtime execution gates are categorized as `VERIFY_REQUIRED` for active P0 testing.
