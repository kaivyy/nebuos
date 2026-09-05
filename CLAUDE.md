# Claude Code Agent Configuration — NebuOS

You are working on the **NebuOS** repository.

This project is strictly governed by the universal repository contract:
👉 **[`AGENTS.md`](AGENTS.md)**

### Baseline & Architecture Foundation:
- **Baseline OS:** Fedora Linux 44 (`quay.io/fedora/fedora-bootc:44`)
- **Deployment Substrate:** `bootc` 1.1+ (OSTree container backend, `/usr` read-only)
- **Active Milestone:** Follow `PROJECT_STATE.md` strictly (Milestone P0 is headless foundation ONLY)
- **Smallest Correct Change:** Prefer minimal, concise changes; reuse standard patterns; no speculative abstractions.

### Mandatory Startup Sequence:
1. Read [`AGENTS.md`](AGENTS.md) and execute the 21-step startup protocol.
2. Read [`PROJECT_STATE.md`](PROJECT_STATE.md) to inspect active milestone and blockers.
3. Read [`HANDOFF.md`](HANDOFF.md) to review previous agent directives.
4. Check [`docs/INDEX.md`](docs/INDEX.md) for relevant technical specifications.

### Strict Prohibitions:
- DO NOT implement features outside the current active milestone.
- DO NOT write code for future milestones (no Wayland/GUI/Compositor/Wine in P0).
- DO NOT execute destructive git or filesystem commands.
- DO NOT rely on previous conversation memory; rely solely on repository files.
