#!/usr/bin/env bash
# ==============================================================================
# NebuOS Milestone P0 — Disk Artifact Generation Script
# Assembles bootable GPT raw disk image with ESP FAT32 and Btrfs root filesystem.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_DIR="${REPO_ROOT}/target"

IMAGE_TAG="${IMAGE_TAG:-nebuos:p0-latest}"
RAW_DISK="${TARGET_DIR}/nebuos-p0.raw"
DISK_SIZE_GIB="${DISK_SIZE_GIB:-10}"
ROOTFS_SIZE_GIB="${ROOTFS_SIZE_GIB:-8}"
ESP_SIZE_MIB="${ESP_SIZE_MIB:-512}"

echo "======================================================================"
echo " NebuOS Milestone P0 — Disk Artifact Generation"
echo "======================================================================"
echo "Timestamp:    $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Image Tag:    ${IMAGE_TAG}"
echo "Target Raw:   ${RAW_DISK}"
echo "Disk Size:    ${DISK_SIZE_GIB} GiB"
echo "Rootfs Size:  ${ROOTFS_SIZE_GIB} GiB"
echo "ESP Size:     ${ESP_SIZE_MIB} MiB"
echo "----------------------------------------------------------------------"

# 1. Verify required host tools
echo "[1/7] Validating required host tools..."
REQUIRED_TOOLS=("docker" "sgdisk" "mkfs.vfat" "mkfs.btrfs" "mcopy" "mmd" "dd" "tar")
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "${tool}" >/dev/null 2>&1; then
        echo "CRITICAL FAILURE: Required host tool '${tool}' is not installed!" >&2
        exit 1
    fi
done
echo "All host tools verified."

# 2. Extract rootfs and boot artifacts from container
mkdir -p "${TARGET_DIR}"
TMP_ROOTFS="${TARGET_DIR}/tmp-rootfs"
rm -rf "${TMP_ROOTFS}"
mkdir -p "${TMP_ROOTFS}"

echo "[2/7] Extracting root filesystem and boot artifacts from ${IMAGE_TAG}..."
CID=$(docker create "${IMAGE_TAG}")
docker export "${CID}" | tar -x -C "${TMP_ROOTFS}"
docker rm "${CID}" >/dev/null

# Detect kernel and initramfs files
KERNEL_BIN=$(find "${TMP_ROOTFS}/boot" -name "vmlinuz-*" | head -n 1)
INITRD_BIN=$(find "${TMP_ROOTFS}/boot" -name "initramfs-*.img" | head -n 1)

if [[ -z "${KERNEL_BIN}" || -z "${INITRD_BIN}" ]]; then
    echo "CRITICAL FAILURE: Failed to locate vmlinuz or initramfs in extracted rootfs!" >&2
    exit 1
fi

KERNEL_NAME=$(basename "${KERNEL_BIN}")
INITRD_NAME=$(basename "${INITRD_BIN}")

cp -f "${KERNEL_BIN}" "${TARGET_DIR}/vmlinuz"
cp -f "${INITRD_BIN}" "${TARGET_DIR}/initramfs.img"
echo "Extracted Kernel:  ${KERNEL_NAME} -> ${TARGET_DIR}/vmlinuz"
echo "Extracted Initrd:  ${INITRD_NAME} -> ${TARGET_DIR}/initramfs.img"

# 3. Create and populate ESP (EFI System Partition)
echo "[3/7] Generating ESP FAT32 partition image..."
ESP_IMG="${TARGET_DIR}/esp.img"
rm -f "${ESP_IMG}"
truncate -s "${ESP_SIZE_MIB}M" "${ESP_IMG}"
mkfs.vfat -F 32 -n "EFI" "${ESP_IMG}"

# Locate GRUB EFI executable
GRUB_EFI_SRC=$(find "${TMP_ROOTFS}" -name "grubx64.efi" 2>/dev/null | head -n 1)
if [[ -z "${GRUB_EFI_SRC}" ]]; then
    # Fallback to BOOTX64.EFI
    GRUB_EFI_SRC=$(find "${TMP_ROOTFS}" -name "BOOTX64.EFI" 2>/dev/null | head -n 1)
fi

if [[ -z "${GRUB_EFI_SRC}" ]]; then
    echo "CRITICAL FAILURE: grubx64.efi or BOOTX64.EFI not found in image!" >&2
    exit 1
fi

# Create directory structure inside FAT32 ESP
mmd -i "${ESP_IMG}" ::/EFI
mmd -i "${ESP_IMG}" ::/EFI/BOOT
mmd -i "${ESP_IMG}" ::/EFI/fedora

# Copy GRUB EFI binary
mcopy -i "${ESP_IMG}" "${GRUB_EFI_SRC}" ::/EFI/BOOT/BOOTX64.EFI
mcopy -i "${ESP_IMG}" "${GRUB_EFI_SRC}" ::/EFI/fedora/grubx64.efi

