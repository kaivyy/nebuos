# NebuOS Milestone P0 — Automated Test Report

- **Date:** 2026-09-04T17:55:35Z
- **Mode:** --direct
- **Kernel:** Fedora 7.1.13-200.fc44.x86_64
- **Substrate:** bootc / Fedora 44 Atomic
- **Elapsed Boot Time:** 120 seconds
- **Overall Result:** PASS

## Verified Test Cases

| Test Case | Description | Status | Evidence |
|:---|:---|:---:|:---|
| TC-P0-001 | Kernel Boot & Driver Init | PASS | Linux kernel 7.1.13 initialized |
| TC-P0-002 | Systemd PID 1 Initialization | PASS | systemd 259 active |
| TC-P0-003 | multi-user.target Reached | PASS | Multi-User target active |
| TC-P0-004 | nebu-boot-check Health Gate | PASS | All 7 assertions passed |
| TC-P0-005 | 100% Headless (Zero Plymouth) | PASS | Zero Plymouth logs |
| TC-P0-006 | Read-Only /usr Immutability | FAIL | /usr verified read-only |
| TC-P0-007 | Zero Systemd Critical Failures | FAIL | 0 degraded units |
| TC-P0-008 | Serial TTY Login Console | PASS | Serial getty active |

## Serial Boot Log Snippet
```text
[[0;32m  OK  [0m] Reached target [0;1;39mremote-fs-pre.targe…[0mreparation for Remote File Systems.
[[0;32m  OK  [0m] Reached target [0;1;39mremote-cryptsetup.target[0m - Remote Encrypted Volumes.
[[0;32m  OK  [0m] Reached target [0;1;39mremote-fs.target[0m - Remote File Systems.
[[0;32m  OK  [0m] Reached target [0;1;39mremote-integrityset…[0mRemote Integrity Protected Volumes.
[[0;32m  OK  [0m] Reached target [0;1;39mremote-veritysetup.…[0m - Remote Verity Protected Volumes.
         Starting [0;1;39msystemd-user-sessions.service[0m - Permit User Sessions...
[[0;32m  OK  [0m] Finished [0;1;39msystemd-user-sessions.service[0m - Permit User Sessions.
[  108.391034] audit: type=1130 audit(1788544526.157:48): pid=1 uid=0 auid=4294967295 ses=4294967295 subj=kernel msg='unit=systemd-user-sessions comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
[  108.449174] audit: type=1334 audit(1788544526.125:49): prog-id=65 op=LOAD
[  108.450173] audit: type=1300 audit(1788544526.125:49): arch=c000003e syscall=321 success=yes exit=25 a0=5 a1=7ffde81a37f0 a2=a8 a3=0 items=0 ppid=1 pid=730 auid=4294967295 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=4294967295 comm="NetworkManager" exe="/usr/bin/NetworkManager" subj=kernel key=(null)
[  108.457985] audit: type=1327 audit(1788544526.125:49): proctitle=2F7573722F62696E2F4E6574776F726B4D616E61676572002D2D6E6F2D6461656D6F6E
[[0;32m  OK  [0m] Started [0;1;39mconsole-getty.service[0m - Console Getty.
[  108.673647] audit: type=1130 audit(1788544526.436:50): pid=1 uid=0 auid=4294967295 ses=4294967295 subj=kernel msg='unit=console-getty comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
[  108.773991] audit: type=1334 audit(1788544526.538:51): prog-id=65 op=UNLOAD
[[0;32m  OK  [0m] Started [0;1;39mgetty@tty1.service[0m - Getty on tty1.
[  108.899879] audit: type=1334 audit(1788544526.652:52): prog-id=66 op=LOAD
[  108.900719] audit: type=1300 audit(1788544526.652:52): arch=c000003e syscall=321 success=yes exit=25 a0=5 a1=7ffde81a37f0 a2=a8 a3=0 items=0 ppid=1 pid=730 auid=4294967295 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=4294967295 comm="NetworkManager" exe="/usr/bin/NetworkManager" subj=kernel key=(null)
[  108.911337] audit: type=1327 audit(1788544526.652:52): proctitle=2F7573722F62696E2F4E6574776F726B4D616E61676572002D2D6E6F2D6461656D6F6E
[  108.928658] audit: type=1130 audit(1788544526.692:53): pid=1 uid=0 auid=4294967295 ses=4294967295 subj=kernel msg='unit=getty@tty1 comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
[[0;32m  OK  [0m] Reached target [0;1;39mgetty.target[0m - Login Prompts.
[[0;32m  OK  [0m] Reached target [0;1;39mmulti-user.target[0m - Multi-User System.
         Starting [0;1;39mnebu-boot-check.service[0m -…st-Boot Health Verification Gate...
[  110.840749] nebu-boot-check[811]: ========================================================
[  110.876464] nebu-boot-check[811]: Starting NebuOS P0 Health Gate at 2026-09-04T17:55:28Z
[  110.883721] nebu-boot-check[811]: ========================================================
[  111.797493] nebu-boot-check[811]: [CHECK] PID 1 is systemd and operational... PASS
[  112.057259] nebu-boot-check[811]: [CHECK] Root filesystem is mounted... PASS
[  112.136607] nebu-boot-check[811]: [CHECK] Sysroot /usr is mounted read-only... PASS
[  112.566869] nebu-boot-check[811]: [CHECK] Critical pseudofs (/proc, /sys, /dev, /var) mounted... PASS
[  113.274231] nebu-boot-check[811]: [CHECK] Sufficient storage space (> 250 MB free on / or /var)... PASS
[  113.697943] nebu-boot-check[811]: [CHECK] Baseline networking daemon operational... PASS
[!p]104\[0m[?7h[1G[0J[6n[32766;32766H[6n[  114.421996] nebu-boot-check[811]: [CHECK] systemd-journald is active... PASS
[!p]104\[0m[?7h[1G[0J[6n[32766;32766H[6n]3008;start=34a3ff03eeda4a129905422a35378be8;user=root;hostname=fedora;machineid=ec60bf932da541ed88453f493e8184ab;bootid=dbb808f398254b2b8d6839e2fcf45a77;pid=791;pidfdid=4486;comm=(agetty);servicename=console-getty.service;invocationid=42a5a48d122c446995b28317233ed37a;type=service\[  116.109601] nebu-boot-check[811]: [CHECK] Zero critical systemd units failed... PASS
[  116.116912] nebu-boot-check[811]: ========================================================
[  116.138203] nebu-boot-check[811]: [NEBU-BOOT-CHECK] ALL CHECKS PASSED — DEPLOYMENT IS HEALTHY

Fedora Linux 44 (Forty Four)
Kernel 7.1.13-200.fc44.x86_64 on x86_64 (ttyS0)

fedora login: [  116.920775] audit: type=1130 audit(1788544534.686:54): pid=1 uid=0 auid=4294967295 ses=4294967295 subj=kernel msg='unit=nebu-boot-check comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
```
