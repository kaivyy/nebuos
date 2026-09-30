//! NebuShell lifecycle state machine.
#![deny(unsafe_code)]

use crate::error::{ShellError, ShellResult};
use std::time::Instant;

/// Lifecycle state for NebuShell instance.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ShellState {
    /// Initial uninitialized state.
    Uninitialized,
    /// Connecting to the Wayland compositor socket.
    Connecting,
    /// Connected to compositor and validated required globals.
    Connected,
    /// Layer shell surfaces created and configured by compositor.
    SurfacesConfigured,
    /// Active rendering and dispatch loop running.
    Active,
    /// Shutting down surfaces and preparing to close socket.
    ShuttingDown,
    /// Terminated, all resources freed.
    Terminated,
}

impl ShellState {
    /// Validate whether transition to target state is legally permitted.
    pub fn can_transition_to(self, target: ShellState) -> bool {
        match (self, target) {
            (ShellState::Uninitialized, ShellState::Connecting) => true,
            (ShellState::Connecting, ShellState::Connected) => true,
            (ShellState::Connecting, ShellState::Terminated) => true,
            (ShellState::Connected, ShellState::SurfacesConfigured) => true,
            (ShellState::Connected, ShellState::ShuttingDown) => true,
            (ShellState::SurfacesConfigured, ShellState::Active) => true,
            (ShellState::SurfacesConfigured, ShellState::ShuttingDown) => true,
            (ShellState::Active, ShellState::ShuttingDown) => true,
            (ShellState::ShuttingDown, ShellState::Terminated) => true,
            // Re-entrant / idempotent transitions
            (s1, s2) if s1 == s2 => true,
            _ => false,
        }
    }
}

/// Lifecycle manager tracking state progression.
#[derive(Debug)]
pub struct ShellLifecycle {
    current: ShellState,
    history: Vec<(ShellState, Instant)>,
}

impl Default for ShellLifecycle {
    fn default() -> Self {
        Self::new()
    }
}

impl ShellLifecycle {
    pub fn new() -> Self {
        let now = Instant::now();
        Self {
            current: ShellState::Uninitialized,
            history: vec![(ShellState::Uninitialized, now)],
        }
    }

    pub fn current(&self) -> ShellState {
        self.current
    }

    pub fn transition_to(&mut self, next: ShellState) -> ShellResult<()> {
        if !self.current.can_transition_to(next) {
            return Err(ShellError::LifecycleError(format!(
                "Illegal lifecycle transition: {:?} -> {:?}",
                self.current, next
            )));
        }
        self.current = next;
        self.history.push((next, Instant::now()));
        Ok(())
    }

    pub fn history(&self) -> &[(ShellState, Instant)] {
        &self.history
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_lifecycle_transitions() {
        let mut lc = ShellLifecycle::new();
        assert_eq!(lc.current(), ShellState::Uninitialized);

        lc.transition_to(ShellState::Connecting).unwrap();
        lc.transition_to(ShellState::Connected).unwrap();
        lc.transition_to(ShellState::SurfacesConfigured).unwrap();
        lc.transition_to(ShellState::Active).unwrap();
        lc.transition_to(ShellState::ShuttingDown).unwrap();
        lc.transition_to(ShellState::Terminated).unwrap();

        assert_eq!(lc.current(), ShellState::Terminated);
    }

    #[test]
    fn test_invalid_transition() {
        let mut lc = ShellLifecycle::new();
        let res = lc.transition_to(ShellState::Active);
        assert!(res.is_err());
    }
}
