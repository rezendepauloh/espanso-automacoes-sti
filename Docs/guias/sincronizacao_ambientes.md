# 🔄 Guia de Sincronização de Ambientes (`sync.sh` & `sync.ps1`)

> **Provisionamento completo do ecossistema Espanso + Kando + GUIs nativas no Windows 10/11 e no Linux (Pop!_OS COSMIC).**

---

## 🪟 Windows 10/11 (`sync.ps1`)

O script [`sync.ps1`](../../sync.ps1) replica no Windows o fluxo automatizado do `sync.sh`:

```powershell
# Compilar sti-forms.exe, instalar, criar .env (se faltar), atualizar Kando e reiniciar Espanso:
pwsh -NoProfile -ExecutionPolicy Bypass -File sync.ps1 -Build
```

### Etapas executadas:
1. **Build & Instalação (`.NET 8 + WPF-UI`):**
   - Executa `dotnet publish gui/windows/StiForms/StiForms.csproj -c Release -r win-x64 --no-self-contained` e instala em `%LOCALAPPDATA%\Programs\StiForms\sti-forms.exe`.
2. **Provisionamento de `.env`:**
   - Caso `.env` não exista na raiz, cria uma cópia inicial a partir de [`.env.example`](../../.env.example).
3. **Vínculo do Espanso (`%APPDATA%\espanso`):**
   - Verifica se `%APPDATA%\espanso` já aponta para o repositório; caso contrário, realiza backup e cria uma `Junction` apontando para o repositório.
4. **Backup e Migração do Kando ([`sync_kando_windows.py`](../../scripts/kando/sync_kando_windows.py)):**
   - Salva backup com timestamp + `.latest.json` de `%APPDATA%\Kando\menus.json` e `config.json` dentro de `scripts/kando/json/backup_windows/` (pasta ignorada pelo Git).
   - Atualiza comandos legados (`chamar_*.ps1`, `arrumar.ps1`, `maiuscula.ps1`, `minuscula.ps1`, `limpa_pdf.ps1`) para chamar `"%LOCALAPPDATA%\Programs\StiForms\sti-forms.exe" --action <acao> [--paste]` diretamente, mantendo os demais menus intactos.
   - Atualiza caminhos antigos de usuário e corrige referências de `janelas.ps1` para `helpers\janelas.ps1`.
5. **Reinício do Espanso:** Executa `espanso restart`.

### Opções úteis do `sync.ps1`:
```powershell
# Apenas recompilar e instalar o sti-forms.exe (sem mexer no Kando nem reiniciar o Espanso):
pwsh -NoProfile -ExecutionPolicy Bypass -File sync.ps1 -Build -SkipKando -NoRestart

# Sincronizar Kando/Espanso sem recompilar o C# (usa o binário já instalado):
pwsh -NoProfile -ExecutionPolicy Bypass -File sync.ps1

# Restaurar o último backup do Kando se necessário:
pwsh -NoProfile -ExecutionPolicy Bypass -File sync.ps1 -RestoreKando

# Pular sincronização do Kando:
pwsh -NoProfile -ExecutionPolicy Bypass -File sync.ps1 -Build -SkipKando
```

---

## 🐧 Linux Pop!_OS / COSMIC (`sync.sh`)

```bash
./sync.sh --build
```

1. Compila `gui/cosmic/` (`cargo build --release`) e instala em `~/.local/bin/sti-forms`.
2. Instala ícone e arquivo `.desktop` (`br.dev.rezendepauloh.StiForms`).
3. Cria link simbólico `~/.local/bin/chamar_espanso_acao -> scripts/kando/calls/chamar_acao.sh`.
4. Garante que `~/.config/espanso` aponte para o repositório e reinicia o Espanso.
