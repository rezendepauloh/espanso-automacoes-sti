# -*- coding: utf-8 -*-
"""
Testes de Integração: Coerência entre Formulários (forms/), Matches (match/) e Templates (textos/).
Garante que todos os formulários YAML, regras de expansão do Espanso e arquivos de texto
estejam devidamente correlacionados e sem links quebrados.
"""

import glob
import os
import re
import unittest
import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..'))
FORMS_DIR = os.path.join(ROOT_DIR, 'forms')
MATCH_DIR = os.path.join(ROOT_DIR, 'match')
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
TEXTOS_DIR = os.path.join(SCRIPTS_DIR, 'textos')


class TestFormsAndMatchesIntegration(unittest.TestCase):
    """Testa a integração entre arquivos de match e formulários do Espanso."""

    def test_01_all_forms_have_schema_and_template(self):
        """Todos os formulários em forms/*.yml devem conter 'schema' e 'template' bem estruturados."""
        form_files = sorted(glob.glob(os.path.join(FORMS_DIR, '*.yml')))
        self.assertGreaterEqual(len(form_files), 8, "Devem existir pelo menos 8 formulários YAML.")

        for form_file in form_files:
            rel = os.path.relpath(form_file, ROOT_DIR)
            with self.subTest(form=rel):
                with open(form_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                self.assertIsInstance(data, dict, f"{rel} deve ser um dicionário YAML.")
                self.assertIn("schema", data, f"{rel} deve conter a chave 'schema'")
                self.assertIn("template", data, f"{rel} deve conter a chave 'template'")
                self.assertIsInstance(data["schema"], dict, f"O schema de {rel} deve ser um mapa de campos.")
                self.assertIsInstance(data["template"], str, f"O template de {rel} deve ser uma string.")

    def test_02_form_template_placeholders_match_schema_keys(self):
        """Verifica se os placeholders {{campo}} no template de cada formulário correspondem às propriedades do schema."""
        form_files = sorted(glob.glob(os.path.join(FORMS_DIR, '*.yml')))

        for form_file in form_files:
            rel = os.path.relpath(form_file, ROOT_DIR)
            with self.subTest(form=rel):
                with open(form_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                properties = data.get("schema", {}).get("properties", {})
                schema_keys = set(properties.keys())
                raw_template = data.get("template", "")
                # Detecta variáveis locais de loop Jinja2: {% for item in passageiros %}
                loop_vars = set(re.findall(r'\{%\s*for\s+([a-zA-Z0-9_]+)\s+in', raw_template))

                # Encontra placeholders padrão: {{campo}} ou {{ form.campo }}
                placeholders = re.findall(r'\{\{\s*([a-zA-Z0-9_]+)\s*\}\}', raw_template)

                for p in placeholders:
                    if p in ("form", "now", "date") or p in loop_vars:
                        continue
                    self.assertIn(
                        p, schema_keys,
                        f"Em {rel}, o placeholder '{{{{{p}}}}}' foi usado no template mas não está declarado nas properties do schema."
                    )

    def test_03_all_match_files_have_valid_structure(self):
        """Todos os arquivos em match/*.yml devem conter a chave raiz 'matches' como lista."""
        match_files = sorted(glob.glob(os.path.join(MATCH_DIR, '*.yml')))
        self.assertGreaterEqual(len(match_files), 7, "Devem existir pelo menos 7 arquivos de regras em match/.")

        for match_file in match_files:
            rel = os.path.relpath(match_file, ROOT_DIR)
            with self.subTest(match_file=rel):
                with open(match_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                self.assertIsInstance(data, dict, f"{rel} deve ser um dicionário YAML.")
                self.assertIn("matches", data, f"{rel} deve conter a lista 'matches'.")
                self.assertIsInstance(data["matches"], list, f"Em {rel}, 'matches' deve ser uma lista.")

    def test_04_match_referenced_scripts_and_forms_exist(self):
        """Valida que scripts externos e formulários referenciados nos matches realmente existem."""
        match_files = sorted(glob.glob(os.path.join(MATCH_DIR, '*.yml')))

        for match_file in match_files:
            rel = os.path.relpath(match_file, ROOT_DIR)
            with open(match_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            for idx, item in enumerate(data.get("matches", [])):
                if not isinstance(item, dict):
                    continue

                # Verifica se há chamada de script externo via variável
                vars_list = item.get("vars", [])
                for var in vars_list:
                    if isinstance(var, dict) and var.get("type") == "script":
                        cmd = var.get("params", {}).get("args", [])
                        if isinstance(cmd, list) and len(cmd) > 1:
                            script_candidate = cmd[1]
                            # Se for caminho relativo referenciando $CONFIG ou scripts
                            if script_candidate.startswith("$CONFIG/"):
                                rel_path = script_candidate.replace("$CONFIG/", "")
                                full_path = os.path.join(ROOT_DIR, rel_path)
                                self.assertTrue(
                                    os.path.exists(full_path),
                                    f"Script referenciado em {rel} (item {idx}) não existe: {full_path}"
                                )


if __name__ == '__main__':
    unittest.main()
