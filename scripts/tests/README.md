# 🧪 Diretório de Testes Unitários Automatizados (scripts/tests)

Este diretório abriga a nossa suíte de testes unitários desenvolvida para garantir que qualquer modificação ou adição de novas palavras ou regras no repositório ocorra sem introduzir bugs ou quebras de funcionamento (regressão zero).

## 📄 Arquivos e Estrutura de Testes

### [rodar_testes.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/tests/rodar_testes.ps1)
* **Função**: Orquestrador e executor central colorido.
* **O que faz**:
  * Executa os testes Python com a flag `-v` para detalhar caso a caso.
  * Invoca os testes de biblioteca do PowerShell.
  * Consolida todos os resultados e emite um relatório resumido colorido direto no console, indicando se o projeto está 100% íntegro.

### [test_nlp_and_templates.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/tests/test_nlp_and_templates.py)
* **Função**: Suíte de testes unitários Python.
* **O que faz**:
  * Valida o carregamento sob demanda do dicionário JSON.
  * Testa o algoritmo NLP Spacy para expansão de termos e correções contextuais ("e" vs "é").
  * Valida a inteligência de pluralização de comarcas e cálculos de datas de viagem.
  * Garante que todos os arquivos físicos HTML de respostas rápidas mapeados em `respostas.py` existam no disco.
  * Valida a leitura de todos os templates de suporte celular da pasta `textos/celular/`.

### [test_library.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/tests/test_library.ps1)
* **Função**: Suíte de testes unitários PowerShell.
* **O que faz**:
  * Valida o parsing e carregamento de dados do dicionário central do JSON para Hashtable.
  * Testa correções ortográficas, capitalizações e expansões via `Invoke-TextCorrection`.
  * Valida o complexo processador de quebras de linha de PDFs (`Clean-PdfText`), cobrindo remoção de hífens, junção artificial de linhas e detecção correta de parágrafos.

---

## 🚀 Como executar todos os testes da sua máquina:

Basta abrir um terminal PowerShell e rodar o script orquestrador:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\tests\rodar_testes.ps1"
```
Se tudo estiver correto, você receberá a mensagem final verde de sucesso total! 🌟
