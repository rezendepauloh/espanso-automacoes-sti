use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

/// Mapa de variáveis carregadas de .env (prioritário) e .env.example (fallback).
#[derive(Debug, Clone, Default)]
pub struct EnvStore {
    primary: HashMap<String, String>,
    fallback: HashMap<String, String>,
}

impl EnvStore {
    pub fn load_from_repo_root(repo_root: &Path) -> Self {
        let primary = parse_env_file(&repo_root.join(".env"));
        let fallback = parse_env_file(&repo_root.join(".env.example"));
        Self { primary, fallback }
    }

    pub fn from_maps(primary: HashMap<String, String>, fallback: HashMap<String, String>) -> Self {
        Self { primary, fallback }
    }

    /// Ordem de precedência: variável do processo -> .env -> .env.example -> default.
    pub fn get(&self, key: &str, default: &str) -> String {
        if let Ok(val) = std::env::var(key)
            && !val.is_empty()
        {
            return val;
        }
        if let Some(val) = self.primary.get(key)
            && !val.is_empty()
        {
            return val.clone();
        }
        if let Some(val) = self.fallback.get(key)
            && !val.is_empty()
        {
            return val.clone();
        }
        default.to_string()
    }

    pub fn get_list(&self, key: &str) -> Vec<String> {
        let raw = self.get(key, "");
        if raw.is_empty() {
            return Vec::new();
        }
        raw.split('|')
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect()
    }

    /// Substitui placeholders ${VAR} em uma string.
    pub fn interpolate_str(&self, input: &str) -> String {
        if !input.contains("${") {
            return input.to_string();
        }

        let mut out = String::with_capacity(input.len());
        let mut rest = input;
        while let Some(start) = rest.find("${") {
            out.push_str(&rest[..start]);
            let after_prefix = &rest[start + 2..];
            if let Some(end) = after_prefix.find('}') {
                let var_name = &after_prefix[..end];
                if is_valid_var_name(var_name) {
                    out.push_str(&self.get(var_name, ""));
                } else {
                    out.push_str("${");
                    out.push_str(var_name);
                    out.push('}');
                }
                rest = &after_prefix[end + 1..];
            } else {
                out.push_str(&rest[start..]);
                return out;
            }
        }
        out.push_str(rest);
        out
    }

    /// Se a string for exatamente "${VAR}", retorna Some("VAR").
    pub fn extract_exact_var(input: &str) -> Option<&str> {
        let trimmed = input.trim();
        let inner = trimmed.strip_prefix("${")?.strip_suffix('}')?;
        if is_valid_var_name(inner) {
            Some(inner)
        } else {
            None
        }
    }
}

fn is_valid_var_name(s: &str) -> bool {
    let mut chars = s.chars();
    let Some(first) = chars.next() else {
        return false;
    };
    (first.is_ascii_alphabetic() || first == '_')
        && chars.all(|c| c.is_ascii_alphanumeric() || c == '_')
}

pub fn parse_env_file(path: &Path) -> HashMap<String, String> {
    let mut map = HashMap::new();
    let Ok(content) = fs::read_to_string(path) else {
        return map;
    };

    for raw_line in content.lines() {
        let line = raw_line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let line = line.strip_prefix("export ").map(str::trim).unwrap_or(line);
        let Some((k, v)) = line.split_once('=') else {
            continue;
        };
        let key = k.trim();
        let mut val = v.trim().to_string();

        if val.len() >= 2 {
            let bytes = val.as_bytes();
            let first = bytes[0];
            let last = bytes[val.len() - 1];
            if (first == b'"' && last == b'"') || (first == b'\'' && last == b'\'') {
                let inner = &val[1..val.len() - 1];
                val = if first == b'"' {
                    inner.replace("\\\"", "\"").replace("\\\\", "\\")
                } else {
                    inner.to_string()
                };
            }
        }
        map.insert(key.to_string(), val);
    }

    map
}

/// Descobre a raiz do repositório espanso-automacoes-sti a partir de um arquivo de formulário,
/// variável ESPANSO_CONFIG_DIR ou diretório atual.
pub fn discover_repo_root(hint_path: Option<&Path>) -> PathBuf {
    if let Some(p) = hint_path {
        let abs = if p.is_absolute() {
            p.to_path_buf()
        } else {
            std::env::current_dir().unwrap_or_default().join(p)
        };
        let mut curr = abs.parent();
        while let Some(dir) = curr {
            if dir.join("forms").is_dir() && (dir.join("match").is_dir() || dir.join("scripts").is_dir()) {
                return dir.to_path_buf();
            }
            curr = dir.parent();
        }
    }

    if let Ok(espanso_dir) = std::env::var("ESPANSO_CONFIG_DIR") {
        let p = PathBuf::from(espanso_dir);
        if p.join("forms").is_dir() {
            return p;
        }
    }

    if let Ok(cwd) = std::env::current_dir() {
        let mut curr = Some(cwd.as_path());
        while let Some(dir) = curr {
            if dir.join("forms").is_dir() && dir.join("scripts").is_dir() {
                return dir.to_path_buf();
            }
            curr = dir.parent();
        }
    }

    if let Ok(exe) = std::env::current_exe() {
        let mut curr = exe.parent();
        while let Some(dir) = curr {
            if dir.join("forms").is_dir() && dir.join("scripts").is_dir() {
                return dir.to_path_buf();
            }
            curr = dir.parent();
        }
    }

    PathBuf::from(".")
}
