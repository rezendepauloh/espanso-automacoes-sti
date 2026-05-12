# 📞 Chamadas de Gatilhos Kando (calls)

Este diretório armazena scripts curtos (wrappers de uma única linha) cujo objetivo exclusivo é interagir com as teclas físicas do sistema operacional para disparar formulários e atalhos do **Espanso** a partir dos cliques nos menus do **Kando**.

## 📄 Estrutura e Funcionamento

### [chamar_gatilho.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/calls/chamar_gatilho.ps1)
* **Função**: O despachador genérico parametrizado.
* **O que faz**:
  * Aceita um parâmetro `-Gatilho` (ex: `:ola`).
  * Realiza uma pequena pausa para que o menu radial do Kando suma completamente da tela (evitando que ele absorva as teclas digitadas).
  * Simula a digitação física caractere por caractere do gatilho e aperta a tecla `Espaço` ou `Enter`, fazendo com que o Espanso intercepte o atalho e exiba o formulário imediatamente na tela!

### ⚙️ Wrappers de Atalhos Específicos
Todas as outras chamadas deste diretório importam o `chamar_gatilho.ps1` passando o parâmetro correspondente em uma linha limpa (reduzindo a duplicação de código ao zero absoluto):
* `chamar_celular.ps1` -> Dispara o atalho `:cel`
* `chamar_devolução_chamado.ps1` -> Dispara o atalho `:dev`
* `chamar_diaria.ps1` -> Dispara o atalho `:diaria`
* `chamar_ola.ps1` -> Dispara o atalho `:ola`
* `chamar_transporte_material.ps1` -> Dispara o atalho `:tmat`
* `chamar_transporte_urbano.ps1` -> Dispara o atalho `:turb`
* `chamar_transporte_viagem.ps1` -> Dispara o atalho `:tvia`
