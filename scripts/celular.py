# -*- coding: utf-8 -*-
import sys
from lib import utils

# Mapeamento de modelos para arquivos de template
MAPA_TEMPLATES = {
    "Modelo 01 - Quando há observação": "celular_obs",
    "Modelo 01 - Mensagem após resposta": "celular_pos_resposta",
    "Modelo 01 - Mensagem extra (se houver dificuldade com ligações": "celular_dificuldade",
    "Modelo 01 - Mensagem adicional (após ajuste no OXE)": "celular_ajuste_oxe",
    "Modelo 02 - Quando não há observação": "celular_sem_obs",
    "Modelo 03 - Quando a observação é crítica": "celular_critico",
    "Mensagem de lembrete amigável": "celular_lembrete",
    "Mensagem mais objetiva (se já passou bastante tempo)": "celular_objetivo",
}

def main():
    if len(sys.argv) < 2:
        from lib.utils import run_edf_form
        data = run_edf_form("celular")
        nome = data.get("nome", "")
        modelo = data.get("modelo", "")
        observacao = data.get("observacao", "")
        critica = data.get("critica", "")
    else:
        if len(sys.argv) < 5:
            print("⚠️ Erro: Argumentos insuficientes.")
            sys.exit(1)
        nome = sys.argv[1]
        modelo = sys.argv[2]
        observacao = sys.argv[3]
        critica = sys.argv[4]

    template_name = MAPA_TEMPLATES.get(modelo)
    
    if not template_name:
        print(f"⚠️ Erro: Modelo '{modelo}' não reconhecido.")
        sys.exit(1)

    try:
        template_content = utils.read_template(template_name)
        if not template_content:
            print(f"⚠️ Erro: Template '{template_name}' não encontrado.")
            sys.exit(1)

        # Formata o texto com as variáveis
        texto = template_content.format(
            nome=nome,
            observacao=observacao,
            critica=critica
        )

        utils.format_output(texto)

    except Exception as e:
        print(f"⚠️ Erro ao processar celular: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()