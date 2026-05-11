# -*- coding: utf-8 -*-
import json
from pathlib import Path

# Carregamento dinâmico do dicionário unificado JSON
_DIC_PATH = Path(__file__).parent / "dicionario.json"

try:
    with open(_DIC_PATH, "r", encoding="utf-8") as f:
        DICIONARIO = json.load(f)
except Exception as e:
    import sys
    print(f"⚠️ Erro crítico ao carregar o dicionário JSON: {e}", file=sys.stderr)
    DICIONARIO = {}
