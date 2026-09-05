# ADR-0004: Rust as Primary Implementation Language for Core Components

**Status:** APPROVED  
**Date:** 2026-09-04  
**Deciders:** Principal Systems Architect, Rust Systems Engineer  
**Consulted:** PRD §4, §83, §84  

---

## 1. Context and Problem Statement
Operating system userland daemons—specifically display compositors, desktop shells, and application sandboxing daemons—handle untrusted user input, direct hardware graphics devices, and complex IPC. Historically, C and C++ implementations have suffered from widespread memory safety vulnerabilities (buffer overflows, use-after-free, data races). NebuOS requires a programming language that guarantees memory safety, eliminates data races, provides zero-cost abstractions, and matches C/C++ execution performance.

## 2. Decision Drivers
- **Memory Safety:** Compile-time guarantees eliminating use-after-free, double free, and buffer overflow CVEs.
- **Concurrency Safety:** Compile-time prevention of data races (`Send` / `Sync` traits) essential for multi-threaded compositor and runtime event loops.
- **Predictable Performance:** Zero garbage collection pauses, predictable latency, minimal memory footprint.
- **Modern Ecosystem:** First-class async I/O (`tokio`, `calloop`), D-Bus integration (`zbus`), and modular compositor primitives (`smithay`).
- **Strict Resource Budget:** Capable of running within strict memory budgets (Compositor <= 35 MB, Shell <= 45 MB, Runtime <= 15 MB).

## 3. Considered Options
- **Option 1: Rust for All Core NebuOS Components [SELECTED]**
- **Option 2: Modern C++ (C++20 / C++23)**
- **Option 3: Go (Golang)**
- **Option 4: C (C11) with Sanitizers**

## 4. Decision Outcome
**Chosen Option: Option 1 — Rust as the Primary Systems Language.**

All newly developed NebuOS components—`nebu-compositor`, `nebu-shell`, `nebu-runtime-daemon`, `nebu-installer-ui`, and `compat.db` tooling—are implemented in 100% safe Rust, isolating unavoidable FFI bindings (`libdrm`, `libinput`, SQLite) into audited `unsafe` blocks.

### Positive Consequences
- Elimination of entire classes of memory corruption security vulnerabilities.
- Zero garbage collection overhead ensures smooth 60/120 FPS compositor frame pacing.
- Fearless concurrency across multi-threaded renderers and background I/O tasks.
- Cargo package management and unit test integration streamline developer workflows.

### Negative Consequences
- Slower compilation times compared to C/Go (mitigated via Cargo sccache and modular crate design).
- Steeper learning curve for new contributors.

## 5. Pros and Cons of Alternatives

### Option 2: Modern C++
- *Pros:* Immense graphics library ecosystem; mature tooling.
- *Cons:* Lack of borrow checker; memory safety depends on programmer discipline; legacy undefined behavior footguns.

### Option 3: Go
- *Pros:* Rapid development, fast compile times.
- *Cons:* Garbage collection pauses induce frame drops in display compositors; heavy runtime footprint; poor C FFI ergonomics for DRM/KMS.

### Option 4: C (C11)
- *Pros:* Universal portability, minimal footprint.
- *Cons:* Zero compile-time memory safety; manual resource management prone to memory leaks.

## 6. Confirmation and Validation
- Zero `unsafe` blocks permitted in core business logic; all FFI crates run under Miri and AddressSanitizer in CI.
