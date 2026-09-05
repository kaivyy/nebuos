#!/usr/bin/env python3
"""
Generate Development Documentation for NebuOS (docs/development/):
- 00-development-model.md
- 01-repository-structure.md
- 02-build-system.md
- 03-ci-cd.md
- 04-dependency-policy.md
- 05-coding-guidelines.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs/development"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_file(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: development/{filename} ({len(content.splitlines())} lines)")

# 00-development-model.md
write_file("00-development-model.md", r"""# Development Model Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define the software engineering model, git branching strategy, RFC process, and issue escalation workflows.

---

## 1. Monorepo Architecture & Branching Strategy
NebuOS maintains core system components in a single unified Git repository to ensure synchronized API evolution across compositor, shell, runtime, and compatibility databases.

```mermaid
gitGraph
    commit id: "v1.0.0-rc1"
    branch feature/patch-engine
    checkout feature/patch-engine
    commit id: "add tier 5 patcher"
    commit id: "unit tests green"
    checkout main
    merge feature/patch-engine id: "merge PR #104"
    branch release/1.0-stable
    checkout release/1.0-stable
    commit id: "tag v1.0.0"
```

## 2. Request for Comments (RFC) Process
Any substantial architectural change (introducing an external C dependency, modifying the SQLite schema, or altering sandbox boundaries) requires an RFC markdown document submitted to `docs/decisions/` and consensus from the Systems Architect.

## 3. Related Documents
- [01-repository-structure.md](01-repository-structure.md)
- [03-ci-cd.md](03-ci-cd.md)
""")

# 01-repository-structure.md
write_file("01-repository-structure.md", r"""# Repository Structure Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Establish the monorepo directory layout, Cargo workspace structure, and unidirectional dependency flow.

---

## 1. Monorepo Workspace Topology

```text
nebuos/
├── Cargo.toml                 # Cargo workspace configuration
├── crates/                    # Core Rust Components
│   ├── nebu-compositor/       # Wayland compositor (Smithay)
│   ├── nebu-shell/            # Native desktop shell (Slint/Iced)
│   ├── nebu-runtime-daemon/   # Background application manager
│   ├── nebu-runtime-core/     # PE parsing & sandbox orchestration
│   ├── nebu-compat-db/        # SQLite compatibility database client
│   ├── nebu-patcher/          # Declarative patch & registry engine
│   ├── nebu-gpu-probe/        # GPU detection & profile allocator
│   └── nebu-cli/              # Command line developer tool
├── data/
│   ├── profiles/              # Declarative JSON compatibility profiles
│   ├── patches/               # Curated .patch & .reg files
│   └── schema.sql             # Master SQLite schema DDL
├── packaging/
│   ├── bootc/                 # Containerfile & OSTree build manifests
│   └── grub/                  # GRUB2 configurations & themes
├── tests/
│   ├── tier0_system/          # Boot & initramfs integration tests
│   ├── tier1_apps/            # Office & AutoCAD automation tests
│   └── tier2_graphics/        # Vulkan / DXVK conformance suites
└── docs/                      # Engineering blueprints and ADRs
```

## 2. Unidirectional Dependency Rule
Circular dependencies between crates are strictly prohibited:
```text
nebu-shell ----------> nebu-runtime-core
     |                       |
     v                       v
nebu-compositor -----> nebu-compat-db ------> SQLite
```

## 3. Related Documents
- [00-development-model.md](00-development-model.md)
- [02-build-system.md](02-build-system.md)
""")

# 02-build-system.md
write_file("02-build-system.md", r"""# Build System Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify reproducible compilation toolchains, containerized build environments, and offline vendoring.

---

## 1. Build Requirements & Toolchains
- **Rust Toolchain:** Stable channel (1.78+ or latest 1.80+), compiled with `opt-level = 3`, `lto = "thin"`, and `codegen-units = 1` for release builds.
- **Hermetic Container Builds:** System images are built inside reproducible Buildah / Podman containers, guaranteeing identical bit-for-bit artifacts regardless of the host build machine.
- **Vendoring:** Production release builds vendor all third-party crates (`cargo vendor`), enabling completely offline builds without network access.

