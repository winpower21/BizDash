#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{Manager, AppHandle};
use tauri_plugin_shell::{ShellExt, process::CommandChild};
use std::sync::Mutex;

struct BackendState {
    child: Mutex<Option<CommandChild>>,
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(BackendState {
            child: Mutex::new(None),
        })
        .setup(|app| {
            start_backend(app.handle().clone());
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                kill_backend(window.app_handle().clone());
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri app");
}

fn start_backend(app: AppHandle) {
    tauri::async_runtime::spawn(async move {
        let state = app.state::<BackendState>();

        let (rx, child) = app
            .shell()
            .sidecar("bizdash-backend")
            .expect("sidecar not found")
            .spawn()
            .expect("failed to spawn backend");

        *state.child.lock().unwrap() = Some(child);

        println!("Backend process spawned");

        // while let Some(event) = rx.recv().await {
        //     match event {
        //         tauri_plugin_shell::process::CommandEvent::Stdout(line) => {
        //             println!("BACKEND: {}", String::from_utf8_lossy(&line));
        //         }
        //         tauri_plugin_shell::process::CommandEvent::Stderr(line) => {
        //             eprintln!("BACKEND ERR: {}", String::from_utf8_lossy(&line));
        //         }
        //         _ => {}
        //     }
        // }
    });
}

fn kill_backend(app: AppHandle) {
    let state = app.state::<BackendState>();

    // shorten mutex guard lifetime
    let child_opt = {
        state.child.lock().unwrap().take()
    };

    if let Some(child) = child_opt {
        let _ = child.kill();
        println!("Backend killed");
    }
}
