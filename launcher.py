import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
from PIL import Image, ImageTk
import os
import re
from pathlib import Path
import json
import sys

def resource_path(relative_path):
    """Get path to bundled resource (inside PyInstaller temp folder)."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_data_dir():
    """Writable directory next to the exe (not MEIPASS, which is temp/read-only)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

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
        messagebox.showerror("Error", f"Failed to save settings:\n{e}")

settings = load_settings()

# Merge saved game paths over defaults
game_paths = {**DEFAULT_GAME_PATHS, **settings.get("game_paths", {})}

image_cache = {}

# === Setup GUI ===
root = tk.Tk()
root.title("kimxnas Jackbox Pack Launcher :D")
root.resizable(False, False)

try:
    root.iconbitmap(resource_path('icon.ico'))
except Exception:
    pass

try:
    banner_img = Image.open(resource_path("kimxnas_banner.png")).resize((580, 80), Image.Resampling.LANCZOS)
    banner_photo = ImageTk.PhotoImage(banner_img)
    tk.Label(root, image=banner_photo).pack(pady=5)
except Exception:
    pass

game_image_label = tk.Label(root)
game_image_label.pack()

def sanitize_name(name):
    safe = name.replace(" ", "_")
    return re.sub(r'[^A-Za-z0-9_-]', '', safe)

def update_game_image(*args):
    game_name = selected_game.get()
    safe_name = sanitize_name(game_name)

    if safe_name in image_cache:
        photo = image_cache[safe_name]
        game_image_label.configure(image=photo)
        game_image_label.image = photo
        return

    for ext in [".webp", ".png", ".jpg", ".jpeg"]:
        image_path = Path(resource_path("game_images")) / f"{safe_name}{ext}"
        if image_path.exists():
            img = Image.open(image_path).resize((550, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            image_cache[safe_name] = photo
            game_image_label.configure(image=photo)
            game_image_label.image = photo
            return

    game_image_label.configure(image=None)
    game_image_label.image = None

# === Main controls frame ===
frame = tk.Frame(root)
frame.pack(pady=10)

selected_game = tk.StringVar()
selected_game.set(list(game_paths.keys())[0])
selected_game.trace_add("write", update_game_image)

dropdown = ttk.Combobox(frame, textvariable=selected_game, values=list(game_paths.keys()), width=40, state="readonly")
dropdown.grid(row=0, column=0, padx=10)

play_button = tk.Button(frame, text="Play!", command=lambda: launch_game(), width=10)
play_button.grid(row=0, column=1, padx=(0, 10))

close_after_launch_var = tk.BooleanVar(value=settings.get("close_after_launch", False))
show_launch_prompt_var = tk.BooleanVar(value=settings.get("show_launch_prompt", True))

def on_setting_change():
    settings["close_after_launch"] = close_after_launch_var.get()
    settings["show_launch_prompt"] = show_launch_prompt_var.get()
    save_settings(settings)

options_frame = tk.Frame(frame)
options_frame.grid(row=0, column=2, sticky="w")

small_font = ("Segoe UI", 8)

tk.Checkbutton(
    options_frame, text="Close launcher after start",
    variable=close_after_launch_var, command=on_setting_change,
    font=small_font, padx=2, pady=0,
).pack(anchor="w")

tk.Checkbutton(
    options_frame, text="Show launch confirmation",
    variable=show_launch_prompt_var, command=on_setting_change,
    font=small_font, padx=2, pady=0,
).pack(anchor="w")

# Settings gear button
tk.Button(frame, text="⚙", command=lambda: open_settings(), width=3, font=("Segoe UI", 10)).grid(row=0, column=3, padx=(0, 6))

# === Settings window ===
def open_settings():
    win = tk.Toplevel(root)
    win.title("Settings — Game Paths")
    win.resizable(False, False)
    win.grab_set()

    try:
        win.iconbitmap(resource_path('icon.ico'))
    except Exception:
        pass

    header_frame = tk.Frame(win)
    header_frame.pack(padx=16, pady=(10, 4), fill="x")

    tk.Label(header_frame, text="Set the path to each game's .exe file.", font=("Segoe UI", 9), fg="gray").pack(side="left")
    tk.Button(header_frame, text="Auto-detect from folder…", command=lambda: auto_detect(), font=("Segoe UI", 9)).pack(side="right")

    container = tk.Frame(win)
    container.pack(padx=16, pady=4)

    entries = {}
    for i, game_name in enumerate(game_paths):
        tk.Label(container, text=game_name, anchor="w", width=28, font=("Segoe UI", 9)).grid(row=i, column=0, sticky="w", pady=3)

        entry_var = tk.StringVar(value=game_paths.get(game_name, ""))
        entry = tk.Entry(container, textvariable=entry_var, width=42, font=("Segoe UI", 9))
        entry.grid(row=i, column=1, padx=6)

        def browse(var=entry_var, name=game_name):
            path = filedialog.askopenfilename(
                title=f"Select exe for {name}",
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
                initialdir=str(Path(var.get()).parent) if Path(var.get()).parent.exists() else "C:\\",
            )
            if path:
                var.set(path)

        tk.Button(container, text="Browse…", command=browse, font=("Segoe UI", 9)).grid(row=i, column=2)

        entries[game_name] = entry_var

    def auto_detect():
        folder = filedialog.askdirectory(title="Select folder to search for Jackbox games", parent=win)
        if not folder:
            return

        # Build a lookup: normalized exe name -> game name
        # e.g. "the jackbox party pack 2.exe" -> "The Jackbox Party Pack 2"
        name_to_game = {(name + ".exe").lower(): name for name in game_paths}

        found = {}
        for dirpath, _, filenames in os.walk(folder):
            for fname in filenames:
                key = fname.lower()
                if key in name_to_game:
                    game = name_to_game[key]
                    if game not in found:  # first match wins
                        found[game] = os.path.join(dirpath, fname)

        if not found:
            messagebox.showinfo("Auto-detect", "No Jackbox games found in that folder.", parent=win)
            return

        for game, path in found.items():
            entries[game].set(path)

        missed = [g for g in game_paths if g not in found]
        msg = f"Found {len(found)} game(s)."
        if missed:
            msg += f"\n\nNot found ({len(missed)}):\n" + "\n".join(f"  • {g}" for g in missed)
        messagebox.showinfo("Auto-detect", msg, parent=win)

    def save_paths():
        for name, var in entries.items():
            game_paths[name] = var.get()
        settings["game_paths"] = dict(game_paths)
        save_settings(settings)
        messagebox.showinfo("Saved", "Game paths saved!", parent=win)
        win.destroy()

    tk.Button(win, text="Save", command=save_paths, width=12, font=("Segoe UI", 10)).pack(pady=(10, 12))

# === Launch ===
def launch_game():
    game_name = selected_game.get()
    game_path = Path(game_paths[game_name])

    if not game_path.is_file():
        messagebox.showerror("Error", f"Game executable not found:\n{game_path}\n\nSet the correct path in ⚙ Settings.")
        return

    try:
        subprocess.Popen([str(game_path)], cwd=str(game_path.parent))
        if show_launch_prompt_var.get():
            messagebox.showinfo("Launching", f"Launching {game_name}!")
        if close_after_launch_var.get():
            root.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"Could not launch:\n{e}")

update_game_image()
root.mainloop()
