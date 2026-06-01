import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import webbrowser
import urllib.request
import json
from PIL import Image, ImageTk
import os
import sys
from pathlib import Path

from shared import (
    sanitize_name, validate_exe_path, validate_image_path,
    auto_detect_games, track_recent, track_stats,
    get_banner_path, get_top_stats, get_last_played,
    detect_steam_jackbox, export_settings, import_settings,
    is_autostart_enabled, set_autostart, version_tuple,
)


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
        banner_src = get_banner_path(settings, resource_path_fn("1111111111.png"))
        banner_img = Image.open(banner_src).resize((580, 80), Image.Resampling.LANCZOS)
        banner_photo = ImageTk.PhotoImage(banner_img)
        tk.Label(root, image=banner_photo).pack(pady=5)
    except Exception:
        pass

    game_image_label = tk.Label(root)
    game_image_label.pack()

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
        values=list(game_paths.keys()), width=38, state="readonly"
    ).grid(row=0, column=0, padx=10)

    tk.Button(frame, text="Play!", command=lambda: launch_game(), width=10).grid(row=0, column=1, padx=(0, 6))

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

    # Last played indicator under the main row
    last_played_var = tk.StringVar(value="")
    tk.Label(root, textvariable=last_played_var, font=("Segoe UI", 8), fg="gray").pack(pady=(0, 4))

    def update_last_played(*_):
        pack = selected_game.get()
        rel = get_last_played(settings, pack)
        last_played_var.set(f"Last played {rel}" if rel else "")

    selected_game.trace_add("write", update_last_played)

    # ── Settings dialog (tabbed) ────────────────────────────────────
    def open_settings():
        win = tk.Toplevel(root)
        win.title("Settings")
        win.geometry("640x540")
        win.resizable(False, False)
        win.grab_set()
        try:
            win.iconbitmap(resource_path_fn('icon.ico'))
        except Exception:
            pass

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        tab_general = ttk.Frame(notebook)
        tab_paths   = ttk.Frame(notebook)
        tab_about   = ttk.Frame(notebook)
        notebook.add(tab_general, text=" General ")
        notebook.add(tab_paths,   text=" Game Paths ")
        notebook.add(tab_about,   text=" About ")

        # ── GENERAL TAB ─────────────────────────────────────────────
        # UI Style
        ui_lf = tk.LabelFrame(tab_general, text="UI Style", padx=10, pady=6, font=("Segoe UI", 9, "bold"))
        ui_lf.pack(fill="x", padx=8, pady=(8, 4))
        style_var = tk.StringVar(value=settings.get("ui_theme", "classic"))
        tk.Radiobutton(ui_lf, text="Classic", variable=style_var, value="classic", font=("Segoe UI", 9)).pack(side="left")
        tk.Radiobutton(ui_lf, text="Modern", variable=style_var, value="modern", font=("Segoe UI", 9)).pack(side="left", padx=(12, 0))

        # Launch Behavior
        beh_lf = tk.LabelFrame(tab_general, text="Launch Behavior", padx=10, pady=6, font=("Segoe UI", 9, "bold"))
        beh_lf.pack(fill="x", padx=8, pady=4)
        close_set_var      = tk.BooleanVar(value=settings.get("close_after_launch", False))
        prompt_set_var     = tk.BooleanVar(value=settings.get("show_launch_prompt", True))
        autostart_set_var  = tk.BooleanVar(value=is_autostart_enabled())
        tk.Checkbutton(beh_lf, text="Close launcher after launch", variable=close_set_var, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Checkbutton(beh_lf, text="Show launch confirmation",    variable=prompt_set_var, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Checkbutton(beh_lf, text="Start with Windows",          variable=autostart_set_var, font=("Segoe UI", 9)).pack(anchor="w")

        # Custom Banner
        banner_lf = tk.LabelFrame(tab_general, text="Custom Banner", padx=10, pady=6, font=("Segoe UI", 9, "bold"))
        banner_lf.pack(fill="x", padx=8, pady=4)
        tk.Label(banner_lf, text="Replaces the default header banner. PNG or JPG, under 10 MB.",
                 font=("Segoe UI", 8), fg="gray").pack(anchor="w")
        banner_var = tk.StringVar(value=settings.get("custom_banner", "") or "(default)")
        banner_row = tk.Frame(banner_lf)
        banner_row.pack(fill="x", pady=4)
        tk.Entry(banner_row, textvariable=banner_var, font=("Segoe UI", 9), state="readonly", width=58).pack(side="left", padx=(0, 4))

        def pick_banner():
            path = filedialog.askopenfilename(
                title="Choose banner image",
                filetypes=[("Image", "*.png *.jpg *.jpeg"), ("All files", "*.*")],
                parent=win,
            )
            if not path:
                return
            ok, reason = validate_image_path(path)
            if not ok:
                messagebox.showerror("Invalid image", reason, parent=win)
                return
            banner_var.set(path)

        tk.Button(banner_row, text="Choose…", command=pick_banner, font=("Segoe UI", 9)).pack(side="left", padx=2)
        tk.Button(banner_row, text="Reset",   command=lambda: banner_var.set("(default)"), font=("Segoe UI", 9)).pack(side="left")

        # ── GAME PATHS TAB ──────────────────────────────────────────
        paths_top = tk.Frame(tab_paths)
        paths_top.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(paths_top, text="Configure each pack's .exe path",
                 font=("Segoe UI", 9), fg="gray").pack(side="left")

        entries = {}

        def auto_detect():
            folder = filedialog.askdirectory(title="Select games folder", parent=win)
            if not folder:
                return
            found = auto_detect_games(folder, game_paths)
            if not found:
                messagebox.showinfo("Auto-detect", "No Jackbox games found.", parent=win)
                return
            for game, path in found.items():
                entries[game].set(path)
            missed = [g for g in game_paths if g not in found]
            msg = f"Found {len(found)} game(s)."
            if missed:
                msg += f"\n\nNot found ({len(missed)}):\n" + "\n".join(f"  • {g}" for g in missed)
            messagebox.showinfo("Auto-detect", msg, parent=win)

        def steam_detect():
            found = detect_steam_jackbox(game_paths)
            if not found:
                messagebox.showinfo("Steam detect",
                    "No Jackbox packs found in your Steam library.", parent=win)
                return
            for game, path in found.items():
                entries[game].set(path)
            messagebox.showinfo("Steam detect",
                f"Found {len(found)} pack(s) via Steam.", parent=win)

        tk.Button(paths_top, text="Auto-detect folder…", command=auto_detect, font=("Segoe UI", 9)).pack(side="right", padx=2)
        tk.Button(paths_top, text="🎮 Detect from Steam", command=steam_detect, font=("Segoe UI", 9)).pack(side="right", padx=2)

        # Scrollable paths list
        canvas = tk.Canvas(tab_paths, borderwidth=0, highlightthickness=0, height=320)
        scrollbar = ttk.Scrollbar(tab_paths, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=4)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=4)

        for game_name in game_paths:
            row = tk.Frame(scroll_frame)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=game_name, anchor="w", width=28, font=("Segoe UI", 9)).pack(side="left", padx=4)
            var = tk.StringVar(value=game_paths.get(game_name, ""))
            tk.Entry(row, textvariable=var, width=42, font=("Segoe UI", 9)).pack(side="left", padx=4)

            def browse(v=var, n=game_name):
                path = filedialog.askopenfilename(
                    title=f"Select exe for {n}",
                    filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
                    initialdir=str(Path(v.get()).parent) if Path(v.get()).parent.exists() else "C:\\",
                    parent=win,
                )
                if path:
                    v.set(path)

            tk.Button(row, text="Browse…", command=browse, font=("Segoe UI", 9)).pack(side="left")
            entries[game_name] = var

        # ── ABOUT TAB ───────────────────────────────────────────────
        stats_lf = tk.LabelFrame(tab_about, text="Pack Stats", padx=10, pady=6, font=("Segoe UI", 9, "bold"))
        stats_lf.pack(fill="x", padx=8, pady=(8, 4))
        top = get_top_stats(settings, top_n=10)
        if not top:
            tk.Label(stats_lf, text="No launches yet — go play something!",
                     font=("Segoe UI", 9), fg="gray").pack(anchor="w", pady=4)
        else:
            for pack, count in top:
                short = pack.replace("The Jackbox Party Pack", "Pack")
                row = tk.Frame(stats_lf)
                row.pack(fill="x", pady=1)
                tk.Label(row, text=short, font=("Segoe UI", 9), anchor="w").pack(side="left")
                tk.Label(row, text=f"{count} launches", font=("Segoe UI", 9, "bold"), fg="#1e6091").pack(side="right")

        backup_lf = tk.LabelFrame(tab_about, text="Backup", padx=10, pady=6, font=("Segoe UI", 9, "bold"))
        backup_lf.pack(fill="x", padx=8, pady=4)

        def export_now():
            path = filedialog.asksaveasfilename(
                title="Export settings to…",
                defaultextension=".json",
                initialfile="jackbox-launcher-settings.json",
                filetypes=[("JSON", "*.json")],
                parent=win,
            )
            if not path:
                return
            ok, err = export_settings(settings, path)
            if ok:
                messagebox.showinfo("Exported", f"Settings exported to:\n{path}", parent=win)
            else:
                messagebox.showerror("Export failed", err, parent=win)

        def import_now():
            path = filedialog.askopenfilename(
                title="Import settings from…",
                filetypes=[("JSON", "*.json"), ("All files", "*.*")],
                parent=win,
            )
            if not path:
                return
            ok, data = import_settings(path)
            if not ok:
                messagebox.showerror("Import failed", str(data), parent=win)
                return
            if not messagebox.askyesno("Overwrite settings?",
                "This will replace your current settings and restart. Continue?",
                parent=win):
                return
            settings.clear()
            settings.update(data)
            save_settings_fn(settings)
            subprocess.Popen(restart_args, creationflags=0x00000008)
            root.destroy()

        bk_row = tk.Frame(backup_lf)
        bk_row.pack(fill="x")
        tk.Label(bk_row, text="Save/restore settings to/from a JSON file.",
                 font=("Segoe UI", 9), fg="gray").pack(side="left")
        tk.Button(bk_row, text="Import", command=import_now, font=("Segoe UI", 9), width=10).pack(side="right", padx=2)
        tk.Button(bk_row, text="Export", command=export_now, font=("Segoe UI", 9), width=10).pack(side="right", padx=2)

        # Version + update check
        ver_lf = tk.LabelFrame(tab_about, text="About", padx=10, pady=6, font=("Segoe UI", 9, "bold"))
        ver_lf.pack(fill="x", padx=8, pady=4)
        ver_row = tk.Frame(ver_lf)
        ver_row.pack(fill="x")
        tk.Label(ver_row, text=f"Version {current_version}", font=("Segoe UI", 9), fg="gray").pack(side="left")

        def manual_check():
            try:
                url = f"https://api.github.com/repos/{github_repo}/releases/latest"
                req = urllib.request.Request(url, headers={"User-Agent": "JackboxLauncher"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    data = json.loads(r.read())
                latest = data.get("tag_name", "").lstrip("v")
                if latest and version_tuple(latest) > version_tuple(current_version):
                    if messagebox.askyesno("Update Available",
                        f"v{latest} is available.\n\nOpen the download page?",
                        parent=win):
                        webbrowser.open(f"https://github.com/{github_repo}/releases/latest")
                else:
                    messagebox.showinfo("Up to date", f"You're on v{current_version}.", parent=win)
            except Exception as e:
                messagebox.showerror("Update check failed", str(e), parent=win)

        tk.Button(ver_row, text="Check for updates", command=manual_check, font=("Segoe UI", 9)).pack(side="right")

        # ── Save ────────────────────────────────────────────────────
        def save_all():
            for name, var in entries.items():
                game_paths[name] = var.get()
            settings["game_paths"] = dict(game_paths)
            new_theme = style_var.get()
            theme_changed = new_theme != settings.get("ui_theme", "classic")
            settings["ui_theme"] = new_theme
            settings["close_after_launch"] = close_set_var.get()
            settings["show_launch_prompt"] = prompt_set_var.get()
            banner_choice = banner_var.get()
            settings["custom_banner"] = "" if banner_choice == "(default)" else banner_choice
            set_autostart(autostart_set_var.get())
            save_settings_fn(settings)

            # Sync main UI checkboxes
            close_var.set(close_set_var.get())
            prompt_var.set(prompt_set_var.get())

            win.destroy()
            if theme_changed:
                subprocess.Popen(restart_args, creationflags=0x00000008)
                root.destroy()
            else:
                messagebox.showinfo("Saved", "Settings saved!", parent=root)

        tk.Button(win, text="Save", command=save_all, width=12, font=("Segoe UI", 10, "bold")).pack(pady=(6, 12))

    def launch_game():
        game_name = selected_game.get()
        path_str = game_paths.get(game_name, "")
        ok, reason = validate_exe_path(path_str)
        if not ok:
            messagebox.showerror("Error",
                f"Can't launch {game_name}:\n{reason}\n\nFix in ⚙ Settings.")
            return
        game_path = Path(path_str)
        try:
            subprocess.Popen([str(game_path)], cwd=str(game_path.parent), shell=False)
            track_recent(settings, save_settings_fn, game_name)
            track_stats(settings, save_settings_fn, game_name)
            update_last_played()
            if prompt_var.get():
                messagebox.showinfo("Launching", f"Launching {game_name}!")
            if close_var.get():
                root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch:\n{e}")

    update_game_image()
    update_last_played()
    root.mainloop()
