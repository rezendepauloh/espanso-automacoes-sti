import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import sys
from datetime import datetime
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
    data = run_edf_form("transporte_viagem")
    destino_raw = data.get("destino", "")
    data_saida = data.get("data_saida", "")
    hora_saida = data.get("hora_saida", "")
    data_retorno = data.get("data_retorno", "")
    hora_retorno = data.get("hora_retorno", "")
    motivo_viagem = data.get("motivo_viagem", "")
    demandas = data.get("demandas", "")
    passageiros = data.get("passageiros", "")
else:
    destino_raw = sys.argv[1]
    data_saida = sys.argv[2]
    hora_saida = sys.argv[3]
    data_retorno = sys.argv[4]
    hora_retorno = sys.argv[5]
    motivo_viagem = sys.argv[6]
    demandas = sys.argv[7]
    passageiros = sys.argv[8]

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
    try:
        # Tenta formato ISO (YYYY-MM-DD) enviado pelo EDF
        data = datetime.strptime(data_str, "%Y-%m-%d")
    except ValueError:
        # Fallback para o formato brasileiro (DD/MM/YYYY) do Espanso legado
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

def formatar_cidades(texto_cidades):
    """Lê as cidades digitadas, pluraliza a frase e formata a lista com vírgulas e 'e'."""
    cidades = [c.strip() for c in texto_cidades.splitlines() if c.strip()]
    
    if len(cidades) == 0:
        return "<strong>Não Informado</strong>."
    
    elif len(cidades) == 1:
        return f"<strong>{cidades[0]}</strong>."
    
    elif len(cidades) == 2:
        return f"<strong>{cidades[0]} e {cidades[1]}</strong>."
    
    else:
        # Pega todas as cidades menos a última, junta com vírgula, e adiciona "e a última"
        cidades_virgula = ", ".join(cidades[:-1])
        ultima_cidade = cidades[-1]
        return f"<strong>{cidades_virgula} e {ultima_cidade}</strong>."

# =====================
# PROCESSAMENTO
# =====================
try:
    data_saida_fmt, dia_saida = formatar_data(data_saida)
    data_retorno_fmt, dia_retorno = formatar_data(data_retorno)

    passageiros_html = multiline_to_ul(passageiros)
    demandas_html = multiline_to_ul(demandas)

    # Chama a nossa nova função inteligente para o texto do destino
    texto_destino_formatado = formatar_cidades(destino_raw)

    texto = f"""Prezados, boa tarde!
<br /><br />
Solicito transporte para atender uma <strong>viagem de demanda do DMP</strong>, que será realizada junto da nossa equipe.
<br /><br />
<strong>Destino:</strong> {texto_destino_formatado}
<br /><br />
<strong>Período:</strong>
<ul>
<li>Saída: <strong>{data_saida_fmt}</strong> ({dia_saida}) às <strong>{hora_saida}</strong></li>
<li>Retorno: <strong>{data_retorno_fmt}</strong> ({dia_retorno}) às <strong>{hora_retorno}</strong></li>
</ul>
<br /><br />
<strong>Motivo:</strong> {motivo_viagem}
<br /><br />
<strong>Demandas/chamados:</strong>
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
    print(f"⚠️ Erro ao gerar transporte de viagem: {e}")
    sys.exit(1)