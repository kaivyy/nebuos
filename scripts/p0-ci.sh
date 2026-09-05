#!/usr/bin/env bash
# ==============================================================================
# NebuOS Milestone P0 — Master CI / End-to-End Orchestrator
# Executes full build -> deploy -> test -> verification pipeline.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

START_TIME=$(date +%s)

echo "======================================================================"
echo " NebuOS Milestone P0 — Continuous Integration Pipeline"
echo "======================================================================"
echo "Start Time: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Host:       $(hostname) ($(uname -srm))"
echo "Repo:       ${REPO_ROOT}"
echo "======================================================================"

# Stage 1: Build & Image Validation
echo ""
echo ">>> STAGE 1: Image Build & Container Validation"
"${SCRIPT_DIR}/build-p0.sh"

# Stage 2: Disk Artifact Generation
echo ""
echo ">>> STAGE 2: Disk Artifact Generation (GPT + ESP + Btrfs)"
"${SCRIPT_DIR}/deploy-p0.sh"

# Stage 3: Automated Boot Verification
echo ""
echo ">>> STAGE 3: Automated QEMU Boot Verification"
"${SCRIPT_DIR}/test-p0.sh"

END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))

echo ""
echo "======================================================================"
echo " NebuOS Milestone P0 — CI Pipeline Completed Successfully"
echo " Total Pipeline Duration: ${TOTAL_DURATION}s"
echo " Status: ALL HEALTH GATES PASSED (100% Headless Foundation Validated)"
echo "======================================================================"
