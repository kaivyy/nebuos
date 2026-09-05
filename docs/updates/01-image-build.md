# Image Build Specification — NebuOS

**Status:** APPROVED ARCHITECTURAL SPECIFICATION  
**Document ID:** NEBU-SPEC-BLD-001  
**Authority:** DevOps/Infrastructure Engineer, OS Update/Release Engineer, Security Architect  
**Purpose:** Specify the Containerfile definitions, multi-stage build pipelines, registry topology, cryptographic signing, OCI layer caching, and reproducibility standards for NebuOS base images.  

---

## 1. Status and Invariants

- **Status:** APPROVED — Governs image creation across Milestone P0 through P8.
- **Architectural Invariants:**
  1. **OCI Standard:** Every NebuOS image is a standard compliant OCI container image bootable via `bootc`.
  2. **Zero Build Pollution:** Production OS images contain zero build tools (no `cargo`, `rustc`, `gcc`, development headers, or compiler caches).
  3. **Immutable Identity:** Every release is identified and referenced by an immutable SHA-256 digest (`sha256:....`). Tagging (e.g. `:stable`) is strictly an alias pointer.
  4. **Promotion Over Rebuild:** A release candidate promoted from testing to stable is NEVER rebuilt from source. Promotion retags the identical, bit-for-bit immutable SHA-256 digest that passed regression testing.
  5. **Signed Provenance:** Every image must be signed via Sigstore/Cosign and attested with in-toto supply chain metadata before entering public registries.
  6. **Separation of Milestone Containerfiles:** Milestone P0 relies strictly on `Containerfile.p0`. Graphical and runtime layers are introduced in subsequent milestones.

---

## 2. Containerfile Architecture

NebuOS maintains two distinct container specifications within the repository:

### 2.1 `Containerfile.p0` (Milestone P0: Headless Foundation)
Strictly minimal containerfile designed to validate boot, systemd, and transactional updates without graphical dependencies:

```dockerfile
# Stage 1: Minimal P0 Base from Fedora bootc
FROM quay.io/fedora/fedora-bootc:44 AS p0-base

# Configure lean package manifest (core headless only)
RUN dnf install -y \
    kernel-core \
    kernel-modules \
    systemd \
    btrfs-progs \
    util-linux \
    shadow-utils \
    NetworkManager \
    grub2-tools \
    grub2-efi-x64 \
    efibootmgr \
    && dnf clean all

# Apply minimal configuration
COPY configs/p0/selinux.config /etc/selinux/config
COPY configs/p0/dracut.conf.d/ /etc/dracut.conf.d/
COPY configs/p0/tmpfiles.d/ /usr/lib/tmpfiles.d/
COPY configs/p0/systemd/ /usr/lib/systemd/system/

# Regenerate initramfs with minimal dracut modules
RUN dracut -vf /usr/lib/modules/$(uname -r)/initramfs.img $(uname -r)

# Final bootc lint validation
RUN bootc container lint
```

### 2.2 `Containerfile.release` (Production Release)
Multi-stage build compiling custom NebuOS Rust components and assembling the complete desktop and compatibility stack:

```dockerfile
# Stage 1: Rust Builder Container
FROM rust:1.80-bookworm AS rust-builder
WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY crates/ crates/
RUN cargo build --release --locked --workspace \
    -p nebu-compositor \
    -p nebu-shell \
    -p nebu-runtime-daemon \
    -p nebu-update-service

# Stage 2: Production Base OS Assembly
FROM quay.io/fedora/fedora-bootc:44 AS nebuos-base

# Install core system & desktop dependencies
RUN dnf install -y \
    kernel \
    kernel-modules-extra \
    systemd \
    btrfs-progs \
    mesa-vulkan-drivers \
    mesa-dri-drivers \
    pipewire \
    wireplumber \
    bubblewrap \
    wine-core \
    wine-staging \
    sqlite \
    fwupd \
    power-profiles-daemon \
    && dnf clean all

# Copy compiled Rust binaries from Stage 1
COPY --from=rust-builder /build/target/release/nebu-compositor /usr/bin/
COPY --from=rust-builder /build/target/release/nebu-shell /usr/bin/
COPY --from=rust-builder /build/target/release/nebu-runtime-daemon /usr/bin/
COPY --from=rust-builder /build/target/release/nebu-update-service /usr/libexec/nebu/

# Copy system configurations and preseeded compatibility DB
COPY configs/desktop/systemd/ /usr/lib/systemd/system/
COPY configs/desktop/user-systemd/ /usr/lib/systemd/user/
COPY configs/desktop/dbus-1/ /usr/share/dbus-1/system.d/
COPY data/compat.db /usr/share/nebu/compat.db
COPY keys/release.pub /etc/pki/nebu/release.pub

# Strip unneeded debug symbols to minimize layer size
RUN strip --strip-unneeded /usr/bin/nebu-* /usr/libexec/nebu/*

# Lint image for bootc compliance
RUN bootc container lint
```

