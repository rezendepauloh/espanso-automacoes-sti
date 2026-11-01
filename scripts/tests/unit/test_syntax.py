# -*- coding: utf-8 -*-
"""
Testes Unitários: Validação de Sintaxe (AST/Parser) de todos os componentes.
Garante que nenhum script Python, Bash, PowerShell, arquivo YAML ou JSON possua erros de sintaxe.
"""

import glob
import json
import os
import py_compile
import shutil
import subprocess
import unittest
import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..'))
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
FORMS_DIR = os.path.join(ROOT_DIR, 'forms')
MATCH_DIR = os.path.join(ROOT_DIR, 'match')
CONFIG_DIR = os.path.join(ROOT_DIR, 'config')


class TestSyntaxValidation(unittest.TestCase):
    """Valida a integridade sintática estática de todo o ecossistema STI."""

    def test_01_all_python_scripts_compile_cleanly(self):
        """Valida compilação AST de todos os scripts Python em scripts/."""
        py_files = sorted(glob.glob(os.path.join(SCRIPTS_DIR, '**', '*.py'), recursive=True))
        self.assertGreaterEqual(len(py_files), 10, "Deveriam existir pelo menos 10 scripts Python.")

        for py_file in py_files:
            rel = os.path.relpath(py_file, ROOT_DIR)
            with self.subTest(python_script=rel):
                try:
                    py_compile.compile(py_file, doraise=True)
                except py_compile.PyCompileError as e:
                    self.fail(f"Erro de sintaxe Python em {rel}: {e}")

    def test_02_all_bash_scripts_syntax_valid(self):
        """Valida sintaxe 'bash -n' em todos os scripts Bash (.sh)."""
        bash_files = sorted(glob.glob(os.path.join(SCRIPTS_DIR, '**', '*.sh'), recursive=True))
        if not bash_files:
            self.skipTest("Nenhum script Shell (.sh) encontrado para validação.")

        for script in bash_files:
            rel = os.path.relpath(script, ROOT_DIR)
            with self.subTest(bash_script=rel):
                res = subprocess.run(
                    ['bash', '-n', script],
                    capture_output=True,
                    text=True
                )
                self.assertEqual(
                    res.returncode, 0,
                    f"Erro de sintaxe Bash em {rel}:\n{res.stderr}"
                )

    def test_03_all_yaml_files_are_valid(self):
        """Valida que todos os arquivos YAML em forms/, match/ e config/ possuem sintaxe válida."""
        yaml_files = []
        for folder in (FORMS_DIR, MATCH_DIR, CONFIG_DIR):
            if os.path.isdir(folder):
                yaml_files.extend(glob.glob(os.path.join(folder, '*.yml')))
                yaml_files.extend(glob.glob(os.path.join(folder, '*.yaml')))

        self.assertGreaterEqual(len(yaml_files), 15, "Deveriam existir pelo menos 15 arquivos YAML mapeados.")

        for yml_file in sorted(yaml_files):
            rel = os.path.relpath(yml_file, ROOT_DIR)
            with self.subTest(yaml_file=rel):
                with open(yml_file, 'r', encoding='utf-8') as f:
                    try:
                        content = yaml.safe_load(f)
                        self.assertIsNotNone(content, f"Arquivo YAML {rel} não deve estar vazio.")
                    except yaml.YAMLError as exc:
                        self.fail(f"Erro de parsing YAML em {rel}: {exc}")

    def test_04_json_dictionary_valid(self):
        """Valida se o dicionário central JSON em scripts/lib/dicionario.json é válido e populado."""
        json_path = os.path.join(SCRIPTS_DIR, 'lib', 'dicionario.json')
        self.assertTrue(os.path.isfile(json_path), "Arquivo dicionario.json não encontrado.")

        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as exc:
                self.fail(f"Erro de sintaxe JSON em dicionario.json: {exc}")

        self.assertIsInstance(data, dict, "dicionario.json deve conter um objeto JSON raiz.")
        self.assertGreaterEqual(len(data), 100, "O dicionário central deve possuir pelo menos 100 termos.")

    def test_05_powershell_scripts_ast_valid(self):
        """Valida a integridade sintática (AST) de todos os scripts PowerShell (.ps1) via pwsh."""
        pwsh_cmd = shutil.which("pwsh") or shutil.which("powershell")
        if not pwsh_cmd:
            self.skipTest("PowerShell (pwsh) não encontrado no PATH; ignorando verificação AST de PS1.")

        ps1_files = sorted(glob.glob(os.path.join(SCRIPTS_DIR, '**', '*.ps1'), recursive=True))
        self.assertGreaterEqual(len(ps1_files), 10, "Deveriam existir pelo menos 10 scripts PowerShell.")

        # Validação em lote eficiente via AST parser do PowerShell
        ps1_script = f"""
        $scripts = Get-ChildItem -Path '{SCRIPTS_DIR}' -Filter '*.ps1' -Recurse
        $errorsFound = @()
        foreach ($f in $scripts) {{
            $tokens = $null
            $errors = $null
            $ast = [System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$tokens, [ref]$errors)
            if ($errors.Count -gt 0) {{
                $errorsFound += "$($f.FullName): $($errors)"
            }}
        }}
        if ($errorsFound.Count -gt 0) {{
            $errorsFound | ForEach-Object {{ [Console]::Error.WriteLine($_) }}
            exit 1
        }}
        exit 0
        """

        res = subprocess.run(
            [pwsh_cmd, "-NoProfile", "-Command", ps1_script],
            capture_output=True,
            text=True
        )
        self.assertEqual(
            res.returncode, 0,
            f"Erro de sintaxe encontrado em scripts PowerShell:\n{res.stderr}"
        )


if __name__ == '__main__':
    unittest.main()
