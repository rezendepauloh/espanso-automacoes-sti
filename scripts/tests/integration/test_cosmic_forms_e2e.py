# -*- coding: utf-8 -*-
"""
Testes de Integração: Binário Nativo COSMIC (sti-forms) & Suíte Rust.
Valida todos os formulários YAML via `sti-forms --dump-resolved` e executa `cargo test`.
"""

import glob
import json
import os
import shutil
import subprocess
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..'))
FORMS_DIR = os.path.join(ROOT_DIR, 'forms')
COSMIC_DIR = os.path.join(ROOT_DIR, 'gui', 'cosmic')


class TestCosmicFormsE2E(unittest.TestCase):
    """Testes E2E headless do binário sti-forms e da suíte Cargo."""

    def test_01_sti_forms_dump_resolved_all_forms(self):
        """Executa `sti-forms --form <nome> --dump-resolved` para todos os formulários."""
        bin_path = os.path.join(COSMIC_DIR, 'target', 'release', 'sti-forms')
        if not os.path.isfile(bin_path):
            bin_path = shutil.which('sti-forms') or ''
        if not bin_path or not os.path.isfile(bin_path):
            self.skipTest("Binário sti-forms ainda não compilado.")

        form_files = sorted(glob.glob(os.path.join(FORMS_DIR, '*.yml')))
        self.assertGreaterEqual(len(form_files), 10)

        for form_file in form_files:
            form_name = os.path.splitext(os.path.basename(form_file))[0]
            with self.subTest(form=form_name):
                res = subprocess.run(
                    [bin_path, '--form', form_name, '--dump-resolved'],
                    cwd=ROOT_DIR,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                )
                self.assertEqual(res.returncode, 0, f"Falha em {form_name}: {res.stderr}")
                payload = json.loads(res.stdout)
                self.assertEqual(payload.get('form_name'), form_name)
                self.assertGreater(len(payload.get('field_order', [])), 0)

    def test_02_cargo_test_suite_passes(self):
        """Executa `cargo test --lib --tests` em gui/cosmic/."""
        cargo = shutil.which('cargo')
        if not cargo or not os.path.isfile(os.path.join(COSMIC_DIR, 'Cargo.toml')):
            self.skipTest("Cargo ou gui/cosmic/Cargo.toml indisponível.")

        res = subprocess.run(
            [cargo, 'test', '--lib', '--tests'],
            cwd=COSMIC_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
        )
        self.assertEqual(res.returncode, 0, f"cargo test falhou:\n{res.stdout}\n{res.stderr}")


if __name__ == '__main__':
    unittest.main()
