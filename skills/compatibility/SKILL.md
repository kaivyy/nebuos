# Compatibility Platform & Database Skill — NebuOS

## 1. Purpose
Governs the SQLite compatibility database, application binary fingerprinting, declarative patch engine DSL, and compatibility certification tiers.

## 2. Scope
Applies to Milestone P4 (Compatibility Engine) and Milestone P7 (Compatibility Lab).

## 3. Relevant Documentation
- `docs/roadmap/05-p4-compatibility-engine.md`: Milestone P4 roadmap.
- `docs/compatibility/00-compatibility-specification.md`: Compatibility platform.
- `docs/compatibility/01-database-schema.md`: SQLite schema and queries.
- `docs/compatibility/02-compatibility-profile.md`: Profile JSON schema.
- `docs/compatibility/03-patch-engine.md`: 9-tier patch hierarchy.

## 4. Allowed Changes
- Creating SQLite database migrations and schema files.
- Implementing PE header parser and SHA-256 fingerprinting algorithms.
- Authoring declarative application compatibility profiles (`profiles/*.json`).

## 5. Forbidden Changes
- **NO UNSUPPORTED CLAIMS:** Never certify an application as compatible without executing the full 12-point compatibility lifecycle test.
- **NO PROPRIETARY ASSETS:** Never embed proprietary Microsoft DLLs or fonts in compatibility profiles.

## 6. Architecture Constraints
- Application Certification Tiers: Platinum, Gold, Silver, Bronze, Broken.
- Verification Lifecycle: Install -> Launch -> Open -> Edit -> Save -> Export -> Print -> GPU -> Plugin -> Stress -> Close -> Reopen.

## 7. Implementation Guidance
- Fingerprint executables by hashing the `.text` section and matching PE header fields (`Subsystem`, `Characteristics`, `TimeDateStamp`) to prevent false matches across versions.
- Execute patches in declarative order: DLL overrides -> Registry tweaks -> Environment variables.

## 8. Verification
- Run automated SQLite schema migration tests against seed databases.
- Test PE parser against known benign Win32/x64 binaries (7-Zip, Notepad++ installers).

## 9. Common Failure Modes
- Profile conflicts when multiple patch recipes modify the same registry key.
- False positive binary identification due to generic installer wrappers.

## 10. Handoff Requirements
- Report total registered application profiles and schema migration test logs in `HANDOFF.md`.
