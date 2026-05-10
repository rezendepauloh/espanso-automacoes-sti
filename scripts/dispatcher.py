# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import subprocess
from lib import utils

# Garante UTF-8
utils.setup_utf8()

BASE = Path(__file__).parent

def main():
    if len(sys.argv) < 2:
        from lib.utils import run_edf_form
        data = run_edf_form("ola")
        nome = data.get("nome", "")
        chamado = data.get("chamado", "")
        tipo = data.get("tipo", "").strip()
        equipamento = data.get("equipamento", "")
        tipo_material = data.get("tipo_material", "")
        defeito = data.get("defeito", "")
        patrimonio = data.get("patrimonio", "")
        
        # Imprime o cabeçalho do chamado (antes no match/ola.yml)
        print(f"Boa tarde, <strong>{nome}</strong>, tudo bem? Aqui é da <strong>manutenção da STI</strong>.<br /><br />"
              f"Estou entrando em contato em relação ao seu chamado: <strong>{chamado}</strong><br /><br />", end="", flush=True)
        sys.stdout.flush()
    else:
        if len(sys.argv) < 7:
            print("⚠️ Erro: Argumentos insuficientes no dispatcher.")
            sys.exit(1)
        tipo = sys.argv[1].strip()
        chamado = sys.argv[2]
        equipamento = sys.argv[3]
        tipo_material = sys.argv[4]
        defeito = sys.argv[5]
        patrimonio = sys.argv[6]

    # ===============================
    # ATENDIMENTOS NORMAIS
    # ===============================
    if tipo != "📦 Material":
        script = BASE / "respostas.py"
        subprocess.run(["python", str(script), tipo], text=True)
        return

    # ===============================
    # MATERIAL
    # ===============================
    script = BASE / "material.py"
    subprocess.run(
        [
            "python",
            str(script),
            equipamento,
            tipo_material,
            defeito,
            patrimonio,
            chamado,
        ],
        text=True
    )

if __name__ == "__main__":
    main()