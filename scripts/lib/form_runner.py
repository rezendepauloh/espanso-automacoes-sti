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
        form_title = f"Espanso - {config_path.stem.replace('_', ' ').title()}"
        root.title(form_title)
        root.configure(bg="#1e1e2e")
        root.attributes("-topmost", True)
        root.geometry("540x680")
        root.minsize(480, 400)
        root.eval('tk::PlaceWindow . center')
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background="#1e1e2e", foreground="#cdd6f4", font=("Cantarell", 10))
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Cantarell", 10, "bold"))
        style.configure("TEntry", fieldbackground="#313244", foreground="#ffffff")
        style.configure("TCombobox", fieldbackground="#313244", foreground="#ffffff")
        style.configure("TButton", background="#89b4fa", foreground="#11111b", font=("Cantarell", 10, "bold"))
        
        canvas = tk.Canvas(root, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="15")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=510)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        entries = {}
        row = 0
        for field_name, field_info in properties.items():
            title = field_info.get("title", field_name)
            lbl = ttk.Label(scrollable_frame, text=title)
            lbl.grid(row=row, column=0, sticky="w", pady=(8, 2))
            row += 1
            
            enums = field_info.get("enum")
            field_type = field_info.get("type")
            default_val = defaults.get(field_name, "")
            
            if enums:
                combo = ttk.Combobox(scrollable_frame, values=enums, state="readonly")
                if default_val and default_val in enums:
                    combo.set(default_val)
                elif enums:
                    combo.current(0)
                combo.grid(row=row, column=0, sticky="ew", pady=(0, 6))
                entries[field_name] = (combo, "combobox")
            elif field_type == "array":
                txt = tk.Text(scrollable_frame, height=3, bg="#313244", fg="#ffffff", insertbackground="#ffffff", relief="flat", font=("Cantarell", 10))
                if isinstance(default_val, list):
                    txt.insert("1.0", "\n".join(str(x) for x in default_val))
                elif default_val:
                    txt.insert("1.0", str(default_val))
                txt.grid(row=row, column=0, sticky="ew", pady=(0, 6))
                entries[field_name] = (txt, "text")
            else:
                entry = ttk.Entry(scrollable_frame)
                if default_val:
                    entry.insert(0, str(default_val))
                entry.grid(row=row, column=0, sticky="ew", pady=(0, 6))
                entries[field_name] = (entry, "entry")
            row += 1
            
        scrollable_frame.columnconfigure(0, weight=1)
        
        result_data = {}
        def on_submit(event=None):
            for fname, (widget, wtype) in entries.items():
                if wtype == "text":
                    result_data[fname] = widget.get("1.0", "end-1c").strip()
                else:
                    result_data[fname] = widget.get().strip()
            root.destroy()
            
        def on_cancel(event=None):
            root.destroy()
            
        btn_frame = ttk.Frame(root, padding="15")
        btn_frame.pack(side="bottom", fill="x")
        
        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(8, 0))
        ok_btn = ttk.Button(btn_frame, text="Preencher", command=on_submit)
        ok_btn.pack(side=tk.RIGHT)
        
        root.bind("<Escape>", on_cancel)
        root.mainloop()
        return result_data
        
    except Exception as err:
        # Fallback para Zenity caso o Tkinter falhe
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