---

## 3. Registry Topology & Environment Isolation

NebuOS partitions its OCI image distribution across three distinct registry namespaces:

```
+-------------------------------------------------------------------------+
|                        OCI CONTAINER REGISTRIES                         |
+-------------------------------------------------------------------------+
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
+---------------------+    +---------------------+    +---------------------+
|   PUBLIC RELEASE    |    |   INTERNAL TESTING  |    |  DEVELOPMENT / CI   |
| quay.io/nebuos/base |    | quay.io/nebu-ci/base|    | quay.io/nebu-dev/   |
+---------------------+    +---------------------+    +---------------------+
| - Signed GA images  |    | - Ephemeral builds  |    | - Daily nightly     |
| - Channel tags:     |    | - Compatibility Lab |    | - Feature branches  |
|   :stable, :testing |    | - Auto-deleted after|    | - Auto-pruned after |
| - Immutable digests |    |   14 days           |    |   7 days            |
+---------------------+    +---------------------+    +---------------------+
```

### Registry Rules:
1. **Zero Contamination:** Internal CI test images are never uploaded to the public production namespace.
2. **Access Control:** Public production registry permits write access exclusively from automated GitHub Actions / GitLab CI release runners authenticated via hardware OIDC tokens. Human developers have zero direct write credentials to the production registry.

---

## 4. Promotion vs. Rebuild Invariant

A fundamental failure mode in operating system engineering is rebuilding an image when promoting it from testing to production. Recompiling source code can introduce silent compiler non-determinism, new upstream package dependencies, or timestamp discrepancies.

NebuOS enforces an absolute **Promotion Over Rebuild** invariant:

```
[Main Branch Commit]
         │
         ▼
[CI Builds Candidate Image]  ───> Image SHA-256 Digest: sha256:7f83b165...
         │
         ▼
[Pushed to Registry]         ───> quay.io/nebu-ci/base:rc-1.0.1 (Digest: sha256:7f83b165...)
         │
         ▼
[Regression Test Gating]     ───> Passes all Gates (Security, Virtual Boot, Hardware Lab)
         │
         ▼
[Release Promotion Action]   ───> Cosign verifies digest; Retags existing digest:
                                   skopeo copy or crane tag:
                                   quay.io/nebuos/base@sha256:7f83b165... -> quay.io/nebuos/base:stable
```

**Outcome:** The bits tested in the Compatibility Lab are mathematically identical to the bits downloaded by end users.

---

## 5. Cryptographic Signing & Supply Chain Security

Every NebuOS base image is signed using **Sigstore / Cosign** before publication.

### 5.1 Trust Architecture
- **Root Keypair:** Ed25519 signing keypair generated inside a dedicated Hardware Security Module (HSM) / Cloud KMS.
- **Client Verification Key:** The public root certificate is embedded immutably into the client rootfs at `/etc/pki/nebu/release.pub`.
- **Transparency Log:** Signature metadata and build provenance are recorded into the public Rekor transparency log.
- **Client-Side Enforcement:** `bootc` and `NebuUpdateService` execute verification before staging:
  ```bash
  cosign verify --key /etc/pki/nebu/release.pub quay.io/nebuos/base@sha256:<digest>
  ```
  If signature verification fails, the operation immediately aborts with an exit code of `1`, leaving the client disk untouched.

### 5.2 Key Compromise & Revocation Strategy
1. **Secondary Offline Key:** A high-entropy offline recovery key is maintained in secure cold storage.
2. **Revocation Publishing:** In the event of primary key compromise, a signed revocation statement is published to the transparency log.
3. **Emergency Trust Update:** A signed emergency OS image (signed by the offline recovery key) is released, which rotates `/etc/pki/nebu/release.pub` on client systems.

---

## 6. OCI Layer Reuse & Bandwidth Optimization

