# Update and Deployment Interface Specification — NebuOS

**Status:** APPROVED ARCHITECTURAL SPECIFICATION  
**Document ID:** NEBU-SPEC-IFACE-UPD-001  
**Authority:** Principal OS Architect, Systems Engineer, Interface Architect  
**Purpose:** Formal programmatic interface specification, D-Bus Introspection XML, Polkit authorization rules, and Rust trait definitions for the NebuOS Update Subsystem (`org.nebu.Update1`).  

---

## 1. Status and Invariants

- **Status:** APPROVED — Definitive interface contract between `NebuUpdateService`, desktop clients (`nebu-shell`), CLI tools, and `bootc`.
- **Architectural Invariants:**
  1. **Unprivileged Client Principle:** Graphical desktop shells (`nebu-shell`) and user processes are strictly forbidden from executing root-level `bootc` commands directly. All update querying, staging, and reboot scheduling must route through `org.nebu.Update1` over D-Bus.
  2. **Strict Polkit Mediation:** Read-only inspection methods (`GetCurrentVersion`, `GetUpdateStatus`, `GetHealthStatus`) are accessible to unprivileged desktop sessions without password prompts. Privileged state-altering methods (`StageUpdate`, `ApplyUpdate`, `Rollback`, `ScheduleRestart`) require Polkit authorization (`org.nebu.update.manage`).
  3. **Asynchronous Non-Blocking Dispatch:** All long-running operations (downloading layers, verifying signatures, staging deployments) return immediate job object paths (`/org/nebu/Update1/Jobs/<id>`); state transitions and progress metrics are streamed via signals.

---

## 2. D-Bus Interface Definition: `org.nebu.Update1`

- **Bus Type:** System Message Bus (`dbus-broker`)
- **Well-Known Name:** `org.nebu.Update1`
- **Object Path:** `/org/nebu/Update1`

### 2.1 Introspection XML
```xml
<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
"http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node name="/org/nebu/Update1">
  <interface name="org.nebu.Update1">
    
    <!-- Version & System Information -->
    <method name="GetCurrentVersion">
      <arg name="version_info" type="a{sv}" direction="out"/>
    </method>
    
    <!-- Update Checking & Discovery -->
    <method name="CheckForUpdates">
      <arg name="force" type="b" direction="in"/>
      <arg name="status" type="s" direction="out"/>
    </method>
    
    <method name="GetUpdateStatus">
      <arg name="status_dict" type="a{sv}" direction="out"/>
    </method>
    
    <method name="GetAvailableRelease">
      <arg name="release_metadata" type="a{sv}" direction="out"/>
    </method>
    
    <!-- Download, Verification, and Staging -->
    <method name="DownloadUpdate">
      <arg name="job_path" type="o" direction="out"/>
    </method>
    
    <method name="VerifyUpdate">
      <arg name="verification_result" type="b" direction="out"/>
    </method>
    
    <method name="StageUpdate">
      <arg name="job_path" type="o" direction="out"/>
    </method>
    
    <!-- Activation, Reboot, and Rollback -->
    <method name="ScheduleRestart">
      <arg name="scheduled_time_utc" type="t" direction="in"/>
      <arg name="success" type="b" direction="out"/>
    </method>
    
    <method name="ApplyUpdate">
      <arg name="reboot_immediately" type="b" direction="in"/>
      <arg name="success" type="b" direction="out"/>
    </method>
    
    <method name="GetHealthStatus">
      <arg name="health_dict" type="a{sv}" direction="out"/>
    </method>
    
    <method name="Rollback">
      <arg name="reboot_immediately" type="b" direction="in"/>
      <arg name="success" type="b" direction="out"/>
    </method>

    <!-- Properties -->
    <property name="State" type="s" access="read"/>
    <property name="ProgressPercentage" type="d" access="read"/>
    <property name="CurrentChannel" type="s" access="read"/>
    <property name="StagedVersion" type="s" access="read"/>
    <property name="LastCheckTimestamp" type="t" access="read"/>

    <!-- Signals -->
    <signal name="StateChanged">
      <arg name="old_state" type="s"/>
      <arg name="new_state" type="s"/>
    </signal>
    
    <signal name="DownloadProgress">
      <arg name="bytes_downloaded" type="t"/>
      <arg name="total_bytes" type="t"/>
      <arg name="percentage" type="d"/>
    </signal>
    
    <signal name="UpdateStaged">
      <arg name="version" type="s"/>
      <arg name="release_id" type="s"/>
    </signal>
    
    <signal name="RollbackOccurred">
      <arg name="failed_version" type="s"/>
      <arg name="restored_version" type="s"/>
      <arg name="reason" type="s"/>
    </signal>

  </interface>
</node>
```

---

