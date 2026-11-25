use crate::models::form_schema::UiRule;
use std::collections::HashMap;

/// Avalia se um campo deve estar visível considerando TODAS as regras aplicáveis (pai + filho).
/// Todas as regras herdadas e locais devem ser satisfeitas (AND lógico), corrigindo regras aninhadas como em `ola.yml`.
pub fn is_field_visible(
    field_name: &str,
    field_rules: &HashMap<String, Vec<UiRule>>,
    current_values: &HashMap<String, String>,
) -> bool {
    let Some(rules) = field_rules.get(field_name) else {
        return true;
    };

    rules.iter().all(|rule| evaluate_single_rule(rule, current_values))
}

pub fn evaluate_single_rule(rule: &UiRule, current_values: &HashMap<String, String>) -> bool {
    let trigger = rule.trigger_field();
    let expected = rule.expected_string();
    let actual = current_values.get(&trigger).map(String::as_str).unwrap_or("");
    let is_match = actual.trim() == expected.trim();

    match rule.effect.to_uppercase().as_str() {
        "HIDE" => !is_match,
        _ => is_match, // SHOW é o padrão
    }
}