Image-based operating systems can consume significant bandwidth if not properly structured. NebuOS optimizes layer layering to achieve minimal download deltas:

### 6.1 Layer Ordering Strategy (Bottom to Top)
```
[Layer 0: Fedora Minimal Base Rootfs]          ~ 450 MB  (Static - Updated rarely)
[Layer 1: Core Kernel & Drivers]               ~ 350 MB  (Updated bi-weekly/monthly)
[Layer 2: Standard Desktop Daemons & Mesa]     ~ 400 MB  (Updated bi-weekly)
[Layer 3: Wine / Proton Staging Runnners]      ~ 600 MB  (Updated monthly)
[Layer 4: NebuOS Rust Binaries (Compositor/Shell)] ~ 45 MB   (Updated frequently)
[Layer 5: Configuration, Systemd Units, DB]    ~ 15 MB   (Updated frequently)
```

### 6.2 Delta Transfer Benefits
- When NebuOS releases a minor desktop bugfix (e.g. `nebu-shell` update), `bootc` downloads **only Layers 4 and 5** (~60 MB total), completely skipping Layers 0 through 3.
- All layer blobs are compressed using `zstd:chunked` compression, enabling random-access reading and reduced CPU overhead during decompression.

---

## 7. Architecture Support & Hardware Gating

- **Primary Architecture:** `x86_64` (v3 microarchitecture baseline with AVX2/FMA support).
- **Secondary Architecture:** `aarch64` (ARM64).
- **Gating Policy:** While `aarch64` container builds may run in CI for forward compatibility, **no ARM64 update channel is exposed to users** until physical ARM64 desktop hardware is certified in Milestone P7.

---

## 8. NVIDIA Driver Layering Architecture

NVIDIA proprietary graphics drivers cannot be legally redistributed as an integrated part of the open-source base image. Furthermore, dynamic local compilation (DKMS / akmods) violates the read-only immutability invariant of NebuOS.

### 8.1 Dedicated Pre-Built Driver Layers
1. **OCI Driver Extension Layer:** CI compiles the NVIDIA kernel module (`nvidia.ko`, `nvidia-modeset.ko`, `nvidia-uvm.ko`) and packages userspace libraries into a container extension layer (`quay.io/nebuos/driver-nvidia:<kernel-ver>`).
2. **Lockstep Build:** The driver layer is built against the exact kernel header package of the base OS image.
3. **Layer Composition:** On systems with NVIDIA GPUs, `bootc` pulls the base image combined with the matching NVIDIA layer.
4. **Failure Prevention:** If the NVIDIA driver build fails in CI, the entire release is blocked. The system will never ship a kernel update that leaves NVIDIA users with broken graphics.

---

## 9. Fedora Upstream Maintenance

NebuOS tracks upstream Fedora Atomic releases with a structured cadence:

| Upstream Event | NebuOS Classification | CI / Engineering Action | Target Channel |
|---|---|---|---|
| **Routine Package Security Update** | Normal Base Rebuild | Automated CI build -> Smoke test -> Promote | `testing` -> `stable` (3 days) |
| **Upstream Kernel Minor Bump (e.g. 6.14 -> 6.15)** | Driver ABI Validation | Automated CI build -> Full QEMU boot -> Hardware Lab GPU test | `testing` (7 days) -> `stable` |
| **Major Fedora Release (e.g. Fedora 44 -> 45)** | Major Release Event | Dedicated branch -> Re-compile all crates -> Full Compatibility Lab Suite | Dedicated Beta (30 days) -> `stable` |

---

## 10. Resource Budgets & Build SLAs

- **Base Image Download Size (Compressed):** <= 1.2 GB.
- **Installed Uncompressed Sysroot Footprint:** <= 3.2 GB.
- **CI Build Time (8-core runner with cached layers):** <= 12 minutes.
- **Reproducibility Assertion:** `SOURCE_DATE_EPOCH` is pinned to commit timestamp; file ordering in tar archives is sorted deterministically.

---

## 11. Related Specifications
- [00-update-specification.md](00-update-specification.md) — Master update specification.
- [02-release-channels.md](02-release-channels.md) — Channel definitions and promotion criteria.
- [03-regression-gates.md](03-regression-gates.md) — Automated quality gates.
- [../decisions/ADR-0011-os-image-updates-and-rollback.md](../decisions/ADR-0011-os-image-updates-and-rollback.md) — Binding architectural decision.
