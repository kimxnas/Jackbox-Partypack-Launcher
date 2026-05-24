import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw
import os
import re
import sys
import json
import random
import webbrowser
import subprocess
import urllib.request
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG       = "#0D0920"
FRAME_BG = "#1A0F38"
CARD_BG  = "#241554"
BORDER   = "#3D2070"
YELLOW   = "#FFE600"
YELLOW_H = "#FFCC00"
PINK     = "#FF2D78"
PINK_H   = "#CC1060"
CYAN     = "#00D4FF"
CYAN_H   = "#00A8CC"
TEXT     = "#FFFFFF"
SUBTEXT  = "#C0A0E0"

BASE_W  = 620
BASE_H  = 485
PANEL_W = 340
ANIM_FRAMES   = 20
ANIM_INTERVAL = 8

GAME_INFO = {
    "The Jackbox Party Pack": [
        {"name": "You Don't Know Jack", "min": 1, "max": 4, "tags": {"trivia"}},
        {"name": "Fibbage XL",          "min": 2, "max": 8, "tags": {"bluffing"}},
        {"name": "Drawful",             "min": 2, "max": 8, "tags": {"drawing"}},
        {"name": "Word Spud",           "min": 2, "max": 8, "tags": {"comedy"}},
        {"name": "Lie Swatter",         "min": 2, "max": 8, "tags": {"trivia"}},
    ],
    "The Jackbox Party Pack 2": [
        {"name": "Fibbage 2", "min": 2, "max": 8, "tags": {"bluffing"}},
        {"name": "Earwax",    "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Bidiots",   "min": 2, "max": 6, "tags": {"drawing"}},
        {"name": "Quiplash",  "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Bomb Corp", "min": 2, "max": 4, "tags": {"social"}},
    ],
    "The Jackbox Party Pack 3": [
        {"name": "Quiplash 2",          "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Trivia Murder Party", "min": 2, "max": 8, "tags": {"trivia"}},
        {"name": "Guesspionage",        "min": 2, "max": 8, "tags": {"trivia"}},
        {"name": "Tee K.O.",            "min": 3, "max": 8, "tags": {"drawing", "comedy"}},
        {"name": "Fakin' It",           "min": 3, "max": 6, "tags": {"social"}},
    ],
    "The Jackbox Party Pack 4": [
        {"name": "Fibbage 3",               "min": 2, "max": 8,  "tags": {"bluffing"}},
        {"name": "Survive the Internet",    "min": 3, "max": 8,  "tags": {"comedy"}},
        {"name": "Monster Seeking Monster", "min": 3, "max": 7,  "tags": {"social"}},
        {"name": "Bracketeering",           "min": 3, "max": 16, "tags": {"trivia"}},
        {"name": "Civic Doodle",            "min": 3, "max": 8,  "tags": {"drawing"}},
    ],
    "The Jackbox Party Pack 5": [
        {"name": "YDKJ Full Stream", "min": 1, "max": 8, "tags": {"trivia"}},
        {"name": "Split the Room",   "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Mad Verse City",   "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Patently Stupid",  "min": 3, "max": 8, "tags": {"drawing", "comedy"}},
        {"name": "Zeeple Dome",      "min": 2, "max": 6, "tags": {"social"}},
    ],
    "The Jackbox Party Pack 6": [
        {"name": "Quiplash 3",            "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Trivia Murder Party 2", "min": 2, "max": 8, "tags": {"trivia"}},
        {"name": "Role Models",           "min": 3, "max": 6, "tags": {"social"}},
        {"name": "Joke Boat",             "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Dictionarium",          "min": 3, "max": 8, "tags": {"comedy"}},
    ],
    "The Jackbox Party Pack 7": [
        {"name": "The Devils and the Details",    "min": 3, "max": 8, "tags": {"social"}},
        {"name": "Champ'd Up",                    "min": 3, "max": 8, "tags": {"drawing"}},
        {"name": "Talking Points",                "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Blather 'Round",                "min": 2, "max": 6, "tags": {"comedy"}},
        {"name": "Wheel of Enormous Proportions", "min": 2, "max": 8, "tags": {"trivia"}},
    ],
    "The Jackbox Party Pack 8": [
        {"name": "Drawful Animate", "min": 2, "max": 8, "tags": {"drawing"}},
        {"name": "Job Job",         "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Poll Mine",       "min": 2, "max": 8, "tags": {"trivia", "social"}},
        {"name": "Weapons Drawn",   "min": 4, "max": 8, "tags": {"drawing", "social"}},
        {"name": "The Wheel of Enormous Proportions", "min": 2, "max": 8, "tags": {"trivia"}},
    ],
    "The Jackbox Party Pack 9": [
        {"name": "Fibbage 4",   "min": 2, "max": 8, "tags": {"bluffing"}},
        {"name": "Roomerang",   "min": 3, "max": 7, "tags": {"social"}},
        {"name": "Junktopia",   "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Nonsensory",  "min": 3, "max": 8, "tags": {"comedy"}},
        {"name": "Squidproquo", "min": 3, "max": 8, "tags": {"social"}},
    ],
    "The Jackbox Party Pack 10": [
        {"name": "Tee K.O. 2",   "min": 3, "max": 8, "tags": {"drawing", "comedy"}},
        {"name": "Timejinx",     "min": 2, "max": 8, "tags": {"trivia"}},
        {"name": "Dodo Re Mi",   "min": 2, "max": 8, "tags": {"music"}},
        {"name": "Hypnotorious", "min": 3, "max": 8, "tags": {"social"}},
        {"name": "FixyText",     "min": 3, "max": 8, "tags": {"comedy"}},
    ],
}


