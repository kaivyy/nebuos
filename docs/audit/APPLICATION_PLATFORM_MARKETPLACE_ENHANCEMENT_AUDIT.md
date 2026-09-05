# Application Platform & Nebu Marketplace Phase Enhancement Audit Report — NebuOS

**Document ID:** NEBU-AUDIT-APP-MKT-2026-001  
**Audit Date:** 2026-09-04  
**Auditor Roles:** Principal Developer Experience Architect, Application Platform Lead, Linux Systems Architect, Security Architect, Release Gate Auditor  
**Audit Scope:** Full repository forensic audit and architecture enhancement establishing the Application Platform, Flatpak packaging foundation, Flathub discovery integration, Fedora repository separation, Nebu App Manager abstraction, native Nebu Marketplace, permission governance, and developer platform for Milestone P6 and Phase P8.  
**Final Audit Status:** **PASS WITH NOTES**  

---

## 1. Executive Summary

This audit report documents the comprehensive phase enhancement integrating the **Application Platform** and **Nebu Marketplace** into the architectural baseline and engineering roadmap of NebuOS.

NebuOS provides a unified, distraction-free desktop operating system where users can seamlessly discover, install, launch, and manage both native Linux software and certified Windows applications without running virtual machines or mutating the immutable host operating system. To achieve this without embarking on a multi-year effort to build a proprietary package ecosystem from scratch, NebuOS formally establishes an architecture built upon mature, battle-tested upstream foundations:
1. **Flatpak Foundation:** Flatpak is established as the primary packaging and unprivileged sandboxing foundation for third-party Linux desktop applications.
2. **Flathub Discovery:** Flathub is leveraged as an external upstream discovery and retrieval ecosystem. NebuOS does not fork Flathub, does not host complete Flathub mirrors, and does not claim ownership of upstream packages.
3. **Fedora Repository Separation:** Fedora RPM repositories provide base OS components and development containers, strictly isolated from desktop end-user applications.
4. **Dedicated Windows Compatibility Pathway:** Windows applications are not packaged into Flatpaks; they are managed through declarative installation recipes and executed via the Nebu Compatibility Engine (`nebu-runtime-daemon`) in isolated per-application Btrfs prefixes.
5. **Nebu App Manager Abstraction:** The Marketplace UI and NebuShell launcher never invoke package managers directly. All transactions route through `nebu-app-manager-daemon` via D-Bus (`org.nebu.AppManager1`).
6. **Milestone Allocation:** Application Platform and Marketplace implementation is formally assigned to **Milestone P6** (with subphases P6.0 through P6.4) and Phase P8 (Production Readiness). Zero implementation code was created during this audit; Milestone P0 remains the active next implementation milestone.

The final verdict of this enhancement audit is **PASS WITH NOTES**. All architectural decisions, specifications, roadmaps, agent contracts, skills, traceability matrices, risk registers, and project state snapshots are completely aligned. The sole "note" designates that actual implementation of all application platform and marketplace crates is strictly deferred to Milestone P6.

---

## 2. Current Architecture Assessment

Prior to this phase enhancement, the repository exhibited several architectural ambiguities regarding application distribution:
- **Generic "Software Center":** Earlier specifications described a generic dual-catalog store without defining the concrete packaging mechanisms, runtime dependencies, or sandbox boundaries for Linux software.
- **Unclear Packaging Technology:** PRD §45 and §46 mentioned package management and application stores, but the relationship between the host `bootc` immutable sysroot, Flatpaks, and local RPMs was not formally codified in a dedicated ADR.
- **Risk of Direct Packaging Invocations:** Without an explicit abstraction daemon, there was a risk that frontend developers might spawn shell processes or call package manager CLIs directly from the UI.
- **Conflated Lifecycles:** The separation between base OS transactional updates (`bootc`), application updates, compatibility database updates, and firmware updates was not comprehensively cross-referenced across all governance files.

Through this enhancement, these ambiguities have been decisively resolved with the approval of `ADR-0012`, the expansion of Phase P6 in the implementation roadmap, the publication of four in-depth application specifications, and the updating of universal agent governance.

---

## 3. Application Distribution Strategy

NebuOS enforces a **pragmatic, modular, and non-reinventing** application distribution strategy:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Nebu Marketplace UI                             │
│                  (Native Rust Slint GUI Client)                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Session D-Bus (org.nebu.AppManager1)
                                    v
┌────────────────────────────────────────────────────────────────────────┐
│                       Nebu App Manager Daemon                          │
│               (Policy, Lifecycle, Staging, SQLite Index)               │
└───────┬───────────────────────────┼───────────────────────────┬────────┘
        │                           │                           │
        v                           v                           v
