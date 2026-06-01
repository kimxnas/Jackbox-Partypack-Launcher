"""Shared helpers used by both ui_classic and ui_modern."""
import os
import re
import sys
import json
import time
import shutil
from pathlib import Path

# Pre-compiled regex — sanitize is called on every dropdown change
_SANITIZE_RE = re.compile(r'[^A-Za-z0-9_-]')

# Standard names Steam uses for Jackbox installs
_STEAM_DIR_MAP = {
    "The Jackbox Party Pack":    "The Jackbox Party Pack",
    "The Jackbox Party Pack 2":  "The Jackbox Party Pack 2",
    "The Jackbox Party Pack 3":  "The Jackbox Party Pack 3",
    "The Jackbox Party Pack 4":  "The Jackbox Party Pack 4",
    "The Jackbox Party Pack 5":  "The Jackbox Party Pack 5",
    "The Jackbox Party Pack 6":  "The Jackbox Party Pack 6",
    "The Jackbox Party Pack 7":  "The Jackbox Party Pack 7",
    "The Jackbox Party Pack 8":  "The Jackbox Party Pack 8",
    "The Jackbox Party Pack 9":  "The Jackbox Party Pack 9",
    "The Jackbox Party Pack 10": "The Jackbox Party Pack 10",
}


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
    """Add game to recent list (most-recent first), persist. Also records timestamp."""
    recent = settings.get("recent_games", [])
    if game_name in recent:
        recent.remove(game_name)
    recent.insert(0, game_name)
    settings["recent_games"] = recent[:max_items]
    times = settings.get("last_played", {})
    times[game_name] = int(time.time())
    settings["last_played"] = times
    save_fn(settings)


def format_relative_time(ts):
    """Convert unix timestamp to '2h ago', '3 days ago', etc."""
    if not ts:
        return None
    delta = int(time.time()) - int(ts)
    if delta < 60:
        return "just now"
    if delta < 3600:
        m = delta // 60
        return f"{m}m ago"
    if delta < 86400:
        h = delta // 3600
        return f"{h}h ago"
    days = delta // 86400
    if days < 30:
        return f"{days}d ago"
    months = days // 30
    return f"{months}mo ago"


def get_last_played(settings, game_name):
    """Return human-readable last-played string for a game, or None."""
    ts = settings.get("last_played", {}).get(game_name)
    return format_relative_time(ts)


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


# ── Steam library detection ─────────────────────────────────────────

def _steam_install_dir():
    """Locate Steam's install directory on Windows."""
    candidates = [
        os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"), "Steam"),
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), "Steam"),
        r"C:\Steam",
    ]
    # Also try registry
    try:
        import winreg
        for hive, path in [
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
        ]:
            try:
                with winreg.OpenKey(hive, path) as k:
                    val, _ = winreg.QueryValueEx(k, "InstallPath" if hive == winreg.HKEY_LOCAL_MACHINE else "SteamPath")
                    candidates.insert(0, val)
            except OSError:
                pass
    except ImportError:
        pass
    for c in candidates:
        if c and Path(c).is_dir():
            return c
    return None


def _parse_steam_library_paths(steam_dir):
    """Parse libraryfolders.vdf to get all Steam library locations."""
    vdf_path = Path(steam_dir) / "steamapps" / "libraryfolders.vdf"
    if not vdf_path.is_file():
        return [str(Path(steam_dir) / "steamapps")]
    libraries = [str(Path(steam_dir) / "steamapps")]
    try:
        content = vdf_path.read_text(encoding="utf-8", errors="ignore")
        # VDF path entries: "path"  "C:\\Some\\Other\\SteamLibrary"
        for match in re.finditer(r'"path"\s*"([^"]+)"', content):
            lib_path = match.group(1).replace("\\\\", "\\")
            steamapps = Path(lib_path) / "steamapps"
            if steamapps.is_dir() and str(steamapps) not in libraries:
                libraries.append(str(steamapps))
    except Exception:
        pass
    return libraries


def detect_steam_jackbox(game_paths):
    """
    Walk all Steam libraries looking for installed Jackbox packs.
    Returns dict {pack_name: exe_path}. Empty if Steam not found or no packs installed.
    """
    steam = _steam_install_dir()
    if not steam:
        return {}
    libraries = _parse_steam_library_paths(steam)
    found = {}
    for lib in libraries:
        common = Path(lib) / "common"
        if not common.is_dir():
            continue
        for pack_name, dir_name in _STEAM_DIR_MAP.items():
            if pack_name in found or pack_name not in game_paths:
                continue
            pack_dir = common / dir_name
            if not pack_dir.is_dir():
                continue
            # Find the .exe in the pack folder
            expected_exe = pack_dir / f"{pack_name}.exe"
            if expected_exe.is_file():
                found[pack_name] = str(expected_exe)
                continue
            # Fallback: any exe in the folder containing the pack name
            for exe in pack_dir.glob("*.exe"):
                if "uninstall" not in exe.name.lower():
                    found[pack_name] = str(exe)
                    break
    return found


# ── Settings backup / restore ───────────────────────────────────────

def export_settings(settings, dest_path):
    """Save settings to a user-chosen JSON file. Returns (ok, error)."""
    try:
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        return True, None
    except Exception as e:
        return False, str(e)


def import_settings(src_path):
    """Load settings from a JSON file. Returns (ok, settings_dict_or_error)."""
    try:
        with open(src_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False, "File is not a valid settings JSON (expected object)"
        return True, data
    except Exception as e:
        return False, str(e)


# ── Windows autostart ───────────────────────────────────────────────

_AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_AUTOSTART_VALUE = "JackboxLauncher"


def is_autostart_enabled():
    """Check if the launcher is registered to start with Windows."""
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _AUTOSTART_KEY) as k:
            winreg.QueryValueEx(k, _AUTOSTART_VALUE)
            return True
    except OSError:
        return False
    except ImportError:
        return False


def set_autostart(enabled, exe_path=None):
    """Enable or disable autostart on Windows. Returns (ok, error)."""
    if sys.platform != "win32":
        return False, "Autostart only supported on Windows"
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _AUTOSTART_KEY, 0,
                            winreg.KEY_SET_VALUE) as k:
            if enabled:
                target = exe_path or sys.argv[0]
                winreg.SetValueEx(k, _AUTOSTART_VALUE, 0, winreg.REG_SZ, f'"{target}"')
            else:
                try:
                    winreg.DeleteValue(k, _AUTOSTART_VALUE)
                except OSError:
                    pass
        return True, None
    except Exception as e:
        return False, str(e)
