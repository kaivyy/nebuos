#!/usr/bin/env bash
# ==============================================================================
# NebuOS Milestone P0 — Build Automation Script
# Builds the immutable OS container image using Docker and validates headless baseline.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_DIR="${REPO_ROOT}/target"

IMAGE_TAG="${IMAGE_TAG:-nebuos:p0-latest}"
CONTAINERFILE="${CONTAINERFILE:-${REPO_ROOT}/Containerfile.p0}"
NO_CACHE="${NO_CACHE:-0}"

mkdir -p "${TARGET_DIR}"

echo "======================================================================"
echo " NebuOS Milestone P0 — Image Build & Validation"
echo "======================================================================"
echo "Timestamp:     $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Image Tag:     ${IMAGE_TAG}"
echo "Containerfile: ${CONTAINERFILE}"
echo "Repo Root:     ${REPO_ROOT}"
echo "Target Dir:    ${TARGET_DIR}"
echo "----------------------------------------------------------------------"

# 1. Check Docker daemon availability
echo "[1/5] Checking Docker daemon..."
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker daemon is not running or not accessible." >&2
    exit 1
fi
echo "Docker daemon OK."

# 2. Build the container image
echo "[2/5] Building OCI image: ${IMAGE_TAG}..."
BUILD_ARGS=()
if [[ "${NO_CACHE}" == "1" ]]; then
    BUILD_ARGS+=("--no-cache")
fi

docker build "${BUILD_ARGS[@]}" -f "${CONTAINERFILE}" -t "${IMAGE_TAG}" "${REPO_ROOT}"
echo "Image build succeeded: ${IMAGE_TAG}"

# 3. Validate base container with bootc container lint
echo "[3/5] Running bootc container lint..."
if docker run --rm "${IMAGE_TAG}" bootc container lint; then
    echo "bootc container lint: PASSED"
else
    echo "ERROR: bootc container lint failed" >&2
    exit 1
fi

# 4. In-container baseline verification
echo "[4/5] Verifying P0 headless baseline constraints..."

# 4a. Plymouth MUST NOT be installed (100% headless requirement)
if docker run --rm "${IMAGE_TAG}" rpm -q plymouth >/dev/null 2>&1; then
    echo "CRITICAL FAILURE: plymouth package is installed! P0 must be 100% headless." >&2
    exit 1
else
    echo "PASS: Plymouth is not installed."
fi

# 4b. Mandatory system packages must be present
for pkg in kernel-core kernel-modules btrfs-progs systemd NetworkManager dracut grub2-efi-x64; do
    if ! docker run --rm "${IMAGE_TAG}" rpm -q "${pkg}" >/dev/null 2>&1; then
        echo "CRITICAL FAILURE: Mandatory package ${pkg} is missing!" >&2
        exit 1
    fi
done
echo "PASS: All mandatory system packages verified."

# 4c. Health check script and service must exist
if ! docker run --rm "${IMAGE_TAG}" test -x /usr/libexec/nebu/nebu-boot-check; then
    echo "CRITICAL FAILURE: /usr/libexec/nebu/nebu-boot-check is missing or not executable!" >&2
    exit 1
fi
if ! docker run --rm "${IMAGE_TAG}" test -f /usr/lib/systemd/system/nebu-boot-check.service; then
    echo "CRITICAL FAILURE: /usr/lib/systemd/system/nebu-boot-check.service is missing!" >&2
    exit 1
fi
echo "PASS: nebu-boot-check script and service unit verified."

# 4d. nebu-boot-check service must be enabled
ENABLED_STATUS=$(docker run --rm "${IMAGE_TAG}" systemctl is-enabled nebu-boot-check.service 2>&1 || true)
if [[ "${ENABLED_STATUS}" != "enabled" ]]; then
    echo "CRITICAL FAILURE: nebu-boot-check.service is not enabled (status: ${ENABLED_STATUS})!" >&2
    exit 1
fi
echo "PASS: nebu-boot-check.service is enabled."

# 4e. Kernel and initramfs artifacts must exist in /boot
KERNEL_FILES=$(docker run --rm "${IMAGE_TAG}" bash -c "ls -1 /boot/vmlinuz-* /boot/initramfs-*.img 2>/dev/null" || true)
if [[ -z "${KERNEL_FILES}" ]]; then
    echo "CRITICAL FAILURE: Kernel or initramfs missing in /boot!" >&2
    exit 1
fi
echo "PASS: Kernel and initramfs artifacts located in /boot:"
echo "${KERNEL_FILES}"

# 5. Record build metadata
echo "[5/5] Recording build metadata..."
IMAGE_ID=$(docker inspect --format='{{.Id}}' "${IMAGE_TAG}")
IMAGE_SIZE=$(docker inspect --format='{{.Size}}' "${IMAGE_TAG}")
IMAGE_CREATED=$(docker inspect --format='{{.Created}}' "${IMAGE_TAG}")

cat <<EOF > "${TARGET_DIR}/build-meta.json"
{
  "milestone": "P0",
  "image_tag": "${IMAGE_TAG}",
  "image_id": "${IMAGE_ID}",
  "image_size_bytes": ${IMAGE_SIZE},
  "created_at": "${IMAGE_CREATED}",
  "build_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "status": "VALIDATED"
}
EOF

echo "Build metadata saved to ${TARGET_DIR}/build-meta.json"
echo "======================================================================"
echo " BUILD AND VALIDATION SUCCEEDED: ${IMAGE_TAG}"
echo "======================================================================"
