use crate::models::form_schema::FormConfig;
use std::collections::{BTreeMap, HashMap};

/// Normaliza valores derivados antes de gerar a saída final (ex.: `hora` em `transporte_urbano.yml`).
pub fn finalize_output_values(
    config: &FormConfig,
    values: &HashMap<String, String>,
) -> HashMap<String, String> {
    let mut final_values = values.clone();

    if config.template.contains("{% if data == 'hoje' %}") {
        let data_val = final_values.get("data").map(String::as_str).unwrap_or("");
        let hora_final = if data_val == "hoje" {
            final_values.get("hora_hoje").cloned().unwrap_or_default()
        } else {
            final_values.get("hora").cloned().unwrap_or_default()
        };
        final_values.insert("hora".to_string(), hora_final);
    }

    final_values
}

/// Formata os valores finais respeitando o contrato `template` / `EDF` esperado pelos scripts Python
/// ou gera JSON estruturado quando `--json` é solicitado.
pub fn format_output(
    config: &FormConfig,
    field_order: &[String],
    values: &HashMap<String, String>,
    as_json: bool,
) -> Result<String, String> {
    let final_values = finalize_output_values(config, values);

    if as_json {
        let mut ordered = BTreeMap::new();
        for key in field_order {
            ordered.insert(key.clone(), final_values.get(key).cloned().unwrap_or_default());
        }
        return serde_json::to_string_pretty(&ordered)
            .map_err(|e| format!("Erro ao serializar JSON: {e}"));
    }

    let ordered_keys: Vec<String> = if config.template.contains("{% if data == 'hoje' %}") {
        ["data", "data_manual", "hora", "local", "demandas", "passageiros"]
            .into_iter()
            .map(String::from)
            .collect()
    } else {
        field_order.to_vec()
    };

    let mut out = String::new();
    for key in ordered_keys {
        out.push_str(&format!("===FIELD:{key}===\n"));
        let v = final_values.get(&key).map(String::as_str).unwrap_or("");
        if !v.is_empty() {
            out.push_str(v);
            out.push('\n');
        }
    }
    out.push_str("===END===\n");
    Ok(out)
}
