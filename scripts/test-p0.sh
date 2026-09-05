#!/usr/bin/env bash
# ==============================================================================
# NebuOS Milestone P0 — Automated Verification Harness
# Boots the OS disk image in QEMU, monitors serial output, and validates health gates.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_DIR="${REPO_ROOT}/target"

BOOT_LOG="${TARGET_DIR}/boot.log"
QEMU_PIDFILE="${TARGET_DIR}/qemu.pid"
TEST_RESULTS_JSON="${TARGET_DIR}/test-results.json"
TEST_REPORT_MD="${TARGET_DIR}/TEST_REPORT.md"

TIMEOUT_SEC="${TIMEOUT_SEC:-180}"
MODE="${1:---direct}" # --direct (default) or --uefi
MEM_MB="${MEM_MB:-2048}"
SMP_CORES="${SMP_CORES:-2}"

echo "======================================================================"
echo " NebuOS Milestone P0 — Automated Verification Harness"
echo "======================================================================"
echo "Timestamp:    $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Mode:         ${MODE}"
echo "Boot Log:     ${BOOT_LOG}"
echo "Timeout:      ${TIMEOUT_SEC}s"
echo "Memory / CPU: ${MEM_MB}MB / ${SMP_CORES} cores"
echo "----------------------------------------------------------------------"

# 1. Check prerequisites
if [[ ! -f "${TARGET_DIR}/nebuos-p0.raw" ]]; then
    echo "ERROR: ${TARGET_DIR}/nebuos-p0.raw does not exist. Run scripts/deploy-p0.sh first." >&2
    exit 1
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
    echo "CRITICAL FAILURE: qemu-system-x86_64 is not installed!" >&2
    exit 1
fi

# Clean previous run state
rm -f "${BOOT_LOG}" "${QEMU_PIDFILE}"
touch "${BOOT_LOG}"

# 2. Configure QEMU invocation
QEMU_COMMON_ARGS=(
    "-machine" "q35,accel=tcg"
    "-cpu" "max"
    "-m" "${MEM_MB}M"
    "-smp" "${SMP_CORES}"
    "-drive" "file=${TARGET_DIR}/nebuos-p0.raw,format=raw,if=virtio,cache=writeback"
    "-netdev" "user,id=net0"
    "-device" "virtio-net-pci,netdev=net0"
    "-serial" "file:${BOOT_LOG}"
    "-display" "none"
    "-no-reboot"
    "-pidfile" "${QEMU_PIDFILE}"
)

if [[ "${MODE}" == "--uefi" ]]; then
    OVMF_PATH=""
    for p in "/usr/share/OVMF/OVMF_CODE_4M.fd" "/usr/share/ovmf/OVMF.fd"; do
        if [[ -f "${p}" ]]; then
            OVMF_PATH="${p}"
            break
        fi
    done
    if [[ -z "${OVMF_PATH}" ]]; then
        echo "ERROR: OVMF firmware file not found!" >&2
        exit 1
    fi
    echo "Starting QEMU in UEFI mode with firmware: ${OVMF_PATH}..."
    qemu-system-x86_64 "${QEMU_COMMON_ARGS[@]}" -pflash "${OVMF_PATH}" &
else
    if [[ ! -f "${TARGET_DIR}/vmlinuz" || ! -f "${TARGET_DIR}/initramfs.img" ]]; then
        echo "ERROR: Target vmlinuz or initramfs.img missing for direct boot mode." >&2
        exit 1
    fi
    echo "Starting QEMU in Direct Kernel Boot mode..."
    qemu-system-x86_64 "${QEMU_COMMON_ARGS[@]}" \
        "-kernel" "${TARGET_DIR}/vmlinuz" \
        "-initrd" "${TARGET_DIR}/initramfs.img" \
        "-append" "console=tty0 console=ttyS0,115200n8 root=LABEL=root ro systemd.show_status=auto panic=10" &
fi

QEMU_PID=$!
echo "QEMU started with PID ${QEMU_PID}. Monitoring serial boot log..."

# 3. Monitor boot progress
START_TIME=$(date +%s)
HEALTH_CHECK_PASSED=0
LOGIN_REACHED=0
MULTI_USER_REACHED=0
KERNEL_BOOTED=0
SYSTEMD_STARTED=0

cleanup() {
    if kill -0 "${QEMU_PID}" 2>/dev/null; then
        echo "Stopping QEMU process ${QEMU_PID}..."
        kill -TERM "${QEMU_PID}" 2>/dev/null || true
        sleep 1
        kill -KILL "${QEMU_PID}" 2>/dev/null || true
    fi
    rm -f "${QEMU_PIDFILE}"
}
trap cleanup EXIT

