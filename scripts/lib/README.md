# 📚 Diretório de Bibliotecas Compartilhadas (lib)

Este diretório armazena módulos e dados comuns que são importados e reutilizados por múltiplos scripts executivos do projeto, seguindo os princípios de reuso de código e modularidade.

## 📄 Arquivos e Estrutura

### [dicionario.json](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/lib/dicionario.json)
* **Função**: O banco de dados centralizado de palavras, abreviações e siglas.
* **O que faz**: Contém um único dicionário em JSON estruturado com mais de 340 palavras que necessitam de correção de caixa, acentuação ou expansão (como `mpms` -> `MPMS`, `sajmp` -> `SAJMP`, `vc` -> `você`).

### [dicionario.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/lib/dicionario.ps1)
* **Função**: Carregador do dicionário para PowerShell.
* **O que faz**: Lê dinamicamente o arquivo central [dicionario.json](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/lib/dicionario.json) e o converte em uma Hashtable PowerShell global (`$global:meuDicionario`) para correções instantâneas em tempo de execução.

### [dictionary.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/lib/dictionary.py)
* **Função**: Carregador do dicionário para Python.
* **O que faz**: Lê o arquivo central [dicionario.json](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/lib/dicionario.json) e o expõe como um dicionário Python nativo (`DICIONARIO`) para correções textuais inteligentes.

### [utils.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/lib/utils.ps1)
* **Função**: Funções utilitárias globais do PowerShell.
* **O que faz**:
  * `Setup-Encoding`: Garante o output correto em UTF-8 no PowerShell 5.1/7.
  * `Invoke-TextCorrection`: Realiza a correção gramatical e ortográfica em lote de um texto usando o dicionário carregado.
  * `Clean-PdfText`: Algoritmo inteligente que remove hífens de final de linha e junta parágrafos quebrados de arquivos PDF copiados.
  * `Set-ClipboardAndPaste`: Altera a área de transferência do Windows e simula o atalho `CTRL+V` para colar instantaneamente.

### [utils.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/lib/utils.py)
* **Função**: Funções utilitárias globais do Python.
* **O que faz**:
  * `setup_utf8`: Configura os encodings de terminal do Windows para evitar erros de caracteres acentuados.
  * `fix_text_with_ai`: Motor NLP Spacy híbrido que limpa o texto, corrige acentuação contextualizada (como discernir "e" vs "é") e aplica o dicionário de siglas.
  * `read_template`: Lê templates HTML locais com segurança para renderização.
  * `run_edf_form`: Executa o executável `EDF.exe` e extrai os campos preenchidos do formulário do Espanso.
  * `format_output`: Imprime a saída formatada de modo compatível com o mecanismo de renderização HTML do Espanso.
