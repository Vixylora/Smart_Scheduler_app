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
    def __init__(self, master, theme, cfg, on_change, on_select=None):
        self.theme = theme; self.cfg = cfg; self.on_change = on_change; self.on_select = on_select
        self.tree = ttk.Treeview(master, columns=("pid","arr","burst","prio","rem"), show="headings", height=5)
        for c, h in [("pid","PID"),("arr","Arr."),("burst","Burst"),("prio","Prio."),("rem","Rem.")]:
            self.tree.heading(c, text=h); self.tree.column(c, width=50, anchor="center", stretch=True)
        style_table(self.tree, theme)
        self.tree.bind("<ButtonRelease-1>", self._on_select)
        self._procs = []

    def pack(self, **kw): self.tree.pack(**kw)
    def grid(self, **kw): self.tree.grid(**kw)

    def set_processes(self, procs):
        self._procs = procs
        for r in self.tree.get_children(): self.tree.delete(r)
        for i, p in enumerate(procs):
            self.tree.insert("", "end", iid=p.pid, values=(p.pid, p.arrival, p.burst, p.priority, f"{p.remaining}/{p.burst}"))

    def _on_select(self, event):
        item = self.tree.identify_row(event.y)
        if item and self.on_select:
            self.on_select(item)
