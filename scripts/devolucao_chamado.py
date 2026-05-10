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
    data = run_edf_form("devolucao_chamado")
    nome = data.get("nome", "")
    genero = data.get("genero", "")
else:
    nome = sys.argv[1]
    genero = sys.argv[2]

# =====================
# PROCESSAMENTO
# =====================
try:

    if (genero == "Homem"):
        inicio = "Prezado Senhor"
    else:
        inicio = "Prezada Senhora"

    texto = f"""{inicio} {nome},
<br /><br />
Obrigado por entrar em contato com a <strong>Central de Serviços de TI do MPMS</strong>.
<br /><br />
Tendo em vista a implantação do novo Portal de Serviços e que todos os procedimentos realizados pela equipe da <strong>Secretaria de Tecnologia da Informação</strong> não surtiram efeito, será necessário realizar a devolução do seu equipamento, através do menu <strong>"Gestão Administrativa" -> "Devolução de Material Permanente"</strong>, disponível no link <a href="https://portaldeservicos.mpms.mp.br" target="_blank">https://portaldeservicos.mpms.mp.br</a>.
<br /><br />
Ademais, para que o andamento dos trabalhos desempenhados por você não seja prejudicado é possível já realizar, em um outro pedido, uma <strong>"Solicitação de Material Permanente"</strong>, no mesmo link citado.
<br /><br />
Qualquer dúvida referente ao <strong>Portal de Serviços</strong>, ou como efetuar os procedimentos acima, podem ser sanadas diretamente com o suporte da Ábaco através dos contatos abaixo:
<ol>
<li><strong>Telefone:</strong> 0800 647 0777</li>
<li><strong>Whatsapp:</strong> 800 647 0777</li>
<li><strong>E-mail:</strong> <a href="mailto:atendimento@abaco.com.br">atendimento@abaco.com.br</a></li>
</ol>
<strong>Observação:</strong> Caso tenha qualquer dúvida ou não concorde na solução aplicada nesse atendimento, favor responder este e-mail de fechamento para realizar a reabertura do chamado.
<br /><br />
Atenciosamente,
<br /><br />
Secretaria de Tecnologia da Informação - STI<br />
Central de Serviços de TI<br />
Fone: (67) 3318-3939 | Opção => 2
"""

    print(texto)

except Exception as e:
    print(f"⚠️ Erro ao gerar transporte de viagem: {e}")
    sys.exit(1)