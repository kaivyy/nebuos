# Documentation Synchronization & Drift Control Skill — NebuOS

## 1. Purpose
Governs documentation integrity, bidirectional traceability between specs and code, cross-referencing consistency, and documentation drift detection.

## 2. Scope
Applies across all 111+ documentation files in `docs/` and root registers.

## 3. Relevant Documentation
- `docs/INDEX.md`: Master documentation index.
- `docs/TRACEABILITY.md`: Requirements traceability matrix.
- `docs/audit/DOCUMENTATION_AUDIT_REPORT.md`: Comprehensive documentation audit.

## 4. Allowed Changes
- Updating technical specifications when system behavior or APIs change.
- Refreshing cross-reference links in `docs/INDEX.md` and `docs/TRACEABILITY.md`.
- Adding deprecation notices to legacy blueprint files in `docs/architecture/`.

## 5. Forbidden Changes
- **NO SILENT DRIFT:** Never change implementation behavior without updating corresponding specifications.
- **NO REDUNDANT SOURCES OF TRUTH:** Do not create duplicate files that compete with existing specifications.

## 6. Architecture Constraints
- Maintain the documentation hierarchy: `PRD.md` > `ADRs` > `Specifications` > `Roadmap` > `Implementation`.
- Ensure all 103 PRD requirements remain mapped in `docs/TRACEABILITY.md`.

## 7. Implementation Guidance
- Detect documentation drift whenever a PR modifies code without touching `docs/`.
- Ensure GitHub Markdown relative links use correct relative paths from their directory.

## 8. Verification
- Run static link validation to guarantee 0 broken relative links across `docs/`.
- Verify that every ADR in `docs/decisions/` is indexed in `docs/INDEX.md`.

## 9. Common Failure Modes
- Updating a file path during refactoring but leaving broken links in `docs/INDEX.md`.
- Describing speculative, unimplemented features as "current capabilities" in docs.

## 10. Handoff Requirements
- Report total documentation files modified and link verification results in `HANDOFF.md`.
