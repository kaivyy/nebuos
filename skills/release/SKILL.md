# Release Engineering & Update Lifecycle Skill — NebuOS

## 1. Purpose
Governs container image packaging, ostree artifact signing, transactional update distribution (`bootc update`), automatic rollback mechanisms, and release gates.

## 2. Scope
Applies to Milestone P0 (Base image provisioning) and Milestone P8 (Production Release).

## 3. Relevant Documentation
- `docs/updates/00-update-specification.md`: Master update specification.
- `docs/updates/01-image-build.md`: Containerfile layer optimization.
- `docs/updates/02-release-channels.md`: Release channels and versioning taxonomy.
- `docs/updates/04-rollback-recovery.md`: Rollback procedures and boot counter.
- `docs/development/06-release-engineering.md`: Release engineering workflow.
- `docs/decisions/ADR-0002-fedora-base.md`: Fedora Linux 44 Base OS.
- `docs/decisions/ADR-0011-os-image-updates-and-rollback.md`: OS updates and rollback.
- `docs/decisions/ADR-0012-application-distribution-and-marketplace.md`: Application distribution and marketplace.
- `docs/decisions/ADR-0014-boot-experience-and-graphical-handoff.md`: Boot experience and graphical handoff.

## 4. Allowed Changes
- Configuring OCI container registry push/pull manifests.
- Authoring update verification scripts.
- Managing release notes and compatibility matrix changelogs.

## 5. Forbidden Changes
- **NO MUTABLE UPDATES:** Never perform live in-place package upgrades on the root filesystem (`dnf upgrade` on running system is strictly forbidden).
- **NO DATA LOSS ON ROLLBACK:** Rollback operations must NEVER delete or alter `/var` or `/var/home`.
- **NO UNVERSIONED PRODUCTION TAGS:** Never publish or reference `:latest` as a production release identity.
- **NO CONFLATING UPDATE LIFECYCLES:** Never couple application updates or compatibility DB updates into the base OS `bootc` update pipeline.

## 6. Architecture Constraints
- Upstream Base: Fedora Linux 44 (`quay.io/fedora/fedora-bootc:44`).
- Immutable Digest Pinning: Production and release builds must pin the exact image SHA-256 digest (`quay.io/fedora/fedora-bootc:44@sha256:...`).
- Updates are 100% container-native via native `bootc` staging commands (following the actual bootc 1.x CLI in Fedora 44, e.g. `bootc upgrade` staging flow) executing in the background without disrupting active user sessions or creating custom update engines.
- Rollbacks are instantaneous via selecting the previous ostree deployment entry in GRUB BLS.
- Automatic recovery triggers if 3 consecutive boot attempts fail to pass post-boot deterministic health checks (`boot_counter <= 0`). In P0, health check verifies PID 1, root/critical mounts, network, and 0 failed units headlessly.
- Recovery/Rollback Boot Mode (ADR-0014): Rollback boot executes silently under silent kernel parameters; once the desktop is reached, NebuShell presents a non-modal recovery notification card to inform the user.
- **Four-Way Update Separation:** Strictly isolate OS updates (`bootc`), application updates (Flatpak / App Manager), compatibility database updates (SQLite delta), and firmware (`fwupd`). Desktop app updates must never require an OS reboot.

## 7. Implementation Guidance
- Ensure release container images are cryptographically signed using Sigstore/`cosign` with Ed25519 root keys.
- Verify that image layer caching minimizes bandwidth consumption during incremental OTA updates.
- Adhere to the "No Surprise Reboot" policy; updates activate only on user-initiated reboot.

## 8. Verification
- Simulate a failed update in QEMU and assert that GRUB automatically rolls back to the prior deployment.
- Verify that `/var/home` user documents remain 100% intact across updates and rollbacks.
- Confirm container image manifest has valid Cosign signature before deployment.

## 9. Common Failure Modes
- Update modifying `/etc` configuration files without preserving user customizations via 3-way merge.
- Missing `grubenv` boot counter update, preventing automated rollback on boot hangs.

## 10. Handoff Requirements
- Record image digest hashes, update test logs, and rollback verification evidence in `HANDOFF.md`.
