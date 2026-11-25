# -*- coding: utf-8 -*-
"""
Testes Unitários: Segurança, Carregamento de .env e Sanitização de Dados Pessoais.
Valida a resolução de variáveis ${VAR} nos esquemas YAML e garante ausência de dados pessoais hardcoded.
"""

import glob
import os
import unittest
import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..'))
FORMS_DIR = os.path.join(ROOT_DIR, 'forms')

import sys
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from lib.utils import _parse_edf_output, get_env, get_env_list, interpolate_env_str, resolve_form_data


class TestSecurityAndEnv(unittest.TestCase):
    """Testa interpolação de .env e higiene de segurança do repositório."""

    def test_01_env_example_exists_and_loads(self):
        """Garante que .env.example exista e forneça defaults seguros via get_env/get_env_list."""
        env_example = os.path.join(ROOT_DIR, '.env.example')
        self.assertTrue(os.path.isfile(env_example), ".env.example deve existir na raiz.")
        self.assertNotEqual(get_env("STI_RAMAL"), "")
        self.assertGreaterEqual(len(get_env_list("STI_LOCAIS_URBANOS")), 1)

    def test_02_resolve_form_data_expands_strings_and_arrays(self):
        """Valida que resolve_form_data expande ${VAR} para string e array conforme o schema."""
        os.environ["TEST_STI_ARRAY"] = "Item A|Item B|Item C"
        os.environ["TEST_STI_STR"] = "valor_seguro"
        try:
            sample = {
                "schema": {
                    "type": "object",
                    "properties": {
                        "lista": {"type": "array"},
                        "texto": {"type": "string"},
                    },
                },
                "data": {
                    "lista": "${TEST_STI_ARRAY}",
                    "texto": "prefixo_${TEST_STI_STR}",
                },
            }
            resolved = resolve_form_data(sample)
            self.assertEqual(resolved["data"]["lista"], ["Item A", "Item B", "Item C"])
            self.assertEqual(resolved["data"]["texto"], "prefixo_valor_seguro")
            self.assertEqual(interpolate_env_str("Ramal: ${TEST_STI_STR}"), "Ramal: valor_seguro")
        finally:
            os.environ.pop("TEST_STI_ARRAY", None)
            os.environ.pop("TEST_STI_STR", None)

    def test_03_forms_data_resolve_cleanly_without_hardcoded_personal_names(self):
        """Garante que todos os forms/*.yml resolvem listas sem nomes pessoais hardcoded."""
        for form_path in sorted(glob.glob(os.path.join(FORMS_DIR, '*.yml'))):
            with open(form_path, 'r', encoding='utf-8') as f:
                raw = yaml.safe_load(f)
            resolved = resolve_form_data(raw)
            self.assertIsInstance(resolved.get("data", {}), dict)

    def test_04_no_hardcoded_personal_usernames_in_repo(self):
        """Garante ausência de nomes de usuário pessoais e caminhos locais hardcoded no repositório."""
        forbidden_tokens = ("paulo" + "goncalves", "paulo" + "_admin")
        extensions = ("*.py", "*.ps1", "*.sh", "*.yml", "*.yaml", "*.md", "*.html")
        files_to_check = []
        for ext in extensions:
            files_to_check.extend(glob.glob(os.path.join(ROOT_DIR, '**', ext), recursive=True))

        self_path = os.path.realpath(__file__)
        for path in files_to_check:
            if os.path.realpath(path) == self_path:
                continue
            rel = os.path.relpath(path, ROOT_DIR)
            if rel.startswith(".git") or "__pycache__" in rel or rel == ".env":
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            for token in forbidden_tokens:
                self.assertNotIn(
                    token, content,
                    f"Referência pessoal '{token}' encontrada em {rel}."
                )

    def test_05_parse_edf_output_supports_multiline_fields(self):
        """Valida o parser compartilhado entre sti-forms (COSMIC) e EDF.exe."""
        raw = (
            "===FIELD:nome===\nMaria\n"
            "===FIELD:passageiros===\nPessoa 1\nPessoa 2\n"
            "===FIELD:vazio===\n"
            "===END===\n"
        )
        parsed = _parse_edf_output(raw)
        self.assertEqual(parsed["nome"], "Maria")
        self.assertEqual(parsed["passageiros"], "Pessoa 1\nPessoa 2")
        self.assertEqual(parsed["vazio"], "")


if __name__ == '__main__':
    unittest.main()
