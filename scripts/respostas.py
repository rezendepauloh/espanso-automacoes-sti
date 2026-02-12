#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import io
from pathlib import Path

# 🔴 FORÇA UTF-8 NO STDOUT (ESSENCIAL NO WINDOWS)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = Path(__file__).parent / "textos"

MAPA = {
    # "HP_BIOS": BASE / "bios" / "hp_bios.txt",
    # "LENTIDAO": BASE / "desempenho" / "lentidao.txt",
    # "PEDIR_FOTOS": BASE / "solicitacoes" / "pedir_fotos.txt",
    # "FORA_DOMINIO": BASE / "dominio" / "fora_dominio.txt",
    # "TEL_PROBLEMA": BASE / "telefonia" / "problema_telefone.txt",
    # "TEL_CABOS": BASE / "telefonia" / "teste_cabos.txt",
    # "TEL_RAMAL": BASE / "telefonia" / "troca_ramal.txt",
    "🔊 HP_BIOS": BASE / "bios" / "hp_bios.txt",
    "🐢 LENTIDAO": BASE / "desempenho" / "lentidao.txt",
    "📸 PEDIR_FOTOS": BASE / "solicitacoes" / "pedir_fotos.txt",
    "⛔ FORA_DOMINIO": BASE / "dominio" / "fora_dominio.txt",
    "📞 TEL_PROBLEMA": BASE / "telefonia" / "problema_telefone.txt",
    "🔌 TEL_CABOS": BASE / "telefonia" / "teste_cabos.txt",
    "📞 TEL_RAMAL": BASE / "telefonia" / "troca_ramal.txt",    
}

def main():
    if len(sys.argv) < 2:
        print("Tipo de atendimento não informado.")
        return

    tipo = sys.argv[1].strip().upper()
    arquivo = MAPA.get(tipo)

    if not arquivo or not arquivo.exists():
        print(f"Tipo de atendimento inválido: {tipo}")
        return

    with open(arquivo, "r", encoding="utf-8") as f:
        print(f.read())

if __name__ == "__main__":
    main()