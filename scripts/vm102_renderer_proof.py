#!/usr/bin/env python3
import socket
import sys
import time
import json

# Unbuffered stdout
sys.stdout.reconfigure(line_buffering=True)

sock_path = "/var/run/qemu-server/102.serial0"

def get_socket():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(2.0)
    for attempt in range(20):
        try:
            s.connect(sock_path)
            return s
        except Exception as e:
            time.sleep(1.0)
    print("ERROR: Failed to connect to VM 102 serial socket")
    sys.exit(1)

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
    # Try multiple times to obtain root prompt
    for i in range(25):
        s.sendall(b"\n")
        time.sleep(0.5)
        out = read_all(s, 1.0)
        if "#" in out or "root@" in out:
            return True
        if "login:" in out:
            s.sendall(b"root\n")
            time.sleep(0.5)
            out = read_all(s, 1.0)
            if "Password:" in out:
                s.sendall(b"nebuos\n")
                time.sleep(1.0)
                out = read_all(s, 1.5)
                if "#" in out or "root@" in out or "type=shell" in out:
                    s.sendall(b"\n")
                    time.sleep(0.5)
                    return True
        elif "Password:" in out:
            s.sendall(b"nebuos\n")
            time.sleep(1.0)
            out = read_all(s, 1.5)
            if "#" in out or "root@" in out or "type=shell" in out:
                s.sendall(b"\n")
                time.sleep(0.5)
                return True
        time.sleep(1.0)
    return False

s = get_socket()
print("[1/3] Waiting for VM 102 serial console root shell...")
if not ensure_shell(s):
    print("ERROR: Failed to establish root shell via serial socket")
    sys.exit(1)
print("Root shell established.")

# Disable pager, terminal echo
s.sendall(b"export PAGER=cat SYSTEMD_PAGER=cat TERM=dumb\n")
time.sleep(0.3)
s.sendall(b"stty -echo\n")
time.sleep(0.5)
read_all(s, 0.5)

def run_cmd(s, cmd, timeout=25.0):
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
        part = buf.split(start_tag, 1)[1].split("__NB_END__", 1)[0]
        return part.strip()
    return buf.strip()

print("[2/3] Collecting read-only hardware & driver telemetry from VM 102...")
results = {}
commands = [
    ("uname", "uname -a"),
    ("cmdline", "cat /proc/cmdline"),
    ("dev_dri", "ls -la /dev/dri"),
    ("pci_virtio_gpu", "cat /sys/bus/pci/devices/0000:00:01.0/uevent"),
    ("modules", "lsmod | grep -E 'virtio|drm'"),
    ("udev_card1", "udevadm info /dev/dri/card1"),
    ("packages", "rpm -qa | grep -E 'mesa|drm|seat|glvnd'"),
    ("dri_drivers", "ls -la /usr/lib64/dri/ 2>/dev/null || ls -la /usr/lib/dri/"),
    ("drm_probe", "/usr/bin/nebu-compositor --drm-probe"),
    ("renderer_probe", "/usr/bin/nebu-compositor --renderer-probe")
]

for key, cmd in commands:
    print(f"Executing: {cmd}")
    out = run_cmd(s, cmd)
    results[key] = out
    print(f"--- Output for {key} ---\n{out}\n------------------------")

with open("/tmp/vm102_renderer_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("[3/3] VM 102 Renderer probe execution finished. Results written to /tmp/vm102_renderer_results.json.")
