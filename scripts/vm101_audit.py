#!/usr/bin/env python3
import socket
import sys
import time
import json

sock_path = "/var/run/qemu-server/101.serial0"

def get_socket():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(2.0)
    s.connect(sock_path)
    return s

def read_all(s, duration=1.0):
    buf = ""
    start = time.time()
    while time.time() - start < duration:
        try:
            chunk = s.recv(2048).decode("utf-8", errors="replace")
            if chunk:
                buf += chunk
        except socket.timeout:
            pass
    return buf

def ensure_shell(s):
    # Send Ctrl-C and q to clear any pager
    s.sendall(b"\x03\nq\n\n")
    time.sleep(0.5)
    out = read_all(s, 1.0)
    if "#" in out:
        return True
    if "login:" in out:
        s.sendall(b"root\n")
        time.sleep(0.5)
        read_all(s, 0.5)
        s.sendall(b"nebuos\n")
        time.sleep(1.0)
        out = read_all(s, 1.0)
        return "#" in out
    return False

s = get_socket()
if not ensure_shell(s):
    print("ERROR: Failed to establish root shell via serial socket")
    sys.exit(1)

# Disable pager, terminal echo, bracketed paste
s.sendall(b"export PAGER=cat SYSTEMD_PAGER=cat TERM=dumb\n")
time.sleep(0.3)
s.sendall(b"stty -echo\n")
time.sleep(0.5)
read_all(s, 0.5)

def run_cmd(s, cmd, timeout=12.0):
    start_tag = "__NB_START__"
    full_cmd = f"printf '{start_tag}\\n'; {cmd}; printf '__NB_EN%s__\\n' 'D'\n"
    s.sendall(full_cmd.encode("utf-8"))
    buf = ""
    start = time.time()
    while time.time() - start < timeout:
        try:
            chunk = s.recv(2048).decode("utf-8", errors="replace")
            if chunk:
                buf += chunk
                if "__NB_END__" in buf:
                    break
        except socket.timeout:
            pass
    
    if start_tag in buf and "__NB_END__" in buf:
        content = buf.split(start_tag, 1)[1].split("__NB_END__", 1)[0]
        return content.strip("\r\n ")
    return buf.strip()

commands = [
    ("uname_a", "uname -a"),
    ("os_release", "cat /etc/os-release"),
    ("systemctl_version", "systemctl --version | head -n 2"),
    ("system_state", "systemctl is-system-running"),
    ("failed_units", "systemctl list-units --state=failed --no-pager"),
    ("boot_check_service", "systemctl status nebu-boot-check.service --no-pager"),
    ("boot_check_journal", "journalctl -u nebu-boot-check.service --no-pager -n 30"),
    ("boot_check_done", "cat /run/nebu-boot-check.done 2>/dev/null || echo NOT_FOUND"),
    ("default_target", "systemctl get-default"),
    ("mounts", "findmnt -A"),
    ("df", "df -hT"),
    ("btrfs_subvols", "btrfs subvolume list / 2>&1 || echo NO_SUBVOLS"),
    ("btrfs_show", "btrfs filesystem show / 2>&1"),
    ("usr_ro_test", "touch /usr/nebu_ro_test 2>&1 || true"),
    ("var_mount", "findmnt /var"),
    ("selinux_status", "sestatus 2>&1 || getenforce"),
    ("selinux_config", "cat /etc/selinux/config"),
    ("bootc_version", "bootc --version 2>&1 || echo NOT_FOUND"),
    ("bootc_status", "bootc status 2>&1 || echo FAILED"),
    ("network_status", "systemctl is-active NetworkManager.service && ip -brief addr"),
    ("scope_forbidden_pkgs", "rpm -qa | grep -iE 'wayland|smithay|slint|plymouth|wine|proton|dxvk' || echo NONE_FOUND"),
    ("ps_aux", "ps aux --sort=pid"),
    ("systemd_analyze", "systemd-analyze"),
    ("systemd_blame", "systemd-analyze blame | head -n 20"),
    ("systemd_crit_chain", "systemd-analyze critical-chain")
]

results = {}
for key, cmd in commands:
    print(f"Running {key}...", flush=True)
    res = run_cmd(s, cmd)
    results[key] = res
    print(f" -> {key} completed ({len(res)} bytes)", flush=True)

s.sendall(b"stty echo\n")
s.close()

with open("/tmp/vm101_audit_output.json", "w") as f:
    json.dump(results, f, indent=2)

print("AUDIT SUCCESS! Output saved to /tmp/vm101_audit_output.json", flush=True)
