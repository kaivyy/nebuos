#!/usr/bin/env python3
import json
import socket
import subprocess
import sys
import threading
import time

# Unbuffered stdout
sys.stdout.reconfigure(line_buffering=True)

sock_path = "/var/run/qemu-server/102.serial0"


def get_socket():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(2.0)
    for attempt in range(45):
        try:
            s.connect(sock_path)
            return s
        except Exception:
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
    for i in range(50):
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


def run_cmd(s, cmd, timeout=40.0):
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


def inject_input_events_background():
    time.sleep(2.0)
    events = [
        "sendkey a",
        "sendkey shift-b",
        "sendkey c",
        "mouse_move 120 80",
        "mouse_move -40 -30",
        "mouse_button 1",
        "mouse_button 0",
    ]
    for ev in events:
        try:
            subprocess.run(
                ["qm", "monitor", "102"],
                input=f"{ev}\n".encode("utf-8"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5.0,
            )
        except Exception:
            pass
        time.sleep(0.35)


print("[2/3] Collecting pre-flight info, running P1.7 Presentation probe and regressions on VM 102...")
results = {}

# Baseline system inspection commands
pre_commands = [
    ("uname", "uname -a"),
    ("cmdline", "cat /proc/cmdline"),
    ("binary_version", "/usr/bin/nebu-compositor --help"),
    ("drm_nodes", "ls -la /dev/dri/"),
    ("pre_sockets", "ls -la /run/user/0/ /tmp/ /var/run/ 2>/dev/null | grep -i wayland || true"),
    ("packages", "rpm -qa | grep -E 'mesa|drm|seat|input|xkb|wayland'"),
]

for key, cmd in pre_commands:
    print(f"Executing: {cmd}")
    out = run_cmd(s, cmd)
    results[key] = out
    print(f"--- Output for {key} ---\n{out}\n------------------------")

# Execute nebu-compositor --presentation-probe (P1.7 target proof)
print("\n>>> Executing TARGET PROOF: nebu-compositor --presentation-probe <<<")
presentation_probe_out = run_cmd(s, "/usr/bin/nebu-compositor --presentation-probe; echo \"EXIT_CODE=$?\"", timeout=40.0)
results["presentation_probe"] = presentation_probe_out
print(f"--- Output for presentation_probe ---\n{presentation_probe_out}\n------------------------")

# Regression probes: P1.2, P1.3, P1.4, P1.6
regression_commands = [
    ("drm_probe", "/usr/bin/nebu-compositor --drm-probe; echo \"EXIT_CODE=$?\""),
    ("renderer_probe", "/usr/bin/nebu-compositor --renderer-probe; echo \"EXIT_CODE=$?\""),
    ("output_probe", "/usr/bin/nebu-compositor --output-probe; echo \"EXIT_CODE=$?\""),
    ("wayland_probe", "/usr/bin/nebu-compositor --wayland-probe; echo \"EXIT_CODE=$?\""),
]

for key, cmd in regression_commands:
    print(f"\nExecuting regression check: {cmd}")
    out = run_cmd(s, cmd, timeout=35.0)
    results[key] = out
    print(f"--- Output for {key} ---\n{out}\n------------------------")

# Regression probe: P1.5 with input event injection
print("\n>>> Executing regression check: /usr/bin/nebu-compositor --input-probe with injection <<<")
injector = threading.Thread(target=inject_input_events_background)
injector.start()
input_probe_out = run_cmd(s, "/usr/bin/nebu-compositor --input-probe; echo \"EXIT_CODE=$?\"", timeout=40.0)
injector.join()
results["input_probe"] = input_probe_out
print(f"--- Output for input_probe ---\n{input_probe_out}\n------------------------")

# Post-probe diagnostics and hygiene verification
post_commands = [
    ("post_probe_processes", "ps aux | grep -E 'nebu|compositor|wayland' | grep -v grep || true"),
    ("post_probe_sockets", "ls -la /run/user/0/ /tmp/ /var/run/ 2>/dev/null | grep -i wayland || true"),
    ("dmesg_tail", "dmesg | tail -n 35"),
]

for key, cmd in post_commands:
    print(f"Executing: {cmd}")
    out = run_cmd(s, cmd)
    results[key] = out
    print(f"--- Output for {key} ---\n{out}\n------------------------")

with open("/tmp/vm102_presentation_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("[3/3] VM 102 Presentation probe execution finished. Results written to /tmp/vm102_presentation_results.json.")
