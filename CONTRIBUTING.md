# Contributing to NebuOS — Developer & Agent Workflow

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
  - Containerfile builds successfully without errors based on Fedora 44 (`quay.io/fedora/fedora-bootc:44`).
  - Production releases must pin immutable SHA-256 digests (`@sha256:...`); unversioned tags or `:latest` are strictly prohibited.
  - `bootc container lint` reports zero violations.
  - Image size meets milestone budget constraints (<1.8GB for P0 uncompressed).
- **Testing Evidence:**
  - Pull requests and handoffs must include terminal execution logs verifying acceptance criteria. Assertions without empirical evidence will be rejected.
- **Minimal Change & Milestone Discipline:**
  - Prefer the smallest correct change. Do not introduce speculative abstractions or unapproved dependencies.
  - Adhere strictly to the active milestone boundary. Features belonging to future milestones (e.g., Wayland/GUI/Wine in P0) will be rejected immediately.

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