## 2. Related Documents
- [01-repository-structure.md](01-repository-structure.md)
- [03-ci-cd.md](03-ci-cd.md)
""")

# 03-ci-cd.md
write_file("03-ci-cd.md", r"""# CI/CD Pipeline Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Detail continuous integration stages, automated linting, test gating, and cryptographic release signing.

---

## 1. Automated Pipeline Stages

```mermaid
flowchart LR
    LINT["1. Lint & Format (cargo fmt, clippy)"] --> TEST["2. Unit & Integration Tests (cargo test)"]
    TEST --> IMAGE_BUILD["3. OS Image Build (bootc build)"]
    IMAGE_BUILD --> LAB_TEST["4. Compatibility Lab Automated Tests"]
    LAB_TEST --> SIGN["5. Image Signing (Cosign / Sigstore)"]
    SIGN --> DEPLOY["6. Push OCI Container Artifact"]
```

## 2. Gating Criteria
- **Zero Warnings:** `cargo clippy -- -D warnings` must exit cleanly.
- **Security Check:** `cargo audit` must report zero unpatched high-severity CVEs in the dependency tree.

## 3. Related Documents
- [02-build-system.md](02-build-system.md)
- [../testing/00-testing-strategy.md](../testing/00-testing-strategy.md)
""")

# 04-dependency-policy.md
write_file("04-dependency-policy.md", r"""# Third-Party Dependency Policy — NebuOS

**Status:** REVIEW  
**Purpose:** Establish strict criteria for incorporating external libraries, licensing compliance, and security audits.

---

## 1. Dependency Admission Criteria
Before any third-party crate or library is added to the NebuOS tree, it must satisfy:
1. **Permissive Licensing:** Must be licensed under MIT, Apache 2.0, BSD-3, or LGPL 2.1+. Proprietary or GPLv3 code in userspace library crates is rejected.
2. **Maintenance Health:** Active upstream maintenance within the preceding 6 months.
3. **No Unsafe Bloat:** Crates with massive uncurated `unsafe` blocks or bloated transitive dependency graphs are rejected in favor of minimal, audited alternatives.

## 2. Core Dependencies Audit Table

| Dependency | Purpose | License | Rationale for Adoption |
|---|---|---|---|
| `smithay` | Wayland Compositor Primitives | MIT | Pure Rust, eliminates C memory safety vulnerabilities in compositor. |
| `tokio` | Async Event Loop for Daemons | MIT | Battle-tested, high throughput, zero-allocation timers. |
| `rusqlite` | SQLite3 Database Client | MIT | Low overhead, zero-cost abstraction over embedded SQLite3. |
| `zbus` | Pure Rust D-Bus Implementation | MIT | Safe, asynchronous IPC without `libdbus` C dependencies. |
| `bubblewrap` | Sandboxing Primitive | LGPL-2.0+ | Flatpak standard, unprivileged user namespaces. |

## 3. Related Documents
- [00-development-model.md](00-development-model.md)
- [05-coding-guidelines.md](05-coding-guidelines.md)
""")

# 05-coding-guidelines.md
write_file("05-coding-guidelines.md", r"""# Rust Coding Guidelines Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Establish system coding conventions, error handling architectures, unsafe guidelines, and observability patterns.

---

## 1. Core Language Guidelines
1. **No Panics in Daemons:** Background services (`nebu-runtime-daemon`, `nebu-compositor`) must never call `.unwrap()` or `.expect()` in runtime code paths. All errors must be handled via `Result<T, E>`.
2. **Strict Error Handling:** Use `thiserror` for internal module error enums and `anyhow` exclusively for CLI entry points.
3. **Unsafe Encapsulation:** Any `unsafe` block (e.g. DRM ioctls, Wayland FFI) must be wrapped in a safe Rust abstraction accompanied by a `// SAFETY:` rationale comment.
4. **Structured Logging:** All logging must use the `tracing` crate emitting structured JSON events to `systemd-journald`.

## 2. Related Documents
- [04-dependency-policy.md](04-dependency-policy.md)
- [00-development-model.md](00-development-model.md)
""")

print("Development documentation generated successfully.")
