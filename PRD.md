PRODUCT REQUIREMENTS DOCUMENT (PRD)

NEBUOS

Lightweight Linux Desktop OS with Native-Feeling Windows Application Compatibility

Version: 1.0
Status: Master Product Specification
Target Architecture: x86_64
Primary Language: Rust
Base OS: Fedora Atomic / Image-Based Fedora
Display Architecture: Wayland
Windows Compatibility: Wine
Gaming Compatibility: Proton + DXVK + VKD3D
Virtual Machine: NOT PART OF NEBUOS
Primary Goal: Fast, lightweight, stable desktop OS capable of running Linux and Windows applications without a Windows virtual machine.

1. PRODUCT VISION

NebuOS adalah operating system desktop berbasis Linux yang dirancang untuk memberikan pengalaman desktop modern, ringan, cepat, aman, dan mudah digunakan, sekaligus menyediakan compatibility layer terintegrasi untuk menjalankan aplikasi Windows.

NebuOS tidak bertujuan membuat ulang Windows.

NebuOS juga tidak bertujuan membuat kernel baru.

NebuOS menggunakan Linux sebagai hardware and kernel foundation dan membangun desktop, runtime, compatibility engine, application management, patch system, testing infrastructure, dan user experience sendiri.

Prinsip utama:

1. Linux kernel tetap menjadi foundation.
2. Wayland menjadi display protocol.
3. NebuCompositor menjadi compositor utama.
4. NebuShell menjadi desktop shell.
5. Rust menjadi bahasa utama komponen Nebu.
6. Wine menjadi foundation Windows compatibility.
7. Proton digunakan terutama untuk gaming.
8. DXVK dan VKD3D digunakan untuk graphics translation ketika diperlukan.
9. Tidak menggunakan VM sebagai bagian dari application runtime.
10. Windows binary tetap dijalankan melalui compatibility layer.
11. Proprietary Windows applications tidak didistribusikan oleh NebuOS.
12. Compatibility harus diuji menggunakan software nyata.
13. Update OS harus melewati regression testing sebelum Stable.
14. Performance dan resource usage menjadi requirement utama, bukan optimasi belakangan.

2. PRODUCT GOALS

2.1 Primary Goals

NebuOS harus:

- boot dengan cepat
- memiliki idle RAM rendah
- responsif pada hardware lama
- tetap mampu menggunakan hardware modern
- menyediakan desktop modern
- mendukung aplikasi Linux native
- mendukung Windows applications melalui Wine
- mendukung Windows games melalui Proton
- menyediakan compatibility database
- menyediakan application profiles
- menyediakan patch engine
- menyediakan graphics compatibility layer
- menyediakan automated compatibility testing
- menyediakan atomic updates
- menyediakan rollback
- memiliki installer sederhana
- memiliki UI yang tidak membutuhkan terminal untuk operasi umum
- tidak membutuhkan VM untuk menjalankan Windows applications
- dapat berjalan pada hardware dengan RAM 4 GB
- scalable sampai workstation dengan RAM puluhan GB

3. NON-GOALS

NebuOS tidak akan:

- membuat kernel baru dari nol
- mengganti Linux kernel dengan kernel Rust custom
- membuat GPU driver dari nol
- membuat Vulkan dari nol
- membuat Wine replacement dari nol pada tahap awal
- membuat ulang aplikasi Microsoft Office
- membuat ulang AutoCAD
- membuat ulang Maya
- membuat ulang 3ds Max
- mendistribusikan proprietary Windows applications tanpa izin
- menggunakan VM sebagai solusi compatibility utama
- memaksa seluruh komponen Linux ditulis Rust
- menggunakan Electron/Chromium untuk desktop shell
- menjanjikan 100% compatibility semua aplikasi Windows

4. TARGET USERS

4.1 General Users

Kebutuhan:

- browsing
- office
- multimedia
- file management
- basic productivity
- messaging
- Windows applications

4.2 Developers

Kebutuhan:

- terminal
- Git
- compilers
- Rust
- Node.js
- Python
- containers jika dibutuhkan
- IDE
- Linux tooling
- Windows development applications

4.3 Professional Users

Target:

- AutoCAD
- Maya
- 3ds Max
- Adobe applications
- engineering applications
- productivity applications
- professional Windows software

4.4 Gamers

Target:

- Steam
- Windows games
- Proton
- DXVK
- VKD3D
- Vulkan
- game controller
- GPU acceleration

5. HARDWARE TARGET

5.1 Architecture

Initial release:

x86_64

Future:

ARM64

ARM64 bukan target initial release.

5.2 Minimum Hardware

Target minimum:

CPU:

- 2 cores
- x86_64

RAM:

- 4 GB

Storage:

- 64 GB

GPU:

- Intel integrated GPU
- AMD integrated/dedicated GPU
- supported NVIDIA GPU

Storage recommendation:

- SATA SSD

HDD boleh digunakan tetapi bukan performance target.

5.3 Recommended Hardware

CPU:

- 4 cores or more

RAM:

- 8 GB or more

