# Security Architecture & Containment Skill — NebuOS

## 1. Purpose
Governs the defense-in-depth security architecture: SELinux policies, Bubblewrap unprivileged namespaces, seccomp BPF syscall filters, and cgroups resource limits.

## 2. Scope
Applies across all milestones (P0 through P8).

## 3. Relevant Documentation
- `docs/specification/04-security-specification.md`: Security architecture.
- `docs/decisions/ADR-0010-bubblewrap-security-isolation.md`: Bubblewrap isolation.
- `docs/audit/P0_READY_GATE.md`: P0 SELinux permissive mandate.

## 4. Allowed Changes
- Authoring Bubblewrap arguments (`--ro-bind`, `--unshare-net`, `--tmpfs`).
- Writing BPF seccomp filter definitions.
- Authoring custom SELinux type enforcement files (`nebu-sandbox.te`).

## 5. Forbidden Changes
- **NO HARDCODED SECRETS:** Never commit or hardcode credentials, private tokens, signing keys, or passwords.
- **NO UNSAFE SHELL EXECUTION:** Never invoke raw shell strings (`sh -c`, `bash -c`, or unescaped subprocess shells) with untrusted parameters. Use structured argument vectors (`Command::new`).
- **NO PERMANENT SECURITY DISABLEMENT:** Never disable SELinux or seccomp globally to "make something work" without documenting an explicit security exception.
- **NO SETUID ROOT BINARIES:** All containerization must use unprivileged user namespaces (`bwrap`).
- **NO ARBITRARY FILESYSTEM ACCESS:** Services must operate with minimum filesystem visibility.

## 6. Architecture Constraints
- Multi-tier containment model: cgroups v2 -> Bubblewrap -> seccomp-bpf -> SELinux.
- SELinux Policy: `permissive` during P0–P4; `enforcing` activated in P5 with `nebu-sandbox.te`.
- Root filesystem isolation: `/usr` is strictly read-only; `/` is never exposed to Windows apps.
- Least Privilege: Services run as unprivileged dedicated users/groups; avoid running daemons as root unless required for kernel/mount operations.
- Application Security & Trust Tiers (P6): Distinguish Publisher Trust, Package Integrity, Runtime Sandbox, and Compatibility. Never assume third-party packages are safe without verification. Mandatory cryptographic signature and SHA-256 checksum checks prior to staging.

## 7. Implementation Guidance
- Ensure offline applications have their network namespace severed via `bwrap --unshare-net`.
- Block dangerous syscalls via seccomp: `ptrace`, `kexec_load`, `sys_rawio`, `reboot`.
- Validate all paths: Enforce canonicalization and reject path traversal (`..`, symlink escapes) for all runtime prefix and file access routines.
- Secure Defaults: Always fail closed; if security validation cannot verify safety, deny access by default.
- Permission Transparency: Require explicit pre-installation user authorization for sensitive entitlements (camera, microphone, unconfined home directory, raw devices). Support remote package revocation and quarantine.

## 8. Verification
- Verify that a compromised binary inside `bwrap` cannot read files in `~/.ssh` or `/var/log`.
- Inspect `/var/log/audit/audit.log` for unexpected SELinux avc denials.

## 9. Common Failure Modes
- Incompatible seccomp filters breaking Wine's Windows NT exception handling.
- Spurious SELinux avc denials blocking `bwrap` pseudo-terminal allocation.

## 10. Handoff Requirements
- Document active SELinux mode, audit log status, and containment test results in `HANDOFF.md`.