def run(settings, save_settings_fn, resource_path_fn, game_paths, restart_args,
        current_version="1.0.0", github_repo=""):
    image_cache  = {}
    panel_open   = [False]
    anim_running = [False]

    def version_tuple(v):
        try:
            return tuple(int(x) for x in v.lstrip('v').split('.'))
        except Exception:
            return (0,)

    root = ctk.CTk()
    root.title("Jackbox Launcher")
    root.geometry(f"{BASE_W}x{BASE_H}")
    root.resizable(False, False)
    root.configure(fg_color=BG)

    try:
        root.iconbitmap(resource_path_fn('icon.ico'))
    except Exception:
        pass

    container = ctk.CTkFrame(root, fg_color=BG, corner_radius=0)
    container.pack(fill="both", expand=True)

    left = ctk.CTkFrame(container, fg_color=BG, corner_radius=0, width=BASE_W)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    divider = ctk.CTkFrame(container, fg_color=BORDER, width=1)
    divider.pack(side="left", fill="y")
    divider.pack_propagate(False)

    right = ctk.CTkFrame(container, fg_color=FRAME_BG, corner_radius=0, width=0)
    right.pack(side="left", fill="y")
    right.pack_propagate(False)

    right_inner = ctk.CTkFrame(right, fg_color="transparent")

    # ── Header ────────────────────────────────────────────────────────
    header = ctk.CTkFrame(left, fg_color=FRAME_BG, corner_radius=0, height=68)
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

    recommend_btn = ctk.CTkButton(
        header, text="🎲  Find a Game",
        font=("Segoe UI", 11),
        fg_color=CARD_BG, hover_color=BORDER,
        text_color=CYAN, corner_radius=15,
        width=130, height=32,
        command=lambda: toggle_panel(),
    )
    if settings.get("show_find_a_game", True):
        recommend_btn.place(relx=1.0, x=-68, rely=0.5, anchor="e")

    # ── Game image ────────────────────────────────────────────────────
    # Border + rounded corners are baked into the PIL image to avoid
    # CTk-vs-PIL corner-curve mismatch
    img_label = ctk.CTkLabel(left, text="")
    img_label.pack(pady=(14, 0))

    def sanitize(name):
        return re.sub(r'[^A-Za-z0-9_-]', '', name.replace(" ", "_"))

    def round_image(pil, inner_radius=14, border=2, ssaa=4):
        """Bake border + rounded corners into a single flat image (no CTk frame needed)."""
        inner_w, inner_h = 560, 214
        outer_w, outer_h = inner_w + border * 2, inner_h + border * 2
        outer_radius = inner_radius + border

        pil = pil.convert("RGB").resize((inner_w, inner_h), Image.Resampling.LANCZOS)

        # Supersampled outer rounded mask — clips border+image into rounded shape on BG
        big = (outer_w * ssaa, outer_h * ssaa)
        outer_mask = Image.new("L", big, 0)
        ImageDraw.Draw(outer_mask).rounded_rectangle(
            (0, 0, big[0], big[1]), outer_radius * ssaa, fill=255
        )
        outer_mask = outer_mask.resize((outer_w, outer_h), Image.Resampling.LANCZOS)

        # Composite BORDER onto BG using outer mask → rounded purple shape
        bg_layer = Image.new("RGB", (outer_w, outer_h), BG)
        border_layer = Image.new("RGB", (outer_w, outer_h), BORDER)
        result = Image.composite(border_layer, bg_layer, outer_mask)

        # Supersampled inner rounded mask for the actual game image
        big_i = (inner_w * ssaa, inner_h * ssaa)
        inner_mask = Image.new("L", big_i, 0)
        ImageDraw.Draw(inner_mask).rounded_rectangle(
            (0, 0, big_i[0], big_i[1]), inner_radius * ssaa, fill=255
        )
        inner_mask = inner_mask.resize((inner_w, inner_h), Image.Resampling.LANCZOS)

        # Paste the game image centered inside the border
        result.paste(pil, (border, border), mask=inner_mask)
        return result

    def update_image(*_):
        key = sanitize(selected_game.get())
        if key in image_cache:
            img_label.configure(image=image_cache[key])
            return
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            p = Path(resource_path_fn("game_images")) / f"{key}{ext}"
            if p.exists():
                pil = Image.open(p)
                pil = round_image(pil)  # returns 564×218 with border baked in
                ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(564, 218))
                image_cache[key] = ctk_img
                img_label.configure(image=ctk_img)
                return
        img_label.configure(image=None)

    # ── Dropdown ──────────────────────────────────────────────────────
    selected_game = ctk.StringVar(value=list(game_paths.keys())[0])
    selected_game.trace_add("write", update_image)

    ctk.CTkOptionMenu(
        left, variable=selected_game,
        values=list(game_paths.keys()),
        fg_color=CARD_BG, button_color=BORDER, button_hover_color=PINK,
        text_color=TEXT, font=("Segoe UI", 13),
        dropdown_fg_color=FRAME_BG, dropdown_text_color=TEXT,
        dropdown_hover_color=BORDER,
        dynamic_resizing=False, width=580, height=44, corner_radius=10,
    ).pack(pady=(12, 0))

    # ── Recently played row ───────────────────────────────────────────
    recent_frame = ctk.CTkFrame(left, fg_color="transparent")
    # packed/forgotten dynamically by render_recent()

    def render_recent():
        for w in recent_frame.winfo_children():
            w.destroy()
        recent = settings.get("recent_games", [])
        show = settings.get("show_recent", True)
        if not show or not recent:
            recent_frame.pack_forget()
            return
        ctk.CTkLabel(recent_frame, text="Recent:", font=("Segoe UI", 11), text_color=SUBTEXT).pack(side="left", padx=(0, 8))
        for pack_name in recent[:3]:
            if pack_name not in game_paths:
                continue
            short = pack_name.replace("The Jackbox Party Pack", "Pack")
            ctk.CTkButton(
                recent_frame, text=short,
                width=82, height=26, corner_radius=13,
                fg_color=CARD_BG, hover_color=BORDER,
                text_color=CYAN, font=("Segoe UI", 10),
                command=lambda p=pack_name: selected_game.set(p),
            ).pack(side="left", padx=3)
        recent_frame.pack(pady=(10, 0))

    # ── Play button ───────────────────────────────────────────────────
    ctk.CTkButton(
        left, text="▶   PLAY!",
        font=("Segoe UI Black", 22),
        fg_color=YELLOW, hover_color=YELLOW_H, text_color="#0D0920",
        corner_radius=30, width=280, height=62,
        command=lambda: launch_game(),
    ).pack(pady=(12, 0))

    # Variables previously in bottom row checkboxes — now lived in settings
    close_var  = ctk.BooleanVar(value=settings.get("close_after_launch", False))
    prompt_var = ctk.BooleanVar(value=settings.get("show_launch_prompt", True))

    # ── Right panel content ───────────────────────────────────────────
    ctk.CTkLabel(right_inner, text="FIND A GAME", font=("Impact", 24), text_color=CYAN).pack(pady=(20, 4))
    ctk.CTkFrame(right_inner, fg_color=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 12))

    player_count = [4]
    player_var = ctk.StringVar(value="4")

    def change_players(delta):
        player_count[0] = max(1, min(16, player_count[0] + delta))
        player_var.set(str(player_count[0]))

    p_row = ctk.CTkFrame(right_inner, fg_color="transparent")
    p_row.pack(pady=(0, 12))
    ctk.CTkLabel(p_row, text="Players", font=("Segoe UI", 12), text_color=SUBTEXT).pack()
    stepper = ctk.CTkFrame(p_row, fg_color="transparent")
    stepper.pack(pady=4)
    ctk.CTkButton(stepper, text="−", width=36, height=36, corner_radius=18,
        fg_color=CARD_BG, hover_color=BORDER, font=("Segoe UI Black", 16),
        command=lambda: change_players(-1)).pack(side="left", padx=6)
    ctk.CTkLabel(stepper, textvariable=player_var,
        font=("Impact", 28), text_color=YELLOW, width=40).pack(side="left")
    ctk.CTkButton(stepper, text="+", width=36, height=36, corner_radius=18,
        fg_color=CARD_BG, hover_color=BORDER, font=("Segoe UI Black", 16),
        command=lambda: change_players(1)).pack(side="left", padx=6)

    ctk.CTkLabel(right_inner, text="Style", font=("Segoe UI", 12), text_color=SUBTEXT).pack()

    TAGS = ["Trivia", "Drawing", "Comedy", "Bluffing", "Social", "Music"]
    active_tags = set()
    tag_buttons = {}

    def toggle_tag(tag):
        t = tag.lower()
        if t in active_tags:
            active_tags.discard(t)
            tag_buttons[tag].configure(fg_color=CARD_BG, hover_color=BORDER, text_color=TEXT)
        else:
            active_tags.add(t)
            tag_buttons[tag].configure(fg_color=CYAN, hover_color=CYAN_H, text_color="#0D0920")

    tags_frame = ctk.CTkFrame(right_inner, fg_color="transparent")
    tags_frame.pack(pady=6)

    current_row = None
    for i, tag in enumerate(TAGS):
        if i % 3 == 0:
            current_row = ctk.CTkFrame(tags_frame, fg_color="transparent")
            current_row.pack(pady=2)
        b = ctk.CTkButton(
            current_row, text=tag, width=88, height=30, corner_radius=15,
            fg_color=CARD_BG, hover_color=BORDER, text_color=TEXT,
            font=("Segoe UI", 11),
            command=lambda t=tag: toggle_tag(t),
        )
        b.pack(side="left", padx=4)
        tag_buttons[tag] = b

    ctk.CTkFrame(right_inner, fg_color=BORDER, height=1).pack(fill="x", padx=16, pady=(10, 10))

    ctk.CTkButton(
        right_inner, text="List Matches",
        width=280, height=36, corner_radius=18,
        fg_color=CARD_BG, hover_color=BORDER,
        font=("Segoe UI", 13), text_color=TEXT,
        command=lambda: list_matches(),
    ).pack(pady=(0, 6))

    ctk.CTkButton(
        right_inner, text="🎲  Random Pick!",
        width=280, height=36, corner_radius=18,
        fg_color=YELLOW, hover_color=YELLOW_H, text_color="#0D0920",
        font=("Segoe UI Black", 13),
        command=lambda: random_pick(),
    ).pack()

    ctk.CTkFrame(right_inner, fg_color=BORDER, height=1).pack(fill="x", padx=16, pady=(10, 6))

    result_box = ctk.CTkTextbox(
        right_inner,
        fg_color=CARD_BG, border_color=BORDER, border_width=1,
        text_color=YELLOW, font=("Bahnschrift", 14),
        corner_radius=10, wrap="word",
        state="disabled",
    )
    result_box.pack(padx=12, pady=(0, 12), fill="both", expand=True)

    def get_matches():
        count = player_count[0]
        results = []
        for pack_name, games in GAME_INFO.items():
            short = pack_name.replace("The Jackbox Party Pack", "Pack")
            for g in games:
                if not (g["min"] <= count <= g["max"]):
                    continue
                if active_tags and not (active_tags & g["tags"]):
                    continue
                results.append((g["name"], pack_name, short))
        return results

    def set_result(text):
        result_box.configure(state="normal")
        result_box.delete("0.0", "end")
        result_box.insert("0.0", text)
        result_box.configure(state="disabled")

    def list_matches():
        matches = get_matches()
        if not matches:
            set_result("No games match\nyour filters.")
        else:
            set_result("\n".join(f"{g}  ({short})" for g, _, short in matches))

    def random_pick():
        matches = get_matches()
        if not matches:
            set_result("No games match\nyour filters.")
        else:
            g, pack, short = random.choice(matches)
            set_result(f"🎲  {g}\n({short})")
            selected_game.set(pack)

    # ── Animation ─────────────────────────────────────────────────────
    def animate_to(target_w):
        start_w = root.winfo_width()
        opening = target_w > BASE_W
        if not opening:
            right_inner.pack_forget()

        def step(n):
            if n >= ANIM_FRAMES:
                root.geometry(f"{target_w}x{BASE_H}")
                right.configure(width=max(0, target_w - BASE_W))
                if opening:
                    right_inner.pack(fill="both", expand=True)
                anim_running[0] = False
                return
            t = n / ANIM_FRAMES
            ease = t * t * (3 - 2 * t)
            w = int(start_w + (target_w - start_w) * ease)
            root.geometry(f"{w}x{BASE_H}")
            right.configure(width=max(0, w - BASE_W))
            root.after(ANIM_INTERVAL, lambda: step(n + 1))

        step(1)

    def toggle_panel():
        if anim_running[0]:
            return
        anim_running[0] = True
        if panel_open[0]:
            panel_open[0] = False
            recommend_btn.configure(text="🎲  Find a Game", text_color=CYAN)
            animate_to(BASE_W)
        else:
            panel_open[0] = True
            recommend_btn.configure(text="✕  Close", text_color=PINK)
            set_result("")
            animate_to(BASE_W + PANEL_W)

    # ── Settings window ───────────────────────────────────────────────
    def open_settings():
        win = ctk.CTkToplevel(root)
        win.title("Settings")
        win.geometry("680x720")
        win.resizable(False, False)
        win.grab_set()
        win.configure(fg_color=BG)

        try:
            win.iconbitmap(resource_path_fn('icon.ico'))
        except Exception:
            pass

        style_card = ctk.CTkFrame(win, fg_color=FRAME_BG, corner_radius=12)
        style_card.pack(padx=16, pady=(14, 0), fill="x")
        ctk.CTkLabel(style_card, text="UI Style", font=("Segoe UI Black", 13), text_color=YELLOW).pack(anchor="w", padx=14, pady=(10, 4))

        style_var = ctk.StringVar(value=settings.get("ui_theme", "modern"))
        ctk.CTkSegmentedButton(
            style_card, values=["classic", "modern"], variable=style_var,
            fg_color=CARD_BG, selected_color=YELLOW, selected_hover_color=YELLOW_H,
            unselected_color=CARD_BG, unselected_hover_color=BORDER,
            text_color="#0D0920", font=("Segoe UI", 12),
        ).pack(padx=14, pady=(0, 12), anchor="w")

        # Launch behavior
        beh_card = ctk.CTkFrame(win, fg_color=FRAME_BG, corner_radius=12)
        beh_card.pack(padx=16, pady=(10, 0), fill="x")
        ctk.CTkLabel(beh_card, text="Launch Behavior", font=("Segoe UI Black", 13), text_color=YELLOW).pack(anchor="w", padx=14, pady=(10, 4))

        close_set_var  = ctk.BooleanVar(value=settings.get("close_after_launch", False))
        prompt_set_var = ctk.BooleanVar(value=settings.get("show_launch_prompt", True))

        for text, var in [("Close launcher after launch", close_set_var),
                          ("Show launch confirmation", prompt_set_var)]:
            ctk.CTkCheckBox(
                beh_card, text=text, variable=var,
                font=("Segoe UI", 11), text_color=SUBTEXT,
                fg_color=PINK, hover_color=PINK_H,
                checkmark_color=TEXT, border_color=BORDER,
            ).pack(anchor="w", padx=14, pady=2)
        ctk.CTkFrame(beh_card, fg_color="transparent", height=8).pack()

        # Visibility toggles
        vis_card = ctk.CTkFrame(win, fg_color=FRAME_BG, corner_radius=12)
        vis_card.pack(padx=16, pady=(10, 0), fill="x")
        ctk.CTkLabel(vis_card, text="Visibility", font=("Segoe UI Black", 13), text_color=YELLOW).pack(anchor="w", padx=14, pady=(10, 4))

        show_recent_var = ctk.BooleanVar(value=settings.get("show_recent", True))
        show_find_var   = ctk.BooleanVar(value=settings.get("show_find_a_game", True))

        for text, var in [("Show recently played", show_recent_var),
                          ("Show Find a Game button", show_find_var)]:
            ctk.CTkCheckBox(
                vis_card, text=text, variable=var,
                font=("Segoe UI", 11), text_color=SUBTEXT,
                fg_color=PINK, hover_color=PINK_H,
                checkmark_color=TEXT, border_color=BORDER,
            ).pack(anchor="w", padx=14, pady=2)
        ctk.CTkFrame(vis_card, fg_color="transparent", height=8).pack()

        # About / Updates
        about_card = ctk.CTkFrame(win, fg_color=FRAME_BG, corner_radius=12)
        about_card.pack(padx=16, pady=(10, 0), fill="x")

        about_row = ctk.CTkFrame(about_card, fg_color="transparent")
        about_row.pack(padx=14, pady=10, fill="x")
        ctk.CTkLabel(about_row, text=f"Version {current_version}",
                     font=("Segoe UI", 11), text_color=SUBTEXT).pack(side="left")

        def manual_check():
            try:
                url = f"https://api.github.com/repos/{github_repo}/releases/latest"
                req = urllib.request.Request(url, headers={"User-Agent": "JackboxLauncher"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    data = json.loads(r.read())
                latest = data.get("tag_name", "").lstrip("v")
                if latest and version_tuple(latest) > version_tuple(current_version):
                    if messagebox.askyesno("Update Available",
                        f"v{latest} is available (you have v{current_version}).\n\nOpen the download page?",
                        parent=win):
                        webbrowser.open(f"https://github.com/{github_repo}/releases/latest")
                else:
                    messagebox.showinfo("Up to date", f"You're on the latest version (v{current_version}).", parent=win)
            except Exception as e:
                messagebox.showerror("Update check failed", f"Couldn't reach GitHub:\n{e}", parent=win)

        ctk.CTkButton(
            about_row, text="Check for updates", command=manual_check,
            fg_color=CARD_BG, hover_color=BORDER,
            font=("Segoe UI", 11), height=28, corner_radius=8, width=140,
        ).pack(side="right")

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

        def save_all():
            for name, var in entries.items():
                game_paths[name] = var.get()
            settings["game_paths"] = dict(game_paths)
            new_theme = style_var.get()
            theme_changed = new_theme != settings.get("ui_theme", "modern")
            settings["ui_theme"] = new_theme
            settings["show_recent"] = show_recent_var.get()
            settings["show_find_a_game"] = show_find_var.get()
            settings["close_after_launch"] = close_set_var.get()
            settings["show_launch_prompt"] = prompt_set_var.get()
            save_settings_fn(settings)

            # Sync the local BooleanVars used by launch_game
            close_var.set(close_set_var.get())
            prompt_var.set(prompt_set_var.get())

            # Apply visibility changes live
            render_recent()
            if show_find_var.get():
                if not recommend_btn.winfo_ismapped():
                    recommend_btn.place(relx=1.0, x=-68, rely=0.5, anchor="e")
            else:
                recommend_btn.place_forget()
                if panel_open[0]:  # close panel if it was open
                    toggle_panel()

            win.destroy()
            if theme_changed:
                # DETACHED_PROCESS (0x00000008) — escapes Nuitka's Job Object
                # so the new instance survives the parent closing
                subprocess.Popen(restart_args, creationflags=0x00000008)
                root.destroy()

        ctk.CTkButton(
            win, text="Save", command=save_all,
            fg_color=YELLOW, hover_color=YELLOW_H,
            text_color="#0D0920", font=("Segoe UI Black", 14),
            width=160, height=42, corner_radius=20,
        ).pack(pady=(10, 14))

    # ── Launch ────────────────────────────────────────────────────────
    def track_recent(name):
        recent = settings.get("recent_games", [])
        if name in recent:
            recent.remove(name)
        recent.insert(0, name)
        settings["recent_games"] = recent[:3]
        save_settings_fn(settings)
        render_recent()

    def launch_game():
        name = selected_game.get()
        path = Path(game_paths[name])
        if not path.is_file():
            messagebox.showerror("Error", f"Exe not found:\n{path}\n\nSet the path in ⚙ Settings.", parent=root)
            return
        try:
            subprocess.Popen([str(path)], cwd=str(path.parent))
            track_recent(name)
            if prompt_var.get():
                messagebox.showinfo("Launching", f"Launching {name}!", parent=root)
            if close_var.get():
                root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch:\n{e}", parent=root)

    update_image()
    render_recent()
    root.mainloop()