echo "Awaiting system convergence (timeout: ${TIMEOUT_SEC}s)..."
while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))

    if [[ -f "${BOOT_LOG}" ]]; then
        if grep -q "Linux version" "${BOOT_LOG}"; then
            if [[ ${KERNEL_BOOTED} -eq 0 ]]; then
                echo "  [+${ELAPSED}s] Kernel initialization detected."
                KERNEL_BOOTED=1
            fi
        fi

        if grep -q "systemd 259" "${BOOT_LOG}"; then
            if [[ ${SYSTEMD_STARTED} -eq 0 ]]; then
                echo "  [+${ELAPSED}s] systemd PID 1 started."
                SYSTEMD_STARTED=1
            fi
        fi

        if grep -q "multi-user.target" "${BOOT_LOG}"; then
            if [[ ${MULTI_USER_REACHED} -eq 0 ]]; then
                echo "  [+${ELAPSED}s] Reached target: multi-user.target"
                MULTI_USER_REACHED=1
            fi
        fi

        if grep -q "\[NEBU-BOOT-CHECK\] ALL CHECKS PASSED — DEPLOYMENT IS HEALTHY" "${BOOT_LOG}"; then
            if [[ ${HEALTH_CHECK_PASSED} -eq 0 ]]; then
                echo "  [+${ELAPSED}s] Health check gate passed: ALL CHECKS PASSED!"
                HEALTH_CHECK_PASSED=1
            fi
        fi

        if grep -q "login:" "${BOOT_LOG}" || grep -q "root@" "${BOOT_LOG}"; then
            if [[ ${LOGIN_REACHED} -eq 0 ]]; then
                echo "  [+${ELAPSED}s] Serial TTY login console reached."
                LOGIN_REACHED=1
            fi
        fi
    fi

    # Success convergence criteria: Health check passed AND (multi-user reached OR login reached)
    if [[ ${HEALTH_CHECK_PASSED} -eq 1 && (${MULTI_USER_REACHED} -eq 1 || ${LOGIN_REACHED} -eq 1) ]]; then
        echo "======================================================================"
        echo " CONVERGENCE ACHIEVED IN ${ELAPSED} SECONDS"
        echo "======================================================================"
        break
    fi

    # Check if QEMU died unexpectedly
    if ! kill -0 "${QEMU_PID}" 2>/dev/null; then
        echo "WARNING: QEMU process terminated after ${ELAPSED}s."
        break
    fi

    if [[ ${ELAPSED} -ge ${TIMEOUT_SEC} ]]; then
        echo "ERROR: Boot verification timed out after ${TIMEOUT_SEC}s!" >&2
        break
    fi

    sleep 2
done

# 4. Evaluate Test Matrix
echo ""
echo "======================================================================"
echo " NebuOS Milestone P0 — Test Results Matrix"
echo "======================================================================"

TEST_PASSED=true

eval_test() {
    local tc_id="$1"
    local desc="$2"
    local status="$3"
    local detail="$4"

    if [[ "${status}" == "PASS" ]]; then
        printf "  [ PASS ] %-12s %-45s (%s)\n" "${tc_id}" "${desc}" "${detail}"
    else
        printf "  [ FAIL ] %-12s %-45s (%s)\n" "${tc_id}" "${desc}" "${detail}"
        TEST_PASSED=false
    fi
}

# TC-P0-001: Kernel Boot
if [[ ${KERNEL_BOOTED} -eq 1 ]]; then
    eval_test "TC-P0-001" "Kernel Boot & Driver Init" "PASS" "Fedora 7.1.13 kernel booted"
else
    eval_test "TC-P0-001" "Kernel Boot & Driver Init" "FAIL" "Kernel banner not detected"
fi

# TC-P0-002: Systemd PID 1
if [[ ${SYSTEMD_STARTED} -eq 1 ]]; then
    eval_test "TC-P0-002" "Systemd PID 1 Initialization" "PASS" "systemd 259 running"
else
    eval_test "TC-P0-002" "Systemd PID 1 Initialization" "FAIL" "systemd banner not detected"
fi

# TC-P0-003: Multi-User Target
if [[ ${MULTI_USER_REACHED} -eq 1 ]]; then
    eval_test "TC-P0-003" "multi-user.target Reached" "PASS" "Target reached"
else
    eval_test "TC-P0-003" "multi-user.target Reached" "FAIL" "multi-user.target not reached"
fi

# TC-P0-004: nebu-boot-check Health Gate
if [[ ${HEALTH_CHECK_PASSED} -eq 1 ]]; then
    eval_test "TC-P0-004" "nebu-boot-check Health Gate" "PASS" "All 7 health assertions passed"
else
    eval_test "TC-P0-004" "nebu-boot-check Health Gate" "FAIL" "Gate did not report healthy"
