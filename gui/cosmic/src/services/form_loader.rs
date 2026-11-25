use crate::models::form_schema::{FormConfig, ResolvedDefault, SchemaProperty, UiElement, UiOptions, UiRule};
use crate::services::env_loader::{EnvStore, discover_repo_root};
use chrono::{Duration, Local, Timelike};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone)]
pub struct LoadedForm {
    pub form_name: String,
    pub display_title: String,
    pub config: FormConfig,
    /// Ordem exata das chaves em `schema.properties` no arquivo YAML.
    pub field_order: Vec<String>,
    /// Ordem normalizada de elementos do `uischema` (ou gerada a partir de `field_order`).
    pub layout_elements: Vec<UiElement>,
    /// Regras acumuladas por campo (container pai + regra própria do campo).
    pub field_rules: HashMap<String, Vec<UiRule>>,
    /// Valores iniciais já resolvidos com .env e defaults dinâmicos.
    pub resolved_defaults: HashMap<String, ResolvedDefault>,
    /// Metadados de opções por campo vindos do `uischema`.
    pub field_options: HashMap<String, UiOptions>,
}

pub fn resolve_form_path(form_arg: Option<&str>, config_arg: Option<&str>) -> Result<PathBuf, String> {
    if let Some(cfg) = config_arg {
        let p = PathBuf::from(cfg);
        if p.is_file() {
            return Ok(p);
        }
        return Err(format!("Arquivo de formulário não encontrado: {}", p.display()));
    }

    let name = form_arg.ok_or_else(|| "Informe --form <nome> ou --form-config <caminho>.".to_string())?;
    let clean = name.trim().trim_end_matches(".yml").trim_end_matches(".yaml");
    if clean.is_empty() || clean.contains('/') || clean.contains('\\') || clean.contains("..") {
        return Err(format!("Nome de formulário inválido: '{name}'"));
    }

    let root = discover_repo_root(None);
    let candidate = root.join("forms").join(format!("{clean}.yml"));
    if candidate.is_file() {
        return Ok(candidate);
    }

    Err(format!(
        "Formulário '{clean}' não encontrado em {}",
        candidate.display()
    ))
}

pub fn load_form_from_path(path: &Path) -> Result<LoadedForm, String> {
    let raw_yaml = fs::read_to_string(path)
        .map_err(|e| format!("Falha ao ler {}: {e}", path.display()))?;

    let config: FormConfig = serde_yaml::from_str(&raw_yaml)
        .map_err(|e| format!("Falha ao interpretar YAML {}: {e}", path.display()))?;

    // Preserva a ordem exata das propriedades no YAML original
    let field_order = extract_property_order(&raw_yaml, &config);

    let repo_root = discover_repo_root(Some(path));
    let env = EnvStore::load_from_repo_root(&repo_root);

    let form_name = path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("formulario")
        .to_string();

    let display_title = format!("Espanso STI — {}", prettify_name(&form_name));

    let layout_elements = if let Some(ui) = &config.uischema {
        ui.elements.clone()
    } else {
        field_order
            .iter()
            .map(|k| UiElement {
                element_type: "Control".to_string(),
                scope: Some(format!("#/properties/{k}")),
                elements: Vec::new(),
                options: None,
                rule: None,
            })
            .collect()
    };

    let mut field_rules: HashMap<String, Vec<UiRule>> = HashMap::new();
    let mut field_options: HashMap<String, UiOptions> = HashMap::new();
    collect_ui_metadata(&layout_elements, &[], &mut field_rules, &mut field_options);

    let mut resolved_defaults = resolve_defaults(&config, &env);
    apply_dynamic_defaults(&form_name, &mut resolved_defaults);

    Ok(LoadedForm {
        form_name,
        display_title,
        config,
        field_order,
        layout_elements,
        field_rules,
        resolved_defaults,
        field_options,
    })
}

fn prettify_name(name: &str) -> String {
    name.split('_')
        .filter(|s| !s.is_empty())
        .map(|word| {
            let mut chars = word.chars();
            match chars.next() {
                Some(first) => format!("{}{}", first.to_uppercase(), chars.as_str()),
                None => String::new(),
            }
        })
        .collect::<Vec<_>>()
        .join(" ")
}

fn extract_property_order(raw_yaml: &str, config: &FormConfig) -> Vec<String> {
    if let Ok(serde_yaml::Value::Mapping(root)) = serde_yaml::from_str::<serde_yaml::Value>(raw_yaml)
        && let Some(serde_yaml::Value::Mapping(schema)) = root.get(serde_yaml::Value::String("schema".into()))
        && let Some(serde_yaml::Value::Mapping(props)) = schema.get(serde_yaml::Value::String("properties".into()))
    {
        let mut ordered = Vec::with_capacity(props.len());
        for (k, _) in props {
            if let serde_yaml::Value::String(name) = k {
                ordered.push(name.clone());
            }
        }
        if !ordered.is_empty() {
            return ordered;
        }
    }
    config.schema.properties.keys().cloned().collect()
}