Storage:

- 128 GB SSD/NVMe or more

GPU:

- modern Intel iGPU
- AMD GPU
- NVIDIA GPU

5.4 Professional Hardware

CPU:

- 8 cores or more

RAM:

- 16 GB or more

Storage:

- NVMe

GPU:

- dedicated GPU

RAM:

- 32 GB or more recommended for heavy 3D/CAD

6. RESOURCE TARGETS

6.1 Idle RAM

Target:

4 GB machine:

- system usable
- minimal background services
- target idle below approximately 1 GB

8 GB machine:

- target idle below approximately 1 GB

Ideal optimized configuration:

- approximately 500-800 MB depending on hardware/services

These are engineering targets, not promises.

6.2 CPU

Idle CPU:

Target:

- near zero to very low CPU utilization

No unnecessary polling loops.

No permanent high-frequency background scanning.

6.3 Storage

Base installation target:

Prefer:

- under 15 GB for base OS excluding user applications

Long-term target:

- under 20 GB for complete base installation depending on selected components.

6.4 Boot

Target:

From SSD:

- usable desktop preferably within several seconds

From NVMe:

- faster target

Boot performance must be benchmarked rather than claimed.

7. CORE ARCHITECTURE

Architecture:

Linux kernel
↓
Hardware drivers
↓
systemd
↓
Mesa
↓
PipeWire
↓
NetworkManager
↓
Wayland
↓
NebuCompositor
↓
NebuShell
↓
Nebu Runtime
↓
Applications

Windows application path:

Windows EXE
↓
Nebu Runtime
↓
Compatibility Database
↓
Application Profile
↓
Wine
↓
Linux

Gaming path:

Windows Game
↓
Nebu Runtime
↓
Proton
↓
DXVK/VKD3D
↓
Vulkan
↓
Mesa
↓
GPU

8. BASE OPERATING SYSTEM

NebuOS should use an image-based Fedora foundation.

The base layer should contain:

- Linux kernel
- systemd
- udev
- Mesa
- PipeWire
- NetworkManager
- filesystem
- security components
- hardware support
- graphics infrastructure
- package/image infrastructure

Development environment may temporarily retain GNOME or another existing desktop for debugging.

Production NebuOS should not depend on GNOME Shell.

9. ATOMIC UPDATE MODEL

NebuOS should use immutable/image-based deployment.

Current system:

NebuOS Image A

Update:

NebuOS Image B

The new image must be:

- built
- verified
- tested
- staged
- booted
- validated

Rollback must be supported.

Update flow:

Fedora upstream
↓
Nebu build system
↓
Nebu patches/configuration
↓
Build image
↓
System tests
↓
Compatibility tests
↓
Hardware tests
↓
Performance tests
↓
PASS
↓
Stable release

FAILED builds must not reach Stable.

10. RELEASE CHANNELS

Provide:

Nightly

For developers.

May contain:

- experimental Wine
- experimental Mesa
- experimental Nebu components

Beta

For testers.

More stable than Nightly.

Stable

Production users.

Only validated components.

LTS

Future option for professional/enterprise deployments.

11. NEBUCOMPOSITOR

NebuCompositor is the primary Wayland compositor.

Responsibilities:

- window rendering
- window placement
- window movement
- window resizing
- fullscreen
- workspaces
- multi-monitor
- input handling
- focus management
- GPU composition
- scaling
- HiDPI
- display management
- frame scheduling

Technology:

- Rust
- Wayland protocols
- DRM/KMS
- libinput
- Vulkan/OpenGL where appropriate

Requirements:

- low latency
- low memory
- no unnecessary animation
- smooth window movement
- efficient frame scheduling

12. NEBUSHELL

NebuShell is the user-facing desktop environment.

It should be conceptually similar to the functionality provided by GNOME Shell but independently implemented.

Components:

- launcher
- panel/taskbar
- desktop
- app switcher
- workspace manager
- notification system
- system tray
- quick settings
- lock screen
- login integration
- power menu
- volume controls
- network controls
- Bluetooth controls

NebuShell must not require Electron.

NebuShell must not require Chromium.

NebuShell should be native Rust where practical.

13. DESKTOP UX

Primary principle:

The user should not need to understand Linux internals.

Normal operation must be possible without terminal.

Examples:

Install application:

- graphical installer

Remove application:

- graphical uninstall

Network:

- graphical UI

GPU:

- graphical UI

Windows application:

- double-click EXE

Troubleshooting:

- graphical diagnostics

Logs:

- graphical viewer

Updates:

- graphical UI

Rollback:

- graphical UI

14. NEBU APPLICATION MODEL

NebuOS should represent applications as managed entities.

Application metadata:

- ID
- name
- version
- vendor
- architecture
- installation location
- runtime
- prefix
- dependencies
- compatibility profile
- patch profile
- graphics profile
- launch command
- environment
- status

Example:

AutoCAD 2024

ID:
autodesk.autocad.2024

Runtime:
Wine

Prefix:
~/.nebu/apps/autodesk.autocad.2024/

