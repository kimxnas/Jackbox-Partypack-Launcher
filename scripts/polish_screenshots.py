"""
Polish raw launcher screenshots into a pro-looking README image.

Usage:
    1. Save your screenshots as `modern.png` and `classic.png` in this folder.
    2. Run: python scripts/polish_screenshots.py
    3. Output: screenshot.png in the project root (overwrites existing)

What it does:
    - Rounds each window's corners (anti-aliased)
    - Adds a soft drop shadow for depth
    - Places them side-by-side on a Jackbox-themed purple gradient
    - Adds small "Modern" / "Classic" labels underneath
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path
import sys

# Jackbox palette
BG_TOP     = (26, 10, 46)    # deep purple
BG_BOTTOM  = (13, 9, 32)     # almost black
YELLOW     = (255, 230, 0)
SUBTEXT    = (192, 160, 224)


def round_corners(img, radius=12, ssaa=4):
    img = img.convert("RGBA")
    big = (img.width * ssaa, img.height * ssaa)
    mask = Image.new("L", big, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, big[0], big[1]), radius * ssaa, fill=255)
    mask = mask.resize(img.size, Image.Resampling.LANCZOS)
    img.putalpha(mask)
    return img


def add_shadow(img, offset=(0, 18), color=(0, 0, 0, 140), blur=30, pad=50):
    canvas = Image.new("RGBA",
                       (img.width + pad * 2, img.height + pad * 2 + offset[1]),
                       (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, color)
    shadow.putalpha(img.getchannel("A"))  # match alpha shape
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(shadow, (pad + offset[0], pad + offset[1]))
    canvas.alpha_composite(img, (pad, pad))
    return canvas


def gradient_bg(w, h, top, bottom):
    bg = Image.new("RGB", (w, h), top)
    px = bg.load()
    for y in range(h):
        t = y / h
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return bg


def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for f in candidates:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def main():
    here = Path(__file__).parent
    modern_path  = here / "modern.png"
    classic_path = here / "classic.png"
    output_path  = here.parent / "screenshot.png"

    if not modern_path.exists() or not classic_path.exists():
        print(f"Place modern.png and classic.png in {here}")
        print("Then re-run this script.")
        sys.exit(1)

    modern  = Image.open(modern_path).convert("RGBA")
    classic = Image.open(classic_path).convert("RGBA")

    # Normalize heights so they sit nicely side-by-side
    target_h = 480
    def scale(img):
        ratio = target_h / img.height
        return img.resize((int(img.width * ratio), target_h), Image.Resampling.LANCZOS)
    modern  = scale(modern)
    classic = scale(classic)

    # Round corners + shadow each
    modern  = add_shadow(round_corners(modern,  radius=10))
    classic = add_shadow(round_corners(classic, radius=10))

    # Composition: side by side
    spacing       = 30
    side_padding  = 40
    label_room    = 60
    title_room    = 90

    inner_w = modern.width + spacing + classic.width
    inner_h = max(modern.height, classic.height)
    total_w = inner_w + side_padding * 2
    total_h = inner_h + title_room + label_room

    canvas = gradient_bg(total_w, total_h, BG_TOP, BG_BOTTOM).convert("RGBA")

    # Title
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(46, bold=True)
    title = "JACKBOX LAUNCHER"
    tw = draw.textlength(title, font=title_font)
    draw.text(((total_w - tw) / 2, 22), title, fill=YELLOW, font=title_font)

    # Paste windows
    y_offset = title_room
    canvas.alpha_composite(modern, (side_padding, y_offset))
    canvas.alpha_composite(classic, (side_padding + modern.width + spacing, y_offset))

    # Labels under each
    label_font = load_font(18, bold=True)
    def label(text, x_center):
        lw = draw.textlength(text, font=label_font)
        draw.text((x_center - lw / 2, total_h - 44), text, fill=SUBTEXT, font=label_font)

    label("Modern",  side_padding + modern.width / 2)
    label("Classic", side_padding + modern.width + spacing + classic.width / 2)

    canvas.convert("RGB").save(output_path, "PNG", optimize=True)
    print(f"Saved polished screenshot to: {output_path}")


if __name__ == "__main__":
    main()
