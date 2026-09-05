# Gemini / Antigravity Agent Configuration — NebuOS

You are working on the **NebuOS** repository.

This project is strictly governed by the universal repository contract:
👉 **[`AGENTS.md`](AGENTS.md)**

### Mandatory Directives:
1. **Universal Contract:** Read [`AGENTS.md`](AGENTS.md) and strictly follow the 21-step startup protocol.
2. **Current State:** Read [`PROJECT_STATE.md`](PROJECT_STATE.md) and [`HANDOFF.md`](HANDOFF.md) to understand current milestone and restrictions.
3. **Architecture Baseline:** Fedora Linux 44 (`quay.io/fedora/fedora-bootc:44`), `bootc` 1.1+, Btrfs subvolumes (`@`, `@home`, `@var`), `/usr` read-only. Digest pinning for release.
4. **Knowledge Graph (`graphify`):**
   - For codebase queries, run `graphify query "<question>"` when `graphify-out/graph.json` exists.
   - Read `graphify-out/GRAPH_REPORT.md` only for broad review.
   - After modifying code, run `graphify update .` to keep the graph current.
5. **Milestone Boundary:** Respect milestone isolation. Do not implement future milestone features prematurely (Milestone P0 is strictly headless foundation; NO Wayland, Smithay, GUI, Wine, Proton).
6. **Smallest Correct Change:** Prefer the smallest correct change. Reuse standard patterns and avoid speculative abstractions.
