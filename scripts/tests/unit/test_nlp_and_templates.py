# -*- coding: utf-8 -*-
"""
Testes Unitários: NLP, Dicionário Centralizado e Manipulação de Templates.
Valida o mecanismo de correção textual por IA (NLP/Spacy), carregamento do dicionário,
formatação de dados temporais e geográficos para despachos e integridade dos arquivos HTML.
"""

import os
import sys
import unittest
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..'))
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
FORMS_DIR = os.path.join(ROOT_DIR, 'forms')

for d in (ROOT_DIR, SCRIPTS_DIR, os.path.join(SCRIPTS_DIR, 'lib'), os.path.join(SCRIPTS_DIR, 'python')):
    if d not in sys.path:
        sys.path.insert(0, d)

from lib.utils import fix_text_with_ai, read_template
from lib.dictionary import DICIONARIO
from python.diaria_viagem import formatar_data, formatar_cidades
from python.respostas import MAPA
from python.celular import MAPA_TEMPLATES


class TestNlpAndTemplates(unittest.TestCase):
    """Testa algoritmos de NLP, parsing de dicionário e templates HTML."""

    def test_01_dictionary_loading(self):
        """Testa se o dicionário JSON centralizado foi carregado corretamente no Python."""
        self.assertIsNotNone(DICIONARIO)
        self.assertIn("mpms", DICIONARIO)
        self.assertEqual(DICIONARIO["mpms"], "MPMS")
        self.assertEqual(DICIONARIO["sti"], "STI")
        self.assertEqual(DICIONARIO["sajmp"], "SAJMP")

    def test_02_text_correction_ai(self):
        """Testa a função de correção de texto usando o dicionário centralizado."""
        original = "ola, tudo bem? aqui e o paulo do mpms. vc pode ver o problema no pc com windows? tbm preciso do pdf do sajmp"
        corrected = fix_text_with_ai(original, DICIONARIO)

        self.assertIn("MPMS", corrected)
        self.assertIn("Windows", corrected)
        self.assertIn("SAJMP", corrected)
        self.assertIn("também", corrected)
        self.assertIn("você", corrected)

    def test_03_formatar_data(self):
        """Testa a lógica de formatação de data e retorno de dia da semana."""
        # Formato ISO
        data_iso = "2026-05-11"
        data_fmt, dia_semana = formatar_data(data_iso)
        self.assertEqual(data_fmt, "11/05/2026")
        self.assertEqual(dia_semana, "segunda-feira")

        # Formato brasileiro de fallback
        data_br = "15/05/2026"
        data_fmt_br, dia_semana_br = formatar_data(data_br)
        self.assertEqual(data_fmt_br, "15/05/2026")
        self.assertEqual(dia_semana_br, "sexta-feira")

    def test_04_formatar_cidades(self):
        """Testa a pluralização e junção de cidades para os destinos de viagem."""
        # 0 cidades
        self.assertEqual(formatar_cidades(""), "na comarca de <strong>Não Informado</strong>")

        # 1 cidade
        self.assertEqual(formatar_cidades("Campo Grande"), "na comarca de <strong>Campo Grande</strong>")

        # 2 cidades
        self.assertEqual(formatar_cidades("Dourados\nTrês Lagoas"), "nas comarcas de <strong>Dourados e Três Lagoas</strong>")

        # 3 cidades ou mais
        self.assertEqual(formatar_cidades("Bonito\nCorumbá\nCoxim"), "nas comarcas de <strong>Bonito, Corumbá e Coxim</strong>")

    def test_05_respostas_templates_exist(self):
        """Testa se todos os arquivos HTML mapeados em respostas.py realmente existem fisicamente."""
        self.assertGreater(len(MAPA), 0)
        for tipo, caminho in MAPA.items():
            self.assertTrue(
                caminho.exists(),
                f"Erro: O arquivo HTML para '{tipo}' não existe em: {caminho}"
            )

    def test_06_celular_templates_exist(self):
        """Testa se todos os templates de celular mapeados são localizados e carregados corretamente."""
        self.assertGreater(len(MAPA_TEMPLATES), 0)
        for modelo, template_name in MAPA_TEMPLATES.items():
            conteudo = read_template(template_name)
            self.assertIsNotNone(conteudo, f"Template '{template_name}' não deveria retornar None.")
            self.assertNotEqual(conteudo, "", f"Erro: O arquivo HTML para celular '{template_name}' (modelo: '{modelo}') está vazio ou não foi encontrado.")

    def test_07_admin_forms_exist(self):
        """Testa se os novos formulários administrativos criados para o EDF existem no disco e são válidos."""
        novos_formularios = ["analisador.yml", "manutencao.yml", "remove_profiles.yml"]

        for form in novos_formularios:
            caminho_form = Path(FORMS_DIR) / form
            self.assertTrue(caminho_form.exists(), f"Erro: O arquivo de formulário administrativo '{form}' não foi encontrado em: {caminho_form}")

            conteudo = caminho_form.read_text(encoding="utf-8")
            self.assertIn("schema:", conteudo, f"Formulário '{form}' deve conter 'schema:'")
            self.assertIn("template:", conteudo, f"Formulário '{form}' deve conter 'template:'")


if __name__ == "__main__":
    unittest.main()
