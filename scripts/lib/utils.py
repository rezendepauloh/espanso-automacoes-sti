# -*- coding: utf-8 -*-
import sys
import io
from pathlib import Path
import re
import os

# Carrega o modelo de português (Lazy loading)
_nlp = None
_env_cache = None
_env_example_cache = None


def _get_repo_root():
    """Retorna a raiz do repositório (pai de scripts/)."""
    return Path(__file__).resolve().parent.parent.parent


def _parse_env_file(file_path):
    """Faz parsing simples e seguro de arquivos .env sem dependências externas."""
    values = {}
    if not file_path.exists():
        return values

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and ((val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")):
            quote = val[0]
            val = val[1:-1]
            if quote == '"':
                val = val.replace('\\"', '"').replace('\\\\', '\\')
        values[key] = val
    return values


def load_env(force_reload=False):
    """Carrega variáveis de .env (prioritário) e .env.example (fallback)."""
    global _env_cache, _env_example_cache
    if force_reload or _env_cache is None or _env_example_cache is None:
        root = _get_repo_root()
        _env_cache = _parse_env_file(root / ".env")
        _env_example_cache = _parse_env_file(root / ".env.example")
    return _env_cache


def get_env(key, default=""):
    """Obtém variável de ambiente: os.environ -> .env -> .env.example -> default."""
    if key in os.environ and os.environ[key] != "":
        return os.environ[key]
    env_map = load_env()
    if key in env_map and env_map[key] != "":
        return env_map[key]
    if _env_example_cache and key in _env_example_cache and _env_example_cache[key] != "":
        return _env_example_cache[key]
    return default


def get_env_list(key, sep="|", default=None):
    """Obtém lista de valores a partir de variável separada por '|'."""
    raw = get_env(key, "")
    if not raw:
        return list(default) if default else []
    return [item.strip() for item in raw.split(sep) if item.strip()]


def interpolate_env_str(text):
    """Substitui placeholders ${VAR} em strings usando get_env()."""
    if not isinstance(text, str) or "${" not in text:
        return text
    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", lambda m: get_env(m.group(1), ""), text)


def resolve_form_data(form_data):
    """Resolve placeholders ${VAR} na seção 'data' de um esquema de formulário YAML."""
    if not isinstance(form_data, dict):
        return form_data

    resolved = dict(form_data)
    properties = resolved.get("schema", {}).get("properties", {}) or {}
    data = dict(resolved.get("data", {}) or {})

    for key, val in data.items():
        field_type = (properties.get(key) or {}).get("type")
        if isinstance(val, str):
            exact_match = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", val.strip())
            if exact_match and field_type == "array":
                data[key] = get_env_list(exact_match.group(1))
            else:
                data[key] = interpolate_env_str(val)
        elif isinstance(val, list):
            expanded = []
            for item in val:
                if isinstance(item, str):
                    exact_match = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", item.strip())
                    if exact_match:
                        expanded.extend(get_env_list(exact_match.group(1)))
                    else:
                        expanded.append(interpolate_env_str(item))
                else:
                    expanded.append(item)
            data[key] = expanded

    resolved["data"] = data
    return resolved

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("pt_core_news_sm")
        except Exception:
            return None
    return _nlp

def fix_text_with_ai(text, custom_dict=None):
    if not text:
        return text

    nlp = get_nlp()
    
    # 1. Limpeza básica
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    # 2. Processamento com Spacy para contexto
    if nlp:
        doc = nlp(text.lower())
        tokens = []
        for i, token in enumerate(doc):
            word = token.text
            
            # Inteligência de Contexto: e vs é
            if word == "e":
                if i > 0 and i < len(doc)-1:
                    prev_t = doc[i-1]
                    next_t = doc[i+1]
                    # Se antes for substantivo/pronome e depois for adjetivo/advérbio/substantivo
                    if prev_t.pos_ in ["NOUN", "PRON"] and next_t.pos_ in ["ADJ", "ADV", "NOUN"]:
                        word = "é"
            
            tokens.append(word)
        
        # Reconstrói
        text = ""
        for i, t in enumerate(tokens):
            text += t
            if i < len(tokens) - 1:
                if tokens[i+1] not in [".", ",", "!", "?", ";", ":"]:
                    text += " "
    
    # 3. Capitalização após pontuação
    text = re.sub(r'(^|[.:!?]\s+)([a-zà-ÿ])', lambda m: m.group(1) + m.group(2).upper(), text)
    
    # 4. Dicionário Customizado (Siglas)
    if custom_dict:
        for key in sorted(custom_dict.keys(), key=len, reverse=True):
            pattern = re.compile(rf'\b{key}\b', re.IGNORECASE)
            text = pattern.sub(custom_dict[key], text)

    return text

def paste_text():
    """Simula Ctrl+V de forma cross-platform (evdev/uinput ou xdotool/wtype no Linux, PowerShell no Windows)."""
    if sys.platform.startswith("win"):
        os.system('powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait(\'^v\')"')
    else:
        try:
            import evdev, time
            ui = evdev.UInput({evdev.ecodes.EV_KEY: [evdev.ecodes.KEY_LEFTCTRL, evdev.ecodes.KEY_V]}, name="Espanso-Paster")
            ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTCTRL, 1)
            ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_V, 1)
            ui.syn()
            time.sleep(0.05)
            ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_V, 0)
            ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTCTRL, 0)
            ui.syn()
            ui.close()
        except Exception:
            os.system("wtype -M ctrl -k v -m ctrl 2>/dev/null || xdotool key ctrl+v 2>/dev/null || true")