Profile:
autodesk/autocad/2024

15. WINDOWS FILESYSTEM COMPATIBILITY

Windows applications expect:

C:\

NebuOS must provide this through the Wine prefix.

Example:

C:\Program Files\Autodesk\AutoCAD 2024

maps internally to:

~/.nebu/apps/autodesk.autocad.2024/drive_c/Program Files/Autodesk/AutoCAD 2024

The application should believe it is operating inside a normal Windows filesystem.

16. APPLICATION PREFIX MODEL

Each major Windows application should have an isolated prefix.

Example:

~/.nebu/apps/

microsoft.office.2024/
autodesk.autocad.2024/
autodesk.maya.2026/
autodesk.3dsmax.2026/

Each prefix can contain:

drive_c/
registry/
config/
cache/
logs/
metadata/

Benefits:

- isolation
- easier troubleshooting
- easier rollback
- safer dependency management
- fewer conflicts
- predictable configuration

17. NEBU RUNTIME

Nebu Runtime is the main Windows application execution manager.

Responsibilities:

- detect executable
- detect installer
- identify application
- query compatibility DB
- select runtime
- create prefix
- configure prefix
- install dependencies
- configure registry
- configure DLLs
- configure graphics
- apply patches
- launch application
- monitor application
- collect logs
- report errors
- manage uninstall

CLI:

nebu run application.exe

GUI:

Double-click application.exe

18. INSTALLER

When user opens setup.exe:

Nebu Runtime must determine whether it is:

- installer
- application
- launcher
- unknown executable

Installer flow:

setup.exe
↓
Nebu Runtime
↓
detect application
↓
query compatibility DB
↓
create prefix
↓
apply profile
↓
run installer
↓
detect installed executable
↓
register application
↓
create launcher
↓
complete

19. APPLICATION REGISTRATION

After installation, NebuOS should create:

- application metadata
- desktop entry
- launcher icon
- uninstall entry
- compatibility metadata
- runtime configuration

User should see:

AutoCAD

rather than:

wine /path/to/program.exe

20. NEBU COMPATIBILITY DATABASE

The Compatibility DB is a core NebuOS component.

Data:

Application
Version
Architecture
Runtime
Wine version
Proton version
Dependencies
DLL overrides
Registry settings
Environment variables
Graphics backend
GPU requirements
Driver requirements
Known bugs
Patch IDs
Test results
Certification status

Possible statuses:

CERTIFIED
SUPPORTED
MOSTLY_COMPATIBLE
LIMITED
UNTESTED
BROKEN
UNSUPPORTED

21. COMPATIBILITY PROFILES

Example:

Microsoft Office 2024

Profile:

microsoft.office.2024

Contains:

- Wine version
- prefix configuration
- fonts
- DLL settings
- COM/OLE settings
- registry
- graphics configuration
- installer behavior
- known issues
- activation notes
- printing configuration

22. NEBU PATCH ENGINE

NebuPatcher manages compatibility modifications.

Priority:

1. environment configuration
2. Wine configuration
3. registry
4. DLL configuration
5. COM/OLE compatibility
6. .NET configuration
7. graphics configuration
8. API improvements
9. binary modification only as last resort

Every patch must be:

- versioned
- identifiable
- reversible where possible
- testable
- associated with an application/version
- documented

Example:

patches/autodesk/autocad/2024/

23. WINE STRATEGY

Do not rewrite Wine initially.

Use upstream Wine.

Nebu should maintain:

- Wine stable
- Wine testing
- Nebu-patched Wine where necessary

Fork Wine only when:

- upstream behavior cannot solve a required compatibility issue
- fundamental API behavior is missing
- performance requires modification
- Nebu-specific integration is required

Whenever possible:

- upstream fixes to Wine.

24. PROTON STRATEGY

Proton should primarily be used for games.

Nebu Runtime may select:

Wine:

- desktop Windows applications

Proton:

- games

The runtime should make the selection automatically.

25. GRAPHICS COMPATIBILITY

Nebu Graphics subsystem must detect:

- GPU vendor
- GPU model
- driver
- Vulkan support
- OpenGL support
- DirectX requirements
- available VRAM
- hybrid GPU configuration

Supported components:

- Mesa
- Vulkan
- OpenGL
- DXVK
- VKD3D

Graphics profiles may be application-specific.

26. HYBRID GPU

If laptop has:

iGPU + dGPU

Nebu should support application-specific GPU selection.

Example:

Office:
iGPU

Browser:
iGPU

AutoCAD:
dGPU

Maya:
dGPU

3ds Max:
dGPU

Game:
dGPU

GPU policy should be configurable.

27. MICROSOFT OFFICE COMPATIBILITY

Initial target:

Office 2019
Office 2021
Office 2024

Future:

Microsoft 365

Applications:

- Word
- Excel
- PowerPoint
- Outlook

Testing:

- launch
- create document
- open document
- save
- print
- PDF export
- fonts
- clipboard
- COM
- OLE
- VBA
- macros
- add-ins
- large files
- networking
- licensing

