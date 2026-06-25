import customtkinter as ctk
from tkinter import ttk, Menu, filedialog, messagebox
from core.process import Process
from core.engine import SimulationEngine
from ui.gantt_widget import GanttWidget
from ui.process_table import ProcessTableWidget, style_table
from persistence.session import save_session, load_session
from persistence.io import import_json, export_json, import_csv, export_csv

def _create_sample():
    return [Process('P1',0,5,2), Process('P2',1,3,1), Process('P3',2,8,4), Process('P4',3,6,3)]

class MainWindow(ctk.CTk):
    def __init__(self, cfg, theme):
        super().__init__()
        self.cfg = cfg; self.theme = theme
        self.title("Smart Scheduler - CPU Scheduling Simulator")
        w = cfg['ui']['window']['width']; h = cfg['ui']['window']['height']
        self.geometry(f"{w}x{h}")
        self.configure(fg_color=theme.bg)
        self.engine = SimulationEngine(cfg)
        ses = load_session()
        self.processes = _create_sample()
        self.algorithm = ses.get('algorithm', cfg['algorithms']['defaults'].get('algorithm', 'Priority'))
        self.quantum = ses.get('quantum', cfg['algorithms']['defaults']['quantum'])
        self.prio_mode = ses.get('priority_mode', cfg['algorithms']['defaults']['priority_mode'])
        self.simulating = False; self.cursor = 0
        self._build_menu()
        self._build_ui()
        self._refresh()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_menu(self):
        mb = Menu(self, bg=self.theme.panel, fg=self.theme.text, activebackground=self.theme.accent, activeforeground="#000", font=("Segoe UI", 9))

        mb.add_command(label="Add Process", command=self._add)
        mb.add_command(label="Delete Process", command=self._delete)

        load_menu = Menu(mb, tearoff=0, bg=self.theme.panel, fg=self.theme.text, activebackground=self.theme.accent, activeforeground="#000", font=("Segoe UI", 9))
        load_menu.add_command(label="Load JSON...", command=self._import_json)
        load_menu.add_command(label="Load CSV...", command=self._import_csv)
        mb.add_cascade(label="Load File", menu=load_menu)

        algo_menu = Menu(mb, tearoff=0, bg=self.theme.panel, fg=self.theme.text, activebackground=self.theme.accent, activeforeground="#000", font=("Segoe UI", 9))
        for a in ["FCFS", "SJF", "Round Robin", "Priority"]:
            algo_menu.add_command(label=a, command=lambda alg=a: (self.algo_cb.set(alg), self._on_algo(None)))
        mb.add_cascade(label="Select Algorithm", menu=algo_menu)

        mb.add_command(label="Start Simulation", command=self._play)

        export_menu = Menu(mb, tearoff=0, bg=self.theme.panel, fg=self.theme.text, activebackground=self.theme.accent, activeforeground="#000", font=("Segoe UI", 9))
        export_menu.add_command(label="Export Processes JSON...", command=self._export_json)
        export_menu.add_command(label="Export Processes CSV...", command=self._export_csv)
        export_menu.add_separator()
        export_menu.add_command(label="Export Comparison CSV...", command=self._export_comp_csv)
        mb.add_cascade(label="Export", menu=export_menu)

        mb.add_command(label="Exit", command=self._on_close)
        self.config(menu=mb)

    def _import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files","*.json")], title="Import Processes from JSON")
        if not path: return
        try:
            self.processes = import_json(path)
            self.engine.invalidate(); self._on_proc_change()
            messagebox.showinfo("Imported", f"Loaded {len(self.processes)} processes from {path}")
        except Exception as e: messagebox.showerror("Import Error", str(e))

    def _import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")], title="Import Processes from CSV")
        if not path: return
        try:
            self.processes = import_csv(path)
            self.engine.invalidate(); self._on_proc_change()
            messagebox.showinfo("Imported", f"Loaded {len(self.processes)} processes from {path}")
        except Exception as e: messagebox.showerror("Import Error", str(e))

    def _export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")], title="Export Processes to JSON")
        if not path: return
        try:
            export_json(self.processes, path)
            messagebox.showinfo("Exported", f"Saved {len(self.processes)} processes to {path}")
        except Exception as e: messagebox.showerror("Export Error", str(e))

    def _export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Export Processes to CSV")
        if not path: return
        try:
            export_csv(self.processes, path)
            messagebox.showinfo("Exported", f"Saved {len(self.processes)} processes to {path}")
        except Exception as e: messagebox.showerror("Export Error", str(e))

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(self, text="Smart Scheduler", font=("Segoe UI", 16, "bold"), text_color=self.theme.accent, anchor="w")
        self.title_lbl.grid(row=0, column=0, pady=(8,4), sticky="w", padx=12)

        self.gantt = GanttWidget(self, self.theme, self.cfg)
        self.gantt.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0,4))

        tables_frame = ctk.CTkFrame(self, fg_color="transparent")
        tables_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=4)
        tables_frame.grid_columnconfigure(0, weight=2)
        tables_frame.grid_columnconfigure(1, weight=1)
        tables_frame.grid_columnconfigure(2, weight=2)
        tables_frame.grid_rowconfigure(0, weight=1)

        proc_frame = ctk.CTkFrame(tables_frame, fg_color=self.theme.panel, corner_radius=8)
        proc_frame.grid(row=0, column=0, sticky="nsew", padx=(0,4))
        ctk.CTkLabel(proc_frame, text="Processes", font=("Segoe UI", 10, "bold"), text_color=self.theme.accent).pack(anchor="w", pady=(6,2), padx=8)
        self.proc_w = ProcessTableWidget(proc_frame, self.theme, self.cfg, self._on_proc_change)
        self.proc_w.pack(fill="both", expand=True, padx=4, pady=(0,4))

        stats_frame = ctk.CTkFrame(tables_frame, fg_color=self.theme.panel, corner_radius=8)
        stats_frame.grid(row=0, column=1, sticky="nsew", padx=4)
        ctk.CTkLabel(stats_frame, text="Statistics", font=("Segoe UI", 10, "bold"), text_color=self.theme.accent).pack(anchor="w", pady=(6,2), padx=8)
        self.stats_t = ttk.Treeview(stats_frame, columns=("pid","w","t","r","c"), show="headings", height=5)
        for c, h in [("pid","PID"),("w","Wait"),("t","Turn"),("r","Resp"),("c","Compl")]:
            self.stats_t.heading(c, text=h); self.stats_t.column(c, width=50, anchor="center", stretch=True)
        style_table(self.stats_t, self.theme)
        self.stats_t.pack(fill="both", expand=True, padx=4, pady=(0,4))

        comp_frame = ctk.CTkFrame(tables_frame, fg_color=self.theme.panel, corner_radius=8)
        comp_frame.grid(row=0, column=2, sticky="nsew", padx=(4,0))
        ctk.CTkLabel(comp_frame, text="Comparison", font=("Segoe UI", 10, "bold"), text_color=self.theme.accent).pack(anchor="w", pady=(6,2), padx=8)
        self.comp_t = ttk.Treeview(comp_frame, columns=("s","a","w","t","r","c","sc"), show="headings", height=5)
        cols = [("s","★",20),("a","Algorithm",75),("w","Wait",45),("t","Turn",45),("r","Resp",45),("c","CPU%",42),("sc","Score",48)]
        for c, h, w in cols:
            self.comp_t.heading(c, text=h); self.comp_t.column(c, width=w, anchor="center", stretch=True)
        style_table(self.comp_t, self.theme)
        self.comp_t.pack(fill="both", expand=True, padx=4, pady=(0,4))

        ctrl_frame = ctk.CTkFrame(self, fg_color=self.theme.panel, corner_radius=8)
        ctrl_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=4)

        ctk.CTkLabel(ctrl_frame, text="Controls", font=("Segoe UI", 11, "bold"), text_color=self.theme.accent).pack(anchor="w", pady=(6,2), padx=8)

        r1 = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        r1.pack(fill="x", padx=8, pady=(0,4))
        ctk.CTkLabel(r1, text="Algorithm:", font=("Segoe UI", 10)).pack(side="left")
        self.algo_cb = ctk.CTkComboBox(r1, values=["FCFS","SJF","Round Robin","Priority"], command=self._on_algo, width=130, state="readonly")
        self.algo_cb.set(self.algorithm); self.algo_cb.pack(side="left", padx=6)
        ctk.CTkLabel(r1, text="Quantum:", font=("Segoe UI", 10)).pack(side="left", padx=(12,0))
        self.quantum_entry = ctk.CTkEntry(r1, width=50, font=("Consolas", 10), justify="center")
        self.quantum_entry.pack(side="left", padx=4)
        self.quantum_entry.insert(0, str(self.quantum))
        self.quantum_entry.bind("<Return>", lambda _: self._on_quantum_change())
        ctk.CTkLabel(r1, text="Priority:", font=("Segoe UI", 10)).pack(side="left", padx=(12,0))
        self.prio_seg = ctk.CTkSegmentedButton(r1, values=["Preemptive","Non-preemptive"], command=self._on_prio_mode_change, width=180)
        self.prio_seg.pack(side="left", padx=4)
        self.prio_seg.set(self.prio_mode)
        self.stat_lbl = ctk.CTkLabel(r1, text="● STOPPED", font=("Segoe UI", 10), text_color=self.theme.warn)
        self.stat_lbl.pack(side="right", padx=6)

        r2 = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        r2.pack(fill="x", padx=8, pady=(0,6))
        self.play_btn = ctk.CTkButton(r2, text="▶ Play", width=80, command=self._play, fg_color=self.theme.accent, hover_color="#00B8D4", text_color="#000")
        self.play_btn.pack(side="left", padx=2)
        ctk.CTkButton(r2, text="⏭ Step", width=70, command=self._step, fg_color=self.theme.panel, border_color=self.theme.accent, border_width=1).pack(side="left", padx=2)
        ctk.CTkButton(r2, text="↺ Reset", width=70, command=self._reset, fg_color=self.theme.panel, border_color=self.theme.accent, border_width=1).pack(side="left", padx=2)
        ctk.CTkButton(r2, text="+ Add", width=60, command=self._add, fg_color=self.theme.panel, border_color=self.theme.success, border_width=1).pack(side="left", padx=2)
        ctk.CTkButton(r2, text="− Del", width=60, command=self._delete, fg_color=self.theme.panel, border_color=self.theme.danger, border_width=1, text_color=self.theme.danger).pack(side="left", padx=2)
        ctk.CTkButton(r2, text="Export CSV", width=90, command=self._export_comp_csv, fg_color=self.theme.panel, border_color=self.theme.accent, border_width=1).pack(side="right", padx=2)

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=4, column=0, sticky="nsew", padx=8, pady=(4,8))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        met = ctk.CTkFrame(bottom, fg_color=self.theme.panel, corner_radius=8)
        met.grid(row=0, column=0, sticky="nsew", padx=(0,4))
        ctk.CTkLabel(met, text="Metrics", font=("Segoe UI", 11, "bold"), text_color=self.theme.accent).pack(anchor="w", pady=(6,4), padx=8)
        self.met = {}
        for lbl in ["Avg Waiting:","Avg Turnaround:","Avg Response:","Throughput:","CPU Util:","Ctx Switches:"]:
            r = ctk.CTkFrame(met, fg_color="transparent"); r.pack(fill="x", padx=8, pady=1)
            ctk.CTkLabel(r, text=lbl, font=("Segoe UI", 10), width=110, anchor="w").pack(side="left")
            v = ctk.CTkLabel(r, text="—", font=("Consolas", 10), text_color="#fff"); v.pack(side="right")
            self.met[lbl] = v

        adv = ctk.CTkFrame(bottom, fg_color=self.theme.panel, corner_radius=8)
        adv.grid(row=0, column=1, sticky="nsew", padx=(4,0))
        ctk.CTkLabel(adv, text="Advisor", font=("Segoe UI", 11, "bold"), text_color=self.theme.accent).pack(anchor="w", pady=(6,4), padx=8)
        self.adv_algo = ctk.CTkLabel(adv, text="", font=("Segoe UI", 10, "bold"), text_color=self.theme.accent, wraplength=350, justify="left")
        self.adv_algo.pack(anchor="w", padx=8)
        self.adv_why = ctk.CTkLabel(adv, text="", font=("Segoe UI", 10), text_color="#ccc", wraplength=350, justify="left")
        self.adv_why.pack(anchor="w", padx=8, pady=(0,6))

    def _on_algo(self, _): self.algorithm = self.algo_cb.get(); self._refresh()
    def _on_proc_change(self): self._refresh()

    def _on_quantum_change(self):
        try:
            self.quantum = max(1, int(self.quantum_entry.get()))
        except ValueError:
            self.quantum = self.cfg['algorithms']['defaults']['quantum']
            self.quantum_entry.delete(0, "end")
            self.quantum_entry.insert(0, str(self.quantum))
        self.engine.invalidate(); self._refresh()

    def _on_prio_mode_change(self, val):
        self.prio_mode = val
        self.engine.invalidate(); self._refresh()

    def _play(self):
        self.simulating = not self.simulating
        self.play_btn.configure(text="⏸ Pause" if self.simulating else "▶ Play", fg_color=self.theme.danger if self.simulating else self.theme.accent)
        if self.simulating: self.after(self.engine.auto_tune_interval(self.processes), self._tick)
        self._refresh()

    def _step(self): self.cursor += 1; self._refresh()
    def _reset(self):
        self.simulating = False; self.play_btn.configure(text="▶ Play", fg_color=self.theme.accent); self.cursor = 0
        for p in self.processes: p.remaining = p.burst; p.waiting = 0; p.turnaround = 0; p.response = 0; p.completion = 0
        self.engine.invalidate(); self._refresh()

    def _add(self):
        n = len(self.processes) + 1; self.processes.append(Process(f"P{n}", 0, 1, 1))
        self.engine.invalidate(); self._refresh()

    def _delete(self):
        if len(self.processes) > 1: self.processes.pop(); self.engine.invalidate(); self._refresh()

    def _tick(self):
        if not self.simulating: return
        self.cursor += 1; self._refresh()
        s = self.engine.simulate(self.processes, self.algorithm, self.quantum, self.prio_mode)
        total = s.get('total_time', 0)
        if self.cursor >= total:
            self.simulating = False; self.play_btn.configure(text="▶ Play", fg_color=self.theme.accent); self._refresh()
        else:
            self.after(self.engine.auto_tune_interval(self.processes), self._tick)

    def _refresh(self):
        self.engine.invalidate()
        s = self.engine.simulate(self.processes, self.algorithm, self.quantum, self.prio_mode)
        comp = self.engine.compare(self.processes)
        rec = self.engine.recommend(self.processes)

        if s and s.get("timeline"):
            for p in self.processes:
                consumed = 0
                for seg in s["timeline"]:
                    if seg["pid"] == p.pid and seg["start"] < self.cursor:
                        seg_end = min(seg["end"], self.cursor)
                        consumed += seg_end - seg["start"]
                p.remaining = max(0, p.burst - int(consumed))

        self.proc_w.set_processes(self.processes)
        self._update_metrics(s)
        self._update_advisor(rec, comp[0]["algorithm"] if comp else None)
        self.gantt.set_data(s.get("timeline", []) if s else [], self.cursor)
        self._update_stats(s)
        self._update_comp(comp)
        self.stat_lbl.configure(text=f"● {'RUNNING' if self.simulating else 'STOPPED'}", text_color=self.theme.warn if self.simulating else self.theme.accent)

    def _clear(self, t): [t.delete(r) for r in t.get_children()]

    def _update_metrics(self, s):
        if not s: return
        vals = [f"{s['averages']['waiting']:.2f}s", f"{s['averages']['turnaround']:.2f}s", f"{s['averages']['response']:.2f}s",
                f"{s['throughput']:.2f}/s", f"{s['cpu_utilization']:.1f}%", str(s['context_switches'])]
        for lbl, v in zip(self.met.keys(), vals): self.met[lbl].configure(text=v)

    def _update_advisor(self, r, comp_best=None):
        if not r: return
        label = f"→ {r['algorithm']}"
        text = r['reason']
        if comp_best and comp_best != r['algorithm']:
            text += f"\n\nNote: comparison shows {comp_best} scores better despite this recommendation"
        self.adv_algo.configure(text=label)
        self.adv_why.configure(text=text)

    def _update_stats(self, s):
        self._clear(self.stats_t)
        if not s: return
        for st in s['stats']:
            self.stats_t.insert("", "end", values=(st.pid, st.waiting, st.turnaround, st.response, st.completion))

    def _update_comp(self, comp):
        self._clear(self.comp_t)
        if not comp: return
        best = comp[0]["score"]
        for e in comp:
            r = e["result"]
            star = "★" if e["score"] == best else ""
            sel = " #" if e["algorithm"] == self.algorithm else ""
            self.comp_t.insert("", "end", values=(star, e["algorithm"]+sel,
                f"{r['averages']['waiting']:.2f}", f"{r['averages']['turnaround']:.2f}",
                f"{r['averages']['response']:.2f}", f"{r['cpu_utilization']:.1f}",
                f"{e['score']:.2f}"))

    def _export_comp_csv(self):
        comp = self.engine.compare(self.processes)
        if not comp: return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Export Comparison to CSV")
        if not path: return
        import csv
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(["Algorithm","AvgWait","AvgTurnaround","AvgResponse","CPU%","ContextSwitches","Score","FairnessPenalty"])
            for e in comp:
                r = e["result"]
                w.writerow([e["algorithm"], f"{r['averages']['waiting']:.2f}", f"{r['averages']['turnaround']:.2f}",
                            f"{r['averages']['response']:.2f}", f"{r['cpu_utilization']:.1f}",
                            r['context_switches'], f"{e['score']:.2f}", f"{e['fairness_penalty']:.2f}"])
        messagebox.showinfo("Exported", f"Comparison saved to {path}")

    def _on_close(self):
        if self.simulating: self.simulating = False
        save_session({'algorithm': self.algorithm, 'quantum': self.quantum, 'priority_mode': self.prio_mode})
        self.destroy()
