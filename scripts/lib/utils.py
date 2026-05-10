# -*- coding: utf-8 -*-
import sys
import io
from pathlib import Path
import spacy
import re
import os

# Carrega o modelo de português (Lazy loading)
_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("pt_core_news_sm")
        except:
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
    """Simula Ctrl+V usando uma chamada rápida ao PowerShell (mais confiável no Windows)."""
    os.system('powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait(\'^v\')"')

def setup_utf8():
    """Força UTF-8 no stdout (essencial para Windows)."""
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def get_script_dir():
    """Retorna o diretório do script atual."""
    return Path(sys.argv[0]).parent

def read_template(name):
    """Lê um template da pasta scripts/templates."""
    template_path = get_script_dir() / "templates" / f"{name}.html"
    if not template_path.exists():
        # Tenta subir um nível se estiver em lib ou subpasta
        template_path = get_script_dir().parent / "templates" / f"{name}.html"
        
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return ""

def format_output(text):
    """Imprime o texto formatado para o Espanso."""
    setup_utf8()
    print(text, end="")

def run_edf_form(form_name):
    """
    Executes the EDF.exe with the specified form config name.
    Parses the boundary-separated output and returns a dictionary of the fields.
    """
    import subprocess
    import os
    
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
    
    if not os.path.exists(edf_path):
        print(f"⚠️ Erro: Espanso Dynamic Forms não encontrado em {edf_path}")
        sys.exit(1)
        
    if not form_config.exists():
        print(f"⚠️ Erro: Configuração de formulário não encontrada em {form_config}")
        sys.exit(1)
        
    # Lógica de valores padrão dinâmicos (ex: hora arredondada no transporte_urbano)
    custom_defaults = {}
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
            custom_defaults["hora_hoje"] = rounded.strftime("%H:%M")
        except:
            pass

    form_config_to_run = form_config
    is_temp = False

    if custom_defaults:
        try:
            content = form_config.read_text(encoding="utf-8")
            modified = False
            for key, val in custom_defaults.items():
                target_empty_single = f"  {key}: ''"
                target_empty_double = f'  {key}: ""'
                if target_empty_single in content:
                    content = content.replace(target_empty_single, f"  {key}: '{val}'")
                    modified = True
                elif target_empty_double in content:
                    content = content.replace(target_empty_double, f"  {key}: '{val}'")
                    modified = True
            
            if modified:
                temp_file = config_dir / "forms" / f".temp_{form_name}.yml"
                temp_file.write_text(content, encoding="utf-8")
                form_config_to_run = temp_file
                is_temp = True
        except:
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
            
        data = {}
        current_field = None
        field_lines = []
        
        for line in result.stdout.splitlines():
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
    except Exception as e:
        print(f"⚠️ Erro ao executar formulário dinâmico: {e}")
        sys.exit(1)
    finally:
        if is_temp and form_config_to_run.exists():
            try:
                os.remove(form_config_to_run)
            except:
                pass

