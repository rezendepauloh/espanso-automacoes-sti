import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import sys
from datetime import datetime, timedelta
import io

# 🔴 FORÇA UTF-8 NO WINDOWS
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# =====================
# ARGUMENTOS
# =====================
# =====================
# ARGUMENTOS / FORMULÁRIO DINÂMICO
# =====================
if len(sys.argv) < 2:
    from lib.utils import run_edf_form
    data = run_edf_form("transporte_urbano")
    data_tipo = data.get("data", "hoje")
    data_manual = data.get("data_manual", "")
    hora = data.get("hora", "")
    local = data.get("local", "")
    demandas = data.get("demandas", "")
    passageiros = data.get("passageiros", "")
else:
    data_tipo = sys.argv[1]
    data_manual = sys.argv[2]
    hora = sys.argv[3]
    local = sys.argv[4]
    demandas = sys.argv[5]
    passageiros = sys.argv[6]

# =====================
# FUNÇÕES AUXILIARES
# =====================
def multiline_to_ul(texto):
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    if not linhas:
        return ""
    itens = "".join(f"<li>{l}</li>" for l in linhas)
    return f"<ul>{itens}</ul>"

def resolver_data(data_tipo, data_manual):
    hoje = datetime.now()
    if data_tipo == "hoje":
        return hoje
    elif data_tipo == "amanhã":
        return hoje + timedelta(days=1)
    else:
        try:
            # Tenta formato ISO (YYYY-MM-DD) enviado pelo Date Picker do EDF
            return datetime.strptime(data_manual, "%Y-%m-%d")
        except ValueError:
            # Fallback para o formato brasileiro (DD/MM/YYYY) legado
            return datetime.strptime(data_manual, "%d/%m/%Y")

def aplicar_artigo(nome_local):
    """Adiciona 'a' ou 'o' automaticamente para os prédios conhecidos."""
    locais_conhecidos = {
        "chácara cachoeira": "a Chácara Cachoeira",
        "chacara cachoeira": "a Chácara Cachoeira",
        "rua da paz": "a Rua da Paz",
        "ricardo brandão": "a Ricardo Brandão",
        "ricardo brandao": "a Ricardo Brandão",
        "casa da mulher brasileira": "a Casa da Mulher Brasileira",
        "dmp": "o DMP",
        "pgj": "a PGJ",
        "fórum": "o Fórum",
        "forum": "o Fórum"
    }
    # Retorna o local com artigo se conhecer, ou o texto original se não conhecer
    return locais_conhecidos.get(nome_local.lower(), nome_local)

def formatar_locais(texto_locais):
    """Lê os locais, aplica os artigos corretos e formata com vírgulas e 'e'."""
    locais_brutos = [l.strip() for l in texto_locais.splitlines() if l.strip()]
    
    if len(locais_brutos) == 0:
        return "<strong>Não Informado</strong>"
        
    # Aplica a regrinha do "o" e "a" para cada prédio digitado
    locais = [aplicar_artigo(l) for l in locais_brutos]
    
    if len(locais) == 1:
        return f"<strong>{locais[0]}</strong>"
    elif len(locais) == 2:
        return f"<strong>{locais[0]} e {locais[1]}</strong>"
    else:
        locais_virgula = ", ".join(locais[:-1])
        ultimo_local = locais[-1]
        return f"<strong>{locais_virgula} e {ultimo_local}</strong>"

dias = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]

# =====================
# PROCESSAMENTO
# =====================
try:
    data_final = resolver_data(data_tipo, data_manual)
    dia_semana = dias[data_final.weekday()]
    data_formatada = data_final.strftime("%d/%m/%Y")

    if data_tipo == "hoje":
        texto_data = f"hoje, <strong>{data_formatada}</strong> (<strong>{dia_semana}</strong>)"
    elif data_tipo == "amanhã":
        texto_data = f"amanhã, <strong>{data_formatada}</strong> (<strong>{dia_semana}</strong>)"
    else:
        texto_data = f"<strong>{data_formatada}</strong> (<strong>{dia_semana}</strong>)"

    locais_formatados = formatar_locais(local)
    demandas_html = multiline_to_ul(demandas)
    passageiros_html = multiline_to_ul(passageiros)

    texto = f"""Prezados, boa tarde!
<br /><br />
Solicito um transporte para {texto_data} às <strong>{hora}</strong> para {locais_formatados}.
<br /><br />
Iremos atender as <strong>seguintes demandas/chamados</strong>:
{demandas_html}
<strong>Servidores/terceirizados:</strong>
{passageiros_html}
Ramal: <strong>2226, 2227 ou 2230</strong>
<br /><br />
Obrigado!
"""

    print(texto)

except Exception as e:
    print(f"⚠️ Erro ao gerar transporte urbano: {e}")
    sys.exit(1)