# -*- coding: utf-8 -*-
import sys, os, yaml
from pathlib import Path

def run_gui_form(form_config_path):
    config_path = Path(form_config_path)
    if not config_path.exists():
        return {}
    try:
        form_data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    properties = form_data.get("schema", {}).get("properties", {})
    defaults = form_data.get("data", {}) or {}
    try:
        import tkinter as tk
        from tkinter import ttk
        root = tk.Tk()
        root.title(f"Espanso - {config_path.stem.replace('_', ' ').title()}")
        root.configure(bg="#24283b")
        root.attributes("-topmost", True)
        root.geometry("480x520")
        root.eval('tk::PlaceWindow . center')
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background="#24283b", foreground="#c0caf5", font=("Cantarell", 10))
        style.configure("TLabel", background="#24283b", foreground="#c0caf5", font=("Cantarell", 10, "bold"))
        style.configure("TEntry", fieldbackground="#1f2335", foreground="#ffffff")
        style.configure("TCombobox", fieldbackground="#1f2335", foreground="#ffffff")
        style.configure("TButton", background="#7aa2f7", foreground="#1a1b26", font=("Cantarell", 10, "bold"))
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        entries = {}
        row = 0
        for field_name, field_info in properties.items():
            title = field_info.get("title", field_name)
            lbl = ttk.Label(main_frame, text=title)
            lbl.grid(row=row, column=0, sticky="w", pady=(8, 2))
            row += 1
            enums = field_info.get("enum")
            default_val = defaults.get(field_name, "")
            if enums:
                combo = ttk.Combobox(main_frame, values=enums, state="readonly")
                if default_val and default_val in enums:
                    combo.set(default_val)
                elif enums:
                    combo.current(0)
                combo.grid(row=row, column=0, sticky="ew", pady=(0, 6))
                entries[field_name] = combo
            else:
                entry = ttk.Entry(main_frame)
                if default_val:
                    entry.insert(0, str(default_val))
                entry.grid(row=row, column=0, sticky="ew", pady=(0, 6))
                entries[field_name] = entry
            row += 1
        result_data = {}
        def on_submit(event=None):
            for fname, widget in entries.items():
                result_data[fname] = widget.get()
            root.destroy()
        def on_cancel(event=None):
            root.destroy()
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, sticky="e", pady=(15, 0))
        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(8, 0))
        ok_btn = ttk.Button(btn_frame, text="Preencher", command=on_submit)
        ok_btn.pack(side=tk.RIGHT)
        root.bind("<Return>", on_submit)
        root.bind("<Escape>", on_cancel)
        for widget in entries.values():
            widget.focus_set()
            break
        root.mainloop()
        return result_data
    except Exception:
        cmd = ["zenity", "--forms", f"--title=Espanso - {config_path.stem}", "--text=Preencha as informações:"]
        fields_order = []
        for field_name, field_info in properties.items():
            cmd.append(f"--add-entry={field_info.get('title', field_name)}")
            fields_order.append(field_name)
        import subprocess
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            if res.returncode != 0 or not res.stdout.strip():
                return {}
            values = res.stdout.strip().split("|")
            return {fname: (values[i] if i < len(values) else "") for i, fname in enumerate(fields_order)}
        except Exception:
            return {}
