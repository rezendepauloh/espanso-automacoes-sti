import sys
from datetime import datetime, timedelta

data_input = sys.argv[1]
hora = sys.argv[2]
local = sys.argv[3]
local_outro = sys.argv[4]
demandas = sys.argv[5]
passageiros = sys.argv[6]

# 📅 Resolver data
hoje = datetime.now()

if data_input == "hoje":
    data_final = hoje
elif data_input == "amanhã":
    data_final = hoje + timedelta(days=1)
else:
    data_manual = input("Informe a data (dd/mm/aaaa): ")
    print(f"Data inválida") if not data_manual else None
    data_final = datetime.strptime(data_manual, "%d/%m/%Y")

dias = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]

dia_semana = dias[data_final.weekday()]
data_formatada = data_final.strftime("%d/%m/%Y")

# 📍 Resolver local
if local == "Outro local" and local_outro.strip():
    local_final = local_outro
else:
    local_final = local

# 🧾 Texto final
texto = f"""Prezados, boa tarde!

Solicito um transporte para {data_formatada} ({dia_semana}) às {hora} para {local_final}.

Iremos atender as seguintes demandas/chamados:

{demandas}

Os servidores/terceirizados que irão para lá serão:

{passageiros}

Ramal: 2226, 2227 ou 2230

Obrigado!
"""

print(texto)