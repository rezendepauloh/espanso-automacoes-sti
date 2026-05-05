#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import io
from pathlib import Path

# 🔴 FORÇA UTF-8 NO STDOUT (ESSENCIAL NO WINDOWS)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = Path(__file__).parent / "textos"

MAPA = {
    "🔊 HP - BIOS":                                          BASE / "bios" / "hp_bios.html",
    "🐢 Lentidão":                                           BASE / "desempenho" / "lentidao.html",
    "📸 Pedir fotos do equipamento":                         BASE / "solicitacoes" / "pedir_fotos.html",
    "⛔ Equipamento fora do domínio":                        BASE / "dominio" / "fora_dominio.html",
    "📞 Telefone com problema":                              BASE / "telefonia" / "problema_telefone.html",
    "📞 Ligar e desligar telefone":                          BASE / "telefonia" / "desconectar_e_conectar_telefone.html",
    "📞 Troca do nome do ramal":                             BASE / "telefonia" / "troca_ramal.html",
    "📞 Instalar o telefone pela primeira vez":              BASE / "telefonia" / "instalar_telefone.html", 
    "📞 Liberação de telefone para ligar para celular":      BASE / "telefonia" / "liberacao_celular.html",  
    "📞 Ensinando a fazer ligações externas e interurbanos": BASE / "telefonia" / "telefones_externos_e_interurbanos.html",
    "🔌 Verificar cabos do telefone":                        BASE / "telefonia" / "teste_cabos.html",
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