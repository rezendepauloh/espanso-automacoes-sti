# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import subprocess
import io

# 🔴 FORÇA UTF-8 NO STDOUT (ESSENCIAL NO WINDOWS)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = Path(__file__).parent

def main():
    tipo = sys.argv[1].strip().upper()
    chamado = sys.argv[2]

    equipamento = sys.argv[3]
    tipo_material = sys.argv[4]
    defeito = sys.argv[5]
    patrimonio = sys.argv[6]

    # ===============================
    # ATENDIMENTOS NORMAIS
    # ===============================
    if tipo != "📦 MATERIAL":
        equipamento = ""
        tipo_material = ""
        defeito = ""
        patrimonio = ""
                
        script = BASE / "respostas.py"
        subprocess.run(
            ["python", script, tipo],
            text=True
        )
        return

    # ===============================
    # MATERIAL
    # ===============================
    script = BASE / "material.py"
    subprocess.run(
        [
            "python",
            script,
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