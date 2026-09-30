#!/usr/bin/env python3
import json
import socket
import subprocess
import sys
import threading
import time

# Unbuffered stdout
sys.stdout.reconfigure(line_buffering=True)

sock_path = "/var/run/qemu-server/103.serial0"
ARTIFACT_HOST = "192.168.1.44:8089"


def get_socket():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(2.0)
    for attempt in range(60):
        try:
            s.connect(sock_path)
            return s
        except Exception:
            time.sleep(1.0)
    print("ERROR: Failed to connect to VM 103 serial socket")
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
    for i in range(30):
        s.sendall(b"\necho SHELL_READY\n")
        time.sleep(0.5)
        out = read_all(s, 1.0)
        if "SHELL_READY" in out or "#" in out or "root@" in out or "fedora" in out or "type=shell" in out:
            return True
        if "login:" in out:
            s.sendall(b"root\n")
            time.sleep(0.5)
            out = read_all(s, 1.0)
            if "Password:" in out:
                s.sendall(b"nebuos\n")
                time.sleep(1.0)
                out = read_all(s, 1.5)
                if "SHELL_READY" in out or "#" in out or "root@" in out or "type=shell" in out or "fedora" in out:
                    s.sendall(b"\n")
                    time.sleep(0.5)
                    return True
        elif "Password:" in out:
            s.sendall(b"nebuos\n")
            time.sleep(1.0)
            out = read_all(s, 1.5)
            if "SHELL_READY" in out or "#" in out or "root@" in out or "type=shell" in out or "fedora" in out:
                s.sendall(b"\n")
                time.sleep(0.5)
                return True
        time.sleep(0.5)
    return False


s = get_socket()
print("[1/4] Waiting for VM 103 serial console root shell...")
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
                ["qm", "monitor", "103"],
                input=f"{ev}\n".encode("utf-8"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5.0,
            )
        except Exception:
            pass
        time.sleep(0.35)


print("[2/4] Unlocking filesystem and deploying nebu-shell artifact to VM 103...")
results = {}

# Unlock writable locations and install binaries
setup_commands = [
    ("mount_status", "mount | grep -E ' / | /usr'"),
    ("try_remount", "mount -o remount,rw /sysroot 2>&1 || mount -o remount,rw / 2>&1 || true"),
    ("deploy_local_bin", f"mkdir -p /usr/local/bin && curl -sSf http://{ARTIFACT_HOST}/nebu-shell -o /usr/local/bin/nebu-shell && chmod +x /usr/local/bin/nebu-shell; echo \"EXIT_CODE=$?\""),
    ("sync_usr_bin", "cp -f /usr/local/bin/nebu-shell /usr/bin/nebu-shell 2>&1 || ln -sf /usr/local/bin/nebu-shell /usr/bin/nebu-shell 2>&1 || true"),
    ("verify_binaries", "ls -lh /usr/local/bin/nebu-shell /usr/bin/nebu-compositor && sha256sum /usr/local/bin/nebu-shell /usr/bin/nebu-compositor"),
    ("shell_version", "/usr/local/bin/nebu-shell --version"),
    ("shell_help", "/usr/local/bin/nebu-shell --help"),
]

for key, cmd in setup_commands:
    print(f"Executing: {cmd}")
    out = run_cmd(s, cmd, timeout=30.0)
    results[key] = out
    print(f"--- Output for {key} ---\n{out}\n------------------------")

print("[3/4] Executing Milestone P2.1 NebuShell Verification Probes on VM 103...")
p2_1_probes = [
    ("p2_1_probe_default", "/usr/local/bin/nebu-shell --verify-p2-1; echo \"EXIT_CODE=$?\""),
    ("p2_1_probe_traditional", "/usr/local/bin/nebu-shell --verify-p2-1 --paradigm traditional; echo \"EXIT_CODE=$?\""),
    ("p2_1_probe_minimal", "/usr/local/bin/nebu-shell --verify-p2-1 --paradigm minimal; echo \"EXIT_CODE=$?\""),
]

for key, cmd in p2_1_probes:
    print(f"\n>>> Executing TARGET P2.1 PROBE: {cmd} <<<")
    out = run_cmd(s, cmd, timeout=40.0)
    results[key] = out
    print(f"--- Output for {key} ---\n{out}\n------------------------")

print("[4/4] Running P2.0 desktop probes and P1 regression probes on VM 103...")

# P2.0 Probes
p2_probes = [
    ("desktop_protocol_probe", "/usr/bin/nebu-compositor --desktop-protocol-probe; echo \"EXIT_CODE=$?\""),
    ("layer_shell_probe", "/usr/bin/nebu-compositor --layer-shell-probe; echo \"EXIT_CODE=$?\""),
]

for key, cmd in p2_probes:
    print(f"\nExecuting P2.0 probe: {cmd}")
    out = run_cmd(s, cmd, timeout=40.0)
    results[key] = out
    print(f"--- Output for {key} ---\n{out}\n------------------------")

# P1 Regression probes: P1.2 (DRM), P1.3 (Renderer), P1.4 (Output), P1.6 (Wayland Core), P1.7 (Presentation)
regression_commands = [
    ("wayland_probe", "/usr/bin/nebu-compositor --wayland-probe; echo \"EXIT_CODE=$?\""),
    ("presentation_probe", "/usr/bin/nebu-compositor --presentation-probe; echo \"EXIT_CODE=$?\""),
    ("output_probe", "/usr/bin/nebu-compositor --output-probe; echo \"EXIT_CODE=$?\""),
    ("renderer_probe", "/usr/bin/nebu-compositor --renderer-probe; echo \"EXIT_CODE=$?\""),
    ("drm_probe", "/usr/bin/nebu-compositor --drm-probe; echo \"EXIT_CODE=$?\""),
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
    ("post_probe_processes", "ps aux | grep -E 'nebu|compositor|shell|wayland' | grep -v grep || true"),
    ("post_probe_sockets", "ls -la /run/user/0/ /tmp/ /var/run/ 2>/dev/null | grep -i wayland || true"),
    ("dmesg_tail", "dmesg | tail -n 35"),
]

for key, cmd in post_commands:
    print(f"Executing: {cmd}")
    out = run_cmd(s, cmd)
    results[key] = out
    print(f"--- Output for {key} ---\n{out}\n------------------------")

with open("/tmp/vm103_p2_1_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n[COMPLETE] VM 103 Milestone P2.1 verification suite finished. Results written to /tmp/vm103_p2_1_results.json.")