28. AUTOCAD COMPATIBILITY

Target versions should be selected individually.

Testing:

Installation
Launch
2D drawing
DWG open
DWG save
Large DWG
Layers
Blocks
Fonts
Plot
PDF
3D
GPU acceleration
Input
Clipboard
Plugins
External references
Stress test

Certification requires real application functionality.

29. MAYA COMPATIBILITY

Testing:

Installation
Launch
Scene loading
Scene editing
Viewport
Textures
Shaders
Animation
Rigging
Rendering
GPU
Plugins
File import
File export
Performance

30. 3DS MAX COMPATIBILITY

Testing:

Installation
Launch
Scene
Viewport
Materials
Modifiers
Animation
Rendering
GPU
Plugins
Import
Export
Large scene
Stress testing

31. COMPATIBILITY LAB

NebuOS must provide a dedicated compatibility test system.

Test categories:

SYSTEM
APPLICATION
GRAPHICS
PERFORMANCE
REGRESSION
INSTALLATION
UNINSTALL
UPDATE
ROLLBACK

Every supported application should have repeatable tests.

32. AUTOMATED TESTING

Example:

AutoCAD test:

Install
↓
Launch
↓
Open test.dwg
↓
Edit
↓
Save
↓
Export PDF
↓
Close
↓
Collect logs
↓
PASS/FAIL

Automation should verify:

- process exit code
- generated files
- expected files
- screenshots where appropriate
- runtime errors
- crash logs
- performance metrics

33. MANUAL TESTING

Some functionality cannot be reliably automated.

Manual testing remains mandatory for:

- complex UI
- viewport behavior
- graphics artifacts
- plugins
- printing
- user interaction
- dialogs
- rendering
- hardware-specific behavior

Therefore Nebu compatibility certification requires a combination of:

Automated testing
+
Manual testing

34. COMPATIBILITY MATRIX

Matrix dimensions:

Application
Version
NebuOS version
Wine version
Kernel
Mesa
GPU
Driver
CPU architecture

Example:

AutoCAD 2024
NebuOS 1.0
Wine 11.x
Mesa 26.x
AMD RX 6600
PASS

35. REGRESSION TESTING

Every change to:

- kernel
- Mesa
- Wine
- Proton
- Nebu Runtime
- compositor
- graphics subsystem

must trigger relevant regression tests.

Critical applications:

- Office
- AutoCAD
- Maya
- 3ds Max
- selected games

A component update must not automatically become Stable.

36. PERFORMANCE TESTING

Measure:

- boot time
- login time
- launcher response
- app launch time
- app close time
- RAM
- CPU
- GPU
- disk IO
- network
- frame latency

Test:

Cold launch
Warm launch

Nebu should optimize perceived responsiveness without falsifying benchmarks.

37. WARM RUNTIME

Nebu Runtime may keep lightweight runtime components warm.

Example:

First launch:

Wine initialization

Later launch:

reuse cached runtime components

Goal:

reduce repeated initialization.

However:

Memory pressure must be respected.

On low-RAM systems:

- aggressively unload idle runtime components

On high-RAM systems:

- allow more caching

38. PREFIX CREATION

Prefix creation should normally happen during installation.

Do not recreate prefix every launch.

Example:

Install AutoCAD:

create prefix once.

Launch:

reuse prefix.

39. APPLICATION CACHE

Possible caches:

- shader cache
- font cache
- dependency cache
- application metadata
- Wine runtime cache

Cache must have:

- size limits
- cleanup policy
- corruption detection
- rebuild mechanism

40. APPLICATION UNINSTALL

Uninstall must remove:

- application files
- runtime configuration
- prefix
- launcher
- compatibility metadata

User data should be separately handled.

Example:

Keep user files?

YES

Delete application environment?

YES

41. SECURITY

NebuOS must use:

- Linux permissions
- sandboxing where practical
- application isolation
- controlled filesystem access
- secure update mechanism
- verified system images

Windows applications should not automatically receive unrestricted access to the entire Linux filesystem.

42. WINDOWS APP SANDBOX

Windows application should ideally receive:

- application prefix
- selected user directories
- temporary directory
- graphics access
- audio access
- network access according to policy

Potential future controls:

Filesystem
Network
GPU
Audio
USB
Camera
Microphone

43. FILESYSTEM DESIGN

NebuOS should support modern Linux filesystems.

Primary candidates:

Btrfs

Reasons:

- snapshots
- rollback
- compression
- modern filesystem features

Alternative:

ext4

for compatibility and simplicity.

44. SNAPSHOT SYSTEM

Before major updates:

Create system snapshot/deployment.

If update fails:

Rollback.

Application data should not automatically be rolled back unless explicitly configured.

45. PACKAGE MANAGEMENT

System layer:

Image-based update system.

Application layer:

Nebu application management.

Native Linux applications may use:

- Flatpak
- distribution packages
- containerized application formats where appropriate

Windows applications use:

Nebu Runtime + Wine/Proton.

46. APPLICATION STORE

Nebu Software Center should provide:

- Linux applications
- Windows compatibility profiles
- runtime information
- compatibility status
- installation
- update
- uninstall
- repair

For proprietary Windows applications:

NebuOS should not distribute proprietary binaries without authorization.

The user may provide the installer.

47. INSTALLER UX

Example:

User downloads:

AutoCAD-2024.exe

Double click.

Nebu:

Detected:
Autodesk AutoCAD 2024

Compatibility:
Certified

Requirements:
8 GB RAM recommended
GPU acceleration supported

[Install]

Installation completes.

Nebu creates:

AutoCAD

launcher.

48. UNKNOWN WINDOWS APPLICATION

If compatibility DB does not recognize application:

Nebu should still allow:

Run with default Wine profile.

Status:

UNTESTED

Nebu should collect diagnostics.

User may optionally submit compatibility information.

49. FAILURE HANDLING

If application crashes:

Nebu Runtime should display:

Application crashed.

Options:

- View logs
- Repair environment
- Reset configuration
- Reinstall dependencies
- Restore previous profile
- Report compatibility issue

Never silently corrupt the prefix.

50. PREFIX REPAIR

Provide:

Repair

Actions:

- verify files
- reset configuration
- reinstall dependencies
- rebuild cache
- restore registry
- apply known patch
- rollback profile

51. DIAGNOSTICS

Nebu Diagnostics should collect:

- OS version
- kernel
- Wine version
- Proton version
- Mesa
- GPU
- driver
- application
- application version
- compatibility profile
- crash information
- relevant logs

Sensitive user data must not be collected unnecessarily.

52. TASK MANAGER

Nebu Task Manager should show:

- CPU
- RAM
- GPU
- disk
- network
- processes
- Windows applications
- Wine processes
- resource consumption

Windows application processes should be grouped.

Example:

AutoCAD

instead of showing dozens of Wine processes individually.

53. FILE MANAGER

Nebu File Manager must support:

- Linux filesystem
- Windows application prefixes
- removable storage
- network shares
- archive files
- permissions
- search
- file associations

Windows prefix directories should preferably be hidden from normal users.

54. FILE ASSOCIATIONS

Examples:

.docx
→ Office

.xlsx
→ Excel

.dwg
→ AutoCAD

.exe
→ Nebu Runtime

.psd
→ compatible application

The association database should be configurable.

55. WINDOWS PATH MAPPING

Nebu should expose:

C:

internally through Wine prefix.

Optional user-accessible mapping:

Windows C:
→ Application environment

Linux home:
→ controlled Windows path

Example:

/home/user/Documents

maps to:

Z:\home\user\Documents

only when explicitly permitted.

56. MULTI-MONITOR

Requirements:

- multiple displays
- mixed DPI
- different refresh rates
- display positioning
- fullscreen
- application-specific display
- GPU selection

57. INPUT

Support:

- keyboard
- mouse
- touchpad
- touchscreen where available
- game controller
- stylus where supported

Windows applications should receive expected input semantics through Wine.

58. AUDIO

Use PipeWire.

Support:

- speakers
- headphones
- microphone
- Bluetooth audio
- application volume
- per-application routing

59. NETWORK

Use Linux networking infrastructure.

Support:

- Ethernet
- WiFi
- Bluetooth networking where supported
- VPN
- DNS
- proxy

Windows applications should receive network access through normal Linux networking.

60. POWER MANAGEMENT

Support:

- shutdown
- reboot
- suspend
- hibernate where hardware permits
- battery
- lid close
- power profiles

61. LAPTOP OPTIMIZATION

Nebu should minimize:

- background processes
- wakeups
- polling
- unnecessary animations
- GPU usage
- CPU usage

Power-aware behavior should be application-dependent.

62. DESKTOP ANIMATIONS

Animations should be:

- minimal
- GPU accelerated
- configurable
- disabled automatically on weak hardware if necessary

Responsiveness has priority over visual effects.

63. LOW-END MODE

NebuOS should have:

Nebu Lite Mode

Features:

- fewer animations
- aggressive memory cleanup
- less caching
- reduced background services
- simplified compositor effects
- low GPU overhead

Target:

4 GB RAM machines.

64. HIGH-PERFORMANCE MODE

For workstation/gaming systems:

- larger caches
- aggressive shader caching
- high performance GPU profile
- fewer power restrictions

65. DEVELOPER MODE

Developer Mode should expose:

- runtime logs
- Wine debug logs
- compositor logs
- graphics diagnostics
- compatibility DB
- prefix management
- application tracing

66. CLI

Nebu should provide:

nebu

Commands:

nebu run
nebu install
nebu uninstall
nebu repair
nebu info
nebu diagnose
nebu prefix
nebu compatibility
nebu update
nebu rollback

CLI is supplementary.

Normal users should not require CLI.

67. DATABASE

Recommended initial database:

SQLite

Use cases:

- installed applications
- compatibility metadata
- runtime state
- local configuration
- cached test results

Do not scan the entire filesystem every time launcher opens.

Application lookup should be database-driven.

68. LAUNCH PERFORMANCE