## 3. Data Dictionary for Variant Dictionaries (`a{sv}`)

### 3.1 `version_info` Dictionary
```json
{
  "nebu_version": "1.0.1",
  "base_platform": "Fedora 44 (bootc)",
  "kernel_version": "6.14.0-200.fc44.x86_64",
  "mesa_version": "25.0.0",
  "image_digest": "sha256:7f83b165249a0c71e2...",
  "release_id": "nebu-20260904.1",
  "channel": "stable",
  "deployment_type": "bootc-ostree"
}
```

### 3.2 `release_metadata` Dictionary
```json
{
  "version": "1.0.2",
  "release_id": "nebu-20261008.1",
  "channel": "stable",
  "architecture": "x86_64",
  "image_digest": "sha256:4a8b1c...",
  "release_date": "2026-10-08T18:00:00Z",
  "minimum_supported_version": "1.0.0",
  "security_level": "normal",
  "reboot_required": true,
  "download_size_bytes": 245367890,
  "release_notes_url": "https://nebuos.org/releases/1.0.2.html",
  "changelog_summary": "Improved S0ix sleep power drain on Intel Meteor Lake; DXVK 2.4 update."
}
```

### 3.3 `health_dict` Dictionary
```json
{
  "boot_successful": true,
  "boot_counter": 0,
  "systemd_failed_units_count": 0,
  "rootfs_readonly": true,
  "network_baseline_active": true,
  "compositor_active": true,
  "watchdog_disarmed": true
}
```

---

## 4. Rust Trait Definition (Specification Model)

The internal architecture of `nebu-update-service` implements the following Rust traits:

```rust
pub struct VersionInfo {
    pub nebu_version: String,
    pub base_platform: String,
    pub kernel_version: String,
    pub mesa_version: String,
    pub image_digest: String,
    pub release_id: String,
    pub channel: String,
}

pub struct ReleaseMetadata {
    pub version: String,
    pub release_id: String,
    pub channel: String,
    pub architecture: String,
    pub image_digest: String,
    pub release_date: u64,
    pub minimum_supported_version: String,
    pub security_level: SecurityUrgency,
    pub reboot_required: bool,
    pub download_size_bytes: u64,
    pub release_notes: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum UpdateState {
    UpToDate,
    Checking,
    UpdateAvailable,
    Downloading,
    Verifying,
    Staging,
    ReadyToRestart,
    Rebooting,
    VerifyingSystem,
    UpdateFailed,
    RollingBack,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SecurityUrgency {
    Normal,
    Important,
    Critical,
}

#[async_trait::async_trait]
pub trait UpdateEngine: Send + Sync {
    async fn get_current_version(&self) -> Result<VersionInfo, UpdateError>;
    async fn check_for_updates(&self, force: bool) -> Result<Option<ReleaseMetadata>, UpdateError>;
    async fn download_and_stage(&self, metadata: &ReleaseMetadata) -> Result<(), UpdateError>;
    async fn verify_staged_image(&self) -> Result<bool, UpdateError>;
    async fn schedule_reboot(&self, timestamp_utc: u64) -> Result<(), UpdateError>;
    async fn apply_update_now(&self) -> Result<(), UpdateError>;
    async fn trigger_rollback(&self, reboot_now: bool) -> Result<(), UpdateError>;
    async fn verify_boot_health(&self) -> Result<bool, UpdateError>;
}
```

---

## 5. Polkit Authorization Policy

Privileged operations are governed by `/usr/share/polkit-1/actions/org.nebu.update.policy`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
 "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/PolicyKit/1.0/policyconfig.dtd">
<policyconfig>
  <vendor>NebuOS Project</vendor>
  <vendor_url>https://nebuos.org</vendor_url>

  <action id="org.nebu.update.manage">
    <description>Manage system updates and trigger reboot or rollback</description>
    <message>Authentication is required to install system updates or modify release channels</message>
    <defaults>
      <allow_any>auth_admin</allow_any>
      <allow_inactive>auth_admin</allow_inactive>
      <allow_active>yes</allow_active>
    </defaults>
  </action>

</policyconfig>
```

**Security Policy:** Active local desktop console users (`allow_active=yes`) are authorized to trigger updates and channel switches without being prompted for root passwords, adhering to consumer desktop expectations while maintaining strict remote isolation (`allow_any=auth_admin`).

---

## 6. Related Documents
- [../updates/00-update-specification.md](../updates/00-update-specification.md) — Master update specification.
- [../updates/04-rollback-recovery.md](../updates/04-rollback-recovery.md) — Rollback recovery mechanics.
- [../decisions/ADR-0011-os-image-updates-and-rollback.md](../decisions/ADR-0011-os-image-updates-and-rollback.md) — Architectural decision.
