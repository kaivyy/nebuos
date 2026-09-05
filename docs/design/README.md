# NebuOS UI/UX, Design System, and Iconography Documentation

Welcome to the authoritative engineering documentation for the **NebuOS Design System, Iconography Architecture, and Desktop Visual Subsystem**.

This directory defines the visual language, design token engine, abstract iconography pipeline, tripartite desktop paradigm (Theme, Layout, Behavior), component taxonomy, accessibility requirements, and external asset licensing policies governing NebuOS desktop interfaces.

---

## 1. Directory Structure and Specifications

| Specification | Title | Description & Scope |
|---|---|---|
| [00-design-system.md](00-design-system.md) | Master Design System & Design Tokens | Mathematical 4px/8px spatial grid, semantic color tokens, typography scale, corner radii, elevation, motion budgets, and interactive states. |
| [01-iconography.md](01-iconography.md) | Iconography Architecture & Pipeline | `NebuIcon` abstract API, prototype library (Lucide/Material Symbols) vs dedicated production Nebu Icon Set, optical sizing (16, 20, 24, 32px), stroke rules, and system vs app icon segregation. |
| [02-theming-layout-behavior.md](02-theming-layout-behavior.md) | Tripartite Desktop Architecture | Separation of styling (`Theme`), spatial geometry (`Layout`), and interaction (`Behavior`); single shell binary with sub-150ms dynamic switching; TOML schema and hot-reload. |
| [03-components.md](03-components.md) | Component Taxonomy & Architecture | Five-tier component model: Foundation, Navigation, Desktop Shell, Feedback, and Application tiers implemented in native Rust/Slint. |
| [04-accessibility-and-performance.md](04-accessibility-and-performance.md) | Accessibility & Performance Taxonomy | Hard Requirements (WCAG AA 4.5:1 contrast, keyboard navigation, reduced motion), Engineering Targets (touch targets >= 44x44px, fractional scaling), and memory budgets (<45MB shell, <35MB marketplace). |
| [05-external-assets-and-licensing.md](05-external-assets-and-licensing.md) | External Assets & Licensing Policy | Asset governance, SPDX license tracking, copyright attribution, font inclusion (Inter, JetBrains Mono), prototype vs production asset lifecycle isolation. |

---

## 2. Reading Paths

### For Desktop & UI Engineers (Milestone P2)
1. Start with [00-design-system.md](00-design-system.md) to understand semantic tokens and spatial grids.
2. Read [01-iconography.md](01-iconography.md) to implement the `NebuIcon` abstraction without coupling to SVG paths.
3. Review [02-theming-layout-behavior.md](02-theming-layout-behavior.md) to implement theme and layout hot-reloading in `nebu-shell`.
4. Consult [03-components.md](03-components.md) for Slint widget hierarchy and state machines.

### For Application Platform Engineers (Milestone P6)
1. Read [01-iconography.md](01-iconography.md) §5 for third-party application icon sanitization and raster caching.
2. Read [03-components.md](03-components.md) Tier 5 for Marketplace Card, Permission Matrix, and Installer Wizard components.
3. Read [04-accessibility-and-performance.md](04-accessibility-and-performance.md) to enforce memory budgets (<35 MB RSS) and contrast compliance.

### For QA, Accessibility & Release Auditors
1. Consult [04-accessibility-and-performance.md](04-accessibility-and-performance.md) for testable exit criteria and contrast assertions.
2. Consult [05-external-assets-and-licensing.md](05-external-assets-and-licensing.md) for license audit checklists and attribution verification.

---

## 3. Foundational Governance & Decisions
- Master Decision: [ADR-0013: NebuOS UI Design System, Iconography, and Desktop Visual Architecture](../decisions/ADR-0013-ui-design-system-and-icon-architecture.md)
- Pluggable Paradigm Decision: [ADR-0009: NebuShell UI Architecture](../decisions/ADR-0009-nebushell-ui-architecture.md)
- Application Store Decision: [ADR-0012: Application Distribution and Marketplace](../decisions/ADR-0012-application-distribution-and-marketplace.md)
