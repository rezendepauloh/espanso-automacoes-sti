use chrono::{TimeZone, Utc};
use std::collections::HashMap;
use std::path::PathBuf;
use sti_forms::models::form_schema::ResolvedDefault;
use sti_forms::services::env_loader::EnvStore;
use sti_forms::services::form_loader::{compute_rounded_time_plus_30, load_form_from_path};
use sti_forms::services::output_formatter::format_output;
use sti_forms::services::rule_engine::is_field_visible;
use sti_forms::services::validator::{iso_to_br_date, normalize_date_to_iso, validate_submission};

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(|p| p.parent())
        .expect("gui/cosmic deve ficar 2 níveis abaixo da raiz do repo")
        .to_path_buf()
}

#[test]
fn load_all_forms_and_resolve_env_defaults() {
    let forms_dir = repo_root().join("forms");
    let entries = std::fs::read_dir(&forms_dir).expect("pasta forms/ existe");

    let mut count = 0;
    for entry in entries.flatten() {
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) == Some("yml") {
            let loaded = load_form_from_path(&path)
                .unwrap_or_else(|e| panic!("Falha ao carregar {}: {e}", path.display()));
            assert!(!loaded.field_order.is_empty(), "field_order vazio em {}", path.display());
            count += 1;
        }
    }
    assert!(count >= 10, "esperava pelo menos 10 formulários YAML, encontrou {count}");
}

#[test]
fn ola_nested_rules_require_parent_and_child() {
    let loaded = load_form_from_path(&repo_root().join("forms/ola.yml")).unwrap();

    let mut vals = HashMap::new();
    vals.insert("tipo".to_string(), "🐢 Lentidão".to_string());
    vals.insert("tipo_material".to_string(), "permanente".to_string());

    // Mesmo com tipo_material == "permanente", se tipo != "📦 Material", patrimonio deve ficar OCULTO!
    assert!(!is_field_visible("equipamento", &loaded.field_rules, &vals));
    assert!(!is_field_visible("tipo_material", &loaded.field_rules, &vals));
    assert!(!is_field_visible("patrimonio", &loaded.field_rules, &vals));

    vals.insert("tipo".to_string(), "📦 Material".to_string());
    vals.insert("tipo_material".to_string(), "consumo".to_string());
    assert!(is_field_visible("equipamento", &loaded.field_rules, &vals));
    assert!(!is_field_visible("patrimonio", &loaded.field_rules, &vals));

    vals.insert("tipo_material".to_string(), "permanente".to_string());
    assert!(is_field_visible("patrimonio", &loaded.field_rules, &vals));
}

#[test]
fn transporte_urbano_dynamic_time_and_output_mapping() {
    let loaded = load_form_from_path(&repo_root().join("forms/transporte_urbano.yml")).unwrap();

    // Deve ter resolvido `local` e `passageiros` como listas não vazias (via .env ou .env.example)
    match loaded.resolved_defaults.get("local") {
        Some(ResolvedDefault::List(items)) => assert!(!items.is_empty()),
        other => panic!("Esperava List para local, veio: {other:?}"),
    }
    match loaded.resolved_defaults.get("hora_hoje") {
        Some(ResolvedDefault::Text(h)) => assert!(h.contains(':')),
        other => panic!("Esperava Text para hora_hoje, veio: {other:?}"),
    }

    let dt = Utc.with_ymd_and_hms(2026, 11, 25, 14, 10, 0).unwrap();
    assert_eq!(compute_rounded_time_plus_30(dt), "15:00");

    let dt2 = Utc.with_ymd_and_hms(2026, 11, 25, 14, 45, 0).unwrap();
    assert_eq!(compute_rounded_time_plus_30(dt2), "15:30");

    let mut vals = HashMap::new();
    vals.insert("data".to_string(), "hoje".to_string());
    vals.insert("hora_hoje".to_string(), "15:00".to_string());
    vals.insert("hora".to_string(), "09:00".to_string());
    vals.insert("local".to_string(), "DMP".to_string());
    vals.insert("demandas".to_string(), "Chamado 1".to_string());
    vals.insert("passageiros".to_string(), "Servidor 1".to_string());

    let out = format_output(&loaded.config, &loaded.field_order, &vals, false).unwrap();
    assert!(out.contains("===FIELD:hora===\n15:00\n"));
}