Launcher should:

- use local indexed metadata
- avoid filesystem-wide scanning
- avoid spawning unnecessary processes
- avoid initializing Wine for native Linux applications
- initialize Windows runtime only when required

Target:

Launcher UI response:
preferably below 100 ms under normal conditions.

69. APPLICATION LAUNCH PIPELINE

Native Linux application:

Launcher
↓
desktop entry
↓
application

Windows application:

Launcher
↓
Nebu Runtime
↓
profile lookup
↓
prefix
↓
Wine
↓
application

Game:

Launcher
↓
Nebu Runtime
↓
Proton
↓
DXVK/VKD3D
↓
game

70. COLD START VS WARM START

Benchmarks must separate:

Cold launch:

- no runtime cache

Warm launch:

- runtime initialized
- filesystem cache populated

Nebu should optimize both.

71. CRASH ISOLATION

A crashed Windows application must not crash:

- NebuShell
- compositor
- system services

A Wine crash should not require rebooting the OS.

72. UPDATE SAFETY

System updates must be transactional.

If:

Kernel update fails
or
Mesa update breaks GPU
or
Wine update breaks applications

the user must be able to boot the previous deployment.

73. WINE UPDATE POLICY

Wine updates must pass:

- core Windows API tests
- application regression tests
- graphics tests
- critical application tests

Only then should the update enter Stable.

74. MESA UPDATE POLICY

Mesa updates must test:

- Intel
- AMD
- NVIDIA where applicable
- Vulkan
- OpenGL
- DXVK
- VKD3D
- CAD applications
- games

75. KERNEL UPDATE POLICY

Kernel updates must test:

- boot
- storage
- USB
- networking
- GPU
- audio
- suspend
- resume
- input

76. TEST HARDWARE LAB

Minimum test hardware:

Intel iGPU machine
AMD GPU machine
NVIDIA GPU machine
older CPU machine
modern CPU machine
4 GB RAM machine
8 GB RAM machine
16+ GB RAM machine
SATA SSD machine
NVMe machine
laptop
desktop

77. COMPATIBILITY CERTIFICATION

Certification levels:

CERTIFIED

All critical tests pass.

SUPPORTED

Most functionality works.

MOSTLY COMPATIBLE

Core functionality works but known limitations exist.

LIMITED

Application works only under specific configuration.

UNTESTED

No official test.

BROKEN

Known failure.

UNSUPPORTED

Fundamental incompatibility.

78. APPLICATION TEST SCORE

Possible score:

Installation: 10%
Launch: 10%
Core functionality: 30%
File handling: 10%
Graphics: 15%
Performance: 10%
Plugins/integrations: 10%
Stability: 5%

The exact scoring system can evolve.

79. COMPATIBILITY REPORT

Every certified application should generate:

Application
Version
NebuOS
Kernel
Wine
Mesa
GPU
Driver
Test date
Test result
Known limitations

80. LEGAL/LICENSING

NebuOS must respect:

- Wine license
- Linux licensing
- Fedora licensing
- Mesa licensing
- DXVK licensing
- VKD3D licensing
- third-party licenses

Proprietary applications remain property of their vendors.

NebuOS must not redistribute proprietary software without appropriate authorization.

81. SOURCE CODE POLICY

Nebu components should be open source where practical.

Repository should clearly separate:

Nebu code
Third-party dependencies
Build configuration
Compatibility profiles
Tests
Documentation

82. REPOSITORY STRUCTURE

nebuos/

core/
runtime/
compatibility/
patcher/
graphics/
security/
updater/
config/

desktop/
compositor/
shell/
launcher/
panel/
notifications/
lockscreen/

apps/
settings/
file-manager/
terminal/
software-center/
task-manager/

compatibility/
microsoft/
autodesk/
adobe/
engineering/
games/
legacy/

patches/
microsoft/
autodesk/
graphics/

packaging/
image/
installer/
iso/

tests/
system/
runtime/
graphics/
compatibility/
performance/
hardware/
regression/

docs/

scripts/

83. CODING LANGUAGE

Primary:

Rust

Use C/C++ where required by existing ecosystem.

Do not rewrite mature dependencies merely to achieve language purity.

84. RUST COMPONENTS

Rust should be used for:

- NebuCompositor
- NebuShell
- NebuRuntime
- NebuPatcher
- NebuCompatibility
- NebuGraphicsManager
- NebuInstaller
- NebuUpdater
- NebuSettings
- NebuFileManager
- NebuTaskManager
- Nebu CLI

85. DEVELOPMENT PRINCIPLES

1. Minimal dependencies.
2. Avoid unnecessary abstractions.
3. Prefer native system APIs.
4. Avoid Electron.
5. Avoid Chromium in core UI.
6. Avoid duplicate functionality.
7. Reuse mature open-source infrastructure.
8. Measure performance.
9. Write tests before claiming compatibility.
10. Do not add features without requirement.
11. Do not create speculative architecture.
12. Keep modules independently testable.

86. DEVELOPMENT PHASES

P0

Research and specification.

Deliverables:

