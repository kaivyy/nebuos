//! NebuCompositor Binary Entrypoint — NebuOS Milestone P1

#![forbid(unsafe_code)]

use std::env;
use std::process::ExitCode;

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    if args.iter().any(|arg| arg == "--renderer-probe") {
        match nebu_compositor::render::run_renderer_probe() {
            Ok(report) => {
                if report.probe_success {
                    ExitCode::SUCCESS
                } else {
                    ExitCode::FAILURE
                }
            }
            Err(err) => {
                eprintln!("nebu-compositor --renderer-probe failed: {err}");
                ExitCode::FAILURE
            }
        }
    } else if args.iter().any(|arg| arg == "--drm-probe") {
        match nebu_compositor::backend::run_drm_probe() {
            Ok(report) => {
                if report.probe_success {
                    ExitCode::SUCCESS
                } else {
                    ExitCode::FAILURE
                }
            }
            Err(err) => {
                eprintln!("nebu-compositor --drm-probe failed: {err}");
                ExitCode::FAILURE
            }
        }
    } else {
        match nebu_compositor::run() {
            Ok(()) => ExitCode::SUCCESS,
            Err(err) => {
                eprintln!("nebu-compositor fatal error: {err}");
                ExitCode::FAILURE
            }
        }
    }
}
