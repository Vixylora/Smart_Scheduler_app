#!/usr/bin/env python3
import sys, subprocess, logging
_missing = []
for pkg in ["customtkinter", "yaml"]:
    try: __import__(pkg.replace("-","_"))
    except ImportError: _missing.append(pkg)
if _missing:
    print(f"Missing: {_missing}. Install? [Y/n]: ", end="")
    if input().strip().lower() != "n":
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + _missing)
    else: sys.exit(0)
from pathlib import Path
from config.loader import load_config
from theme.manager import Theme
from ui.main_window import MainWindow

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    cfg_path = Path(__file__).parent / "config.yaml"
    cfg = load_config(str(cfg_path) if cfg_path.exists() else None)
    theme = Theme(cfg)
    theme.apply()
    app = MainWindow(cfg, theme)
    app.mainloop()

if __name__ == "__main__":
    main()
