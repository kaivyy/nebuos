#!/usr/bin/env python3
import socket
import sys
import time
import json

sock_path = "/var/run/qemu-server/101.serial0"
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(2.0)
s.connect(sock_path)

def read_all(duration=1.0):
    buf = ""
    start = time.time()
    while time.time() - start < duration:
        try:
            c = s.recv(2048).decode("utf-8", errors="replace")
            if c:
                buf += c
        except socket.timeout:
            pass
    return buf

# Check login
s.sendall(b"\n")
time.sleep(0.5)
out = read_all(0.5)
if "login:" in out:
    s.sendall(b"root\n")
    time.sleep(0.5)
    read_all(0.5)
    s.sendall(b"nebuos\n")
    time.sleep(1.0)
    read_all(0.5)

# Disable terminal echo & pager
s.sendall(b"export PAGER=cat SYSTEMD_PAGER=cat TERM=dumb\n")
time.sleep(0.3)
s.sendall(b"stty -echo\n")
time.sleep(0.5)
read_all(0.5)

def run_cmd(cmd, timeout=5.0):
    s.sendall(f"printf '__START__\\n'; {cmd}; printf '__EN%s__\\n' 'D'\n".encode("utf-8"))
    buf = ""
    start = time.time()
    while time.time() - start < timeout:
        try:
            c = s.recv(2048).decode("utf-8", errors="replace")
            if c:
                buf += c
                if "__END__" in buf:
                    break
        except socket.timeout:
            pass
    if "__START__\r\n" in buf and "__END__" in buf:
        return buf.split("__START__\r\n", 1)[1].split("__END__", 1)[0].strip("\r\n ")
    return buf.strip()

results = {
    "uptime": run_cmd("uptime"),
    "system_state": run_cmd("systemctl is-system-running"),
    "health_gate_status": run_cmd("systemctl status nebu-boot-check.service --no-pager"),
    "health_gate_journal": run_cmd("journalctl -u nebu-boot-check.service --no-pager -n 15"),
    "marker_file_check": run_cmd("ls -la /var/tmp/nebu_persistence.test 2>&1 || true"),
    "var_mount": run_cmd("findmnt /var"),
    "boot_success_marker": run_cmd("cat /run/nebu-boot-success 2>&1 || true"),
    "boot_state_file": run_cmd("cat /var/log/nebu-boot-state 2>&1 || true")
}

s.sendall(b"stty echo\n")
s.close()

with open("/tmp/vm101_reboot_output.json", "w") as f:
    json.dump(results, f, indent=2)

print("POST REBOOT DATA CAPTURED:")
print(json.dumps(results, indent=2))