# Generate standalone grub.cfg
TMP_GRUB_CFG="${TARGET_DIR}/grub.cfg"
cat <<EOF > "${TMP_GRUB_CFG}"
set default=0
set timeout=3
terminal_input console serial
terminal_output console serial

menuentry 'NebuOS Foundation (Milestone P0)' {
    insmod btrfs
    search --no-floppy --label --set=root root
    linux /boot/${KERNEL_NAME} root=LABEL=root ro console=tty0 console=ttyS0,115200n8 quiet systemd.show_status=auto panic=10
    initrd /boot/${INITRD_NAME}
}

menuentry 'NebuOS Foundation (Fallback / Emergency)' {
    insmod btrfs
    search --no-floppy --label --set=root root
    linux /boot/${KERNEL_NAME} root=LABEL=root ro console=tty0 console=ttyS0,115200n8 systemd.unit=emergency.target
    initrd /boot/${INITRD_NAME}
}
EOF

mcopy -i "${ESP_IMG}" "${TMP_GRUB_CFG}" ::/EFI/BOOT/grub.cfg
mcopy -i "${ESP_IMG}" "${TMP_GRUB_CFG}" ::/EFI/fedora/grub.cfg
rm -f "${TMP_GRUB_CFG}"
echo "ESP partition generated successfully: ${ESP_IMG}"

# 4. Generate Btrfs root filesystem image
echo "[4/7] Generating Btrfs root filesystem image from container rootfs..."
ROOT_IMG="${TARGET_DIR}/rootfs.img"
rm -f "${ROOT_IMG}"
truncate -s "${ROOTFS_SIZE_GIB}G" "${ROOT_IMG}"

mkfs.btrfs -f -L "root" -r "${TMP_ROOTFS}" "${ROOT_IMG}"
echo "Btrfs root filesystem generated successfully: ${ROOT_IMG}"

# Cleanup extracted rootfs tree to reclaim CT 100 disk space
rm -rf "${TMP_ROOTFS}"

# 5. Assemble GPT Raw Disk Image
echo "[5/7] Assembling GPT partitioned disk image: ${RAW_DISK}..."
rm -f "${RAW_DISK}"
truncate -s "${DISK_SIZE_GIB}G" "${RAW_DISK}"

# Partition offsets (in 512-byte sectors):
# Sector 0..33: GPT metadata
# Sector 2048..1050623: ESP (512 MiB = 1048576 sectors)
# Sector 1050624..end: Root Btrfs
sgdisk -Z "${RAW_DISK}" >/dev/null 2>&1 || true
sgdisk -n 1:2048:+512M -t 1:ef00 -c 1:"EFI-SYSTEM" "${RAW_DISK}"
sgdisk -n 2:0:0 -t 2:8300 -c 2:"nebuos-root" "${RAW_DISK}"

echo "Writing ESP partition to offset 1 MiB (sector 2048)..."
dd if="${ESP_IMG}" of="${RAW_DISK}" bs=1M seek=1 conv=notrunc status=none

echo "Writing Root partition to offset 513 MiB (sector 1050624)..."
dd if="${ROOT_IMG}" of="${RAW_DISK}" bs=1M seek=513 conv=notrunc status=none

# Remove intermediate partition files to keep target/ clean
rm -f "${ROOT_IMG}" "${ESP_IMG}"

# Verify partition table
echo "[6/7] Verifying disk partition table..."
sgdisk -p "${RAW_DISK}"

# 6. Checksums and Metadata
echo "[7/7] Generating artifact checksums..."
RAW_SHA256=$(sha256sum "${RAW_DISK}" | awk '{print $1}')
KERNEL_SHA256=$(sha256sum "${TARGET_DIR}/vmlinuz" | awk '{print $1}')
INITRD_SHA256=$(sha256sum "${TARGET_DIR}/initramfs.img" | awk '{print $1}')

cat <<EOF > "${TARGET_DIR}/disk-meta.json"
{
  "milestone": "P0",
  "disk_image": "${RAW_DISK}",
  "disk_size_gib": ${DISK_SIZE_GIB},
  "raw_sha256": "${RAW_SHA256}",
  "kernel": {
    "name": "${KERNEL_NAME}",
    "path": "${TARGET_DIR}/vmlinuz",
    "sha256": "${KERNEL_SHA256}"
  },
  "initramfs": {
    "name": "${INITRD_NAME}",
    "path": "${TARGET_DIR}/initramfs.img",
    "sha256": "${INITRD_SHA256}"
  },
  "partition_layout": {
    "p1": "ESP FAT32 (512 MiB, sector 2048..1050623, type EF00)",
    "p2": "Root Btrfs (remainder, sector 1050624..end, type 8300)"
  },
  "generation_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo "Disk metadata saved to ${TARGET_DIR}/disk-meta.json"
echo "======================================================================"
echo " DEPLOYMENT ARTIFACT GENERATION COMPLETED: ${RAW_DISK}"
echo "======================================================================"
