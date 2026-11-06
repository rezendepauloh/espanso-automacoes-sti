# 📖 Guia Prático: Atendimento e Respostas Rápidas

> **Manual de operação dos gatilhos principais de atendimento ao usuário via Microsoft Teams e chamados da STI.**

---

## 🎯 1. O Gatilho Mestre `:ola`

O gatilho `:ola` é o ponto de entrada principal para a abertura de interações técnicas no Teams com servidores do MPMS.

### Fluxo Operacional:
1. O usuário digita `:ola` em qualquer caixa de texto ou chat do Teams.
2. O Espanso executa o despachante [`scripts/python/dispatcher.py`](../../scripts/python/dispatcher.py).
3. Uma interface de formulário é exibida para coleta dos dados do chamado:
   - **No Windows**: Dispara o executável nativo `C:\Program Files\Espanso Dynamic Forms\EDF.exe` com base no esquema [`forms/ola.yml`](../../forms/ola.yml).
   - **No Linux**: Dispara a interface gráfica de formulários em Tkinter/Zenity através de [`scripts/lib/form_runner.py`](../../scripts/lib/form_runner.py).
4. O texto final formatado é injetado diretamente na conversa com o cabeçalho padrão de atendimento.

---

## 📦 2. Tipos de Atendimento Disponíveis no Formulário

- **🐢 Lentidão**: Orientações e coleta de evidências para lentidão em estações de trabalho.
- **🔊 HP - BIOS**: Instruções para máquinas HP que apresentam aviso de inicialização/BIOS.
- **📸 Pedir fotos do equipamento**: Solicitação padrão com número do WhatsApp funcional e instruções.
- **⛔ Equipamento fora do domínio**: Orientações para reconexão ao domínio MPMS.
- **📞 Telefonia Fixa**: Problemas de ramal, fiações, liberação de ligações interurbanas.
- **📦 Material**: Formulário expandido dinamicamente para devoluções de teclado, mouse, monitor ou peças ao DMP.

