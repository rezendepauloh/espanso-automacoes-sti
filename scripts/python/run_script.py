#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dispatcher multiplataforma (Linux / Windows) para automações em Python do Espanso.
Garante que o interpretador correto (python no Windows, python3 no Linux) seja chamado
independentemente do ambiente de execução.
"""

import sys
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    target_script = sys.argv[1]
    extra_args = sys.argv[2:]

    # Resolve caminho do script
    script_path = Path(target_script).resolve()
    if not script_path.exists():
        # Tenta resolver relativo à pasta deste dispatcher
        alt_path = (Path(__file__).parent / target_script).resolve()
        if alt_path.exists():
            script_path = alt_path

    # Usa o mesmo interpretador Python em execução
    cmd = [sys.executable, str(script_path)] + extra_args
    res = subprocess.run(cmd)
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
