import json
import os

files = [
    r"c:\Users\User\AppData\Roaming\espanso\scripts\kando\json\casa\menu-settings-backup.json",
    r"c:\Users\User\AppData\Roaming\espanso\scripts\kando\json\trabalho\menu-settings-backup.json"
]

for file_path in files:
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Navega até o item Arrumar
    # children[10] -> children[355] -> children[488] -> children[495] -> children[503]
    # Na verdade, é melhor procurar pelo nome "Arrumar"
    
    def update_menu(item):
        if item.get("type") == "command" and item.get("name") == "Arrumar":
            cmd = item["data"]["command"]
            if "arrumar.ps1" in cmd:
                # Update to Python
                # Use double backslashes for JSON compatibility
                python_path = "python"
                script_path = r"C:\\Users\\User\\AppData\\Roaming\\espanso\\scripts\\ia_arrumar.py"
                item["data"]["command"] = f"{python_path} \"{script_path}\" --kando"
        
        if "children" in item:
            for child in item["children"]:
                update_menu(child)

    for menu in data.get("menus", []):
        update_menu(menu["root"])
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Updated {file_path}")
