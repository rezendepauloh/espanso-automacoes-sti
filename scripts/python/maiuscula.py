#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversão do Clipboard para Maiúsculas (Multiplataforma: Linux & Windows).
Compatível com Espanso (stdout) e Kando (--kando / --paste).
"""

import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from lib.utils import format_output, paste_text


def main():
    is_kando = "--kando" in sys.argv
    should_update_clipboard = "--update-clipboard" in sys.argv or is_kando
    should_paste = "--paste" in sys.argv or is_kando

    text = ""
    try:
        import pyperclip
        text = pyperclip.paste()
    except Exception:
        pass

    if not text:
        return

    upper_text = text.upper()

    if not is_kando:
        format_output(upper_text)

    if should_update_clipboard:
        try:
            import pyperclip
            pyperclip.copy(upper_text)
            if should_paste:
                time.sleep(0.15)
                paste_text()
        except Exception:
            pass


if __name__ == "__main__":
    main()

