import json
import os

def fix_json(file_path, target_user, other_users):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert to string for global replacement
    json_str = json.dumps(data, ensure_ascii=False)
    
    # Fix users
    for user in other_users:
        json_str = json_str.replace(f"C:\\\\Users\\\\{user}", f"C:\\\\Users\\\\{target_user}")
        json_str = json_str.replace(f"C:/Users/{user}", f"C:/Users/{target_user}")

    # Load back
    data = json.loads(json_str)

    # Deduplicate menus by name (keep first)
    seen_names = set()
    unique_menus = []
    for menu in data.get('menus', []):
        name = menu.get('root', {}).get('name')
        if name not in seen_names:
            unique_menus.append(menu)
            seen_names.add(name)
    data['menus'] = unique_menus

    # Add new Espanso items if not present
    for menu in data.get('menus', []):
        root = menu.get('root', {})
        children = root.get('children', [])
        for child in children:
            if child.get('name') == 'Espanso':
                esp_children = child.get('children', [])
                
                # Check if "Atendimento Celular" exists
                if not any(c.get('name') == 'Atendimento Celular' for c in esp_children):
                    esp_children.append({
                        "type": "command",
                        "name": "Atendimento Celular",
                        "icon": "phone_android",
                        "iconTheme": "material-symbols-rounded",
                        "data": {
                            "command": f"pwsh.exe -WindowStyle Hidden -NoProfile -File \"C:\\\\Users\\\\{target_user}\\\\AppData\\\\Roaming\\\\espanso\\\\scripts\\\\calls\\\\chamar_celular.ps1\"",
                            "detached": True,
                            "isolated": False,
                            "delayed": False
                        }
                    })

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Fix Casa
fix_json(
    r"c:\Users\User\AppData\Roaming\espanso\scripts\kando\json\casa\menu-settings-backup.json",
    "User",
    ["paulogoncalves", "paulo_admin"]
)

# Fix Trabalho
fix_json(
    r"c:\Users\User\AppData\Roaming\espanso\scripts\kando\json\trabalho\menu-settings-backup.json",
    "paulogoncalves",
    ["User", "paulo_admin"]
)
