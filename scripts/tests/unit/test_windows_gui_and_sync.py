# -*- coding: utf-8 -*-
"""
Testes Unitários: GUI Nativa Windows (.NET 8 / WPF-UI), sync.ps1 e Sincronizador Kando.
Valida integridade estrutural, descoberta de binário sem afetar o Linux e
transformação segura (backup + migração) de arquivos menus.json do Kando 3.0.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT_DIR = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = ROOT_DIR / "scripts"
GUI_WIN_DIR = ROOT_DIR / "gui" / "windows"

for p in (str(SCRIPTS_DIR), str(SCRIPTS_DIR / "kando")):
    if p not in sys.path:
        sys.path.insert(0, p)

from lib import utils
import sync_kando_windows


class TestWindowsGuiAndSync(unittest.TestCase):
    """Valida os artefatos da GUI Windows C# e a sincronização do Kando."""

    def test_01_windows_solution_and_projects_exist(self):
        """Verifica que StiForms.sln, StiForms.csproj e StiForms.Tests.csproj existem e usam .NET 8 + WPF-UI."""
        sln = GUI_WIN_DIR / "StiForms.sln"
        app_csproj = GUI_WIN_DIR / "StiForms" / "StiForms.csproj"
        tests_csproj = GUI_WIN_DIR / "StiForms.Tests" / "StiForms.Tests.csproj"

        self.assertTrue(sln.is_file(), "StiForms.sln deve existir em gui/windows/.")
        self.assertTrue(app_csproj.is_file(), "StiForms.csproj deve existir.")
        self.assertTrue(tests_csproj.is_file(), "StiForms.Tests.csproj deve existir.")

        csproj_txt = app_csproj.read_text(encoding="utf-8")
        self.assertIn("<TargetFramework>net8.0-windows</TargetFramework>", csproj_txt)
        self.assertIn("<OutputType>WinExe</OutputType>", csproj_txt)
        self.assertIn("<AssemblyName>sti-forms</AssemblyName>", csproj_txt)
        self.assertIn("WPF-UI", csproj_txt)
        self.assertIn("YamlDotNet", csproj_txt)

    def test_02_sync_ps1_exists_and_valid_syntax(self):
        """Valida existência e sintaxe AST de sync.ps1 na raiz do repositório."""
        sync_ps1 = ROOT_DIR / "sync.ps1"
        self.assertTrue(sync_ps1.is_file(), "sync.ps1 deve existir na raiz do repositório.")

        content = sync_ps1.read_text(encoding="utf-8")
        self.assertIn("dotnet publish", content)
        self.assertIn("sync_kando_windows.py", content)

        pwsh_cmd = shutil.which("pwsh") or shutil.which("powershell")
        if pwsh_cmd:
            cmd = (
                f"$t=$null;$e=$null;"
                f"[void][System.Management.Automation.Language.Parser]::ParseFile('{sync_ps1}',[ref]$t,[ref]$e);"
                f"if($e.Count -gt 0){{exit 1}}"
            )
            res = subprocess.run([pwsh_cmd, "-NoProfile", "-Command", cmd], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Erro de sintaxe em sync.ps1: {res.stderr}")

    def test_03_find_windows_forms_binary_prioritizes_env_and_local_install(self):
        """Testa descoberta determinística de sti-forms.exe via STI_FORMS_BIN."""
        with tempfile.TemporaryDirectory() as tmp:
            fake_exe = Path(tmp) / "sti-forms.exe"
            fake_exe.write_text("", encoding="utf-8")

            with mock.patch.dict(os.environ, {"STI_FORMS_BIN": str(fake_exe)}):
                found = utils._find_windows_forms_binary(ROOT_DIR)
                self.assertEqual(found, fake_exe)

    def test_04_kando_windows_sync_migrates_commands_and_creates_backup(self):
        """Valida migração de menus.json (Kando 3.0) para sti-forms.exe --action sem destruir outros menus."""
        sample_menus = {
            "version": "3.0.0",
            "menus": [
                {
                    "root": {
                        "type": "root",
                        "name": "Menu Teste",
                        "children": [
                            {
                                "type": "button",
                                "name": "Atendimento STI",
                                "icon": "file://C:/Users/usuario_antigo/AppData/Roaming/espanso/icons/stash-headset.png",
                                "selectWorkflow": {
                                    "actions": [
                                        {
                                            "type": "execute-command",
                                            "command": 'pwsh.exe -WindowStyle Hidden -NoProfile -File "C:\\Users\\usuario_antigo\\AppData\\Roaming\\espanso\\scripts\\kando\\calls\\chamar_ola.ps1"',
                                            "detached": True,
                                        }
                                    ]
                                },
                            },
                            {
                                "type": "button",
                                "name": "Arrumar",
                                "selectWorkflow": {
                                    "actions": [
                                        {
                                            "type": "execute-command",
                                            "command": 'pwsh.exe -WindowStyle Hidden -NoProfile -File "C:\\Users\\usuario_antigo\\AppData\\Roaming\\espanso\\scripts\\powershell\\arrumar.ps1" -Origem Kando',
                                            "detached": True,
                                        }
                                    ]
                                },
                            },
                            {
                                "type": "button",
                                "name": "Maximizar",
                                "selectWorkflow": {
                                    "actions": [
                                        {
                                            "type": "execute-command",
                                            "command": 'powershell.exe -WindowStyle Hidden -NoProfile -File "C:\\Users\\usuario_antigo\\AppData\\Roaming\\espanso\\scripts\\kando\\janelas.ps1" -Acao Maximizar',
                                            "detached": True,
                                        }
                                    ]
                                },
                            },
                            {
                                "type": "button",
                                "name": "Google",
                                "selectWorkflow": {
                                    "actions": [{"type": "open-uri", "uri": "https://www.google.com"}]
                                },
                            },
                        ],
                    }
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            kando_dir = tmp_path / "kando"
            backup_dir = tmp_path / "backups"
            repo_dir = tmp_path / "repo"
            exe_path = tmp_path / "Programs" / "StiForms" / "sti-forms.exe"
            kando_dir.mkdir(parents=True)

            menus_file = kando_dir / "menus.json"
            menus_file.write_text(json.dumps(sample_menus, ensure_ascii=False, indent=2), encoding="utf-8")

            res = sync_kando_windows.sync_kando_files(
                kando_dir=kando_dir,
                backup_dir=backup_dir,
                repo_dir=repo_dir,
                sti_forms_exe=exe_path,
                current_user="usuario_novo",
                known_users=["usuario_antigo"],
            )

            self.assertEqual(len(res["backups"]), 1)
            self.assertTrue((backup_dir / "menus.latest.json").is_file())

            updated = json.loads(menus_file.read_text(encoding="utf-8"))
            children = updated["menus"][0]["root"]["children"]

            # 1. Atendimento STI deve chamar sti-forms.exe --action ola --paste
            ola_cmd = children[0]["selectWorkflow"]["actions"][0]["command"]
            self.assertEqual(ola_cmd, f'"{exe_path}" --action ola --paste')
            self.assertIn(repo_dir.as_posix(), children[0]["icon"])

            # 2. Arrumar deve chamar sti-forms.exe --action ia_arrumar --paste
            arrumar_cmd = children[1]["selectWorkflow"]["actions"][0]["command"]
            self.assertEqual(arrumar_cmd, f'"{exe_path}" --action ia_arrumar --paste')

            # 3. Maximizar deve ter usuário atualizado e helpers/janelas.ps1 corrigido
            max_cmd = children[2]["selectWorkflow"]["actions"][0]["command"]
            self.assertIn(str(repo_dir), max_cmd)
            self.assertIn(r"\scripts\kando\helpers\janelas.ps1", max_cmd)

            # 4. Atalhos não relacionados permanecem intactos
            self.assertEqual(children[3]["selectWorkflow"]["actions"][0]["uri"], "https://www.google.com")

            # 5. Restauração devolve exatamente o JSON original
            restored = sync_kando_windows.restore_latest_backup(kando_dir, backup_dir)
            self.assertEqual(len(restored), 1)
            restored_json = json.loads(menus_file.read_text(encoding="utf-8"))
            self.assertEqual(restored_json, sample_menus)


if __name__ == "__main__":
    unittest.main()
