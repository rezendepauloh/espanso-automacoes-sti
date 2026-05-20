# -*- coding: utf-8 -*-
import unittest
import sys
from pathlib import Path

# Adiciona o diretório scripts (BASE_DIR) ao sys.path para importação
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


from lib.utils import fix_text_with_ai, read_template
from lib.dictionary import DICIONARIO
from python.diaria_viagem import formatar_data, formatar_cidades
from python.respostas import MAPA
from python.celular import MAPA_TEMPLATES

class TestNlpAndTemplates(unittest.TestCase):
    
    def test_dictionary_loading(self):
        """Testa se o dicionário JSON centralizado foi carregado corretamente no python."""
        self.assertIsNotNone(DICIONARIO)
        self.assertIn("mpms", DICIONARIO)
        self.assertEqual(DICIONARIO["mpms"], "MPMS")
        self.assertEqual(DICIONARIO["sti"], "STI")
        self.assertEqual(DICIONARIO["sajmp"], "SAJMP")

    def test_text_correction_ai(self):
        """Testa a função de correção de texto usando o dicionário centralizado."""
        # Teste 1: Correção de siglas e termos institucionais
        original_1 = "ola, tudo bem? aqui e o paulo do mpms. vc pode ver o problema no pc com windows? tbm preciso do pdf do sajmp"
        # Com o dicionário centralizado, o Spacy analisa o contexto
        corrected_1 = fix_text_with_ai(original_1, DICIONARIO)
        
        self.assertIn("MPMS", corrected_1)
        self.assertIn("Windows", corrected_1)
        self.assertIn("SAJMP", corrected_1)
        self.assertIn("também", corrected_1)
        self.assertIn("você", corrected_1)

    def test_formatar_data(self):
        """Testa a lógica de formatação de data e retorno de dia da semana."""
        # Formato ISO enviado pelo EDF
        data_iso = "2026-05-11"
        data_fmt, dia_semana = formatar_data(data_iso)
        self.assertEqual(data_fmt, "11/05/2026")
        self.assertEqual(dia_semana, "segunda-feira")

        # Formato brasileiro de fallback
        data_br = "15/05/2026"
        data_fmt_br, dia_semana_br = formatar_data(data_br)
        self.assertEqual(data_fmt_br, "15/05/2026")
        self.assertEqual(dia_semana_br, "sexta-feira")

    def test_formatar_cidades(self):
        """Testa a pluralização e junção de cidades para os destinos de viagem."""
        # Caso 0 cidades
        self.assertEqual(formatar_cidades(""), "na comarca de <strong>Não Informado</strong>")
        
        # Caso 1 cidade
        self.assertEqual(formatar_cidades("Campo Grande"), "na comarca de <strong>Campo Grande</strong>")
        
        # Caso 2 cidades
        self.assertEqual(formatar_cidades("Dourados\nTrês Lagoas"), "nas comarcas de <strong>Dourados e Três Lagoas</strong>")
        
        # Caso 3 cidades ou mais
        self.assertEqual(formatar_cidades("Bonito\nCorumbá\nCoxim"), "nas comarcas de <strong>Bonito, Corumbá e Coxim</strong>")

    def test_respostas_templates_exist(self):
        """Testa se todos os arquivos HTML mapeados em respostas.py realmente existem fisicamente."""
        self.assertGreater(len(MAPA), 0)
        for tipo, caminho in MAPA.items():
            self.assertTrue(
                caminho.exists(), 
                f"Erro: O arquivo HTML para '{tipo}' não existe em: {caminho}"
            )

    def test_celular_templates_exist(self):
        """Testa se todos os templates de celular mapeados são localizados e carregados corretamente."""
        self.assertGreater(len(MAPA_TEMPLATES), 0)
        for modelo, template_name in MAPA_TEMPLATES.items():
            conteudo = read_template(template_name)
            self.assertIsNotNone(conteudo, f"Template '{template_name}' não deveria retornar None.")
            self.assertNotEqual(conteudo, "", f"Erro: O arquivo HTML para celular '{template_name}' (modelo: '{modelo}') está vazio ou não foi encontrado.")

    def test_admin_forms_exist(self):
        """Testa se os novos formulários administrativos criados para o EDF existem no disco e são válidos."""
        forms_dir = BASE_DIR.parent / "forms"
        novos_formularios = ["analisador.yml", "manutencao.yml", "remove_profiles.yml"]

        
        for form in novos_formularios:
            caminho_form = forms_dir / form
            self.assertTrue(caminho_form.exists(), f"Erro: O arquivo de formulário administrativo '{form}' não foi encontrado em: {caminho_form}")
            
            # Valida se é um arquivo YAML legível
            try:
                import yaml
                with open(caminho_form, "r", encoding="utf-8") as f:
                    dados = yaml.safe_load(f)
                    self.assertIn("schema", dados, f"Formulário '{form}' deve conter a chave 'schema'")
                    self.assertIn("template", dados, f"Formulário '{form}' deve conter a chave 'template'")
            except ImportError:
                # Fallback se yaml não estiver disponível
                conteudo = caminho_form.read_text(encoding="utf-8")
                self.assertIn("schema:", conteudo, f"Formulário '{form}' deve conter 'schema:'")
                self.assertIn("template:", conteudo, f"Formulário '{form}' deve conter 'template:'")

if __name__ == "__main__":
    unittest.main()

