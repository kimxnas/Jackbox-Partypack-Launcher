import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
from PIL import Image, ImageTk
import os
import re
import sys
from pathlib import Path

def run(settings, save_settings_fn, resource_path_fn, game_paths, restart_args,
        current_version="1.0.0", github_repo=""):
    image_cache = {}

    root = tk.Tk()
    root.title("kimxnas Jackbox Pack Launcher :D")
    root.resizable(False, False)

    try:
        root.iconbitmap(resource_path_fn('icon.ico'))
    except Exception:
        pass

    try:
        banner_img = Image.open(resource_path_fn("1111111111.png")).resize((580, 80), Image.Resampling.LANCZOS)
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

        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            image_path = Path(resource_path_fn("game_images")) / f"{safe_name}{ext}"
            if image_path.exists():
                img = Image.open(image_path).resize((550, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                image_cache[safe_name] = photo
                game_image_label.configure(image=photo)
                game_image_label.image = photo
                return

        game_image_label.configure(image=None)
        game_image_label.image = None

    frame = tk.Frame(root)
    frame.pack(pady=10)

    selected_game = tk.StringVar(value=list(game_paths.keys())[0])
    selected_game.trace_add("write", update_game_image)

    ttk.Combobox(
        frame, textvariable=selected_game,
        values=list(game_paths.keys()), width=40, state="readonly"
    ).grid(row=0, column=0, padx=10)

    tk.Button(frame, text="Play!", command=lambda: launch_game(), width=10).grid(row=0, column=1, padx=(0, 10))

    close_var = tk.BooleanVar(value=settings.get("close_after_launch", False))
    prompt_var = tk.BooleanVar(value=settings.get("show_launch_prompt", True))

    def on_check():
        settings["close_after_launch"] = close_var.get()
        settings["show_launch_prompt"] = prompt_var.get()
        save_settings_fn(settings)

    options_frame = tk.Frame(frame)
    options_frame.grid(row=0, column=2, sticky="w")
    small_font = ("Segoe UI", 8)

    tk.Checkbutton(options_frame, text="Close launcher after start", variable=close_var, command=on_check, font=small_font, padx=2, pady=0).pack(anchor="w")
    tk.Checkbutton(options_frame, text="Show launch confirmation", variable=prompt_var, command=on_check, font=small_font, padx=2, pady=0).pack(anchor="w")

    tk.Button(frame, text="⚙", command=lambda: open_settings(), width=3, font=("Segoe UI", 10)).grid(row=0, column=3, padx=(0, 6))

    def open_settings():
        win = tk.Toplevel(root)
        win.title("Settings")
        win.resizable(False, False)
        win.grab_set()

        try:
            win.iconbitmap(resource_path_fn('icon.ico'))
        except Exception:
            pass

        style_frame = tk.LabelFrame(win, text="UI Style", font=("Segoe UI", 9), padx=8, pady=6)
        style_frame.pack(padx=16, pady=(12, 0), fill="x")

        style_var = tk.StringVar(value=settings.get("ui_theme", "classic"))
        tk.Radiobutton(style_frame, text="Classic", variable=style_var, value="classic", font=("Segoe UI", 9)).pack(side="left")
        tk.Radiobutton(style_frame, text="Modern", variable=style_var, value="modern", font=("Segoe UI", 9)).pack(side="left", padx=(12, 0))

        header_frame = tk.Frame(win)
        header_frame.pack(padx=16, pady=(10, 0), fill="x")
        tk.Label(header_frame, text="Set the path to each game's .exe file.", font=("Segoe UI", 9), fg="gray").pack(side="left")

        entries = {}

        def auto_detect():
            folder = filedialog.askdirectory(title="Select folder to search for Jackbox games", parent=win)
            if not folder:
                return
            name_to_game = {(n + ".exe").lower(): n for n in game_paths}
            found = {}
            for dirpath, _, filenames in os.walk(folder):
                for fname in filenames:
                    key = fname.lower()
                    if key in name_to_game and key not in found:
                        found[name_to_game[key]] = os.path.join(dirpath, fname)
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

        tk.Button(header_frame, text="Auto-detect from folder…", command=auto_detect, font=("Segoe UI", 9)).pack(side="right")

        container = tk.Frame(win)
        container.pack(padx=16, pady=4)

        for i, game_name in enumerate(game_paths):
            tk.Label(container, text=game_name, anchor="w", width=28, font=("Segoe UI", 9)).grid(row=i, column=0, sticky="w", pady=3)
            var = tk.StringVar(value=game_paths.get(game_name, ""))
            tk.Entry(container, textvariable=var, width=42, font=("Segoe UI", 9)).grid(row=i, column=1, padx=6)

            def browse(v=var, n=game_name):
                path = filedialog.askopenfilename(
                    title=f"Select exe for {n}",
                    filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
                    initialdir=str(Path(v.get()).parent) if Path(v.get()).parent.exists() else "C:\\",
                    parent=win,
                )
                if path:
                    v.set(path)

            tk.Button(container, text="Browse…", command=browse, font=("Segoe UI", 9)).grid(row=i, column=2)
            entries[game_name] = var

        def save_all():
            for name, var in entries.items():
                game_paths[name] = var.get()
            settings["game_paths"] = dict(game_paths)
            new_theme = style_var.get()
            theme_changed = new_theme != settings.get("ui_theme", "classic")
            settings["ui_theme"] = new_theme
            save_settings_fn(settings)
            win.destroy()
            if theme_changed:
                # DETACHED_PROCESS (0x00000008) — escapes Nuitka's Job Object
                # so the new instance survives the parent closing
                subprocess.Popen(restart_args, creationflags=0x00000008)
                root.destroy()
            else:
                messagebox.showinfo("Saved", "Settings saved!", parent=root)

        tk.Button(win, text="Save", command=save_all, width=12, font=("Segoe UI", 10)).pack(pady=(10, 12))

    def launch_game():
        game_name = selected_game.get()
        game_path = Path(game_paths[game_name])
        if not game_path.is_file():
            messagebox.showerror("Error", f"Game executable not found:\n{game_path}\n\nSet the correct path in ⚙ Settings.")
            return
        try:
            subprocess.Popen([str(game_path)], cwd=str(game_path.parent))
            if prompt_var.get():
                messagebox.showinfo("Launching", f"Launching {game_name}!")
            if close_var.get():
                root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch:\n{e}")

    update_game_image()
    root.mainloop()
