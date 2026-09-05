# Phase P8: Production Validation Specification — NebuOS

**Status:** APPROVED  
**Phase:** P8  
**Target Duration:** Sprint 24–26  
**Prerequisite:** Phase P0–P7  

---

## 1. Objective
Final production hardening, low-end 4GB RAM budget certification, security audit, atomic update/rollback verification, and release engineering for General Availability (GA) of NebuOS 1.0.

## 2. Scope (What's IN)
- Production binary hardening: Link-Time Optimization (LTO), CFI, stack-clash protection, symbol stripping.
- SELinux enforcing policy validation across all userland daemons and containers.
- Low-End 4GB RAM Mode tuning: zRAM (zstd), `systemd-oomd` PSI thresholds, cache trimming.
- Comprehensive third-party security penetration audit.
- Full atomic OS image upgrade and automated GRUB rollback verification.
- Production ISO installer generation (`nebuos-1.0.0-x86_64.iso`).
- GA Release Certification sign-off.

## 3. Anti-Scope (What's NOT IN)
- NO new architectural features or unproven dependencies added during P8.
- NO post-1.0 experimental features (deferred to Future Phases).

## 4. Dependencies
- All prior phases (P0 through P7).
- Independent security audit firm.
- Cosign production release signing keys.

## 5. Deliverables
- Bootable ISO: `nebuos-1.0.0-x86_64.iso`.
- Signed Container Image: `quay.io/nebuos/base:1.0.0`.
- Release Documentation, User Manual, and Release Notes.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P8-01 (Idle RAM Constraint):** System boots on a physical 4GB RAM machine to an idle graphical desktop with <= 680 MB total RAM consumption (well under the 800 MB limit).
2. **EC-P8-02 (Cold Boot SLA):** Cold boot from UEFI to interactive desktop <= 6.5s on SATA SSD, <= 4.0s on NVMe.
3. **EC-P8-03 (Zero Critical CVEs):** Trivy / Grype vulnerability scan of production base image reports 0 Critical and 0 High vulnerabilities.
4. **EC-P8-04 (Atomic Rollback Validation):** Hard reboot during image upgrade recovers previous working deployment in <= 12s with zero data corruption in `/home`.
5. **EC-P8-05 (Formal Sign-off):** Principal Systems Architect, Security Lead, and Product Lead sign off on GA release certification.

## 7. Known Risks & Mitigations
- **Risk:** Edge-case hardware quirks discovered during broad beta distribution.
  - *Mitigation:* Rapid Hotfix channel infrastructure enables shipping targeted kernel/profile fixes in < 24 hours.
