# Phase P7: Testing Subsystem Specification — NebuOS

**Status:** APPROVED  
**Phase:** P7  
**Target Duration:** Sprint 21–23  
**Prerequisite:** Phase P0–P6  

---

## 1. Objective
Establish the automated Compatibility Test Lab, regression harness, and hardware validation matrix. P7 automates the continuous testing of the top 50 certified Windows applications and native Linux packages across three physical hardware tiers, executing the 11-stage compatibility invariant unattended.

## 2. Scope (What's IN)
- Rust Test Runner: `crates/nebu-test-harness`, `/usr/bin/nebu-test-runner`.
- 11-stage compatibility verification invariant automation (`INSTALL -> LAUNCH -> ... -> REOPEN`).
- Headless Wayland frame capture and perceptual image hashing (SSIM >= 0.98).
- Virtual input injection via `ydotool`.
- Physical Hardware Test Matrix:
  - Tier 0: Low-End (Intel Celeron, 4GB RAM, Intel UHD iGPU).
  - Tier 1: Mid-Tier (AMD Ryzen 5, 16GB RAM, Radeon iGPU).
  - Tier 2: High-End (Intel Core i7 / AMD Ryzen 7, 32GB RAM, NVIDIA RTX dGPU).
- Continuous CI regression reporting dashboard.

## 3. Anti-Scope (What's NOT IN)
- NO manual QA test passes for standard builds (100% automated).
- NO testing of unsupported applications requiring kernel drivers.

## 4. Dependencies
- Compatibility Lab physical test farm.
- `ydotool`, OpenCV / perceptual hashing libraries.
- Headless virtual display drivers (`vkms`).

## 5. Deliverables
- Test Harness: `/usr/bin/nebu-test-runner`.
- Automated Test Scripts: `tests/compat_suite/*.json`.
- Test Reporting Dashboard: `https://qa.nebuos.org`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P7-01 (Automated Lab Throughput):** Test harness executes complete 50-application test matrix unattended in <= 3.0 hours across all 3 hardware tiers.
2. **EC-P7-02 (Compatibility Pass Rate):** Tier 1 certified applications achieve 100% pass rate across all 11 invariant stages.
3. **EC-P7-03 (Flakiness Rate):** Re-running identical test runs produces < 0.5% variance in test results.
4. **EC-P7-04 (Memory Leak Detection):** 48-hour continuous loop execution reveals zero cumulative memory growth in core daemons.
5. **EC-P7-05 (Automated Regression Gating):** Intentionally broken compatibility profile is caught and rejected by gating pipeline.

## 7. Known Risks & Mitigations
- **Risk:** Minor UI popups in Windows applications cause synthetic input tests to desynchronize.
  - *Mitigation:* Implement visual template matching before dispatching keypresses and clicks.
