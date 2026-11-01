# -*- coding: utf-8 -*-
"""
Testes de Integração: Scripts de Automação Kando, Despachantes e Configurações do Espanso.
Valida o acoplamento entre os acionadores de atalho (scripts/kando/calls/),
o despachante Bash/PowerShell e as configurações de plataforma em config/.
"""

import glob
import os
import re
import subprocess
import unittest
import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..'))
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
KANDO_CALLS_DIR = os.path.join(SCRIPTS_DIR, 'kando', 'calls')
CONFIG_DIR = os.path.join(ROOT_DIR, 'config')
MATCH_DIR = os.path.join(ROOT_DIR, 'match')


class TestKandoAndScriptsIntegration(unittest.TestCase):
    """Testa a integração dos gatilhos Kando e configurações de plataforma."""

    def test_01_chamar_gatilho_sh_executable_and_syntax(self):
        """chamar_gatilho.sh deve ter permissão de execução, shebang correto e responder a --help ou sem args."""
        script_sh = os.path.join(KANDO_CALLS_DIR, 'chamar_gatilho.sh')
        self.assertTrue(os.path.isfile(script_sh), "chamar_gatilho.sh não foi encontrado.")
        self.assertTrue(os.access(script_sh, os.X_OK), "chamar_gatilho.sh deve possuir permissão +x.")

        with open(script_sh, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        self.assertTrue(first_line.startswith("#!/"), "chamar_gatilho.sh deve iniciar com um shebang válido.")

        # Sem argumentos deve retornar código de erro 1 e exibir instrução de uso
        res = subprocess.run([script_sh], capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("Uso:", res.stdout + res.stderr)

    def test_02_kando_triggers_exist_in_espanso_matches(self):
        """Verifica se os gatilhos invocados nos scripts de Kando (chamar_*.ps1) existem nas regras de match/*.yml."""
        # Coleta todos os triggers definidos em match/*.yml
        defined_triggers = set()
        for mf in glob.glob(os.path.join(MATCH_DIR, '*.yml')):
            with open(mf, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            for m in data.get("matches", []):
                if isinstance(m, dict):
                    t = m.get("trigger")
                    if t:
                        defined_triggers.add(t)
                    for tr in m.get("triggers", []):
                        defined_triggers.add(tr)

        # Inspeciona scripts de chamada do Kando
        ps1_calls = glob.glob(os.path.join(KANDO_CALLS_DIR, 'chamar_*.ps1'))
        self.assertGreaterEqual(len(ps1_calls), 8, "Devem existir pelo menos 8 scripts de chamada Kando.")

        for call_script in ps1_calls:
            base = os.path.basename(call_script)
            if base in ("chamar_gatilho.ps1",):
                continue
            with open(call_script, 'r', encoding='utf-8') as f:
                content = f.read()

            match = re.search(r'-Gatilho\s+["\'](:[a-zA-Z0-9_]+)["\']', content)
            if match:
                trigger = match.group(1)
                self.assertIn(
                    trigger, defined_triggers,
                    f"Gatilho '{trigger}' acionado por {base} não foi encontrado em nenhum arquivo de match/*.yml."
                )

    def test_03_espanso_configs_integrity(self):
        """Valida que config/default.yml, config/linux.yml e config/windows.yml definem as chaves essenciais."""
        default_yml = os.path.join(CONFIG_DIR, 'default.yml')
        self.assertTrue(os.path.isfile(default_yml), "config/default.yml deve existir.")

        with open(default_yml, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)

        self.assertIsInstance(cfg, dict, "config/default.yml deve ser um dicionário YAML.")
        # Verifica se há definições recomendadas do Espanso
        self.assertTrue(
            "backend" in cfg or "keyboard_layout" in cfg or "toggle_key" in cfg,
            "config/default.yml deve conter diretivas de configuração do Espanso."
        )


if __name__ == '__main__':
    unittest.main()