def setup_utf8():
    """Força UTF-8 no stdout (essencial para Windows)."""
    if sys.stdout and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def get_script_dir():
    """Retorna o diretório do script atual."""
    return Path(sys.argv[0]).parent

def read_template(name):
    """Lê um template da pasta scripts/textos/celular."""
    base_dir = Path(__file__).resolve().parent.parent
    template_path = base_dir / "textos" / "celular" / f"{name}.html"
    if not template_path.exists():
        template_path = get_script_dir().parent / "textos" / "celular" / f"{name}.html"
    if not template_path.exists():
        template_path = get_script_dir() / "textos" / "celular" / f"{name}.html"
        
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return ""

def format_output(text):
    """Imprime o texto formatado para o Espanso."""
    setup_utf8()
    print(text, end="")

def _parse_edf_output(stdout_text):
    """Faz parsing da saída delimitada por ===FIELD:<campo>=== ... ===END===."""
    data = {}
    current_field = None
    field_lines = []

    for line in stdout_text.splitlines():
        if line.startswith("===FIELD:") and line.endswith("==="):
            if current_field:
                data[current_field] = "\n".join(field_lines).strip()
            current_field = line[9:-3]
            field_lines = []
        elif line == "===END===":
            if current_field:
                data[current_field] = "\n".join(field_lines).strip()
            current_field = None
        else:
            if current_field is not None:
                field_lines.append(line)

    return data


def _find_cosmic_forms_binary(config_dir):
    """Localiza o binário nativo Rust/libcosmic (sti-forms) no Linux."""
    import shutil

    candidates = [
        config_dir / "gui" / "cosmic" / "target" / "release" / "sti-forms",
        Path.home() / ".local" / "bin" / "sti-forms",
        config_dir / "gui" / "cosmic" / "target" / "debug" / "sti-forms",
    ]
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate

    which_bin = shutil.which("sti-forms")
    return Path(which_bin) if which_bin else None


def _find_windows_forms_binary(config_dir):
    """Localiza o binário nativo C# WPF-UI (sti-forms.exe) no Windows."""
    import shutil

    candidates = []
    env_bin = os.environ.get("STI_FORMS_BIN", "").strip()
    if env_bin:
        candidates.append(Path(env_bin))

    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        candidates.append(Path(local_app_data) / "Programs" / "StiForms" / "sti-forms.exe")

    candidates.extend([
        config_dir / "gui" / "windows" / "bin" / "sti-forms.exe",
        config_dir / "gui" / "windows" / "StiForms" / "bin" / "Release" / "net8.0-windows" / "win-x64" / "publish" / "sti-forms.exe",
        config_dir / "gui" / "windows" / "StiForms" / "bin" / "Release" / "net8.0-windows" / "sti-forms.exe",
    ])

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    which_bin = shutil.which("sti-forms.exe") or shutil.which("sti-forms")
    return Path(which_bin) if which_bin else None


