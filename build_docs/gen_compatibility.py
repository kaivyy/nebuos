#!/usr/bin/env python3
"""
Generate Compatibility Documentation for NebuOS (docs/compatibility/):
- 00-compatibility-overview.md
- 01-database-schema.md
- 02-profiles.md
- 03-patching.md
- 04-certification.md
- 05-test-matrix.md
- 06-known-limitations.md
"""

import os

DOCS_DIR = "/root/NebuOS/docs/compatibility"
os.makedirs(DOCS_DIR, exist_ok=True)

def write_file(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: compatibility/{filename} ({len(content.splitlines())} lines)")

# 00-compatibility-overview.md
write_file("00-compatibility-overview.md", """# Compatibility Overview — NebuOS

**Status:** REVIEW  
**Purpose:** Establish the core engineering principles, testing rigor, and compatibility philosophy of NebuOS.

---

## 1. The Core NebuOS Differentiator
The fundamental value proposition of NebuOS is not merely a custom desktop UI. The defining differentiator is the **Nebu Compatibility Platform**:
```text
Nebu Compatibility Platform = 
    Nebu Runtime 
  + Upstream Wine/Proton 
  + SQLite Compatibility Database 
  + Layered Patch Engine 
  + Adaptive Graphics Translation 
  + Compatibility Lab 
  + Automated Regression Gates
```

## 2. The Verification Invariant: Beyond "Application Opens"
In NebuOS, an application is never considered compatible simply because its executable launches a window without crashing. Real compatibility demands thorough verification of production workflows:

```mermaid
flowchart LR
    INSTALL["1. INSTALL"] --> LAUNCH["2. LAUNCH"]
    LAUNCH --> OPEN["3. OPEN REAL PROJECT"]
    OPEN --> EDIT["4. EDIT"]
    EDIT --> SAVE["5. SAVE"]
    SAVE --> EXPORT["6. EXPORT PDF/DWG"]
    EXPORT --> PRINT["7. PRINT"]
    PRINT --> GPU["8. GPU ACCELERATION"]
    GPU --> PLUGIN["9. PLUGINS/MACROS"]
    PLUGIN --> STRESS["10. STRESS TEST"]
    STRESS --> CLOSE["11. CLOSE & REOPEN"]
```

Only when all 11 stages succeed without corruption or visual artifacts is an application awarded **CERTIFIED** status.

## 3. Related Documents
- [01-database-schema.md](01-database-schema.md)
- [02-profiles.md](02-profiles.md)
- [04-certification.md](04-certification.md)
""")

# 01-database-schema.md
write_file("01-database-schema.md", """# Compatibility Database Schema Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define the relational SQLite database schema storing application compatibility metadata, profiles, hardware matrices, and certification results.

---

## 1. Database Architecture
- **Engine:** SQLite 3 with Write-Ahead Logging (WAL) enabled (`PRAGMA journal_mode=WAL;`).
- **File Location:** System catalog at `/usr/share/nebu/compat.db` (read-only); user overrides at `~/.local/share/nebu/user_compat.db`.
- **Query Performance:** Indexed lookup by SHA-256 or PE header signature resolves in < 2ms.

## 2. Entity-Relationship Diagram

```mermaid
erDiagram
    APPLICATION ||--o{ APPLICATION_VERSION : has
    APPLICATION_VERSION ||--o{ COMPAT_PROFILE : configures
    COMPAT_PROFILE ||--o{ PROFILE_DEPENDENCY : requires
    COMPAT_PROFILE ||--o{ PROFILE_PATCH : applies
    COMPAT_PROFILE ||--o{ TEST_RUN : verified_by
    APPLICATION_VERSION ||--o{ KNOWN_ISSUE : tracks
    APPLICATION_VERSION ||--|| CERTIFICATION : awarded
```

## 3. Complete DDL Schema

```sql
-- Applications Catalog
CREATE TABLE applications (
    app_id TEXT PRIMARY KEY,          -- e.g. 'autodesk.autocad'
    name TEXT NOT NULL,                -- e.g. 'Autodesk AutoCAD'
    vendor TEXT NOT NULL,              -- e.g. 'Autodesk'
    category TEXT NOT NULL,            -- 'cad', 'office', 'creative', 'game'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Version Specific Entities
CREATE TABLE application_versions (
    version_id TEXT PRIMARY KEY,       -- e.g. 'autodesk.autocad.2024'
    app_id TEXT NOT NULL REFERENCES applications(app_id) ON DELETE CASCADE,
    version_string TEXT NOT NULL,      -- e.g. '2024.1.2'
    architecture TEXT NOT NULL,        -- 'x86_64', 'x86'
    pe_sha256 TEXT UNIQUE,             -- SHA256 of main setup.exe / binary
    installer_type TEXT NOT NULL       -- 'msi', 'inno', 'nsis', 'custom'
);

-- Compatibility Configuration Profiles
CREATE TABLE compat_profiles (
    profile_id TEXT PRIMARY KEY,       -- e.g. 'profile.autodesk.autocad.2024.v1'
    version_id TEXT NOT NULL REFERENCES application_versions(version_id),
    runtime_type TEXT NOT NULL,        -- 'wine', 'proton'
    runtime_version TEXT NOT NULL,     -- 'wine-staging-9.2', 'proton-9.0'
    windows_version TEXT NOT NULL,     -- 'win10', 'win11'
    env_vars_json TEXT,                -- '{"DXVK_ASYNC": "1", "DRI_PRIME": "1"}'
    dll_overrides_json TEXT,           -- '{"d3d11": "native,builtin", "dxgi": "native"}'
    registry_keys_json TEXT,           -- Registry inject array
    graphics_backend TEXT NOT NULL,    -- 'dxvk', 'vkd3d', 'wined3d', 'vulkan'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dependencies
CREATE TABLE profile_dependencies (
    dep_id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id TEXT NOT NULL REFERENCES compat_profiles(profile_id),
    package_name TEXT NOT NULL,        -- 'vcrun2019', 'dotnet48', 'corefonts'
    sha256 TEXT NOT NULL,
    install_order INTEGER NOT NULL
);

-- Patches
CREATE TABLE profile_patches (
    patch_id TEXT PRIMARY KEY,         -- e.g. 'patch.autodesk.license_stub.v1'
    profile_id TEXT NOT NULL REFERENCES compat_profiles(profile_id),
    patch_tier INTEGER NOT NULL,       -- 1=env, 2=wine_cfg, 3=reg, 4=dll, 5=com, etc.
    patch_type TEXT NOT NULL,          -- 'registry_merge', 'file_replace', 'dll_shim'
    payload TEXT NOT NULL,             -- Declarative diff or JSON payload
    reversible BOOLEAN NOT NULL DEFAULT 1
);

-- Certification & Status
CREATE TABLE certifications (
    cert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id TEXT NOT NULL REFERENCES application_versions(version_id),
    status TEXT NOT NULL,              -- 'CERTIFIED', 'SUPPORTED', 'MOSTLY_COMPATIBLE', 'LIMITED', 'BROKEN', 'UNSUPPORTED'
    score_percentage INTEGER NOT NULL, -- 0 to 100
    tested_os_version TEXT NOT NULL,   -- 'NebuOS 1.0'
    tested_kernel TEXT NOT NULL,       -- '6.10.3'
    tested_mesa TEXT NOT NULL,         -- '24.1.5'
    tested_wine TEXT NOT NULL,         -- '9.2-staging'
    tested_gpu TEXT NOT NULL,          -- 'AMD Radeon RX 6600'
    evaluation_date DATE NOT NULL
);

-- Known Limitations & Issues
CREATE TABLE known_issues (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id TEXT NOT NULL REFERENCES application_versions(version_id),
    severity TEXT NOT NULL,            -- 'blocker', 'major', 'minor', 'cosmetic'
    description TEXT NOT NULL,
    workaround TEXT
);

-- Indexes for Sub-millisecond Lookup
CREATE INDEX idx_app_versions_pe_sha ON application_versions(pe_sha256);
CREATE INDEX idx_compat_profiles_version ON compat_profiles(version_id);
CREATE INDEX idx_certifications_version ON certifications(version_id);
```

## 4. Related Documents
- [00-compatibility-overview.md](00-compatibility-overview.md)
- [02-profiles.md](02-profiles.md)
- [04-certification.md](04-certification.md)
""")

# 02-profiles.md
write_file("02-profiles.md", """# Compatibility Profiles Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define the structure, format, and resolution rules for application-specific compatibility profiles.

---

## 1. Profile Hierarchy & Taxonomy
Profiles follow a reverse-DNS naming convention structured by vendor, application name, and release version:
```text
profiles/
├── microsoft/
│   ├── office.2019.json
│   ├── office.2021.json
│   └── office.2024.json
├── autodesk/
│   ├── autocad.2024.json
│   ├── maya.2026.json
│   └── 3dsmax.2026.json
├── adobe/
│   ├── photoshop.2024.json
│   └── illustrator.2024.json
└── games/
    └── default-proton.json
```

## 2. Sample Certified Profile: Autodesk AutoCAD 2024

```json
{
  "profile_id": "autodesk.autocad.2024",
  "name": "Autodesk AutoCAD 2024",
  "runtime": {
    "engine": "wine",
    "version": "wine-staging-9.x",
    "windows_version": "win10"
  },
  "graphics": {
    "backend": "dxvk",
    "d3d11_feature_level": "11_1",
    "prefer_dgpu": true,
    "dxvk_config": {
      "d3d11.maxTessFactor": 64,
      "dxgi.syncInterval": 1
    }
  },
  "dll_overrides": {
    "d3d11": "native,builtin",
    "dxgi": "native,builtin",
    "d3dcompiler_47": "native"
  },
  "dependencies": [
    { "id": "vcrun2019", "order": 1 },
    { "id": "dotnet48", "order": 2 },
    { "id": "corefonts", "order": 3 }
  ],
  "registry_injections": [
    {
      "key": "HKEY_CURRENT_USER\\\\Software\\\\Wine\\\\Direct3D",
      "value": "MaxVersionGL",
      "type": "DWORD",
      "data": 40006
    }
  ],
  "sandbox": {
    "allow_network": true,
    "expose_directories": ["~/Documents/CAD", "~/Downloads"]
  }
}
```

## 3. Related Documents
- [01-database-schema.md](01-database-schema.md)
- [03-patching.md](03-patching.md)
""")

# 03-patching.md
write_file("03-patching.md", """# Patch Engine Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Detail `nebu-patcher`, the 9-tier compatibility patch hierarchy, and transactional patch rollback.

---

## 1. The 9-Tier Patch Hierarchy
To maintain maintainability and avoid destabilizing modifications, `nebu-patcher` strictly enforces a 9-tier priority ladder. Lower-impact configuration fixes MUST be attempted before invasive shims or binary alterations:

```mermaid
graph TD
    T1["Tier 1: Environment Variables (DRI_PRIME, WINEFSYNC)"] --> T2["Tier 2: Wine Configuration (winecfg, winver)"]
    T2 --> T3["Tier 3: Registry Modifications (regedit injection)"]
    T3 --> T4["Tier 4: DLL Configuration & Overrides (native vs builtin)"]
    T4 --> T5["Tier 5: COM / OLE Registration (regsvr32 stubs)"]
    T5 --> T6["Tier 6: .NET Framework Runtime Configuration"]
    T6 --> T7["Tier 7: Graphics Backend Overrides (DXVK, wined3d, VKD3D)"]
    T7 --> T8["Tier 8: Wine API Implementation Improvements (Upstream Patches)"]
    T8 --> T9["Tier 9: Binary Modification (Strictly Last Resort / Discouraged)"]
```

## 2. Patch Atomicity & Rollback
Every patch executed by `nebu-patcher` must provide an inverse operation:
- **Registry Patches:** Stored as JSON key-value pairs; prior key states are backed up before writing.
- **File Replacements:** Original files are retained with `.nebu-orig` suffix.
- **Rollback API:** `nebu patch rollback <app_id> <patch_id>` reverts changes in exact reverse chronological order.

## 3. Related Documents
- [00-compatibility-overview.md](00-compatibility-overview.md)
- [02-profiles.md](02-profiles.md)
""")

# 04-certification.md
write_file("04-certification.md", """# Compatibility Certification Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Specify the 7 certification tiers, empirical grading weights, and formal criteria for application certification.

---

## 1. Certification Status Tiers

| Certification Tier | Formal Criteria | User-Facing Indication |
|---|---|---|
| **CERTIFIED** | 100% of critical workflow tests pass. Zero crashes across 48h stress run. GPU acceleration verified. | Green Badge: "Certified for NebuOS" |
| **SUPPORTED** | Core workflows function reliably (>90% score). Minor non-blocking cosmetic defects permitted. | Blue Badge: "Supported" |
| **MOSTLY_COMPATIBLE** | Core editing functions work, but specific advanced features (e.g. cloud sync, macros) have limitations. | Yellow Badge: "Mostly Compatible" |
| **LIMITED** | Requires specific hardware or legacy configuration profile. | Orange Badge: "Limited Compatibility" |
| **UNTESTED** | Application has not completed official QA test suite. Default Wine profile used. | Gray Badge: "Untested" |
| **BROKEN** | Application fails to install, launch, or save files. Known blocker logged. | Red Badge: "Known Broken" |
| **UNSUPPORTED** | Fundamental incompatibility (requires Windows `.sys` kernel drivers, anti-cheat, unsupported DRM). | Black Badge: "Unsupported (Architecture Limit)" |

## 2. Empirical Test Scoring Formula

An application's overall compatibility score ($S$) is calculated as a weighted composite:
```text
S = (Installation * 0.10)
  + (Launch * 0.10)
  + (Core Functionality * 0.30)
  + (File Handling * 0.10)
  + (Graphics & Viewport * 0.15)
  + (Performance & Latency * 0.10)
  + (Plugins & Add-ins * 0.10)
  + (Stability & Reopen * 0.05)
```
- **Threshold for CERTIFIED:** $S \ge 95\%$ with $0\%$ failure in Core Functionality and File Handling.
- **Threshold for SUPPORTED:** $S \ge 85\%$.

## 3. Related Documents
- [00-compatibility-overview.md](00-compatibility-overview.md)
- [05-test-matrix.md](05-test-matrix.md)
- [../testing/03-compatibility-testing.md](../testing/03-compatibility-testing.md)
""")

# 05-test-matrix.md
write_file("05-test-matrix.md", """# Compatibility Test Matrix Specification — NebuOS

**Status:** REVIEW  
**Purpose:** Define the multi-dimensional validation grid testing applications across OS releases, kernels, graphics drivers, and hardware tiers.

---

## 1. Test Grid Dimensions
Every certified application must be validated against the multi-dimensional parameter matrix:

```text
Dimension 1: Target Application & Release Version (e.g., AutoCAD 2024.1)
Dimension 2: NebuOS Platform Release (e.g., NebuOS 1.0 Stable)
Dimension 3: Wine / Proton Runtime Version (e.g., Wine 9.2 Staging)
Dimension 4: Linux Kernel LTS (e.g., Kernel 6.10)
Dimension 5: Mesa Graphics Driver Version (e.g., Mesa 24.1)
Dimension 6: Physical GPU Architecture (Intel Xe, AMD RDNA2, NVIDIA Ada)
Dimension 7: System Memory Allocation (4 GB Low-End, 8 GB Standard, 32 GB Workstation)
```

## 2. Sample Master Compatibility Matrix Row

| Application | Version | NebuOS | Wine | Kernel | Mesa | GPU Hardware | Memory | Test Status |
|---|---|---|---|---|---|---|---|---|
| MS Word | 2021 (x64) | 1.0 Stable | 9.0 | 6.10.3 | 24.1.4 | Intel Iris Xe | 4 GB | **PASS (CERTIFIED)** |
| MS Excel | 2024 (x64) | 1.0 Stable | 9.2-stg | 6.10.3 | 24.1.4 | AMD Radeon 680M | 8 GB | **PASS (CERTIFIED)** |
| AutoCAD | 2024 (x64) | 1.0 Stable | 9.2-stg | 6.10.3 | 24.1.4 | NVIDIA RTX 4070 | 32 GB | **PASS (CERTIFIED)** |
| Maya | 2026 (x64) | 1.0 Beta | 9.5-stg | 6.10.3 | 24.1.5 | AMD RX 7800 XT | 32 GB | **PASS (SUPPORTED)** |
| 3ds Max | 2026 (x64) | 1.0 Beta | 9.5-stg | 6.10.3 | 24.1.5 | NVIDIA RTX 3080 | 16 GB | **PASS (SUPPORTED)** |

## 3. Related Documents
- [04-certification.md](04-certification.md)
- [../testing/06-hardware-testing.md](../testing/06-hardware-testing.md)
""")

# 06-known-limitations.md
write_file("06-known-limitations.md", """# Known Limitations & Non-Compatibility Boundaries — NebuOS

**Status:** REVIEW  
**Purpose:** Explicitly document structural incompatibilities, unsupported technologies, and architectural boundaries.

---

## 1. Hard Architectural Incompatibilities
NebuOS explicitly acknowledges classes of Windows software that cannot run due to fundamental architectural divergence between the Windows NT kernel and the Linux kernel:

1. **Kernel-Mode Drivers (`.sys`):**
   - Software requiring proprietary Windows ring-0 device drivers (e.g. legacy USB hardware dongles, custom oscilloscopes, virtual network adapters) cannot run.
   - *Policy:* Report as **UNSUPPORTED**. Strictly no virtual machine fallback.
2. **Ring-0 Kernel Anti-Cheat Systems:**
   - Riot Vanguard, BattlEye (Kernel Mode), EasyAntiCheat (Kernel Mode Driver), and Denuvo Anti-Tamper kernel components.
   - *Policy:* Explicitly marked **UNSUPPORTED**. NebuOS will not compromise Linux kernel integrity to load proprietary Windows binary drivers.
3. **16-bit MS-DOS / Windows 3.1 Binaries:**
   - Native x86_64 CPUs cannot execute 16-bit real-mode instructions in 64-bit Long Mode without an emulator (e.g. DOSBox).
   - *Policy:* Excluded from core Wine runtime; relegated to specialized DOS emulator tools.
4. **Active Directory / Windows Domain Deep GPO Binding:**
   - Enterprise workstation management expecting Active Directory Group Policy Objects modifying local Windows NT SAM databases.

## 2. Transparent Reporting Policy
When an unsupported binary is opened, NebuRuntime intercepts execution, displays an educational technical explanation, and refuses execution without corrupting user state.

## 3. Related Documents
- [00-compatibility-overview.md](00-compatibility-overview.md)
- [04-certification.md](04-certification.md)
- [../runtime/00-runtime-overview.md](../runtime/00-runtime-overview.md)
""")

print("Compatibility documentation generated successfully.")