#[test]
fn env_store_interpolates_strings_and_arrays() {
    let mut primary = HashMap::new();
    primary.insert("STI_TEST_LIST".to_string(), "A|B|C".to_string());
    primary.insert("STI_TEST_STR".to_string(), "123".to_string());
    let store = EnvStore::from_maps(primary, HashMap::new());

    assert_eq!(store.get_list("STI_TEST_LIST"), vec!["A", "B", "C"]);
    assert_eq!(store.interpolate_str("Ramal ${STI_TEST_STR}"), "Ramal 123");
}

#[test]
fn validator_enforces_required_dates_integers_and_safe_identifiers() {
    assert_eq!(normalize_date_to_iso("25/11/2026").unwrap(), "2026-11-25");
    assert_eq!(iso_to_br_date("2026-11-25"), "25/11/2026");
    assert!(normalize_date_to_iso("99/99/2026").is_err());

    let loaded = load_form_from_path(&repo_root().join("forms/analisador.yml")).unwrap();
    let mut vals = HashMap::new();
    vals.insert("computer_name".to_string(), "PC-01;whoami".to_string());
    vals.insert("timeout_sec".to_string(), "30".to_string());
    let vis = HashMap::from([
        ("computer_name".to_string(), true),
        ("output_folder".to_string(), true),
        ("timeout_sec".to_string(), true),
        ("skip_major_data".to_string(), true),
    ]);
    assert!(
        validate_submission("analisador", &loaded.config, &vals, &vis, &loaded.field_options)
            .is_err()
    );
}

#[test]
fn celular_and_transporte_urbano_visibility_rules() {
    let celular = load_form_from_path(&repo_root().join("forms/celular.yml")).unwrap();
    let mut vals = HashMap::new();
    vals.insert(
        "modelo".to_string(),
        "Modelo 01 - Quando há observação".to_string(),
    );
    assert!(!is_field_visible("critica", &celular.field_rules, &vals));

    vals.insert(
        "modelo".to_string(),
        "Modelo 03 - Quando a observação é crítica".to_string(),
    );
    assert!(is_field_visible("critica", &celular.field_rules, &vals));

    let urbano = load_form_from_path(&repo_root().join("forms/transporte_urbano.yml")).unwrap();
    let mut uvals = HashMap::new();
    uvals.insert("data".to_string(), "hoje".to_string());
    assert!(is_field_visible("hora_hoje", &urbano.field_rules, &uvals));
    assert!(!is_field_visible("hora", &urbano.field_rules, &uvals));
    assert!(!is_field_visible("data_manual", &urbano.field_rules, &uvals));

    uvals.insert("data".to_string(), "outro dia".to_string());
    assert!(!is_field_visible("hora_hoje", &urbano.field_rules, &uvals));
    assert!(is_field_visible("hora", &urbano.field_rules, &uvals));
    assert!(is_field_visible("data_manual", &urbano.field_rules, &uvals));
}

#[test]
fn all_forms_can_validate_and_format_edf_and_json() {
    let forms_dir = repo_root().join("forms");
    for entry in std::fs::read_dir(&forms_dir).unwrap().flatten() {
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("yml") {
            continue;
        }
        let loaded = load_form_from_path(&path).unwrap();
        let mut vals = HashMap::new();
        for key in &loaded.field_order {
            vals.insert(key.clone(), "teste_ok".to_string());
        }
        let edf = format_output(&loaded.config, &loaded.field_order, &vals, false).unwrap();
        assert!(edf.contains("===END==="), "Faltou ===END=== em {}", loaded.form_name);

        let json_str = format_output(&loaded.config, &loaded.field_order, &vals, true).unwrap();
        let parsed: serde_json::Value = serde_json::from_str(&json_str).unwrap();
        assert!(parsed.is_object(), "Saída JSON inválida em {}", loaded.form_name);
    }
}
