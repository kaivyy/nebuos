# Phase P3: NebuRuntime Specification — NebuOS

**Status:** APPROVED  
**Phase:** P3  
**Target Duration:** Sprint 9–11  
**Prerequisite:** Phase P0, P1, P2  

---

## 1. Objective
Implement `nebu-runtime-daemon` and the Windows PE binary execution pipeline. P3 establishes kernel `binfmt_misc` interception for MZ executables, Bubblewrap sandbox jailing, per-application isolated Wine prefix provisioning via Btrfs reflink, process supervision, and clean lifecycle management.

## 2. Scope (What's IN)
- Rust Crates: `crates/nebu-runtime-daemon`, `crates/nebu-runtime-core`, `crates/nebu-prefix-manager`.
- Kernel `binfmt_misc` registration redirecting `.exe` execution to `/usr/bin/nebu-launch`.
- PE header inspection (zero-copy parsing via `pelite`).
- Btrfs reflink prefix provisioning (< 200ms) from `/usr/share/nebu/prefix-template/`.
- Unprivileged Bubblewrap (`bwrap`) containment with dropped capabilities and seccomp BPF filters.
- Wine process supervision under systemd user transient scopes (`app-nebu-<app_id>.scope`).
- D-Bus Service `org.nebu.Runtime1`.

## 3. Anti-Scope (What's NOT IN)
- NO automated compatibility patching engine (governed by P4).
- NO DXVK/VKD3D Vulkan translation tuning (governed by P5).
- NO graphical software center or installer wizard (governed by P6).
- NO Windows virtual machine fallback (strictly prohibited).

## 4. Dependencies
- Upstream Wine binaries in `/usr/lib/nebu/runtimes/wine-stable/`.
- `bubblewrap` >= 0.8.0.
- Btrfs filesystem with reflink (`FICLONE`) support.
- Rust crates: `pelite`, `zbus`, `nix`, `tokio`.

## 5. Deliverables
- Daemons & CLIs: `/usr/libexec/nebu/nebu-runtime-daemon`, `/usr/bin/nebu-launch`, `/usr/bin/nebu-path`.
- Systemd User Unit: `/usr/lib/systemd/user/nebu-runtime-daemon.service`.
- Prefix Template: `/usr/share/nebu/prefix-template/`.

## 6. Exit Criteria (Testable Conditions)
1. **EC-P3-01 (Transparent PE Interception):** Double-clicking or running `./notepad++.exe` in terminal routes to `nebu-launch` and executes Notepad++ cleanly.
2. **EC-P3-02 (Reflink Provisioning Latency):** Creating a fresh per-app prefix at `~/.nebu/apps/<app_id>/` takes <= 200ms and consumes 0 bytes of initial unique disk space.
3. **EC-P3-03 (Sandbox Isolation Gate):** Test application attempting to read `/root` or `~/.ssh` is blocked with `Permission denied`.
4. **EC-P3-04 (Clean Process Termination):** Closing main application window cleanly flushes Wine registry hives and terminates all wineserver child threads within 3.0s (zero orphan processes).
5. **EC-P3-05 (Daemon Memory Budget):** `nebu-runtime-daemon` idle memory <= 15 MB RSS.

## 7. Known Risks & Mitigations
- **Risk:** Wineserver socket file locking contention during rapid sequential launches.
  - *Mitigation:* Implement deterministic per-prefix `flock` and Unix domain socket paths partitioned under `/run/user/1000/nebu/`.
