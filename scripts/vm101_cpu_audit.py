#!/usr/bin/env python3
import socket
import sys
import time

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
            if c: buf += c
        except socket.timeout: pass
    return buf

def ensure_shell():
    s.sendall(b"\x03\nq\n\n")
    time.sleep(0.5)
    out = read_all(1.0)
    if "#" in out:
        return True
    if "login:" in out:
        s.sendall(b"root\n")
        time.sleep(0.5)
        read_all(0.5)
        s.sendall(b"nebuos\n")
        time.sleep(1.0)
        out = read_all(1.0)
        return "#" in out
    return False

if not ensure_shell():
    print("Could not get shell")
    sys.exit(1)

s.sendall(b"export PAGER=cat SYSTEMD_PAGER=cat TERM=dumb; stty -echo\n")
time.sleep(0.5)
read_all(0.5)

def run(cmd):
    s.sendall(f"printf '__CPUSTART__\\n'; {cmd}; printf '__CPUEN%s__\\n' 'D'\n".encode("utf-8"))
    buf = ""
    start = time.time()
    while time.time() - start < 4.0:
        try:
            c = s.recv(2048).decode("utf-8", errors="replace")
            if c:
                buf += c
                if "__CPUEND__" in buf: break
        except socket.timeout: pass
    if "__CPUSTART__\r\n" in buf and "__CPUEND__" in buf:
        return buf.split("__CPUSTART__\r\n", 1)[1].split("__CPUEND__", 1)[0].strip("\r\n ")
    return buf.strip()

print("=== NPROC ===")
print(run("nproc"))

print("=== LSCPU ===")
print(run("lscpu"))

print("=== FREE MEMORY ===")
print(run("free -m"))

s.sendall(b"stty echo\n")
s.close()
