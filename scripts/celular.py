import sys
from datetime import datetime
import io

# 🔴 FORÇA UTF-8 NO WINDOWS
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# =====================
# ARGUMENTOS
# =====================
nome = sys.argv[1]
modelo = sys.argv[2]
observacao = sys.argv[3]
critica = sys.argv[4]

# =====================
# PROCESSAMENTO
# =====================
try:
    if modelo == "Modelo 01 - Quando há observação":

        texto = f"""Olá <strong>{nome}</strong>, tudo bem? Aqui é o Paulo da manutenção da STI.
<br /><br />
Estamos fazendo um levantamento sobre o <strong>uso dos telefones celulares e fixos</strong>. Consta a seguinte observação para sua unidade:
<br /><br />
<strong>"{observacao}"</strong>
<br /><br />
Gostaria de confirmar algumas informações:
<ul>
<li>Vocês conseguem realizar ligações do telefone fixo para celulares sem problemas?</li>
<li>O celular funcional é usado para WhatsApp?</li>
<li>Teriam interesse em usar WhatsApp pelo telefone fixo?</li>
</ul>
Se possível, faça um teste agora: tente <strong>ligar do telefone fixo para seu celular particular</strong>. Isso ajuda a confirmar se está funcionando corretamente.
<br /><br />
Sua resposta vai nos ajudar a avaliar melhorias na comunicação."""
    
    elif modelo == "Modelo 01 - Mensagem após resposta":
        
        texto = f"""Obrigado pelo retorno! Informo que está em estudo a implementação do WhatsApp nos telefones fixos, para facilitar a comunicação e reduzir a dependência dos celulares funcionais.
<br /><br />
O objetivo é entender a real necessidade dos aparelhos móveis e verificar se é possível substituí-los pelo uso do fixo com WhatsApp."""
        
    elif modelo == "Modelo 01 - Mensagem extra (se houver dificuldade com ligações":

        texto = f"""Caso tenha dificuldade para ligar do fixo para celular, segue uma dica:
<ol>
<li>Para números com DDD 67: <strong>disque apenas o número</strong>.</li>
<li>Para outros DDDs: <strong>inclua o DDD antes do número</strong>.</li>
</ol>
Também preparei um vídeo explicativo para ajudar."""
        
    elif modelo == "Modelo 01 - Mensagem adicional (após ajuste no OXE)":

        texto = f"""Obrigado por testar! Ajustei um parâmetro técnico no sistema de telefonia para permitir ligações para celulares e interurbanos. Por favor, tente novamente a ligação do telefone fixo para seu celular e me avise se funcionou."""

    elif modelo == "Modelo 02 - Quando não há observação":

        texto = f"""Olá <strong>{nome}</strong>, tudo bem? Aqui é o Paulo da manutenção da STI.
<br /><br />
Estamos fazendo um levantamento sobre o <strong>uso dos telefones celulares e fixos</strong>. Não identificamos observações específicas para sua unidade.
<br /><br />
Gostaria de confirmar algumas informações:
<ul>
<li>Vocês conseguem realizar ligações do telefone fixo para celulares sem problemas?</li>
<li>O celular funcional é usado para WhatsApp?</li>
<li>Teriam interesse em usar WhatsApp pelo telefone fixo?</li>
</ul>
Se possível, faça um teste agora: tente <strong>ligar do telefone fixo para seu celular particular</strong>. Isso ajuda a confirmar se está funcionando corretamente.
<br /><br />
Sua resposta vai nos ajudar a avaliar melhorias na comunicação."""

    elif modelo == "Modelo 03 - Quando a observação é crítica":

        texto = f"""Olá <strong>{nome}</strong>, tudo bem? Aqui é o Paulo da manutenção da STI.
<br /><br />
Estamos fazendo um levantamento sobre o <strong>uso dos telefones celulares e fixos</strong>. Consta a seguinte observação para sua unidade:
<br /><br />
<strong>"{observacao}"</strong>
<br /><br />
Vi que mencionaram <strong>{critica}</strong>. Poderia me explicar um pouco mais sobre essa necessidade? Isso ajuda a entender se o WhatsApp no fixo atenderia essa demanda.
<br /><br />
Além disso, gostaria de confirmar:
<ul>
<li>Vocês conseguem realizar ligações do telefone fixo para celulares sem problemas?</li>
<li>O celular funcional é usado para WhatsApp?</li>
<li>Teriam interesse em usar WhatsApp pelo telefone fixo?</li>
</ul>
Se possível, faça um teste agora: tente <strong>ligar do telefone fixo para seu celular particular</strong>. Isso ajuda a confirmar se está funcionando corretamente.
<br /><br />
Sua resposta vai nos ajudar a avaliar melhorias na comunicação."""

    elif modelo == "Mensagem de lembrete amigável":

        texto = f"""Olá <strong>{nome}</strong>, tudo bem? Só passando para lembrar sobre a mensagem anterior referente ao levantamento dos telefones celulares e fixos.
<br /><br />
Sua resposta é muito importante para concluirmos o estudo e melhorar a comunicação. Se puder, me confirme quando possível. Caso precise de ajuda para realizar o teste de ligação ou tenha dúvidas, estou à disposição!"""
        
    elif modelo == "Mensagem mais objetiva (se já passou bastante tempo)":

        texto = f"""Olá <strong>{nome}</strong>, tudo bem? Reforçando o pedido anterior: precisamos das informações sobre o uso dos telefones celulares e fixos para concluir o levantamento.
<br /><br />
Se puder responder ainda hoje, agradeço muito! Qualquer dúvida ou dificuldade, me avise que ajudo."""

    print(texto)

except Exception as e:
    print(f"⚠️ Erro ao gerar dados do celular: {e}")
    sys.exit(1)