fn collect_ui_metadata(
    elements: &[UiElement],
    inherited_rules: &[UiRule],
    field_rules: &mut HashMap<String, Vec<UiRule>>,
    field_options: &mut HashMap<String, UiOptions>,
) {
    for el in elements {
        let mut active_rules = inherited_rules.to_vec();
        if let Some(rule) = &el.rule {
            active_rules.push(rule.clone());
        }

        if let Some(scope) = &el.scope {
            let field_name = scope.trim_start_matches("#/properties/").to_string();
            if !field_name.is_empty() {
                if !active_rules.is_empty() {
                    field_rules.insert(field_name.clone(), active_rules.clone());
                }
                if let Some(opts) = &el.options {
                    field_options.insert(field_name, opts.clone());
                }
            }
        }

        if !el.elements.is_empty() {
            collect_ui_metadata(&el.elements, &active_rules, field_rules, field_options);
        }
    }
}

fn resolve_defaults(config: &FormConfig, env: &EnvStore) -> HashMap<String, ResolvedDefault> {
    let mut out = HashMap::new();

    for (key, prop) in &config.schema.properties {
        let raw_val = config.data.get(key);
        let resolved = resolve_single_default(prop, raw_val, env);
        out.insert(key.clone(), resolved);
    }

    out
}

fn resolve_single_default(
    prop: &SchemaProperty,
    raw_val: Option<&serde_yaml::Value>,
    env: &EnvStore,
) -> ResolvedDefault {
    match prop.field_type.as_str() {
        "array" => {
            let items = match raw_val {
                Some(serde_yaml::Value::String(s)) => {
                    if let Some(var_name) = EnvStore::extract_exact_var(s) {
                        env.get_list(var_name)
                    } else {
                        let interp = env.interpolate_str(s);
                        if interp.is_empty() {
                            Vec::new()
                        } else {
                            interp.lines().map(|l| l.trim().to_string()).filter(|l| !l.is_empty()).collect()
                        }
                    }
                }
                Some(serde_yaml::Value::Sequence(seq)) => {
                    let mut list = Vec::new();
                    for item in seq {
                        if let Some(s) = item.as_str() {
                            if let Some(var_name) = EnvStore::extract_exact_var(s) {
                                list.extend(env.get_list(var_name));
                            } else {
                                let interp = env.interpolate_str(s);
                                if !interp.is_empty() {
                                    list.push(interp);
                                }
                            }
                        }
                    }
                    list
                }
                _ => Vec::new(),
            };
            ResolvedDefault::List(items)
        }
        "boolean" => {
            let b = match raw_val {
                Some(serde_yaml::Value::Bool(b)) => *b,
                Some(serde_yaml::Value::String(s)) => {
                    matches!(env.interpolate_str(s).trim().to_lowercase().as_str(), "true" | "1" | "sim")
                }
                _ => false,
            };
            ResolvedDefault::Bool(b)
        }
        _ => {
            let text = match raw_val {
                Some(serde_yaml::Value::String(s)) => env.interpolate_str(s),
                Some(serde_yaml::Value::Number(n)) => n.to_string(),
                Some(serde_yaml::Value::Bool(b)) => b.to_string(),
                _ => String::new(),
            };
            ResolvedDefault::Text(text)
        }
    }
}

fn apply_dynamic_defaults(form_name: &str, defaults: &mut HashMap<String, ResolvedDefault>) {
    if form_name == "transporte_urbano" {
        let should_fill = matches!(
            defaults.get("hora_hoje"),
            Some(ResolvedDefault::Text(t)) if t.trim().is_empty()
        ) || !defaults.contains_key("hora_hoje");

        if should_fill {
            let suggested = compute_rounded_time_plus_30(Local::now());
            defaults.insert("hora_hoje".to_string(), ResolvedDefault::Text(suggested));
        }
    }
}

/// Soma 30 minutos ao horário atual e arredonda para o próximo bloco de 30 minutos.
pub fn compute_rounded_time_plus_30<Tz: chrono::TimeZone>(now: chrono::DateTime<Tz>) -> String
where
    Tz::Offset: std::fmt::Display,
{
    let plus_30 = now + Duration::minutes(30);
    let min = plus_30.minute();
    let rounded = if min == 0 {
        plus_30
    } else if min <= 30 {
        plus_30 + Duration::minutes((30 - min) as i64)
    } else {
        plus_30 + Duration::minutes((60 - min) as i64)
    };
    rounded.format("%H:%M").to_string()
}
