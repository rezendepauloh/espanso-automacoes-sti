#!/bin/bash
# ==============================================================================
# Executor unificado de ações do Kando no Linux (COSMIC Wayland):
# Executa o script gerador (que abre a GUI nativa sti-forms), envia HTML/texto
# para o clipboard (wl-copy / CopyQ), restaura o foco e simula Ctrl+V.
# ==============================================================================
set -u

ACAO="${1:-}"
if [ -z "$ACAO" ]; then
    echo "Uso: $0 <acao>" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
CONFIG_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
export ESPANSO_CONFIG_DIR="$CONFIG_DIR"

umask 077
LOG_DIR="${XDG_RUNTIME_DIR:-$HOME/.cache}"
mkdir -p "$LOG_DIR" 2>/dev/null || true
LOG_FILE="$LOG_DIR/chamar_espanso_acao.log"

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

run_and_paste() {
    local SCRIPT="$1"
    shift
    local ARGS=("$@")

    log_msg "Início do acionamento: $ACAO ($SCRIPT)"

    export DISPLAY="${DISPLAY:-:1}"
    export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-1}"
    export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

    # 1. Salva a janela com foco ativo antes de abrir o formulário
    local TARGET_APP=""
    local TARGET_TITLE=""
    if command -v kando-cosmic-helper >/dev/null 2>&1; then
        local FOCUSED_RAW
        FOCUSED_RAW=$(kando-cosmic-helper focused 2>/dev/null || true)
        if [ -n "$FOCUSED_RAW" ]; then
            TARGET_APP=$(echo "$FOCUSED_RAW" | awk -F'\t' '{print $1}' | tr -d '"')
            TARGET_TITLE=$(echo "$FOCUSED_RAW" | awk -F'\t' '{print $2}' | tr -d '"')
        fi
    fi

    # 2. Executa o script Python (aciona sti-forms via utils.run_edf_form)
    local OUTPUT
    OUTPUT=$(python3 "$CONFIG_DIR/scripts/python/$SCRIPT" "${ARGS[@]}" 2>> "$LOG_FILE")
    local EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ] && [ -n "$OUTPUT" ]; then
        local PLAIN_TEXT
        PLAIN_TEXT=$(echo "$OUTPUT" | sed -e 's/<[^>]*>//g')

        # 3. Alimenta o CopyQ
        if command -v copyq >/dev/null 2>&1; then
            copyq add "$PLAIN_TEXT" 2>/dev/null || true
            copyq write text/html "$OUTPUT" text/plain "$PLAIN_TEXT" 2>/dev/null || true
            copyq select 0 2>/dev/null || true
        fi

        # 4. Alimenta o clipboard nativo Wayland
        if command -v wl-copy >/dev/null 2>&1; then
            printf '%s' "$PLAIN_TEXT" | wl-copy --type text/plain 2>/dev/null || true
            printf '%s' "$OUTPUT" | wl-copy --type text/html 2>/dev/null || true
        fi

        # 5. Restaura foco na janela original e simula Ctrl+V (37=Control_L, 55=v)
        python3 - "$TARGET_APP" "$TARGET_TITLE" 2>> "$LOG_FILE" << 'PYEOF' || true
import subprocess
import sys
import time

target_app = sys.argv[1] if len(sys.argv) > 1 else ""
target_title = sys.argv[2] if len(sys.argv) > 2 else ""

if target_app:
    try:
        subprocess.run(["kando-cosmic-helper", "focus", target_app, target_title], check=False, timeout=1)
    except Exception:
        pass

time.sleep(0.3)

simulated = False
try:
    res = subprocess.run(
        ["kando-cosmic-helper", "keys", "37:down:30", "55:down:30", "55:up:30", "37:up:30"],
        capture_output=True,
        timeout=1,
    )
    if res.returncode == 0:
        simulated = True
except Exception:
    pass

if not simulated:
    try:
        from evdev import UInput, ecodes
        cap = {ecodes.EV_KEY: [ecodes.KEY_LEFTCTRL, ecodes.KEY_V]}
        ui = UInput(cap, name="Virtual-Paste-Emitter")
        time.sleep(0.05)
        ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTCTRL, 1)
        ui.write(ecodes.EV_KEY, ecodes.KEY_V, 1)
        ui.syn()
        time.sleep(0.04)
        ui.write(ecodes.EV_KEY, ecodes.KEY_V, 0)
        ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTCTRL, 0)
        ui.syn()
        ui.close()
    except Exception:
        pass
PYEOF
        log_msg "Colagem concluída para $ACAO."
    else
        log_msg "Ação cancelada ou sem saída ($ACAO, código: $EXIT_CODE)."
    fi
}

case "$ACAO" in
    transporte_material) run_and_paste "transporte_material.py" ;;
    transporte_urbano)   run_and_paste "transporte_urbano.py" ;;
    devolucao_chamado)   run_and_paste "devolucao_chamado.py" ;;
    diaria_viagem)       run_and_paste "diaria_viagem.py" ;;
    transporte_viagem)   run_and_paste "transporte_viagem.py" ;;
    ola)                 run_and_paste "dispatcher.py" ;;
    celular)             run_and_paste "celular.py" ;;
    ia_arrumar)
        python3 "$CONFIG_DIR/scripts/python/ia_arrumar.py" --kando --update-clipboard --paste
        ;;
    minuscula)
        python3 "$CONFIG_DIR/scripts/python/minuscula.py" --kando --paste
        ;;
    maiuscula)
        python3 "$CONFIG_DIR/scripts/python/maiuscula.py" --kando --paste
        ;;
    *)
        log_msg "Ação desconhecida: $ACAO"
        exit 1
        ;;
esac
