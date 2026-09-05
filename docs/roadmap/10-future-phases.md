# Future Phases Specification — NebuOS

**Status:** PROPOSED  
**Target:** Post-1.0 Milestones (P9+)  

---

## 1. Objective
Establish the strategic engineering roadmap and technical exploration pathways for NebuOS following the 1.0 General Availability release.

## 2. Post-1.0 Phase Roadmap

### Phase P9: ARM64 (AArch64) Architecture Support
- **Scope:** Porting NebuOS base image and native Rust daemons to 64-bit ARM architectures (Apple Silicon Macs via Asahi Linux, Snapdragon X Elite laptops, Raspberry Pi 5).
- **Compatibility Engine:** Integration of FEX-Emu or Box64 binary translation layers to execute x86_64 Windows PE binaries on ARM64 processors.
- **Challenges:** Page size discrepancies (4KB vs 16KB on Apple Silicon), translation memory overhead, SIMD translation latency.

### Phase P10: Enterprise Central Management & Directory Integration
- **Scope:** Fleet management, remote image provisioning, and centralized configuration policies.
- **Features:**
  - FreeIPA / Active Directory domain join for single-sign-on (SSO).
  - Remote compatibility database sync and enterprise-internal profile repositories.
  - Centralized software whitelist/blacklist policy enforcement.

### Phase P11: Advanced Gaming & VR Subsystem
- **Scope:** Enhanced gaming performance and virtual reality headset integration.
- **Features:**
  - Native OpenXR / Monado runtime integration for Windows VR titles.
  - Latency reduction through frame generation (FSR 3 / XeSS frame interpolation).
  - Advanced per-game GPU overclocking and fan curve management.

### Phase P12: NebuCloud Hybrid Workspace Sync
- **Scope:** Seamless, end-to-end encrypted backup and synchronization of application prefixes across devices.
- **Features:**
  - Incremental Btrfs send/receive delta sync to private user cloud storage.
  - Seamless desktop state resumption across desktop PC and laptop.

## 3. Guiding Principles for Future Phases
- Never compromise the core invariants: No VMs, lightweight performance, memory safety, and immutable base OS.
- All future features must continue to respect the 4GB RAM baseline constraints.
