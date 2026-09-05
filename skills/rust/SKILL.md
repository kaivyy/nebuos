# Rust Systems Engineering Skill — NebuOS

## 1. Purpose
This skill establishes strict coding, error-handling, memory-safety, and dependency standards for all Rust components in NebuOS (`nebu-compositor`, `nebu-shell`, `nebu-runtime-daemon`).

## 2. Scope
Applies to milestones P1 through P4 and any custom Rust crates in the workspace.

## 3. Relevant Documentation
- `docs/development/05-coding-guidelines.md`: Rust coding standards.
- `docs/development/04-dependency-policy.md`: Approved external crate list and licensing.
- `docs/interfaces/02-runtime-interfaces.md`: Rust trait definitions.

## 4. Allowed Changes
- Creating and editing Rust files in `src/` or Cargo workspace crates.
- Adding unit and integration tests under `tests/`.
- Writing Rustdoc comments on public APIs.

## 5. Forbidden Changes
- **NO UNJUSTIFIED `unsafe`:** Never use `unsafe` for speed or convenience. All `unsafe` blocks require a detailed `// SAFETY:` rationale.
- **NO PRODUCTION PANICS:** Never call `.unwrap()` or `.expect()` in production codepaths.
- **NO UNAUTHORIZED DEPENDENCIES:** Never add external crates to `Cargo.toml` without satisfying the 10-point Dependency Policy in `AGENTS.md` §11.

## 6. Architecture Constraints
- All daemons must interface asynchronously via `zbus` 4.x.
- Memory allocations must respect individual process budgets (Compositor < 60MB, Shell < 25MB, Runtime Daemon < 15MB).

## 7. Implementation Guidance
- Use `thiserror` for library error enums and `anyhow` for binary application top-levels.
- Structure error types with rich context (e.g., `PrefixError::ReflinkFailed { path, source }`).
- Adhere to the Rust API Guidelines (`clippy`, idiomatic borrowing, RAII).

## 8. Verification
- `cargo fmt --check` must return exit code 0.
- `cargo clippy --workspace --all-targets -- -D warnings` must return exit code 0.
- `cargo test --workspace` must pass all tests.

## 9. Common Failure Modes
- Leaking file descriptors or child processes during process supervisor crashes.
- High memory usage caused by unbounded IPC buffers.

## 10. Handoff Requirements
- Record `clippy` and `cargo test` execution outputs in `HANDOFF.md`.
- Explicitly list any new crate dependencies added to workspace `Cargo.toml`.
