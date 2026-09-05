# Verification & Testing Engineering Skill — NebuOS

## 1. Purpose
Governs the testing pyramid, test environment provisioning, headless QEMU boot harnesses, automated compatibility suites, and release gate certification.

## 2. Scope
Applies to all milestones (P0 through P8).

## 3. Relevant Documentation
- `docs/testing/00-testing-specification.md`: Testing pyramid.
- `docs/testing/02-integration-testing.md`: QEMU test environments.
- `docs/testing/03-compatibility-testing.md`: Windows application test matrix.
- `docs/audit/P0_READY_GATE.md`: P0 12-test acceptance matrix.
- `docs/audit/FEDORA_44_BASELINE_AUDIT.md`: Fedora 44 baseline audit report.

## 4. Allowed Changes
- Authoring automated test scripts in `tests/integration/` and `tests/system/`.
- Adding unit test modules within Rust crates (`#[cfg(test)]`).
- Maintaining regression test manifests.

## 5. Forbidden Changes
- **NO FALSE SUCCESS CLAIMS:** Never assert a test has passed without executing the command and capturing terminal output.
- **NO STATIC ASSUMPTIONS FOR RUNTIME TESTS:** Never declare a test `PASS` based purely on static file inspection if runtime execution is required.
- **NO FABRICATED TEST VALUES:** Never invent initramfs sizes, boot times, or image digests; all values must originate from execution logs.
- **NO DESTRUCTIVE TEST CLEANUP:** Never delete host directories or uncommitted work during test cleanup.

## 6. Architecture Constraints
- Distinguish strictly between:
  - **NOT TESTED:** Code written or modified, but no validation commands executed.
  - **TESTED:** Verification command executed with recorded output.
  - **VERIFY_REQUIRED:** Empirical verification required before release gate sign-off; cannot be resolved via static inspection.
  - **VERIFIED / PASS:** Acceptance criteria mathematically and functionally proven with zero errors.
  - **FAIL:** Acceptance criteria failed; errors captured and analyzed.
  - **ACCEPTED:** Formal sign-off against roadmap exit gates.

## 7. Implementation Guidance
- Author deterministic, reproducible test scripts with explicit timeouts and exit codes.
- Structure QEMU integration tests with serial console logging (`-serial stdio -display none`).
- **Milestone P0 Verification Suite:**
  1. Base image build from `quay.io/fedora/fedora-bootc:44`.
  2. `bootc container lint` exits with code 0.
  3. dracut initramfs embeds core drivers (`nvme`, `ahci`, `virtio_blk`, `virtio_scsi`, `btrfs`).
  4. Btrfs subvolumes (`@`, `@home`, `@var`) mount correctly; `/usr` is read-only.
  5. Headless QEMU UEFI boot to `agetty` login in <= 3.5s with idle RAM < 150 MB RSS.
  6. `systemctl --failed` reports 0 failed units.
  7. NetworkManager acquires DHCP lease.
  8. SELinux permissive mode boot logs show zero critical AVC denials.
  9. Anti-scope scan confirms zero Wayland, Smithay, Slint, Wine, Proton, audio, or GUI packages.

## 8. Verification
- Verify that test runners clean up all child processes, virtual disk images, and tap interfaces upon exit.

## 9. Common Failure Modes
- Flaky tests caused by arbitrary `sleep` calls instead of polling ready states with timeouts.
- Test suites passing falsely because assertions were omitted or errors were swallowed.

## 10. Handoff Requirements
- Include raw execution commands, exit codes, and stdout/stderr summaries in `HANDOFF.md`.
- Explicitly list any unverified items or items marked as `VERIFY_REQUIRED`.
