//! NebuCompositor Binary Entrypoint — NebuOS Milestone P1

use std::process::ExitCode;

fn main() -> ExitCode {
    match nebu_compositor::run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(err) => {
            eprintln!("nebu-compositor fatal error: {err}");
            ExitCode::FAILURE
        }
    }
}
