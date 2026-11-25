#!/bin/bash
# ==============================================================================
# Sincronizador de Ambiente Linux (Pop!_OS / COSMIC) — Espanso + Kando + sti-forms
# ==============================================================================
# Uso: ./sync.sh [--build]
#   --build   Recompila gui/cosmic em modo release antes de instalar
# ==============================================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_BIN="$HOME/.local/bin"
ESPANSO_DIR="$HOME/.config/espanso"
DO_BUILD=false

if [ "${1:-}" = "--build" ]; then
    DO_BUILD=true
fi

mkdir -p "$LOCAL_BIN" "$HOME/.config"

echo "🔄 Sincronizando Espanso Automações STI..."

# 1. Compilar (opcional) e instalar sti-forms em ~/.local/bin/sti-forms
RELEASE_BIN="$REPO_DIR/gui/cosmic/target/release/sti-forms"
if [ "$DO_BUILD" = true ] || [ ! -x "$RELEASE_BIN" ]; then
    echo "🦀 Compilando sti-forms (release)..."
    (cd "$REPO_DIR/gui/cosmic" && cargo build --release)
fi
install -Dm0755 "$RELEASE_BIN" "$LOCAL_BIN/sti-forms"
echo "✔ sti-forms instalado em $LOCAL_BIN/sti-forms"

# 1b. Instalar ícone e .desktop do sti-forms para o compositor COSMIC
APPID="br.dev.rezendepauloh.StiForms"
ICON_DST="$HOME/.local/share/icons/hicolor/scalable/apps/$APPID.svg"
DESKTOP_DST="$HOME/.local/share/applications/$APPID.desktop"
install -Dm0644 "$REPO_DIR/gui/cosmic/res/icons/hicolor/scalable/apps/$APPID.svg" "$ICON_DST"
install -Dm0644 "$REPO_DIR/gui/cosmic/res/$APPID.desktop" "$DESKTOP_DST"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
echo "✔ Ícone e .desktop instalados ($APPID)"

# 2. Linkar chamar_espanso_acao -> scripts/kando/calls/chamar_acao.sh (Kando)
KANDO_TARGET="$REPO_DIR/scripts/kando/calls/chamar_acao.sh"
KANDO_LINK="$LOCAL_BIN/chamar_espanso_acao"
chmod +x "$KANDO_TARGET"

if [ -e "$KANDO_LINK" ] && [ ! -L "$KANDO_LINK" ]; then
    mv "$KANDO_LINK" "${KANDO_LINK}.bak.$(date +%Y%m%d_%H%M%S)"
fi
ln -sfn "$KANDO_TARGET" "$KANDO_LINK"
echo "✔ Kando linkado: $KANDO_LINK -> $KANDO_TARGET"

# 3. Linkar ~/.config/espanso -> repositório (com backup automático se for pasta física)
if [ -L "$ESPANSO_DIR" ] && [ "$(readlink -f "$ESPANSO_DIR")" = "$REPO_DIR" ]; then
    echo "✔ Espanso já aponta para $REPO_DIR"
else
    if [ -e "$ESPANSO_DIR" ] || [ -L "$ESPANSO_DIR" ]; then
        BACKUP_DIR="${ESPANSO_DIR}.bak.$(date +%Y%m%d_%H%M%S)"
        mv "$ESPANSO_DIR" "$BACKUP_DIR"
        echo "📦 Backup da pasta antiga do Espanso salvo em: $BACKUP_DIR"
    fi
    ln -s "$REPO_DIR" "$ESPANSO_DIR"
    echo "✔ Espanso linkado: $ESPANSO_DIR -> $REPO_DIR"
fi

# 4. Reiniciar Espanso se disponível
if command -v espanso >/dev/null 2>&1; then
    espanso restart || true
    echo "✔ Espanso reiniciado"
fi

echo "🎉 Ambiente sincronizado! Agora :ola no Espanso e os atalhos do Kando usam a nova GUI COSMIC."