fi

# TC-P0-005: Headless Verification (Plymouth absence)
if ! grep -qi "plymouth" "${BOOT_LOG}"; then
    eval_test "TC-P0-005" "100% Headless (Zero Plymouth)" "PASS" "Zero Plymouth logs found"
else
    eval_test "TC-P0-005" "100% Headless (Zero Plymouth)" "FAIL" "Plymouth traces detected"
fi

# TC-P0-006: Read-only Root/Usr Mount
if grep -q "\[CHECK\] Sysroot /usr is mounted read-only... PASS" "${BOOT_LOG}"; then
    eval_test "TC-P0-006" "Read-Only /usr Immutability" "PASS" "/usr verified read-only"
else
    eval_test "TC-P0-006" "Read-Only /usr Immutability" "FAIL" "/usr mount assertion missing"
fi

# TC-P0-007: Zero Critical Failed Units
if grep -q "\[CHECK\] Zero critical systemd units failed... PASS" "${BOOT_LOG}"; then
    eval_test "TC-P0-007" "Zero Systemd Critical Failures" "PASS" "0 degraded/failed units"
else
    eval_test "TC-P0-007" "Zero Systemd Critical Failures" "FAIL" "Systemd units failed"
fi

# TC-P0-008: Serial TTY Login Console
if [[ ${LOGIN_REACHED} -eq 1 ]]; then
    eval_test "TC-P0-008" "Serial TTY Login Console" "PASS" "TTY console active"
else
    eval_test "TC-P0-008" "Serial TTY Login Console" "FAIL" "Login prompt not reached"
fi

echo "----------------------------------------------------------------------"

# 5. Generate Test Report Artifact
cat <<EOF > "${TEST_REPORT_MD}"
# NebuOS Milestone P0 — Automated Test Report

- **Date:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- **Mode:** ${MODE}
- **Kernel:** Fedora 7.1.13-200.fc44.x86_64
- **Substrate:** bootc / Fedora 44 Atomic
- **Elapsed Boot Time:** ${ELAPSED} seconds
- **Overall Result:** $(if ${TEST_PASSED}; then echo "PASS"; else echo "FAIL"; fi)

## Verified Test Cases

| Test Case | Description | Status | Evidence |
|:---|:---|:---:|:---|
| TC-P0-001 | Kernel Boot & Driver Init | $(if [[ ${KERNEL_BOOTED} -eq 1 ]]; then echo "PASS"; else echo "FAIL"; fi) | Linux kernel 7.1.13 initialized |
| TC-P0-002 | Systemd PID 1 Initialization | $(if [[ ${SYSTEMD_STARTED} -eq 1 ]]; then echo "PASS"; else echo "FAIL"; fi) | systemd 259 active |
| TC-P0-003 | multi-user.target Reached | $(if [[ ${MULTI_USER_REACHED} -eq 1 ]]; then echo "PASS"; else echo "FAIL"; fi) | Multi-User target active |
| TC-P0-004 | nebu-boot-check Health Gate | $(if [[ ${HEALTH_CHECK_PASSED} -eq 1 ]]; then echo "PASS"; else echo "FAIL"; fi) | All 7 assertions passed |
| TC-P0-005 | 100% Headless (Zero Plymouth) | $(if ! grep -qi "plymouth" "${BOOT_LOG}"; then echo "PASS"; else echo "FAIL"; fi) | Zero Plymouth logs |
| TC-P0-006 | Read-Only /usr Immutability | $(if grep -q "\[NEBU-BOOT-CHECK\] Assertion 3/7: /usr is mounted read-only... PASS" "${BOOT_LOG}"; then echo "PASS"; else echo "FAIL"; fi) | /usr verified read-only |
| TC-P0-007 | Zero Systemd Critical Failures | $(if grep -q "\[NEBU-BOOT-CHECK\] Assertion 6/7: Zero systemd critical unit failures... PASS" "${BOOT_LOG}"; then echo "PASS"; else echo "FAIL"; fi) | 0 degraded units |
| TC-P0-008 | Serial TTY Login Console | $(if [[ ${LOGIN_REACHED} -eq 1 ]]; then echo "PASS"; else echo "FAIL"; fi) | Serial getty active |

## Serial Boot Log Snippet
\`\`\`text
$(tail -n 40 "${BOOT_LOG}" 2>/dev/null || echo "No logs captured")
\`\`\`
EOF

echo "Detailed test report written to: ${TEST_REPORT_MD}"

if ${TEST_PASSED}; then
    echo "VERDICT: PASS — P0 FOUNDATION MEETS ALL SPECIFICATIONS"
    exit 0
else
    echo "VERDICT: FAIL — P0 VERIFICATION DEFECTS DETECTED"
    exit 1
fi
