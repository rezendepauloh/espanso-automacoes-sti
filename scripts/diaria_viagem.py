import sys
from datetime import datetime
import io

# 🔴 FORÇA UTF-8 NO WINDOWS
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# =====================
# ARGUMENTOS
# =====================
destino = sys.argv[1]
data_saida = sys.argv[2]
hora_saida = sys.argv[3]
data_retorno = sys.argv[4]
hora_retorno = sys.argv[5]
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

def formatar_data(data_str):
    data = datetime.strptime(data_str, "%d/%m/%Y")
    dias = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    ]
    return data.strftime("%d/%m/%Y"), dias[data.weekday()]

# =====================
# PROCESSAMENTO
# =====================
try:
    data_saida_fmt, dia_saida = formatar_data(data_saida)
    data_retorno_fmt, dia_retorno = formatar_data(data_retorno)

    passageiros_html = multiline_to_ul(passageiros)

    texto = f"""Prezados, boa tarde!
<br /><br />
Solicito diárias para os <strong>funcionários terceirizados da Luppa</strong>:
{passageiros_html}
<strong>Período:</strong>
<ul>
<li>Saída: <strong>{data_saida_fmt}</strong> ({dia_saida}) às <strong>{hora_saida}</strong></li>
<li>Retorno: <strong>{data_retorno_fmt}</strong> ({dia_retorno}) às <strong>{hora_retorno}</strong></li>
</ul>
<strong>Motivo:</strong> Atendimento de Informática na(s) comarca(s) de <strong>{destino}</strong>.
<br /><br />
Ramal: <strong>2226, 2227 ou 2230</strong>
<br /><br />
Obrigado!
"""

    print(texto)

except Exception as e:
    print(f"⚠️ Erro ao gerar transporte de viagem: {e}")
    sys.exit(1)