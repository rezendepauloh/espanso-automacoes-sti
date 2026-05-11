import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# -*- coding: utf-8 -*-
import sys
import os
from lib.utils import fix_text_with_ai, format_output, paste_text
from lib.dictionary import DICIONARIO
import time

def main():
    # Detecta se é chamado pelo Kando ou Espanso
    is_kando = "--kando" in sys.argv
    should_update_clipboard = "--update-clipboard" in sys.argv or is_kando
    should_paste = "--paste" in sys.argv or is_kando

    # Pega o texto do clipboard
    try:
        import pyperclip
        text = pyperclip.paste()
    except:
        return

    if not text:
        return

    # Mágica da IA
    corrected = fix_text_with_ai(text, DICIONARIO)

    # Saída para Espanso (se não for Kando)
    if not is_kando:
        format_output(corrected)
    
    # Atualiza clipboard e cola (se solicitado)
    if should_update_clipboard:
        try:
            import pyperclip
            pyperclip.copy(corrected)
            
            if should_paste:
                time.sleep(0.2) # Delay para o sistema processar o clipboard
                paste_text()
        except:
            pass

if __name__ == "__main__":
    main()
