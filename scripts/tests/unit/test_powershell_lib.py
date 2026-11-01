# -*- coding: utf-8 -*-
"""
Testes Unitários: Biblioteca de Utilitários do PowerShell (scripts/lib/utils.ps1).
Testa Invoke-TextCorrection, Clean-PdfText e o carregamento do dicionário em PowerShell.
"""

import os
import shutil
import subprocess
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..'))
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
TESTS_DIR = os.path.join(SCRIPTS_DIR, 'tests')
PS_TEST_SCRIPT = os.path.join(TESTS_DIR, 'test_library.ps1')


class TestPowerShellLibrary(unittest.TestCase):
    """Testa a biblioteca PowerShell utils.ps1 e dicionario.ps1."""

    @classmethod
    def setUpClass(cls):
        cls.pwsh_cmd = shutil.which("pwsh") or shutil.which("powershell")

    def setUp(self):
        if not self.pwsh_cmd:
            self.skipTest("PowerShell (pwsh/powershell) não disponível no ambiente host.")

    def test_01_powershell_test_library_suite_passes(self):
        """Executa a suíte de testes unitários do PowerShell (test_library.ps1) e valida código de saída 0."""
        self.assertTrue(os.path.isfile(PS_TEST_SCRIPT), f"Script de teste {PS_TEST_SCRIPT} não encontrado.")

        res = subprocess.run(
            [self.pwsh_cmd, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS_TEST_SCRIPT],
            capture_output=True,
            text=True
        )
        self.assertEqual(
            res.returncode, 0,
            f"Falha na suíte de testes do PowerShell:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        )
        self.assertIn("SUCESSO: Todos os 11 testes PowerShell passaram!", res.stdout)


if __name__ == '__main__':
    unittest.main()
