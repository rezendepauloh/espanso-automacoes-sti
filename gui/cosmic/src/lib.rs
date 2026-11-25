pub mod app;
pub mod models;
pub mod services;

use crate::app::{AppFlags, AppModel};
use crate::services::form_loader::{load_form_from_path, resolve_form_path};
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone)]
pub struct CliOptions {
    pub form_name: Option<String>,
    pub form_config: Option<String>,
    pub json_output: bool,
    pub dump_resolved: bool,
}

pub fn run_cli(opts: CliOptions) -> Result<Option<String>, String> {
    let path = resolve_form_path(opts.form_name.as_deref(), opts.form_config.as_deref())?;
    let loaded = load_form_from_path(&path)?;

    if opts.dump_resolved {
        let dump = serde_json::json!({
            "form_name": loaded.form_name,
            "display_title": loaded.display_title,
            "field_order": loaded.field_order,
            "resolved_defaults": loaded.resolved_defaults,
        });
        let text = serde_json::to_string_pretty(&dump)
            .map_err(|e| format!("Erro ao serializar JSON: {e}"))?;
        return Ok(Some(text));
    }

    let result_slot = Arc::new(Mutex::new(None));
    let flags = AppFlags {
        loaded,
        json_output: opts.json_output,
        result_slot: Arc::clone(&result_slot),
    };

    let settings = cosmic::app::Settings::default()
        .size(cosmic::iced::Size::new(620.0, 680.0))
        .size_limits(
            cosmic::iced::Limits::NONE
                .min_width(480.0)
                .min_height(380.0),
        );

    cosmic::app::run::<AppModel>(settings, flags)
        .map_err(|e| format!("Erro na interface COSMIC: {e}"))?;

    let final_output = result_slot
        .lock()
        .map_err(|_| "Falha ao ler resultado do formulário.".to_string())?
        .take();

    Ok(final_output)
}
