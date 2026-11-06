# -*- coding: utf-8 -*-
"""
Testes Unitários: Portabilidade Multiplataforma (Linux & Windows).
Garante que caminhos de arquivos usem separadores neutros (/),
evita comandos hardcoded específicos de SO e valida interoperabilidade total.
"""

import glob
import os
import re
import sys
import unittest
import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..'))
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
MATCH_DIR = os.path.join(ROOT_DIR, 'match')
FORMS_DIR = os.path.join(ROOT_DIR, 'forms')

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


class TestCrossPlatformPortability(unittest.TestCase):
    """Valida padrões e diretrizes de código multiplataforma em todo o repositório."""

    def test_01_no_hardcoded_backslash_in_powershell_dot_sources(self):
        r"""Verifica se nenhum script PowerShell (.ps1) faz dot-sourcing usando barra invertida (\)."""
        ps1_files = glob.glob(os.path.join(SCRIPTS_DIR, '**', '*.ps1'), recursive=True)
        self.assertGreaterEqual(len(ps1_files), 10, "Devem existir scripts PowerShell para validação.")

        # Padrão: . "$Caminho\arquivo.ps1" ou . "$PSScriptRoot\..\lib\arquivo.ps1"
        forbidden_pattern = re.compile(r'^\s*\.\s+["\'].*\\.*\.ps1["\']', re.MULTILINE)

        for ps1 in ps1_files:
            rel = os.path.relpath(ps1, ROOT_DIR)
            with open(ps1, 'r', encoding='utf-8') as f:
                content = f.read()

            matches = forbidden_pattern.findall(content)
            self.assertEqual(
                len(matches), 0,
                f"Script {rel} usa barra invertida em dot-sourcing ({matches}). Use '/' ou Join-Path para portabilidade."
            )

    def test_02_kando_calls_use_portable_path_separators(self):
        """Verifica se os scripts em scripts/kando/calls/ usam separadores portáveis ao chamar chamar_gatilho.ps1."""
        calls = glob.glob(os.path.join(SCRIPTS_DIR, 'kando', 'calls', 'chamar_*.ps1'))
        for call_file in calls:
            base = os.path.basename(call_file)
            if base == "chamar_gatilho.ps1":
                continue
            with open(call_file, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertNotIn(
                r"\chamar_gatilho.ps1", content,
                f"{base} não deve conter barra invertida '\\chamar_gatilho.ps1'. Use '/'."
            )

    def test_03_espanso_matches_use_forward_slashes_in_config_paths(self):
        """Garante que todas as variáveis %CONFIG% nos arquivos match/*.yml utilizam barras normais (/)."""
        match_files = glob.glob(os.path.join(MATCH_DIR, '*.yml'))
        for match_file in match_files:
            rel = os.path.relpath(match_file, ROOT_DIR)
            with open(match_file, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertNotIn(
                r"%CONFIG%\\", content,
                f"Em {rel}, o prefixo %CONFIG% não deve usar barras invertidas. Use '%CONFIG/'."
            )
            self.assertNotIn(
                r"%CONFIG%\scripts", content,
                f"Em {rel}, caminhos com %CONFIG% não devem conter '\\'."
            )

    def test_04_no_bare_python_in_python_dispatchers(self):
        """Garante que dispatchers Python chamem sys.executable em vez de invocar 'python' hardcoded via subprocess."""
        dispatcher_py = os.path.join(SCRIPTS_DIR, 'python', 'dispatcher.py')
        if os.path.isfile(dispatcher_py):
            with open(dispatcher_py, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertNotIn(
                'subprocess.run(["python"', content,
                "dispatcher.py deve usar sys.executable em vez de ['python'] hardcoded."
            )

    def test_05_read_template_is_directory_independent(self):
        """Testa se read_template() localiza templates HTML independentemente do CWD."""
        from lib.utils import read_template
        # Testa modelo de celular
        html = read_template("celular_obs")
        self.assertNotEqual(html, "", "read_template deve carregar celular_obs.html com sucesso.")
        self.assertIn("telefones celulares", html)

    def test_06_executar_admin_safe_subprocess_flags(self):
        """Garante que executar_admin.py não use CREATE_NEW_CONSOLE diretamente sem proteção de plataforma."""
        exec_py = os.path.join(SCRIPTS_DIR, 'python', 'executar_admin.py')
        with open(exec_py, 'r', encoding='utf-8') as f:
            content = f.read()

        # Não deve haver chamada direta desprotegida a subprocess.CREATE_NEW_CONSOLE no Linux
        self.assertNotIn(
            "creationflags=subprocess.CREATE_NEW_CONSOLE)", content,
            "executar_admin.py não deve passar creationflags diretamente no Linux sem checagem de plataforma."
        )


if __name__ == '__main__':
    unittest.main()
