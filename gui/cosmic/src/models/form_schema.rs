use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

/// Representação completa de um arquivo forms/*.yml (JSON Schema + JSON Forms UI Schema).
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct FormConfig {
    pub schema: FormSchema,
    #[serde(default)]
    pub uischema: Option<UiElement>,
    #[serde(default)]
    pub data: BTreeMap<String, serde_yaml::Value>,
    #[serde(default)]
    pub template: String,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct FormSchema {
    #[serde(rename = "type", default)]
    pub schema_type: String,
    #[serde(default)]
    pub properties: BTreeMap<String, SchemaProperty>,
    #[serde(default)]
    pub required: Vec<String>,
}

/// Ordem dos campos no YAML precisa ser preservada, portanto também extraímos a ordem a partir de Value/Mapping ou uischema.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct SchemaProperty {
    #[serde(rename = "type", default = "default_string_type")]
    pub field_type: String,
    #[serde(default)]
    pub title: Option<String>,
    #[serde(default)]
    pub format: Option<String>,
    #[serde(rename = "enum", default)]
    pub enum_values: Option<Vec<String>>,
    #[serde(default)]
    pub items: Option<Box<SchemaProperty>>,
}

fn default_string_type() -> String {
    "string".to_string()
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct UiElement {
    #[serde(rename = "type")]
    pub element_type: String,
    #[serde(default)]
    pub scope: Option<String>,
    #[serde(default)]
    pub elements: Vec<UiElement>,
    #[serde(default)]
    pub options: Option<UiOptions>,
    #[serde(default)]
    pub rule: Option<UiRule>,
}

#[derive(Debug, Clone, Default, Deserialize, Serialize)]
pub struct UiOptions {
    #[serde(default)]
    pub multi: Option<bool>,
    #[serde(default)]
    pub rows: Option<u16>,
    #[serde(default)]
    pub placeholder: Option<String>,
    #[serde(default)]
    pub format: Option<String>,
    #[serde(rename = "dateFormat", default)]
    pub date_format: Option<String>,
    #[serde(rename = "dateSaveFormat", default)]
    pub date_save_format: Option<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct UiRule {
    #[serde(default = "default_effect")]
    pub effect: String,
    pub condition: RuleCondition,
}

fn default_effect() -> String {
    "SHOW".to_string()
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct RuleCondition {
    pub scope: String,
    pub schema: RuleSchema,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct RuleSchema {
    #[serde(rename = "const", default)]
    pub const_val: Option<serde_yaml::Value>,
}

impl UiRule {
    pub fn trigger_field(&self) -> String {
        self.condition
            .scope
            .trim_start_matches("#/properties/")
            .to_string()
    }

    pub fn expected_string(&self) -> String {
        match &self.condition.schema.const_val {
            Some(serde_yaml::Value::String(s)) => s.clone(),
            Some(serde_yaml::Value::Number(n)) => n.to_string(),
            Some(serde_yaml::Value::Bool(b)) => b.to_string(),
            _ => String::new(),
        }
    }
}

/// Valor inicial já resolvido (após interpolação de .env e padrões dinâmicos).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ResolvedDefault {
    Text(String),
    List(Vec<String>),
    Bool(bool),
}
