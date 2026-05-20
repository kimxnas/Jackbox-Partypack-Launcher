import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import re
import sys
import subprocess
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG         = "#0D0920"
FRAME_BG   = "#1A0F38"
CARD_BG    = "#241554"
BORDER     = "#3D2070"
YELLOW     = "#FFE600"
YELLOW_H   = "#FFCC00"
PINK       = "#FF2D78"
PINK_H     = "#CC1060"
TEXT       = "#FFFFFF"
SUBTEXT    = "#C0A0E0"

def run(settings, save_settings_fn, resource_path_fn, game_paths, restart_args):
    image_cache = {}

    root = ctk.CTk()
    root.title("Jackbox Launcher")
    root.geometry("620x510")
    root.resizable(False, False)
    root.configure(fg_color=BG)

    try:
        root.iconbitmap(resource_path_fn('icon.ico'))
    except Exception:
        pass

    # ── Header ──────────────────────────────────────────────────────
    header = ctk.CTkFrame(root, fg_color=FRAME_BG, corner_radius=0, height=68)
    header.pack(fill="x")
    header.pack_propagate(False)

    ctk.CTkLabel(
        header, text="JACKBOX LAUNCHER",
        font=("Impact", 34), text_color=YELLOW,
    ).place(x=20, rely=0.5, anchor="w")

    ctk.CTkButton(
        header, text="⚙", width=42, height=42,
        fg_color=CARD_BG, hover_color=BORDER,
        font=("Segoe UI", 18), corner_radius=10,
        command=lambda: open_settings(),
    ).place(relx=1.0, x=-16, rely=0.5, anchor="e")

    # ── Game image ───────────────────────────────────────────────────
    img_outer = ctk.CTkFrame(root, fg_color=BORDER, corner_radius=14)
    img_outer.pack(padx=20, pady=(14, 0))

    img_label = ctk.CTkLabel(img_outer, text="", width=560, height=214)
    img_label.pack(padx=2, pady=2)

    def sanitize(name):
        return re.sub(r'[^A-Za-z0-9_-]', '', name.replace(" ", "_"))

    def update_image(*_):
        key = sanitize(selected_game.get())
        if key in image_cache:
            img_label.configure(image=image_cache[key])
            return
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            p = Path(resource_path_fn("game_images")) / f"{key}{ext}"
            if p.exists():
                pil = Image.open(p).resize((560, 214), Image.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(560, 214))
                image_cache[key] = ctk_img
                img_label.configure(image=ctk_img)
                return
        img_label.configure(image=None)

    # ── Dropdown ─────────────────────────────────────────────────────
    selected_game = ctk.StringVar(value=list(game_paths.keys())[0])
    selected_game.trace_add("write", update_image)

    ctk.CTkOptionMenu(
        root,
        variable=selected_game,
        values=list(game_paths.keys()),
        fg_color=CARD_BG,
        button_color=BORDER,
        button_hover_color=PINK,
        text_color=TEXT,
        font=("Segoe UI", 13),
        dropdown_fg_color=FRAME_BG,
        dropdown_text_color=TEXT,
        dropdown_hover_color=BORDER,
        dynamic_resizing=False,
        width=580,
        height=44,
        corner_radius=10,
    ).pack(pady=(12, 0))

    # ── Play button ───────────────────────────────────────────────────
    ctk.CTkButton(
        root,
        text="▶   PLAY!",
        font=("Segoe UI Black", 22),
        fg_color=YELLOW,
        hover_color=YELLOW_H,
        text_color="#0D0920",
        corner_radius=30,
        width=280,
        height=62,
        command=lambda: launch_game(),
    ).pack(pady=(12, 0))

    # ── Bottom checkboxes ─────────────────────────────────────────────
    bottom = ctk.CTkFrame(root, fg_color="transparent")
    bottom.pack(padx=30, pady=(10, 0), fill="x")

    close_var  = ctk.BooleanVar(value=settings.get("close_after_launch", False))
    prompt_var = ctk.BooleanVar(value=settings.get("show_launch_prompt", True))

    def on_check():
        settings["close_after_launch"] = close_var.get()
        settings["show_launch_prompt"] = prompt_var.get()
        save_settings_fn(settings)

    for text, var in [("Close after launch", close_var), ("Show confirmation", prompt_var)]:
        ctk.CTkCheckBox(
            bottom, text=text, variable=var, command=on_check,
            font=("Segoe UI", 11), text_color=SUBTEXT,
            fg_color=PINK, hover_color=PINK_H,
            checkmark_color=TEXT, border_color=BORDER,
        ).pack(side="left", padx=(0, 20))

    # ── Settings window ───────────────────────────────────────────────
    def open_settings():
        win = ctk.CTkToplevel(root)
        win.title("Settings")
        win.geometry("680x560")
        win.resizable(False, False)
        win.grab_set()
        win.configure(fg_color=BG)

        try:
            win.iconbitmap(resource_path_fn('icon.ico'))
        except Exception:
            pass

        # UI Style section
        style_card = ctk.CTkFrame(win, fg_color=FRAME_BG, corner_radius=12)
        style_card.pack(padx=16, pady=(14, 0), fill="x")

        ctk.CTkLabel(style_card, text="UI Style", font=("Segoe UI Black", 13), text_color=YELLOW).pack(anchor="w", padx=14, pady=(10, 4))

        style_var = ctk.StringVar(value=settings.get("ui_theme", "modern"))
        ctk.CTkSegmentedButton(
            style_card,
            values=["classic", "modern"],
            variable=style_var,
            fg_color=CARD_BG,
            selected_color=YELLOW,
            selected_hover_color=YELLOW_H,
            unselected_color=CARD_BG,
            unselected_hover_color=BORDER,
            text_color="#0D0920",
            font=("Segoe UI", 12),
        ).pack(padx=14, pady=(0, 12), anchor="w")

        # Game paths section
        paths_card = ctk.CTkFrame(win, fg_color=FRAME_BG, corner_radius=12)
        paths_card.pack(padx=16, pady=(10, 0), fill="both", expand=True)

        top_row = ctk.CTkFrame(paths_card, fg_color="transparent")
        top_row.pack(padx=14, pady=(10, 6), fill="x")

        ctk.CTkLabel(top_row, text="Game Paths", font=("Segoe UI Black", 13), text_color=YELLOW).pack(side="left")

        entries = {}

        def auto_detect():
            folder = filedialog.askdirectory(title="Select games folder", parent=win)
            if not folder:
                return
            name_to_game = {(n + ".exe").lower(): n for n in game_paths}
            found = {}
            for dirpath, _, filenames in os.walk(folder):
                for fname in filenames:
                    key = fname.lower()
                    if key in name_to_game and name_to_game[key] not in found:
                        found[name_to_game[key]] = os.path.join(dirpath, fname)
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

        ctk.CTkButton(
            top_row, text="Auto-detect from folder…", command=auto_detect,
            fg_color=CARD_BG, hover_color=BORDER,
            font=("Segoe UI", 11), height=30, corner_radius=8,
        ).pack(side="right")

        scroll = ctk.CTkScrollableFrame(
            paths_card, fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=PINK,
        )
        scroll.pack(padx=14, pady=(0, 10), fill="both", expand=True)

        for game_name in game_paths:
            row = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=8)
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(row, text=game_name, font=("Segoe UI", 11), text_color=TEXT, width=190, anchor="w").pack(side="left", padx=10, pady=7)

            var = ctk.StringVar(value=game_paths.get(game_name, ""))
            ctk.CTkEntry(row, textvariable=var, font=("Segoe UI", 10), width=290, fg_color=FRAME_BG, border_color=BORDER, text_color=TEXT).pack(side="left", padx=6)

            def browse(v=var, n=game_name):
                initial = str(Path(v.get()).parent) if Path(v.get()).parent.exists() else "C:\\"
                path = filedialog.askopenfilename(
                    title=f"Select exe for {n}",
                    filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
                    initialdir=initial, parent=win,
                )
                if path:
                    v.set(path)

            ctk.CTkButton(row, text="Browse…", command=browse, width=82, height=28, fg_color=BORDER, hover_color=PINK, font=("Segoe UI", 10), corner_radius=6).pack(side="left", padx=(0, 8))
            entries[game_name] = var

        # Save
        def save_all():
            for name, var in entries.items():
                game_paths[name] = var.get()
            settings["game_paths"] = dict(game_paths)
            new_theme = style_var.get()
            theme_changed = new_theme != settings.get("ui_theme", "modern")
            settings["ui_theme"] = new_theme
            save_settings_fn(settings)
            win.destroy()
            if theme_changed:
                # DETACHED_PROCESS (0x00000008) — escapes Nuitka's Job Object
                # so the new instance survives the parent closing
                subprocess.Popen(restart_args, creationflags=0x00000008)
                root.destroy()

        ctk.CTkButton(
            win, text="Save",
            command=save_all,
            fg_color=YELLOW, hover_color=YELLOW_H,
            text_color="#0D0920", font=("Segoe UI Black", 14),
            width=160, height=42, corner_radius=20,
        ).pack(pady=(10, 14))

    # ── Launch ────────────────────────────────────────────────────────
    def launch_game():
        name = selected_game.get()
        path = Path(game_paths[name])
        if not path.is_file():
            messagebox.showerror("Error", f"Exe not found:\n{path}\n\nSet the path in ⚙ Settings.", parent=root)
            return
        try:
            subprocess.Popen([str(path)], cwd=str(path.parent))
            if prompt_var.get():
                messagebox.showinfo("Launching", f"Launching {name}!", parent=root)
            if close_var.get():
                root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch:\n{e}", parent=root)

    update_image()
    root.mainloop()
