#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import io
from pathlib import Path

# 🔴 FORÇA UTF-8 NO STDOUT (ESSENCIAL NO WINDOWS)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = Path(__file__).parent / "textos"

MAPA = {
    "🔊 HP - BIOS":                    BASE / "bios" / "hp_bios.txt",
    "🐢 Lentidão":                     BASE / "desempenho" / "lentidao.txt",
    "📸 Pedir fotos do equipamento":   BASE / "solicitacoes" / "pedir_fotos.txt",
    "⛔ Equipamento fora do domínio":  BASE / "dominio" / "fora_dominio.txt",
    "📞 Telefone com problema":        BASE / "telefonia" / "problema_telefone.txt",
    "📞 Ligar e desligar telefone":    BASE / "telefonia" / "desconectar_e_conectar_telefone.txt",
    "📞 Troca do nome do ramal":       BASE / "telefonia" / "troca_ramal.txt",
    "📞 Instalar o telefone":          BASE / "telefonia" / "instalar_telefone.txt",     
    "🔌 Verificar cabos do telefone":  BASE / "telefonia" / "teste_cabos.txt",
}

def main():
    if len(sys.argv) < 2:
        print("Tipo de atendimento não informado.")
        return

    tipo = sys.argv[1].strip()
    arquivo = MAPA.get(tipo)

    if not arquivo or not arquivo.exists():
        print(f"Tipo de atendimento inválido: {tipo}")
        return

    with open(arquivo, "r", encoding="utf-8") as f:
        print(f.read())

if __name__ == "__main__":
    main()