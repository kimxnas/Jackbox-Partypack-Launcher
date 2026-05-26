"""Shared helpers used by both ui_classic and ui_modern."""
import os
import re
from pathlib import Path

# Pre-compiled regex — sanitize is called on every dropdown change
_SANITIZE_RE = re.compile(r'[^A-Za-z0-9_-]')


def sanitize_name(name):
    """Convert a game name to a safe filename stem."""
    return _SANITIZE_RE.sub('', name.replace(' ', '_'))


def validate_exe_path(path):
    """Return (ok, reason). Only allow real .exe files (no symlinks pointing elsewhere)."""
    try:
        p = Path(path)
        if not p.is_file():
            return False, "File does not exist"
        if p.suffix.lower() != ".exe":
            return False, "Not an .exe file"
        # Resolve and ensure target is still a real file (catches dangling symlinks)
        if not p.resolve(strict=True).is_file():
            return False, "Target is not a regular file"
        return True, None
    except Exception as e:
        return False, str(e)


def validate_image_path(path, max_mb=10):
    """Return (ok, reason). PNG/JPG only, sane size limit."""
    try:
        p = Path(path)
        if not p.is_file():
            return False, "File does not exist"
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            return False, "Must be PNG or JPG"
        size_mb = p.stat().st_size / (1024 * 1024)
        if size_mb > max_mb:
            return False, f"File too large ({size_mb:.1f} MB > {max_mb} MB limit)"
        return True, None
    except Exception as e:
        return False, str(e)


def auto_detect_games(folder, game_paths):
    """Walk folder looking for {GameName}.exe matches. Returns dict of game_name -> path."""
    name_to_game = {(n + ".exe").lower(): n for n in game_paths}
    found = {}
    for dirpath, _, filenames in os.walk(folder):
        for fname in filenames:
            key = fname.lower()
            if key in name_to_game and name_to_game[key] not in found:
                found[name_to_game[key]] = os.path.join(dirpath, fname)
    return found


def track_recent(settings, save_fn, game_name, max_items=3):
    """Add game to recent list (most-recent first), persist."""
    recent = settings.get("recent_games", [])
    if game_name in recent:
        recent.remove(game_name)
    recent.insert(0, game_name)
    settings["recent_games"] = recent[:max_items]
    save_fn(settings)


def track_stats(settings, save_fn, game_name):
    """Increment launch count for game, persist."""
    stats = settings.get("pack_stats", {})
    stats[game_name] = stats.get(game_name, 0) + 1
    settings["pack_stats"] = stats
    save_fn(settings)


def get_top_stats(settings, top_n=5):
    """Return sorted list of (game_name, count), descending."""
    stats = settings.get("pack_stats", {})
    return sorted(stats.items(), key=lambda kv: kv[1], reverse=True)[:top_n]


def get_banner_path(settings, default_path):
    """Return user's custom banner path if set & valid, else default."""
    custom = settings.get("custom_banner")
    if custom and Path(custom).is_file():
        return custom
    return default_path


def version_tuple(v):
    """Parse 'v1.2.3' into (1, 2, 3) for comparison. Safe on garbage."""
    try:
        return tuple(int(x) for x in v.lstrip('v').split('.'))
    except Exception:
        return (0,)
