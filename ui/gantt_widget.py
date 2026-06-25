import tkinter as tk

class GanttWidget(tk.Canvas):
    def __init__(self, master, theme, cfg):
        super().__init__(master, bg=theme.bg, highlightthickness=0, height=cfg['ui']['gantt'].get('height', 150))
        self.theme = theme; self.cfg = cfg
        self.timeline = []; self.cursor = 0

    def set_data(self, timeline, cursor):
        self.timeline = timeline or []; self.cursor = cursor
        self.after(self.cfg['timing']['lazy_render_delay_ms'], self.redraw)

    def redraw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10: w = 600
        if h < 10: h = self.cfg['ui']['gantt'].get('height', 150)
        if not self.timeline:
            self.create_text(w//2, h//2, text="Run simulation to see timeline", fill=self.theme.text_secondary, font=("monospace", 10))
            return
        total = self.timeline[-1]["end"]
        if total <= 0: return
        pids = sorted(set(t["pid"] for t in self.timeline if t["pid"] != "Idle"))
        rows = len(pids)
        g = self.cfg['ui']['gantt']
        rh = min(g['row_height_max'], (h - 30) // max(rows, 1))
        lm = g['margin_left']; rm = g['margin_right']; cw = w - lm - rm
        colors = self.theme.gantt_bar
        for i, pid in enumerate(pids):
            y = 20 + i * rh
            self.create_text(5, y + rh//2, text=pid, anchor="w", fill=self.theme.text_secondary, font=("monospace", 9))
            bc = colors[i % len(colors)]
            for seg in self.timeline:
                if seg["pid"] != pid or seg["start"] >= self.cursor: continue
                x1 = lm + int(seg["start"] / total * cw)
                end_time = min(seg["end"], self.cursor)
                x2 = lm + int(end_time / total * cw)
                if x2 - x1 < 2: continue
                self.create_rectangle(x1, y+2, x2, y+rh-2, fill=bc, outline="")
                if x2 - x1 > 30:
                    tc = "black" if bc in ("#00E5FF", "#FFB300", "#00E676") else "white"
                    self.create_text((x1 + x2) // 2, y + rh // 2, text=pid, fill=tc, font=("monospace", 8, "bold"))
        end_t = int(total)
        for t in range(0, end_t + 1):
            x = lm + int(t / total * cw)
            self.create_line(x, 10, x, 20 + rows * rh + 4, fill="#444", width=1)
            self.create_text(x, 20 + rows * rh + 4, text=str(t), fill=self.theme.text_secondary, font=("monospace", 8))
        cx_x = lm + int(self.cursor / total * cw)
        self.create_line(cx_x, 8, cx_x, 20 + rows * rh + 4, fill=self.theme.warn, width=2)
        self.create_text(cx_x, 20 + rows * rh + 16, text=f"▲ t={self.cursor:.0f}", fill=self.theme.warn, font=("monospace", 9))
