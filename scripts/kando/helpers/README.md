# ⚙️ Utilitários do Sistema de Janelas (helpers)

Este diretório contém os componentes e utilitários auxiliares do sistema operacional usados pelo Kando para manipular o estado das janelas ativas e executar comandos do PowerShell de modo totalmente invisível.

## 📄 Arquivos e Funcionamento

### [invisivel.vbs](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/helpers/invisivel.vbs)
* **Função**: Executor invisível de plano de fundo.
* **O que faz**:
  * É invocado pelo Kando passando a ação desejada (Maximizar, Minimizar ou Restaurar) como argumento.
  * Resolve dinamicamente a localização da pasta usando a variável de ambiente `%USERPROFILE%` do Windows (garantindo portabilidade total entre computadores Casa vs. Trabalho).
  * Executa o interpretador do PowerShell passando o script [janelas.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/helpers/janelas.ps1) com o parâmetro de visibilidade igual a `0`. Isso garante que as simulações de teclas ocorram instantaneamente, sem piscar nenhuma janela preta de console do Windows na tela!

### [janelas.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/helpers/janelas.ps1)
* **Função**: Manipulador físico de janelas do Windows.
* **O que faz**:
  * Recebe a ação (`Maximizar`, `Minimizar` ou `Restaurar`).
  * Realiza uma pequena pausa de 300ms (essencial para que o menu radial do Kando desapareça e o foco do Windows retorne à aplicação que o usuário estava usando).
  * Simula a sequência de comandos nativos do Windows (`ALT + ESPAÇO` seguido de `x`, `n` ou `r`) para redimensionar a janela atual em foco com altíssima precisão.