def run_edf_form(form_name):
    """
    Executes the native GUI (sti-forms.exe on Windows / sti-forms on Linux),
    falling back to EDF.exe (Windows) or form_runner.py (Linux).
    Resolves .env placeholders and returns a dictionary of the fields.
    """
    import subprocess
    import yaml

    script_dir = get_script_dir()
    # Find the config directory (the directory containing config, match, scripts, etc.)
    config_dir = None
    curr = script_dir.resolve()
    for _ in range(3):
        if (curr / "match").exists() or (curr / "scripts").exists():
            config_dir = curr
            break
        curr = curr.parent

    if not config_dir:
        config_dir = script_dir.parent if script_dir.name == "lib" else script_dir

    form_config = config_dir / "forms" / f"{form_name}.yml"
    edf_path = r"C:\Program Files\Espanso Dynamic Forms\EDF.exe"

    if not form_config.exists():
        print(f"⚠️ Erro: Configuração de formulário não encontrada em {form_config}")
        sys.exit(1)

    try:
        raw_form_data = yaml.safe_load(form_config.read_text(encoding="utf-8"))
        resolved_form_data = resolve_form_data(raw_form_data)
    except Exception as e:
        print(f"⚠️ Erro ao ler configuração do formulário {form_name}: {e}")
        sys.exit(1)

    # Lógica de valores padrão dinâmicos (ex: hora arredondada no transporte_urbano)
    if form_name == "transporte_urbano":
        try:
            from datetime import datetime, timedelta
            now = datetime.now()
            now_plus_30 = now + timedelta(minutes=30)
            minutos = now_plus_30.minute
            if minutos == 0:
                rounded = now_plus_30.replace(second=0, microsecond=0)
            elif minutos <= 30:
                rounded = now_plus_30.replace(minute=30, second=0, microsecond=0)
            else:
                rounded = (now_plus_30 + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            resolved_form_data.setdefault("data", {})
            if not resolved_form_data["data"].get("hora_hoje"):
                resolved_form_data["data"]["hora_hoje"] = rounded.strftime("%H:%M")
        except Exception:
            pass

    # 1. No Windows, prioriza a GUI nativa C# WPF-UI (sti-forms.exe) antes do EDF.exe legado
    if sys.platform.startswith("win"):
        win_bin = _find_windows_forms_binary(config_dir)
        if win_bin is not None:
            try:
                env_proc = os.environ.copy()
                env_proc.setdefault("ESPANSO_CONFIG_DIR", str(config_dir))
                result = subprocess.run(
                    [str(win_bin), "--form-config", str(form_config)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    env=env_proc,
                )
                if result.returncode != 0:
                    sys.exit(0)
                data = _parse_edf_output(result.stdout)
                if not data:
                    sys.exit(0)
                return data
            except Exception as e:
                print(f"⚠️ Erro na GUI nativa Windows ({win_bin}): {e}", file=sys.stderr)

    # 2. Suporte multiplataforma: no Linux (ou sem EDF.exe), prioriza GUI COSMIC (sti-forms) e usa form_runner como fallback
    if not sys.platform.startswith("win") or not os.path.exists(edf_path):
        cosmic_bin = None if sys.platform.startswith("win") else _find_cosmic_forms_binary(config_dir)
        if cosmic_bin is not None:
            try:
                env_proc = os.environ.copy()
                env_proc.setdefault("ESPANSO_CONFIG_DIR", str(config_dir))
                result = subprocess.run(
                    [str(cosmic_bin), "--form-config", str(form_config)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    env=env_proc,
                )
                if result.returncode != 0:
                    sys.exit(0)
                data = _parse_edf_output(result.stdout)
                if not data:
                    sys.exit(0)
                return data
            except Exception as e:
                print(f"⚠️ Erro na GUI nativa COSMIC ({cosmic_bin}): {e}", file=sys.stderr)

        try:
            from lib.form_runner import run_gui_form
            data = run_gui_form(form_config, form_data=resolved_form_data)
            if not data:
                sys.exit(0)
            return data
        except Exception as e:
            print(f"⚠️ Erro no executor de formulários: {e}")
            sys.exit(1)

    form_config_to_run = form_config
    is_temp = False

    if resolved_form_data != raw_form_data:
        try:
            temp_file = config_dir / "forms" / f".temp_{form_name}.yml"
            temp_file.write_text(
                yaml.safe_dump(resolved_form_data, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            form_config_to_run = temp_file
            is_temp = True
        except Exception:
            form_config_to_run = form_config
            is_temp = False

    try:
        result = subprocess.run(
            [str(edf_path), "--form-config", str(form_config_to_run)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode != 0:
            # If the user cancels/closes the window, exit silently
            sys.exit(0)

        return _parse_edf_output(result.stdout)
    except Exception as e:
        print(f"⚠️ Erro ao executar formulário dinâmico: {e}")
        sys.exit(1)
    finally:
        if is_temp and form_config_to_run.exists():
            try:
                os.remove(form_config_to_run)
            except:
                pass

