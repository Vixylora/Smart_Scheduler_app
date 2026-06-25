import os, json
from pathlib import Path

SESSION_DIR = Path.home() / ".config" / "smart-scheduler"
SESSION_FILE = SESSION_DIR / "session.json"

def _ensure_dir():
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

def save_session(state):
    _ensure_dir()
    with open(SESSION_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_session():
    if SESSION_FILE.exists():
        with open(SESSION_FILE) as f:
            return json.load(f)
    return {}
