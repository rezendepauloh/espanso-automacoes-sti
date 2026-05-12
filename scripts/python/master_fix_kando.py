# -*- coding: utf-8 -*-
"""
Script Utilitário Inteligente de Manutenção do Kando
Autodetecta o usuário atual (paulogoncalves, paulo_admin, User) e:
1. Ajusta caminhos absolutos do Windows para o usuário logado no momento.
2. Atualiza referências dos scripts reorganizados (invisivel.vbs, limpa_pdf.ps1, etc.).
3. Corrige e remove menus duplicados.
"""

import sys
import os
import json
import getpass
from pathlib import Path

# Garante UTF-8 no stdout/stderr no Windows
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def fix_json_content(data, target_user, other_users):
    """
    Realiza todas as substituições e melhorias necessárias no conteúdo do JSON do Kando.
    """
    json_str = json.dumps(data, ensure_ascii=False)
    
    # 1. Corrige caminhos de usuários antigos para o usuário alvo
    for user in other_users:
        if user.lower() == target_user.lower():
            continue
        json_str = json_str.replace(f"C:\\\\Users\\\\{user}", f"C:\\\\Users\\\\{target_user}")
        json_str = json_str.replace(f"C:/Users/{user}", f"C:/Users/{target_user}")
        # Substitui também com barras invertidas normais caso ocorra
        json_str = json_str.replace(f"C:\\Users\\{user}", f"C:\\Users\\{target_user}")

    # 2. Corrige os novos caminhos físicos reorganizados
    # invisivel.vbs -> helpers/invisivel.vbs
    json_str = json_str.replace(r"\\scripts\\kando\\invisivel.vbs", r"\\scripts\\kando\\helpers\\invisivel.vbs")
    json_str = json_str.replace(r"/scripts/kando/invisivel.vbs", r"/scripts/kando/helpers/invisivel.vbs")
    
    # janelas.ps1 -> helpers/janelas.ps1
    json_str = json_str.replace(r"\\scripts\\kando\\janelas.ps1", r"\\scripts\\kando\\helpers\\janelas.ps1")
    json_str = json_str.replace(r"/scripts/kando/janelas.ps1", r"/scripts/kando/helpers/janelas.ps1")

    # limpa_pdf.ps1 -> scripts/powershell/limpa_pdf.ps1
    json_str = json_str.replace(r"\\scripts\\kando\\limpa_pdf.ps1", r"\\scripts\\powershell\\limpa_pdf.ps1")
    json_str = json_str.replace(r"/scripts/kando/limpa_pdf.ps1", r"/scripts/powershell/limpa_pdf.ps1")

    data = json.loads(json_str)

    # 3. Deduplica os menus pelo nome (mantendo o primeiro)
    seen_names = set()
    unique_menus = []
    for menu in data.get('menus', []):
        name = menu.get('root', {}).get('name')
        if name not in seen_names:
            unique_menus.append(menu)
            seen_names.add(name)
    data['menus'] = unique_menus

    # 4. Garante que os novos atalhos fundamentais existam
    for menu in data.get('menus', []):
        root = menu.get('root', {})
        children = root.get('children', [])
        for child in children:
            if child.get('name') == 'Espanso':
                esp_children = child.get('children', [])
                
                # Sincroniza atalho de Atendimento Celular se faltar
                if not any(c.get('name') == 'Atendimento Celular' for c in esp_children):
                    esp_children.append({
                        "type": "command",
                        "name": "Atendimento Celular",
                        "icon": "phone_android",
                        "iconTheme": "material-symbols-rounded",
                        "data": {
                            "command": f"pwsh.exe -WindowStyle Hidden -NoProfile -File \"C:\\\\Users\\\\{target_user}\\\\AppData\\\\Roaming\\\\espanso\\\\scripts\\\\kando\\\\calls\\\\chamar_celular.ps1\"",
                            "detached": True,
                            "isolated": False,
                            "delayed": False
                        }
                    })
    
    return data

def main():
    # Autodetecta o usuário logado no Windows
    current_user = getpass.getuser()
    print(f"==================================================")
    print(f"       SINCRO-MANUTENÇÃO DO CONFIG DO KANDO")
    print(f"==================================================")
    print(f"Usuário atual detectado: {current_user}")

    known_users = ["paulogoncalves", "paulo_admin", "User"]
    if current_user not in known_users:
        known_users.append(current_user)

    # Identifica caminhos ativos e backups
    active_config_path = Path(os.path.expandvars(r"%APPDATA%\Kando\config.json"))
    backup_dir = Path(os.path.expandvars(r"%APPDATA%\espanso\scripts\kando\json"))

    print("\nEscolha qual operação deseja realizar:")
    print("1 - Corrigir e atualizar o Kando ATIVO no sistema (%APPDATA%\\Kando\\config.json)")
    print("2 - Corrigir todos os backups JSON em scripts/kando/json/")
    print("3 - Corrigir AMBOS (Ativo e Backups)")
    
    # Se rodando sem interação, tenta rodar no modo total de segurança (Ambos)
    if not sys.stdin.isatty():
        print("\n[Execução Automatizada] Aplicando correções em AMBOS (Ativo e Backups)...")
        opcao = "3"
    else:
        try:
            opcao = input("\nDigite a opção desejada (1, 2 ou 3): ").strip()
        except:
            opcao = "3"

    arquivos_para_processar = []

    if opcao in ["1", "3"]:
        if active_config_path.exists():
            arquivos_para_processar.append((active_config_path, "Kando Ativo"))
        else:
            print(f"⚠️ Aviso: Arquivo de configuração ativo do Kando não encontrado em: {active_config_path}")

    if opcao in ["2", "3"]:
        if backup_dir.exists():
            for p in backup_dir.rglob("*.json"):
                arquivos_para_processar.append((p, f"Backup: {p.relative_to(backup_dir.parent)}"))
        else:
            print(f"ℹ️ Informação: Pasta de backups {backup_dir} não existe localmente.")

    if not arquivos_para_processar:
        print("❌ Nenhum arquivo encontrado para processar.")
        sys.exit(0)

    for caminho, desc in arquivos_para_processar:
        print(f"\nProcessando {desc}...")
        try:
            # Cria backup de segurança de 1º nível
            bkp_path = caminho.with_suffix(".json.bak")
            with open(caminho, "r", encoding="utf-8") as f:
                original_data = json.load(f)
                
            with open(bkp_path, "w", encoding="utf-8") as f:
                json.dump(original_data, f, ensure_ascii=False, indent=2)
                
            # Processa e corrige caminhos
            corrected_data = fix_json_content(original_data, current_user, known_users)
            
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(corrected_data, f, ensure_ascii=False, indent=2)
                
            print(f"  [OK] {desc} atualizado com sucesso!")
            print(f"  [BKP] Cópia de segurança criada em: {bkp_path.name}")
        except Exception as e:
            print(f"  [FALHA] Erro ao processar {desc}: {e}")

    print("\n==================================================")
    print("🎉 Sincronização concluída com sucesso total! 🎉")
    print("==================================================")

if __name__ == "__main__":
    main()
