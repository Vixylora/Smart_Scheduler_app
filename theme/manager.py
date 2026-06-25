class Theme:
    def __init__(self, cfg):
        c = cfg['theme']['colors']
        self.bg = c['background']
        self.panel = c['panel']
        self.accent = c['accent']
        self.warn = c['warn']
        self.text = c['text']
        self.text_secondary = c['text_secondary']
        self.danger = c['danger']
        self.success = c['success']
        self.gantt_bar = c['gantt_bar']
        self.mode = cfg['theme'].get('mode', 'dark')

    def apply(self):
        import customtkinter as ctk
        ctk.set_appearance_mode(self.mode)
