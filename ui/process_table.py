import customtkinter as ctk
from tkinter import ttk

def style_table(tree, theme):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#111", foreground="#fff", fieldbackground="#111", font=("Consolas", 10), rowheight=26)
    style.configure("Treeview.Heading", background="#1A1A2E", foreground=theme.accent, font=("Segoe UI", 9, "bold"), relief="flat")
    style.map("Treeview", background=[("selected", theme.accent)], foreground=[("selected", "#000")])
    tree.configure(style="Treeview")

class ProcessTableWidget:
    def __init__(self, master, theme, cfg, on_change):
        self.theme = theme; self.cfg = cfg; self.on_change = on_change
        self.tree = ttk.Treeview(master, columns=("pid","arr","burst","prio","rem"), show="headings", height=5)
        for c, h in [("pid","PID"),("arr","Arr."),("burst","Burst"),("prio","Prio."),("rem","Rem.")]:
            self.tree.heading(c, text=h); self.tree.column(c, width=50, anchor="center", stretch=True)
        style_table(self.tree, theme)
        self.tree.bind("<Double-1>", self._on_edit)
        self._edit_entry = None

    def pack(self, **kw): self.tree.pack(**kw)
    def grid(self, **kw): self.tree.grid(**kw)

    def set_processes(self, procs):
        self._procs = procs
        for r in self.tree.get_children(): self.tree.delete(r)
        for i, p in enumerate(procs):
            self.tree.insert("", "end", iid=p.pid, values=(p.pid, p.arrival, p.burst, p.priority, f"{p.remaining}/{p.burst}"))

    def _on_edit(self, event):
        col = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        if not item or col in ("#0", "#5"): return
        idx = int(col.replace("#", "")) - 1
        keys = ["pid", "arrival", "burst", "priority"]
        key = keys[idx]
        x, y, w, h = self.tree.bbox(item, col)
        entry = ctk.CTkEntry(self.tree, width=w, height=h, font=("Consolas", 10), justify="center")
        entry.place(x=x, y=y)
        entry.insert(0, self.tree.set(item, col))
        entry.focus(); entry.select_range(0, "end")

        def confirm(ev=None):
            val = entry.get(); entry.destroy()
            for p in self._procs:
                if p.pid == item:
                    try:
                        if key == "pid":
                            old = item; p.pid = val
                            self.tree.item(old, iid=val, values=(val, p.arrival, p.burst, p.priority, f"{p.remaining}/{p.burst}"))
                        else:
                            if key == "arrival": p.arrival = int(val)
                            elif key == "burst": p.burst = int(val); p.remaining = p.burst
                            elif key == "priority": p.priority = int(val)
                            self.tree.set(item, col, val)
                            self.tree.set(item, "rem", f"{p.remaining}/{p.burst}")
                    except: pass
                    break
            self.on_change()

        def cancel(ev=None): entry.destroy()
        entry.bind("<Return>", confirm)
        entry.bind("<Escape>", cancel)
        entry.bind("<FocusOut>", confirm)
