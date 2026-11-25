#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronizador do Kando para Windows (Kando 3.0 menus.json & config.json).
Responsabilidades:
1. Criar backup automático com timestamp em scripts/kando/json/backup_windows/ antes de qualquer alteração.
2. Migrar comandos legados (chamar_*.ps1, arrumar.ps1, limpa_pdf.ps1, etc.) para o executável nativo sti-forms.exe --action.
3. Normalizar caminhos de usuário antigos para o repositório/usuário atual sem apagar menus personalizados.
4. Suportar restauração a partir do último backup (--restore).
"""

import argparse
import getpass
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from lib.utils import get_env_list


# Mapeamento de scripts legados -> argumentos do sti-forms.exe
LEGACY_COMMAND_ACTIONS = {
    "chamar_ola.ps1": "--action ola --paste",
    "chamar_celular.ps1": "--action celular --paste",
    "chamar_devolução_chamado.ps1": "--action devolucao_chamado --paste",
    "chamar_devolucao_chamado.ps1": "--action devolucao_chamado --paste",
    "chamar_transporte_urbano.ps1": "--action transporte_urbano --paste",
    "chamar_transporte_material.ps1": "--action transporte_material --paste",
    "chamar_transporte_viagem.ps1": "--action transporte_viagem --paste",
    "chamar_diaria.ps1": "--action diaria_viagem --paste",
    "chamar_analisador.ps1": "--action analisador",
    "chamar_manutencao.ps1": "--action manutencao",
    "chamar_removeruser.ps1": "--action removeruser",
    "arrumar.ps1": "--action ia_arrumar --paste",
    "maiuscula.ps1": "--action maiuscula --paste",
    "minuscula.ps1": "--action minuscula --paste",
    "limpa_pdf.ps1": "--action limpa_pdf --paste",
}


def quote_cmd(exe_path: str, args: str) -> str:
    return f'"{exe_path}" {args}'


def transform_command_string(cmd: str, repo_dir: str, sti_forms_exe: str, current_user: str, known_users: list[str]) -> str:
    """Atualiza um comando Kando individual para usar caminhos atuais e sti-forms.exe quando aplicável."""
    if not cmd or not isinstance(cmd, str):
        return cmd

    updated = cmd

    # 1. Atualiza caminhos de usuários antigos para o repositório atual
    for user in known_users:
        if user.lower() == current_user.lower():
            continue
        old_win = rf"C:\Users\{user}\AppData\Roaming\espanso"
        old_posix = f"C:/Users/{user}/AppData/Roaming/espanso"
        updated = updated.replace(old_win, repo_dir)
        updated = updated.replace(old_posix, repo_dir.replace("\\", "/"))

    # 2. Corrige caminho legado de helpers/scripts movidos
    updated = updated.replace(r"\scripts\kando\janelas.ps1", r"\scripts\kando\helpers\janelas.ps1")
    updated = updated.replace("/scripts/kando/janelas.ps1", "/scripts/kando/helpers/janelas.ps1")
    updated = updated.replace(r"\scripts\kando\invisivel.vbs", r"\scripts\kando\helpers\invisivel.vbs")
    updated = updated.replace("/scripts/kando/invisivel.vbs", "/scripts/kando/helpers/invisivel.vbs")

    # 3. Se já aponta para sti-forms.exe, apenas atualiza o caminho do executável mantendo os argumentos
    m_existing = re.match(r'^"?[^"]*sti-forms\.exe"?\s+(.+)$', updated, flags=re.IGNORECASE)
    if m_existing:
        return quote_cmd(sti_forms_exe, m_existing.group(1).strip())

    # 4. Converte chamadas PowerShell legadas (chamar_*.ps1, arrumar.ps1, etc.) para sti-forms.exe --action
    lowered = updated.lower()
    for script_name, action_args in LEGACY_COMMAND_ACTIONS.items():
        if script_name.lower() in lowered:
            return quote_cmd(sti_forms_exe, action_args)

    return updated


def transform_kando_node(node, repo_dir: str, sti_forms_exe: str, current_user: str, known_users: list[str]):
    """Percorre recursivamente menus, submenus e botões do Kando 3.0 (e legado) atualizando comandos."""
    if isinstance(node, list):
        for item in node:
            transform_kando_node(item, repo_dir, sti_forms_exe, current_user, known_users)
        return

    if not isinstance(node, dict):
        return

    # Kando 3.0: selectWorkflow.actions[]
    if "command" in node and isinstance(node["command"], str):
        node["command"] = transform_command_string(
            node["command"], repo_dir, sti_forms_exe, current_user, known_users
        )

    # Normaliza ícones file://C:/Users/.../espanso/icons/... para o caminho do repo atual
    if "icon" in node and isinstance(node["icon"], str) and node["icon"].startswith("file://"):
        repo_posix = repo_dir.replace("\\", "/")
        for user in known_users:
            if user.lower() == current_user.lower():
                continue
            node["icon"] = node["icon"].replace(
                f"C:/Users/{user}/AppData/Roaming/espanso",
                repo_posix,
            )

    for value in node.values():
        if isinstance(value, (dict, list)):
            transform_kando_node(value, repo_dir, sti_forms_exe, current_user, known_users)


def sync_kando_files(
    kando_dir: Path,
    backup_dir: Path,
    repo_dir: Path,
    sti_forms_exe: Path,
    current_user: str | None = None,
    known_users: list[str] | None = None,
) -> dict:
    """Executa backup e sincronização do Kando no diretório informado."""
    user = current_user or getpass.getuser()
    users = list(known_users if known_users is not None else get_env_list("STI_KNOWN_USERS"))
    if user not in users:
        users.append(user)

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    updated_files = []
    backed_up_files = []

    for filename in ("menus.json", "config.json"):
        target = kando_dir / filename
        if not target.is_file():
            continue

        # Backup timestamped em scripts/kando/json/backup_windows/ + .bak local
        bkp_stamp = backup_dir / f"{target.stem}.{timestamp}.json"
        bkp_latest = backup_dir / f"{target.stem}.latest.json"
        shutil.copy2(target, bkp_stamp)
        shutil.copy2(target, bkp_latest)
        backed_up_files.append(str(bkp_stamp))

        if filename == "menus.json":
            data = json.loads(target.read_text(encoding="utf-8"))
            transform_kando_node(data, str(repo_dir), str(sti_forms_exe), user, users)
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            updated_files.append(str(target))

    return {
        "updated": updated_files,
        "backups": backed_up_files,
    }


def restore_latest_backup(kando_dir: Path, backup_dir: Path) -> list[str]:
    """Restaura os arquivos do Kando a partir do último backup salvo."""
    restored = []
    for filename in ("menus.json", "config.json"):
        stem = Path(filename).stem
        latest = backup_dir / f"{stem}.latest.json"
        if latest.is_file():
            kando_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(latest, kando_dir / filename)
            restored.append(str(kando_dir / filename))
    return restored


def main():
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Sincroniza menus do Kando no Windows para usar sti-forms.exe.")
    parser.add_argument("--repo-dir", default=str(Path(__file__).resolve().parent.parent.parent))
    parser.add_argument(
        "--kando-dir",
        default=os.path.expandvars(r"%APPDATA%\Kando"),
    )
    parser.add_argument(
        "--sti-forms-exe",
        default=os.path.expandvars(r"%LOCALAPPDATA%\Programs\StiForms\sti-forms.exe"),
    )
    parser.add_argument("--restore", action="store_true", help="Restaura o último backup salvo do Kando.")
    args = parser.parse_args()

    repo_dir = Path(args.repo_dir).resolve()
    kando_dir = Path(args.kando_dir)
    backup_dir = repo_dir / "scripts" / "kando" / "json" / "backup_windows"

    if args.restore:
        restored = restore_latest_backup(kando_dir, backup_dir)
        if not restored:
            print("⚠️ Nenhum backup encontrado para restaurar.")
            sys.exit(1)
        for item in restored:
            print(f"♻️ Restaurado: {item}")
        return

    if not kando_dir.exists():
        print(f"ℹ️ Pasta do Kando não encontrada em {kando_dir}; pulando sincronização do Kando.")
        return

    result = sync_kando_files(
        kando_dir=kando_dir,
        backup_dir=backup_dir,
        repo_dir=repo_dir,
        sti_forms_exe=Path(args.sti_forms_exe),
    )

    for bkp in result["backups"]:
        print(f"📦 Backup Kando salvo em: {bkp}")
    for upd in result["updated"]:
        print(f"✔ Kando sincronizado: {upd}")


if __name__ == "__main__":
    main()
