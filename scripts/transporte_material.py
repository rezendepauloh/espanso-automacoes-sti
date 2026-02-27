import sys
from datetime import datetime
import io

# 🔴 FORÇA UTF-8 NO WINDOWS
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# =====================
# ARGUMENTOS
# =====================
devolver = sys.argv[1]

# =====================
# FUNÇÕES AUXILIARES
# =====================
def multiline_to_list(texto):
    return [l.strip() for l in texto.splitlines() if l.strip()]

def list_to_ul(lista):
    if not lista:
        return ""
    itens = "".join(f"<li>{item}</li>" for item in lista)
    return f"<ul>{itens}</ul>"

def classificar_item(item):
    item_upper = item.upper()

    if "TESTE" in item_upper or "CONTRATO" in item_upper:
        return "contrato"
    elif "PATRIM" in item_upper:
        return "permanente"
    else:
        return "consumo"

# =====================
# PROCESSAMENTO
# =====================
try:
    itens = multiline_to_list(devolver)
    quantidade = len(itens)

    tipos = {"permanente": 0, "consumo": 0, "contrato": 0}

    for item in itens:
        tipo = classificar_item(item)
        tipos[tipo] += 1

    # 📦 Tipo predominante
    if tipos["contrato"] > 0 and tipos["permanente"] == 0 and tipos["consumo"] == 0:
        descricao_tipo = "materiais de contrato (em teste)"
    elif tipos["permanente"] > 0 and tipos["consumo"] == 0 and tipos["contrato"] == 0:
        descricao_tipo = "materiais permanentes"
    elif tipos["consumo"] > 0 and tipos["permanente"] == 0 and tipos["contrato"] == 0:
        descricao_tipo = "materiais de consumo"
    else:
        descricao_tipo = "materiais diversos"

    # 🧮 Texto de contagem
    if quantidade == 1:
        frase_itens = "o seguinte item"
    else:
        frase_itens = f"os seguintes {quantidade} itens"

    if quantidade == 1:
        frase_itens = "o seguinte item"
    else:
        frase_itens = "os seguintes itens"

    itens_html = list_to_ul(itens)

    texto = f"""Prezados, boa tarde!
<br /><br />
Solicito transporte para encaminhar {frase_itens} (<strong>{descricao_tipo}</strong>) <strong>ao prédio do DMP:</strong>
{itens_html}
<br />
<strong>Nota:</strong> Estamos enviando junto o Guia de Remessa para que eles assinem o recebimento.
<br /><br />
Ramal: <strong>2226, 2227 ou 2230</strong>
<br /><br />
Obrigado!
"""

    print(texto)

except Exception as e:
    print(f"⚠️ Erro ao gerar transporte de material: {e}")
    sys.exit(1)