- architecture
- hardware matrix
- dependency list
- license audit
- build strategy
- testing strategy

P1

Base OS.

Deliverables:

- bootable NebuOS image
- kernel
- systemd
- networking
- graphics
- basic terminal

P2

NebuCompositor.

Deliverables:

- Wayland compositor
- input
- windows
- rendering
- multi-monitor

P3

NebuShell.

Deliverables:

- launcher
- panel
- notifications
- workspaces
- settings integration

P4

Native desktop applications.

Deliverables:

- file manager
- settings
- terminal
- task manager
- software center

P5

Nebu Runtime.

Deliverables:

- EXE detection
- Wine management
- prefix management
- launch system

P6

Windows compatibility.

Deliverables:

- Wine
- application profiles
- dependency manager
- Windows filesystem mapping

P7

Compatibility DB.

Deliverables:

- SQLite database
- application profiles
- version management
- hardware matrix

P8

Patch Engine.

Deliverables:

- patch definitions
- patch application
- rollback
- verification

P9

Graphics.

Deliverables:

- GPU detection
- Vulkan
- OpenGL
- DXVK
- VKD3D
- shader cache

P10

Professional applications.

Deliverables:

- Office
- AutoCAD
- Maya
- 3ds Max
- Adobe targets

P11

Installer and update system.

Deliverables:

- ISO
- graphical installer
- atomic updates
- rollback

P12

Performance and production.

Deliverables:

- boot optimization
- memory optimization
- launch optimization
- compatibility regression
- hardware validation
- security audit

87. MVP

MVP must NOT attempt everything.

MVP:

- boot
- Wayland
- NebuCompositor
- NebuShell
- file manager
- settings
- terminal
- network
- audio
- Wine
- EXE launcher
- prefix management
- compatibility DB
- basic patch system

Initial Windows applications:

- 7-Zip
- Notepad++
- selected browsers
- Microsoft Office target
- one CAD application target

Games are not the primary MVP requirement.

88. POST-MVP

After MVP:

- Office certification
- AutoCAD certification
- Maya
- 3ds Max
- Proton
- gaming
- advanced GPU management
- application store
- automatic compatibility reporting

89. PERFORMANCE BENCHMARK

Every release should record:

Boot:
seconds

Idle RAM:
MB

Idle CPU:
%

Launcher:
milliseconds

Native app launch:
milliseconds

Wine cold launch:
seconds

Wine warm launch:
seconds

Application close:
milliseconds/seconds

GPU utilization:
%

Disk IO:
MB/s

90. SUCCESS METRICS

NebuOS is successful if:

- system boots reliably
- desktop remains responsive
- 4 GB RAM systems remain usable
- native Linux applications work
- Windows applications can be installed without terminal
- compatibility profiles work
- Wine updates can be regression-tested
- system rollback works
- GPU acceleration works
- critical Windows applications become certified

91. CRITICAL PRODUCT REQUIREMENT

The primary NebuOS differentiator is not the desktop UI.

It is:

Nebu Compatibility Platform

consisting of:

Nebu Runtime
+
Wine
+
Compatibility DB
+
Patch Engine
+
Graphics Engine
+
Compatibility Lab
+
Regression Testing

92. NO VM REQUIREMENT

NebuOS must not use:

- VirtualBox
- VMware
- QEMU Windows VM
- KVM Windows VM

as the normal Windows application runtime.

Windows applications must run through:

Wine
or
Proton

where technically possible.

Applications requiring Windows kernel drivers, unsupported proprietary hardware interfaces, kernel-level anti-cheat, DRM, or other fundamental Windows-only functionality may remain unsupported.

NebuOS must explicitly report such incompatibility rather than pretending it works.

93. COMPATIBILITY PHILOSOPHY

Never define compatibility as:

"Application opens."

Compatibility means:

INSTALL
↓
LAUNCH
↓
OPEN REAL PROJECT
↓
EDIT
↓
SAVE
↓
EXPORT
↓
PRINT
↓
GPU
↓
PLUGIN
↓
STRESS
↓
CLOSE
↓
REOPEN

Only then should an application receive high certification.

94. FIRST DEVELOPMENT TASKS

First implementation should NOT start with AutoCAD.

Order:

1. Create repository.
2. Create architecture documentation.
3. Build Fedora-based image.
4. Boot image on real hardware.
5. Verify kernel and hardware.
6. Build minimal Wayland environment.
7. Build NebuCompositor.
8. Render desktop.
9. Implement input.
10. Implement windows.
11. Implement NebuShell.
12. Implement launcher.
13. Implement native application launching.
14. Implement Nebu Runtime.
15. Integrate Wine.
16. Run simple Windows applications.
17. Build compatibility DB.
18. Build prefix manager.
19. Build patch engine.
20. Add automated regression testing.
21. Add graphics compatibility.
22. Begin Office testing.
23. Begin CAD testing.
24. Optimize.
25. Productionize installer/update system.

95. FIRST HARDWARE VALIDATION

Initial validation hardware should include:

