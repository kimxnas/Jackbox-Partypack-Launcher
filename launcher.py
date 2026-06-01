import os
import sys
import json
import subprocess
from pathlib import Path

CURRENT_VERSION = "1.7.0"
GITHUB_REPO = "kimxnas/Jackbox-Partypack-Launcher"

def resource_path(relative_path):
    # PyInstaller uses _MEIPASS; Nuitka (standalone & onefile) puts data
    # next to the module so __file__'s dir works for both modes + dev.
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_data_dir():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "JackboxLauncher")
    os.makedirs(path, exist_ok=True)
    return path

SETTINGS_PATH = Path(get_data_dir()) / "launcher_settings.json"

DEFAULT_GAME_PATHS = {
    "The Jackbox Party Pack":    r"C:\Games\The Jackbox Party Pack Collection\1\The Jackbox Party Pack.exe",
    "The Jackbox Party Pack 2":  r"C:\Games\The Jackbox Party Pack Collection\2\The Jackbox Party Pack 2.exe",
    "The Jackbox Party Pack 3":  r"C:\Games\The Jackbox Party Pack Collection\3\The Jackbox Party Pack 3.exe",
    "The Jackbox Party Pack 4":  r"C:\Games\The Jackbox Party Pack Collection\4\The Jackbox Party Pack 4.exe",
    "The Jackbox Party Pack 5":  r"C:\Games\The Jackbox Party Pack Collection\5\The Jackbox Party Pack 5.exe",
    "The Jackbox Party Pack 6":  r"C:\Games\The Jackbox Party Pack Collection\6\The Jackbox Party Pack 6.exe",
    "The Jackbox Party Pack 7":  r"C:\Games\The Jackbox Party Pack Collection\7\The Jackbox Party Pack 7.exe",
    "The Jackbox Party Pack 8":  r"C:\Games\The Jackbox Party Pack Collection\8\The Jackbox Party Pack 8.exe",
    "The Jackbox Party Pack 9":  r"C:\Games\The Jackbox Party Pack Collection\9\The Jackbox Party Pack 9.exe",
    "The Jackbox Party Pack 10": r"C:\Games\The Jackbox Party Pack Collection\10\The.Jackbox.Party.Pack.10.v522\The Jackbox Party Pack 10.exe",
}

def load_settings():
    if SETTINGS_PATH.is_file():
        try:
            with open(SETTINGS_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Error", f"Failed to save settings:\n{e}")

if __name__ == "__main__":
    settings = load_settings()
    game_paths = {**DEFAULT_GAME_PATHS, **settings.get("game_paths", {})}
    theme = settings.get("ui_theme", "classic")

    # Use sys.argv[0] — it's the actual path Windows used to launch the process
    # (script path in dev mode, exe path when compiled)
    argv0 = os.path.abspath(sys.argv[0])
    if argv0.lower().endswith('.py'):
        restart_args = [sys.executable, argv0]
    else:
        restart_args = [argv0]

    if theme == "modern":
        from ui_modern import run
    else:
        from ui_classic import run

    run(settings, save_settings, resource_path, game_paths, restart_args,
        current_version=CURRENT_VERSION, github_repo=GITHUB_REPO)