┌───────────────┐           ┌───────────────┐           ┌────────────────┐
│Flatpak Adapter│           │Fedora Adapter │           │ Compat Adapter │
│ (libflatpak)  │           │(Host/Toolbx)  │           │(nebu-runtime-d)│
└───────┬───────┘           └───────┬───────┘           └───────┬────────┘
        │                           │                           │
        v                           v                           v
┌───────────────┐           ┌───────────────┐           ┌────────────────┐
│    Flathub    │           │ Fedora Repos  │           │ Windows Recipe │
│  Repositories │           │  (Base/Tools) │           │    Catalog     │
└───────────────┘           └───────────────┘           └────────────────┘
```

The strategy adheres to four cardinal invariants:
1. **Never mutate `/usr`:** All third-party software installs to user space (`~/.local/share/flatpak`) or persistent system state (`/var/lib/flatpak`).
2. **Abstract all backends:** The frontend is completely decoupled from backend CLI/library details.
3. **Transparent consent:** Permissions are visualized and authorized before byte download.
4. **Clean removal:** Uninstalling an application purges 100% of its binaries, configurations, prefixes, and shortcuts.

---

## 4. Flatpak Assessment

Flatpak is selected as the primary desktop application distribution and runtime packaging technology for NebuOS:
- **Sandbox Architecture:** Flatpak utilizes unprivileged user namespaces and Bubblewrap (`bwrap`), ensuring that applications run confined without root privileges.
- **Runtimes & SDKs:** Applications share standardized base runtimes (`org.freedesktop.Platform`, `org.gnome.Platform`, `org.kde.Platform`), eliminating duplicate system libraries across applications from the same ecosystem.
- **Portals Integration:** Hardware access (cameras, microphones, file choosers, screen sharing) is mediated via XDG Desktop Portals (`xdg-desktop-portal-nebu`), granting user-controlled fine-grained access.
- **Storage Compatibility:** User-level Flatpaks live in `~/.local/share/flatpak`, while system Flatpaks live in `/var/lib/flatpak`. Both locations reside on the persistent, writable Btrfs `@home` and `@var` subvolumes, fully compatible with the read-only `/usr` sysroot.
- **Deduplication & Compression:** Btrfs filesystem extent sharing and `zstd:1` compression significantly reduce the on-disk footprint of shared Flatpak runtimes.

---

## 5. Flathub Assessment

Flathub is established as the primary external application discovery and retrieval source:
- **Catalog Scale:** Flathub hosts thousands of popular, up-to-date desktop applications (Blender, Steam, Spotify, VS Code, Discord, LibreOffice, GIMP, OBS Studio) packaged directly by upstream developers.
- **Standardized AppStream Metadata:** Applications provide rich `appdata.xml` / `metainfo.xml` specifications containing descriptions, release notes, categories, project URLs, and screenshots.
- **Clear Architectural Boundary:**
  - NebuOS interacts with Flathub strictly as an **external catalog consumer**.
  - NebuOS **does not claim ownership** of Flathub software.
  - NebuOS **does not fork Flathub**.
  - NebuOS **does not build a Flathub mirror/CDN** in initial phases.

---

## 6. Fedora Repository Assessment

Fedora repositories serve as a **complementary** source for the operating system:
- **OS Base Composition:** Fedora 44 repositories are utilized by the CI build system to construct the immutable base OS image deployed via `bootc`.
- **System Command-Line Tools:** Core development utilities and low-level diagnostic tools are baked into the OS image or layered via development containers (Toolbx/Distrobox).
- **Strict Distinction:** End-user desktop applications are **not** installed directly from Fedora RPM repositories via mutable host package managers (`dnf`). This prevents library collisions, maintains host immutability, and guarantees clean uninstallation.

---

## 7. Nebu Marketplace Architecture

The Nebu Marketplace (`crates/nebu-marketplace-ui/`) is specified in [`docs/applications/06-software-center.md`](file:///root/NebuOS/docs/applications/06-software-center.md):
- **Native Implementation:** Developed in pure Rust using the **Slint** UI framework.
- **Zero Heavy Web Engines:** Strictly prohibits Electron, Chromium, or embedded WebKit runtimes.
- **Memory Footprint:** Idle memory consumption strictly capped at <= 35 MB RSS.
- **Four Core Views:**
  1. *Discover:* Featured banners, trending apps, editorial highlights, hardware-tailored recommendations.
  2. *Categories:* Browsable taxonomy (Audio/Video, Development, Graphics, Internet, Office, Games, Education, Utilities, System).
  3. *Installed:* Installed application management, version badges, storage metrics, and uninstallation triggers.
  4. *Updates:* Centralized notification and update triggers for applications.
- **Instant Search:** Local full-text search responding in <= 40 ms via SQLite FTS5 trigram indexes.

---

## 8. Nebu App Manager Architecture

The Nebu App Manager daemon (`crates/nebu-app-manager-daemon/`) is specified in [`docs/applications/07-app-manager-specification.md`](file:///root/NebuOS/docs/applications/07-app-manager-specification.md):
- **Process Model:** Runs as an unprivileged user service (`systemd --user`) via `packaging/systemd/user/nebu-app-manager.service`.
- **D-Bus Interface:** Publishes `org.nebu.AppManager1` and `org.nebu.AppSource1` on the session bus.
- **`ApplicationSource` Trait:** Normalizes interactions across Flatpak, Fedora, and Windows recipe backends.
- **10-State Application Lifecycle:** Manages deterministic state transitions (`Discover -> Inspect -> Verify -> Install -> Register -> Launch -> Update -> Disable -> Repair -> Uninstall`).
- **Resilient Operations:** Implements HTTP range request resumption, pre-flight disk space probes, and atomic staging directory cleanups.

---

## 9. Application Security

The security model is specified in [`docs/applications/08-developer-platform-and-security.md`](file:///root/NebuOS/docs/applications/08-developer-platform-and-security.md):
- **Defense-in-Depth:** Separates Publisher Trust, Package Integrity, Runtime Sandbox, and Application Compatibility.
- **Mandatory Verification:** Cryptographic signatures (GPG, Cosign) and SHA-256 checksums are verified before any package is staged.
- **Never Assume Safety:** Applications from Flathub are never labeled "100% Safe" by default; all applications run in strict Bubblewrap user namespaces.
- **Incident Response & Takedown:** Supports remote revocation lists (`revocations.json`) allowing compromised package versions to be quarantined and unmapped from user launchers within seconds.

---

## 10. Permission Architecture

The permission architecture empowers users with complete transparency:
- **Pre-Installation Consent:** The Marketplace UI presents an understandable permission card detailing requested entitlements before download.
- **Categorized Entitlements:**
  - *Network:* Online streaming, updates, telemetry.
  - *Audio/Video:* Sound playback, microphone input, camera capture.
  - *Filesystem:* User documents, downloads, removable storage, or unconfined home access.
  - *Hardware:* GPU acceleration, USB controllers, Bluetooth adapters.
  - *IPC:* D-Bus session bus or system bus endpoints.
- **Post-Installation Control:** Users can audit and toggle permissions at any time via NebuOS System Settings without modifying the application binary.

---

## 11. Application Compatibility

Compatibility transparency is built directly into the Marketplace catalog:
- **Compatibility Badges:**
  - *Verified:* Tested in Compatibility Lab; 100% functional.
  - *Compatible:* Community tested; functional with minor cosmetic quirks.
  - *Partially Compatible:* Specific features limited (e.g. cloud sync unavailable).
  - *Known Issues:* Explicitly lists known limitations before user installs.
  - *Not Tested:* Unverified application.
- **Quantitative Scoring:** Windows applications display compatibility scores (0–100) generated from automated Compatibility Lab test runs (Milestone P7).

---

## 12. Windows Application Strategy

Windows applications are architecturally isolated from native Linux packages:
- **No Flatpak Packaging:** Windows applications are never forced into Flatpak bundles.
- **Recipe-Driven Installation:** The Marketplace indexes declarative Windows application recipes.
- **Dedicated Prefixes:** Installations execute via `nebu-installer-ui` into isolated Btrfs reflink prefixes (`~/.nebu/apps/<app-id>/`).
- **Supervised Execution:** Runtimes are supervised by `nebu-runtime-daemon` with custom DLL overrides, registry tweaks, and DXVK/VKD3D translation.

---

## 13. Application Update Architecture

NebuOS strictly enforces a **Four-Way Update Separation**:

```text
┌───────────────────────────────┬───────────────────────────────┬───────────────────────────────┐
│ Update Domain                 │ Mechanism / Backend           │ Activation Lifecycle          │
├───────────────────────────────┼───────────────────────────────┼───────────────────────────────┤
│ 1. Operating System Base      │ bootc / OSTree                │ Staged live -> Active reboot  │
│ 2. Desktop Applications       │ Flatpak / Nebu App Manager    │ Staged live -> Live restart   │
│ 3. Compatibility DB & Recipes │ Nebu Compatibility Daemon     │ SQLite delta -> Instant reload│
│ 4. Hardware Firmware          │ fwupd / LVFS                  │ Staged -> Reboot / Capsule    │
└───────────────────────────────┴───────────────────────────────┴───────────────────────────────┘
```

Conflating these update channels is strictly prohibited. Desktop application updates must never prompt for or require an OS reboot.

---

## 14. Developer Platform & Publisher Model

Subphase P6.3 establishes the developer onboarding and submission pipeline:
- **Publisher Verification Tiers:**
  - *Tier 1 (Official Upstream):* Verified domain ownership and cryptographic keys matched directly to upstream software maintainers.
  - *Tier 2 (Community Verified):* Vetted community packagers.
  - *Tier 3 (Unverified):* Flagged with security notices.
- **Automated Validation Pipeline:** Developer submissions undergo automated AppStream XML validation, static malware analysis (ClamAV, YARA), license checking, and sandbox permission auditing.
- **Review & Promotion:** Staged promotion pipeline: `Draft -> Automated Scan -> Compatibility Lab -> Staged Canary -> Public Release`.

---

## 15. Privacy & Telemetry

Nebu Marketplace adheres to strict privacy-by-design principles:
- **Zero Search Profiling:** User search queries execute entirely against the local SQLite metadata cache (`marketplace.db`). Keywords are never transmitted to remote servers.
- **No Dwell/Behavioral Tracking:** The Marketplace does not profile user browsing habits or application usage frequency.
- **Direct Source Attribution:** Application downloads connect directly to upstream CDN endpoints without tracking proxies.

---

## 16. Performance & Multi-Architecture

- **Memory Budgets:**
  - `nebu-marketplace-ui`: Idle RSS <= 35 MB.
  - `nebu-app-manager-daemon`: Idle RSS <= 18 MB.
- **Latency Targets:**
  - Cold startup time <= 250 ms.
  - Full-text search response <= 40 ms.
  - Launch dispatch overhead <= 30 ms.
- **Multi-Architecture:** Initial baseline for Milestone P0 is `x86_64`; architecture and data structures explicitly accommodate `aarch64` (ARM64).

---

## 17. Roadmap Integration

The implementation roadmap (`docs/roadmap/00-implementation-roadmap.md`) has been updated to formally establish:
- **Phase P6: Application Platform & Nebu Marketplace**
  - *P6.0: Application Runtime & App Management*
  - *P6.1: Nebu Marketplace*
  - *P6.2: Application Security*
  - *P6.3: Developer Platform*
  - *P6.4: Ecosystem Integration*
- **Phase P8: Production Validation**
  - Added production signing infrastructure (Cosign, Rekor), CDN mirrors, abuse response, and automated revocation pipelines.

---

## 18. AGENTS.md Alignment

`AGENTS.md` was updated with:
- **Section 6 Table:** Updated Milestone P6 row to `Application Platform & Marketplace` with subphases P6.0–P6.4.
- **Section 22 (Application Platform & Marketplace Governance Policy):** Codified strict rules prohibiting custom package managers, forking Flathub, direct package manager spawning from UI, Electron/webviews, premature monetization, and conflating updates.

---

## 19. SKILL.md Alignment

- **New Skill Created:** [`skills/application/SKILL.md`](file:///root/NebuOS/skills/application/SKILL.md) covering the entire Application Platform, Flatpak integration, App Manager daemon, and Marketplace UI.
- **`skills/README.md`:** Catalog updated to include `application/` skill.
- **`skills/architecture/SKILL.md`:** Updated with Application Platform constraints and update lifecycle separation.
- **`skills/security/SKILL.md`:** Updated with application security model, trust tiers, and permission inspection.
- **`skills/release/SKILL.md`:** Updated with Four-Way Update Separation and reference to `ADR-0012`.
- **`skills/shell/SKILL.md`:** Updated with prohibition against embedding Marketplace into shell core.

---

## 20. ADR Alignment

Approved and published:
- [`docs/decisions/ADR-0012-application-distribution-and-marketplace.md`](file:///root/NebuOS/docs/decisions/ADR-0012-application-distribution-and-marketplace.md)
  - Formalizes Flatpak choice, Flathub discovery, Fedora separation, Nebu App Manager abstraction, Windows compatibility separation, and update independence.

---

## 21. Traceability

[`docs/TRACEABILITY.md`](file:///root/NebuOS/docs/TRACEABILITY.md) was updated:
- Section 2.9 (Package Management, Application Platform & Marketplace) links PRD Sec 45 and Sec 46, as well as subphases P6.0 through P6.4, to `ADR-0012`, `applications/00`, `06`, `07`, `08`, and test cases `TEST-PKG-001`, `TEST-STORE-001`, `TEST-MGR-001`, `TEST-MKT-001`, `TEST-SEC-002`, `TEST-DEV-001`, and `TEST-ECO-001`.

---

## 22. Risk Register

[`docs/RISK_REGISTER.md`](file:///root/NebuOS/docs/RISK_REGISTER.md) was expanded with risks `RSK-044` through `RSK-055`:
- `RSK-044`: Flathub CDN/API outage
- `RSK-045`: Upstream AppStream schema drift
- `RSK-046`: Publisher trust compromise / malicious package submission
- `RSK-047`: Package signing key compromise / supply-chain tampering
- `RSK-048`: Supply-chain vulnerability in bundled Flatpak libraries
- `RSK-049`: Flatpak / Bubblewrap sandbox escape vulnerability
- `RSK-050`: Incompatible application update breaking user workflows
- `RSK-051`: Disk space exhaustion from redundant Flatpak runtimes
- `RSK-052`: Network disconnect during multi-gigabyte package downloads
- `RSK-053`: Legal / DMCA notice regarding third-party recipe
- `RSK-054`: Marketplace metadata origin server outage
- `RSK-055`: Windows application compatibility drift across Wine runtime updates.

---

## 23. Open Questions

[`docs/OPEN_QUESTIONS.md`](file:///root/NebuOS/docs/OPEN_QUESTIONS.md) was updated with unresolved design questions:
- `OQ-043`: Flathub metadata sync strategy (local FTS5 cache vs on-demand API)
- `OQ-044`: Future Nebu Repository hosting infrastructure
- `OQ-045`: Publisher verification levels and KYC workflows
- `OQ-046`: Commercial software & donation support model
- `OQ-047`: Emergency remote package revocation and automated quarantine protocol
- `OQ-048`: Multi-source enterprise and private repository support.

---

## 24. Files Changed

The following files were modified to achieve full architectural synchronization:
1. `AGENTS.md`
2. `docs/roadmap/00-implementation-roadmap.md`
3. `docs/applications/00-application-specification.md`
4. `docs/applications/06-software-center.md`
5. `skills/README.md`
6. `skills/architecture/SKILL.md`
7. `skills/security/SKILL.md`
8. `skills/release/SKILL.md`
9. `skills/shell/SKILL.md`
10. `PROJECT_STATE.md`
11. `docs/TRACEABILITY.md`
12. `docs/RISK_REGISTER.md`
13. `docs/OPEN_QUESTIONS.md`
14. `docs/INDEX.md`

---

## 25. Files Created

The following authoritative architectural files were authored:
1. `docs/decisions/ADR-0012-application-distribution-and-marketplace.md`
2. `docs/applications/07-app-manager-specification.md`
3. `docs/applications/08-developer-platform-and-security.md`
4. `skills/application/SKILL.md`
5. `docs/audit/APPLICATION_PLATFORM_MARKETPLACE_ENHANCEMENT_AUDIT.md`

---

## 26. Remaining Issues & Debt

1. **Zero Implementation Code:** In strict adherence to governance and anti-scope rules, zero application platform or marketplace source code was authored. All crates (`crates/nebu-app-manager-daemon/`, `crates/nebu-marketplace-ui/`, `crates/nebu-installer-ui/`) will be developed in Milestone P6.
2. **Upstream API Endpoint Finalization:** Exact REST/GraphQL API endpoints for Flathub metadata queries will be finalized upon commencement of Subphase P6.1.
3. **P0 Implementation Independence:** Milestone P0 (Foundation OS) remains 100% unaffected and is ready to start immediately.

---

## 27. Final Verdict

**Verdict:** **PASS WITH NOTES**

**Justification:**
- The Application Platform and Nebu Marketplace architecture is comprehensively defined, rigorously grounded in Flatpak and Flathub, and completely isolated from the base OS immutable sysroot.
- The `Nebu App Manager` abstraction guarantees that user interfaces never invoke package backends directly.
- The 10-state lifecycle, permission transparency, security trust tiers, and developer platform are fully documented.
- All universal agent instructions, domain skills, decision records, roadmap phases, risk matrices, and state tracking files are synchronized.
- Zero premature implementation code was introduced, preserving milestone discipline.
- The "NOTES" designation formally records that actual implementation is deferred to Milestone P6, with Milestone P0 remaining the active next engineering milestone.