Development machine:
4+ cores
16+ GB RAM
SSD/NVMe

Low-end test machine:
2-4 cores
4 GB RAM
SATA SSD

Modern test machine:
8+ cores
16+ GB RAM
NVMe
dedicated GPU

GPU test:

Intel
AMD
NVIDIA

96. DEVELOPMENT ENVIRONMENT

Develop initially on Fedora Workstation or equivalent development environment.

Do not immediately remove GNOME/KDE during early development.

Use the existing desktop to:

- debug
- launch terminal
- inspect processes
- test compositor
- diagnose crashes

Once NebuCompositor and NebuShell are stable, production image can remove unnecessary desktop components.

97. CI/CD

CI should perform:

- Rust formatting
- linting
- unit tests
- integration tests
- build
- package validation
- image build
- compatibility tests
- regression tests

Release pipeline:

Commit
↓
CI
↓
Build
↓
System tests
↓
Compatibility tests
↓
Hardware tests
↓
Performance tests
↓
Release candidate
↓
Beta
↓
Stable

98. QUALITY GATES

No release can proceed if:

- boot fails
- critical GPU fails
- networking fails
- data corruption occurs
- rollback fails
- critical application regression occurs
- security vulnerability remains unresolved

99. DOCUMENTATION

Required documentation:

ARCHITECTURE.md
BUILD.md
INSTALL.md
DEVELOPMENT.md
COMPATIBILITY.md
TESTING.md
SECURITY.md
PERFORMANCE.md
UPDATE.md
CONTRIBUTING.md
LICENSE.md

Each compatibility profile must have documentation.

100. FINAL PRODUCT ARCHITECTURE

NebuOS:

Linux Kernel
↓
Fedora Image Base
↓
system services
↓
drivers
↓
Mesa
↓
PipeWire
↓
Wayland
↓
NebuCompositor
↓
NebuShell
↓
Nebu System Apps
↓
Nebu Runtime
↓
Compatibility Engine
↓
Wine / Proton
↓
DXVK / VKD3D
↓
Windows Applications / Games

Core Nebu intellectual/engineering layer:

NebuCompositor
NebuShell
NebuRuntime
NebuCompatibility
NebuPatcher
NebuGraphics
NebuAppManager
NebuInstaller
NebuUpdater
NebuCompatibilityLab

101. FINAL PRODUCT PRINCIPLES

PRINCIPLE 1

Reuse mature infrastructure.

PRINCIPLE 2

Do not rewrite Linux unnecessarily.

PRINCIPLE 3

Do not rewrite Wine unnecessarily.

PRINCIPLE 4

Do not use VM for normal Windows compatibility.

PRINCIPLE 5

Compatibility must be tested with real applications.

PRINCIPLE 6

Every critical update requires regression testing.

PRINCIPLE 7

Performance must be measured.

PRINCIPLE 8

Low-end hardware is a first-class target.

PRINCIPLE 9

Native Rust UI should replace unnecessary heavyweight desktop components.

PRINCIPLE 10

Users should not need to understand Wine prefixes, registry files, DLL overrides, or Linux internals.

PRINCIPLE 11

An application that cannot technically run must be reported as unsupported, not hidden behind misleading compatibility claims.

PRINCIPLE 12

NebuOS should feel like one coherent operating system rather than Fedora + Wine + random scripts glued together.

102. DEFINITION OF DONE

NebuOS 1.0 is considered production-ready only when:

SYSTEM

- reliable boot
- reliable shutdown
- networking
- audio
- Bluetooth
- USB
- suspend/resume
- multi-monitor
- GPU acceleration

DESKTOP

- NebuCompositor
- NebuShell
- launcher
- settings
- file manager
- task manager
- notifications

WINDOWS COMPATIBILITY

- EXE installation
- automatic application detection
- prefix management
- compatibility DB
- patch engine
- diagnostics
- repair
- uninstall

GRAPHICS

- Intel
- AMD
- NVIDIA where supported
- Vulkan
- OpenGL
- DXVK
- VKD3D

APPLICATIONS

- selected Office version certified
- selected AutoCAD version certified or clearly marked limitations
- selected professional applications tested
- selected games tested

UPDATES

- atomic update
- verification
- rollback
- regression testing

PERFORMANCE

- documented RAM usage
- documented boot performance
- documented application launch performance
- low-end hardware test completed

SECURITY

- system image verification
- application isolation
- permissions
- security audit
- crash isolation

103. LONG-TERM VISION

NebuOS should eventually become:

A Linux-based desktop operating system where the user does not need to care whether an application is Linux-native or Windows-native.

The user experience should be:

Install
↓
Click
↓
Run

rather than:

Find Wine version
↓
Create prefix
↓
Install Winetricks
↓
Find DLL
↓
Modify registry
↓
Search forum
↓
Try another Wine version
↓
Cry quietly

NebuOS should absorb this complexity into the operating system itself.

The long-term goal is therefore not merely:

"Linux that runs Windows applications."

The goal is:

"An operating system that manages Windows application compatibility as a first-class system capability."

END OF PRD
