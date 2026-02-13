import sys
from datetime import datetime, timedelta
import io

# 🔴 FORÇA UTF-8 NO WINDOWS
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# =====================
# ARGUMENTOS
# =====================
data_tipo = sys.argv[1]
data_manual = sys.argv[2]
hora = sys.argv[3]
local = sys.argv[4]
local_outro = sys.argv[5]
demandas = sys.argv[6]
passageiros = sys.argv[7]

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
        return datetime.strptime(data_manual, "%d/%m/%Y")

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

    if local == "Outro local" and local_outro.strip():
        local_final = local_outro
    else:
        local_final = local

    demandas_html = multiline_to_ul(demandas)
    passageiros_html = multiline_to_ul(passageiros)

    texto = f"""Prezados, boa tarde!
<br /><br />
Solicito um transporte para <strong>{data_formatada}</strong> (<strong>{dia_semana}</strong>) às <strong>{hora}</strong> para <strong>{local_final}</strong>.
<br /><br />
Iremos atender as <strong>seguintes demandas/chamados</strong>:
{demandas_html}
<strong>Servidores/terceirizados:</strong>
{passageiros_html}
<br />
Ramal: <strong>2226, 2227 ou 2230</strong>
<br /><br />
Obrigado!
"""

    print(texto)

except Exception as e:
    print(f"⚠️ Erro ao gerar transporte urbano: {e}")
    sys.exit(1)