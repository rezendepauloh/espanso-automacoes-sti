import sys
from pathlib import Path
import subprocess
import io

# Adiciona o diretório lib ao path do Python
sys.path.append(str(Path(__file__).parent.parent))

# Força UTF-8 no terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from lib.utils import run_edf_form

def main():
    if len(sys.argv) < 2:
        print("⚠️ Erro: Tipo de script não especificado.")
        sys.exit(1)
        
    script_type = sys.argv[1]
    
    # Mapeia tipo de script para o formulário correspondente
    form_map = {
        "analisador": "analisador",
        "manutencao": "manutencao",
        "removeruser": "remove_profiles"
    }
    
    if script_type not in form_map:
        print(f"⚠️ Erro: Tipo de script '{script_type}' inválido.")
        sys.exit(1)
        
    form_name = form_map[script_type]
    
    # Executa o formulário dinâmico do EDF
    data = run_edf_form(form_name)
    if not data:
        sys.exit(0)  # Usuário cancelou ou fechou a janela
        
    # Caminho para o executor PowerShell mestre
    script_dir = Path(__file__).parent.resolve()
    ps_runner = script_dir.parent / "powershell" / "run_admin_script.ps1"
    
    # Reconstrói os argumentos para o runner PowerShell
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", str(ps_runner),
        "-ScriptType", script_type
    ]
    
    # Adiciona argumentos específicos com base nos campos preenchidos
    for key, value in data.items():
        if value:  # Apenas passa argumentos preenchidos
            cmd.extend([f"-{key}", value])
            
    try:
        # Executa de forma totalmente assíncrona (background) para não travar o Espanso
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        print("🔄 Executando script administrativo em console elevado...")
    except Exception as e:
        print(f"⚠️ Erro ao disparar script PowerShell: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
