# Windows Application Runtime Skill — NebuOS

## 1. Purpose
Governs the architecture, isolation, and execution lifecycle of Windows applications running under Wine/Proton, supervised by `nebu-runtime-daemon`.

## 2. Scope
Applies strictly to Milestone P3 (NebuRuntime).

## 3. Relevant Documentation
- `docs/roadmap/04-p3-neburuntime.md`: Milestone P3 execution plan.
- `docs/specification/02-process-ipc-specification.md`: Process model and cgroups.
- `docs/runtime/00-runtime-specification.md`: Master runtime daemon specification.
- `docs/runtime/04-prefix-management.md`: Prefix directory tree and reflink cloning.
- `docs/decisions/ADR-0004-wine-proton-integration.md`: Dual Wine/Proton strategy.
- `docs/decisions/ADR-0006-btrfs-reflink-prefix-management.md`: Btrfs reflink prefixes.

## 4. Allowed Changes
- Authoring runtime daemon code in `crates/nebu-runtime-daemon/`.
- Managing Btrfs prefix templates in `/usr/share/nebu/prefix-template/`.
- Authoring Bubblewrap (`bwrap`) argument templates.

## 5. Forbidden Changes
- **DO NOT WORK IN P0, P1, OR P2:** Locked until P0, P1, and P2 are complete.
- **NO GLOBAL UNCONFINED WINE:** Never invoke raw `/usr/bin/wine` directly without container sandboxing.
- **NO EXPOSING ROOT AS Z: DRIVE:** The Linux root filesystem (`/`) must NEVER be mounted as `Z:`. Only sandboxed user folders (`~/Documents`) may be mapped.

## 6. Architecture Constraints
- **Per-Application Prefix Isolation:** Every Windows application operates in its own dedicated prefix:
  `~/.var/nebu/prefixes/<app-id>/`
  - `pfx/drive_c/`
  - `pfx/system.reg`, `user.reg`
  - `logs/`
  - `metadata.json`
- **Instant Provisioning:** Prefixes instantiated via Btrfs reflink (`cp --reflink=always -r ...`) in < 50ms.
- **Process Supervision:** Controlled process tree via systemd transient cgroups (`app-nebu-<app-id>.scope`).

## 7. Implementation Guidance
- Maintain separate `wineserver` instances per prefix.
- Implement robust shutdown: terminate child processes cleanly with `SIGTERM` followed by `SIGKILL` on timeout.
- Expose D-Bus API `org.nebu.Runtime1` for application launch, termination, and prefix health repair.

## 8. Verification
- Verify that killing one Windows application leaves other prefixes completely unaffected.
- Verify that modifying files inside `C:\Windows\` does not contaminate the master template.

## 9. Common Failure Modes
- Orphaned `wineserver` processes hanging indefinitely in background.
- Concurrent access corrupting registry hives when locking is omitted.

## 10. Handoff Requirements
- Record prefix creation benchmarks and process tree cleanup test results in `HANDOFF.md`.
