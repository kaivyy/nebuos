#!/usr/bin/env python3
import socket
import sys
import time
import json

sock_path = "/var/run/qemu-server/101.serial0"
log_path = "/tmp/vm101-reboot.log"

# Step 1: Connect to guest and write marker
print("[1/5] Connecting to VM 101 to set pre-reboot marker...", flush=True)
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(2.0)
s.connect(sock_path)

def read_all(sock, duration=1.0):
    buf = ""
    start = time.time()
    while time.time() - start < duration:
        try:
            c = sock.recv(2048).decode("utf-8", errors="replace")
            if c: buf += c
        except: pass
    return buf

s.sendall(b"\x03\nq\n\n")
time.sleep(0.5)
read_all(s, 0.5)

# Write pre-reboot marker to /var/tmp
s.sendall(b"echo 'NebuOS_P0_Persistence_Test' > /var/tmp/nebu_persistence.test && ls -l /var/tmp/nebu_persistence.test\n")
time.sleep(0.5)
marker_out = read_all(s, 0.5)
print(f"Pre-reboot marker set: {marker_out.strip()}", flush=True)

# Issue reboot
print("[2/5] Issuing systemctl reboot...", flush=True)
reboot_start_time = time.time()
s.sendall(b"systemctl reboot\n")
time.sleep(0.5)
s.close()

# Step 2: Stream console during reboot to /tmp/vm101-reboot.log
print("[3/5] Monitoring reboot sequence over serial console...", flush=True)
reboot_log = open(log_path, "w")
reconnected = False
reboot_conn_attempts = 0

while time.time() - reboot_start_time < 60.0:
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(sock_path)
        reconnected = True
        break
    except Exception:
        time.sleep(0.2)

if not reconnected:
    print("ERROR: Could not reconnect to serial socket after reboot", flush=True)
    sys.exit(1)

print("Reconnected to serial socket. Capturing boot transcript...", flush=True)
boot_complete = False
transcript = ""

while time.time() - reboot_start_time < 90.0:
    try:
        chunk = s.recv(2048).decode("utf-8", errors="replace")
        if chunk:
            reboot_log.write(chunk)
            reboot_log.flush()
            transcript += chunk
            if "ALL CHECKS PASSED" in transcript and "login:" in transcript:
                boot_complete = True
                break
    except socket.timeout:
        pass
    except Exception as e:
        time.sleep(0.2)

reboot_duration = time.time() - reboot_start_time
reboot_log.close()

if boot_complete:
    print(f"[4/5] VM 101 Reboot Succeeded in {reboot_duration:.2f}s! Post-boot health gate passed.", flush=True)
else:
    print(f"WARNING: Login prompt or health gate not detected within {reboot_duration:.2f}s", flush=True)

# Step 3: Check post-reboot state and marker persistence
print("[5/5] Checking post-reboot health and /var persistence semantics...", flush=True)
time.sleep(1.0)
s.sendall(b"\n")
time.sleep(0.5)
out = read_all(s, 0.5)
if "login:" in out:
    s.sendall(b"root\n")
    time.sleep(0.5)
    read_all(s, 0.5)
    s.sendall(b"nebuos\n")
    time.sleep(1.0)
    read_all(s, 0.5)

s.sendall(b"export PAGER=cat SYSTEMD_PAGER=cat TERM=dumb; stty -echo\n")
time.sleep(0.5)
read_all(s, 0.5)

def run_cmd(sock, cmd):
    sock.sendall(f"printf '__START__\\n'; {cmd}; printf '__EN%s__\\n' 'D'\n".encode("utf-8"))
    buf = ""
    start = time.time()
    while time.time() - start < 5.0:
        try:
            c = sock.recv(2048).decode("utf-8", errors="replace")
            if c:
                buf += c
                if "__END__" in buf: break
        except: pass
    if "__START__\r\n" in buf and "__END__" in buf:
        return buf.split("__START__\r\n", 1)[1].split("__END__", 1)[0].strip("\r\n ")
    return buf.strip()

post_reboot_results = {
    "reboot_duration_seconds": round(reboot_duration, 2),
    "uptime": run_cmd(s, "uptime"),
    "system_state": run_cmd(s, "systemctl is-system-running"),
    "health_gate_journal": run_cmd(s, "journalctl -u nebu-boot-check.service --no-pager -n 15"),
    "marker_check": run_cmd(s, "ls -l /var/tmp/nebu_persistence.test 2>&1 || true"),
    "var_overlay_mount": run_cmd(s, "findmnt /var"),
    "success_marker": run_cmd(s, "cat /run/nebu-boot-success 2>&1 || true"),
    "boot_state_file": run_cmd(s, "cat /var/log/nebu-boot-state 2>&1 || true")
}

s.sendall(b"stty echo\n")
s.close()

with open("/tmp/vm101_reboot_output.json", "w") as f:
    json.dump(post_reboot_results, f, indent=2)

print("REBOOT VERIFICATION COMPLETE! Saved to /tmp/vm101_reboot_output.json", flush=True)
