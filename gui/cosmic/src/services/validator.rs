use crate::models::form_schema::{FormConfig, SchemaProperty, UiOptions};
use chrono::NaiveDate;
use std::collections::HashMap;

/// Normaliza uma string de data aceitando DD/MM/YYYY ou YYYY-MM-DD para o formato ISO YYYY-MM-DD.
pub fn normalize_date_to_iso(raw: &str) -> Result<String, String> {
    let trimmed = raw.trim();
    if trimmed.is_empty() {
        return Ok(String::new());
    }

    if let Ok(dt) = NaiveDate::parse_from_str(trimmed, "%Y-%m-%d") {
        return Ok(dt.format("%Y-%m-%d").to_string());
    }
    if let Ok(dt) = NaiveDate::parse_from_str(trimmed, "%d/%m/%Y") {
        return Ok(dt.format("%Y-%m-%d").to_string());
    }

    Err(format!(
        "Data inválida: '{trimmed}'. Use DD/MM/AAAA (ex: 25/11/2026) ou AAAA-MM-DD."
    ))
}

/// Converte uma data ISO YYYY-MM-DD para exibição brasileira DD/MM/YYYY.
pub fn iso_to_br_date(raw: &str) -> String {
    let trimmed = raw.trim();
    if let Ok(dt) = NaiveDate::parse_from_str(trimmed, "%Y-%m-%d") {
        return dt.format("%d/%m/%Y").to_string();
    }
    trimmed.to_string()
}

/// Validação de identificador seguro (hostname, IP ou usuário) para formulários administrativos.
pub fn is_safe_identifier(value: &str) -> bool {
    let trimmed = value.trim();
    !trimmed.is_empty()
        && trimmed
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || matches!(c, '.' | '_' | '-' | ':'))
}

/// Validação de caminho seguro sem metacaracteres perigosos de shell.
pub fn is_safe_path_arg(value: &str) -> bool {
    !value
        .chars()
        .any(|c| matches!(c, ';' | '&' | '|' | '`' | '$' | '(' | ')' | '<' | '>' | '"' | '\'' | '\r' | '\n'))
}

pub fn validate_submission(
    form_name: &str,
    config: &FormConfig,
    visible_values: &HashMap<String, String>,
    visibility: &HashMap<String, bool>,
    _field_options: &HashMap<String, UiOptions>,
) -> Result<(), String> {
    for req_field in &config.schema.required {
        let is_visible = visibility.get(req_field).copied().unwrap_or(true);
        if !is_visible {
            continue;
        }
        let val = visible_values.get(req_field).map(String::as_str).unwrap_or("");
        if val.trim().is_empty() {
            let label = config
                .schema
                .properties
                .get(req_field)
                .and_then(|p| p.title.as_deref())
                .unwrap_or(req_field);
            return Err(format!("O campo obrigatório \"{}\" precisa ser preenchido.", label.trim_end_matches(':')));
        }
    }

    for (field, prop) in &config.schema.properties {
        let is_visible = visibility.get(field).copied().unwrap_or(true);
        if !is_visible {
            continue;
        }
        let val = visible_values.get(field).map(String::as_str).unwrap_or("").trim();
        if val.is_empty() {
            continue;
        }

        validate_field_type(form_name, field, prop, val)?;
    }

    Ok(())
}

fn validate_field_type(
    form_name: &str,
    field: &str,
    prop: &SchemaProperty,
    val: &str,
) -> Result<(), String> {
    let label = prop.title.as_deref().unwrap_or(field).trim_end_matches(':');

    if prop.field_type == "integer" && val.parse::<i64>().is_err() {
        return Err(format!("O campo \"{label}\" deve conter um número inteiro válido."));
    }

    if prop.format.as_deref() == Some("date") {
        normalize_date_to_iso(val)?;
    }

    if matches!(form_name, "analisador" | "manutencao" | "remove_profiles") {
        if field == "computer_name" && !is_safe_identifier(val) {
            return Err(format!("O campo \"{label}\" contém caracteres não permitidos para hostname/IP."));
        }
        if field == "output_folder" && !is_safe_path_arg(val) {
            return Err(format!("O campo \"{label}\" contém caracteres de shell não permitidos."));
        }
        if field == "users_to_purge" {
            for user in val.split(',').map(str::trim).filter(|s| !s.is_empty()) {
                if !is_safe_identifier(user) {
                    return Err(format!("Usuário inválido em \"{label}\": '{user}'."));
                }
            }
        }
    }

    Ok(())
}
