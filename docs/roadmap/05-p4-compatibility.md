# Phase P4: Compatibility Subsystem Specification — NebuOS

**Status:** APPROVED  
**Phase:** P4  
**Target Duration:** Sprint 12–14  
**Prerequisite:** Phase P3  

---

## 1. Objective
Implement the NebuOS Compatibility Engine and Relational Database. P4 provides automated application identification via PE header fingerprinting and SHA-256 matching, queries the centralized SQLite compatibility database, and applies declarative 9-tier compatibility patches (DLL overrides, registry injections, font aliases, environment variables) automatically at launch.

## 2. Scope (What's IN)
- Rust Crates: `crates/nebu-compat-db`, `crates/nebu-patcher`.
- Relational SQLite database schema (`/usr/share/nebu/compat.db`) in WAL mode.
- Declarative 9-tier patch engine with Kahn's topological DAG dependency resolution.
- Application detection engine: PE32/PE32+ header analysis, Authenticode extraction, installer classification.
- Pre-packaged, certified JSON compatibility profiles for top 50 productivity applications.
- CLI diagnostic and management tool: `/usr/bin/nebu-compat-tool`.

## 3. Anti-Scope (What's NOT IN)
- NO source-code modifications to upstream Wine.
- NO manual registry hacking by end users (all patches declarative).
- NO bypasses for ring-0 anti-cheat or Windows kernel drivers.

## 4. Dependencies
- SQLite 3.42+ with FTS5 search.
- Rust crates: `rusqlite`, `serde_json`, `sha2`, `pelite`.

## 5. Deliverables
- Database: `/usr/share/nebu/compat.db`.
- CLI: `/usr/bin/nebu-compat-tool`.
- Profile Store: `/usr/share/nebu/profiles/*.json`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P4-01 (Profile Query Latency):** Querying application profile by SHA-256 executes in <= 2.0ms (cold) and <= 0.3ms (warm).
2. **EC-P4-02 (Deterministic Patching):** Patch engine applies 15 sequential registry injections and 5 DLL overrides in <= 150ms with atomic rollback support.
3. **EC-P4-03 (Installer Detection):** Classifier correctly distinguishes Inno Setup, NSIS, and MSI installer packages with 100% accuracy on test corpus.
4. **EC-P4-04 (Seed Application Verification):** Certified applications (Microsoft Office 2024, AutoCAD 2024, Notepad++) launch without manual configuration.
5. **EC-P4-05 (Unsupported Feature Rejection):** Applications demanding ring-0 drivers trigger clear, informative error dialogs rather than silent crashes.

## 7. Known Risks & Mitigations
- **Risk:** Upstream application update alters executable hash, causing profile lookup miss.
  - *Mitigation:* Implement fuzzy fallback matching on `ProductName` and `OriginalFilename` metadata in `compat.db`.
