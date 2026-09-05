//! NebuCompositor Binary Entrypoint — NebuOS Milestone P1

#![forbid(unsafe_code)]

use std::env;
use std::process::ExitCode;

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    if args.iter().any(|arg| arg == "--wayland-probe") {
        match nebu_compositor::wayland::run_wayland_probe() {
            Ok(report) => {
                if report.probe_success {
                    ExitCode::SUCCESS
                } else {
                    ExitCode::FAILURE
                }
            }
            Err(err) => {
                eprintln!("nebu-compositor --wayland-probe failed: {err}");
                ExitCode::FAILURE
            }
        }
    } else if args.iter().any(|arg| arg == "--input-probe") {
        match nebu_compositor::input::run_input_probe() {
            Ok(report) => {
                if report.probe_success {
                    ExitCode::SUCCESS
                } else {
                    ExitCode::FAILURE
                }
            }
            Err(err) => {
                eprintln!("nebu-compositor --input-probe failed: {err}");
                ExitCode::FAILURE
            }
        }
    } else if args.iter().any(|arg| arg == "--output-probe") {
        match nebu_compositor::output::run_output_probe() {
            Ok(report) => {
                if report.probe_success {
                    ExitCode::SUCCESS
                } else {
                    ExitCode::FAILURE
                }
            }
            Err(err) => {
                eprintln!("nebu-compositor --output-probe failed: {err}");
                ExitCode::FAILURE
            }
        }
    } else if args.iter().any(|arg| arg == "--renderer-probe") {
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
    } else if args.iter().any(|arg| arg == "--help" || arg == "-h") {
        println!("NebuCompositor — NebuOS Display Server Substrate");
        println!();
        println!("Usage: nebu-compositor [OPTIONS]");
        println!();
        println!("Options:");
        println!(
            "  --wayland-probe    Execute Milestone P1.6 Wayland Core & Surface Lifecycle Proof"
        );
        println!("  --input-probe      Execute Milestone P1.5 Input Subsystem Integration Proof");
        println!(
            "  --output-probe     Execute Milestone P1.4 Output Presentation & Event-Loop Proof"
        );
        println!("  --renderer-probe   Execute Milestone P1.3 Renderer Initialization Proof");
        println!("  --drm-probe        Execute Milestone P1.2 DRM/KMS Proof");
        println!("  --help, -h         Print this help message");
        ExitCode::SUCCESS
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
