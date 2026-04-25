# -*- coding: utf-8 -*-
import sys
import io
from pathlib import Path
import spacy
import re

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
