# CPU Utilization & Wakeup Architecture — NebuOS

**Status:** REVIEW  
**Purpose:** Detail the zero-polling invariant, timer coalescing, event-driven daemons, and energy-aware CPU frequency governance.

---

## 1. The Zero-Polling Invariant
No NebuOS daemon or userland component is permitted to use `sleep()` in an active loop or poll filesystems/hardware at high frequency.
- **Event-Driven Architecture:** All daemon main loops are strictly driven by `epoll`, `timerfd`, `signalfd`, and `eventfd`.
- **Timer Coalescing:** Non-urgent background timers (e.g. update checks, battery polling) are aligned to 60-second ticks to allow the CPU to remain in deep C-states (C6/C7/C8).

## 2. Idle State Invariant
At idle desktop (no user interaction, no background tasks), total CPU utilization across all CPU cores must measure **< 0.5%**, preventing laptop fan spin-up and maximizing battery endurance.

## 3. Related Documents
- [00-performance-goals.md](00-performance-goals.md)
- [01-memory.md](01-memory.md)
