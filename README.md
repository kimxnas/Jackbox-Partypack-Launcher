# Jackbox Party Pack Launcher

A clean, no-frills launcher for all 10 Jackbox Party Packs. Pick a pack, hit Play — that's it. Now with game suggestions, recently-played quick launch, pack stats, custom banners, and built-in update checks.

![Launcher screenshot](screenshot.png)

## Download

Head to [**Releases**](https://github.com/kimxnas/Jackbox-Partypack-Launcher/releases) and grab the latest `JackboxPartypackLauncher.exe`. No install, no dependencies — just run it.

> ⚠️ Windows may show a "SmartScreen" warning since the exe isn't code-signed.
> Click **More info → Run anyway**. The source is open if you want to inspect it.

## Features

- **🎲 Find a Game** — slide-out panel that recommends specific Jackbox games based on player count and style (Trivia, Drawing, Comedy, Bluffing, Social, Music). List all matches or let it randomly pick one for you
- **Recently played** — your last 3 launched packs appear as quick-launch chips above the dropdown
- **Pack stats** — see your most-played packs ranked in settings
- **Custom banners** — swap in your own header image (classic UI)
- **Classic & Modern UI** — toggle between the original look and a sleek dark Jackbox-themed theme in settings
- **Game cover art** — smoothly rounded box art that updates as you switch packs (preloaded in the background for instant switching)
- **Auto-detect** — point it at your games folder and it finds all the exes automatically
- **Per-game path config** — set or override any path individually via the ⚙ settings menu
- **Tabbed settings** — General / Game Paths / About — no more endless scrolling
- **Visibility toggles** — hide Recently Played or the Find a Game button if you prefer a minimal view
- **Check for updates** — one click in settings tells you if a newer release is on GitHub
- **Settings persist** — your paths and preferences live in `%APPDATA%\JackboxLauncher` and survive moves/updates
- **Safe by default** — exe paths are validated (must be a real `.exe`), banners size-checked, subprocesses spawned with `shell=False`

## How to use

1. Download `JackboxPartypackLauncher.exe` from [Releases](https://github.com/kimxnas/Jackbox-Partypack-Launcher/releases)
2. Run it — no install needed
3. Click **⚙** → **Game Paths** → **Auto-detect from folder…** and select your Jackbox games folder
4. (Optional) Switch to the modern UI and try **🎲 Find a Game** to get suggestions
5. Select a pack from the dropdown and hit **Play!**

> Settings are saved automatically in `%APPDATA%\JackboxLauncher`.

## Planned

- **Inno Setup installer** — proper Windows installer for instant startup (no extraction each launch)
- **Discord Rich Presence** — show what pack you're playing on your Discord status

## Build from source

```
pip install pillow customtkinter nuitka
python -m nuitka --standalone --onefile --windows-disable-console --enable-plugin=tk-inter --windows-icon-from-ico=icon.ico --onefile-tempdir-spec="%CACHE_DIR%/JackboxLauncher" --include-data-dir=game_images=game_images --include-data-files=icon.ico=icon.ico --include-module=ui_classic --include-module=ui_modern --include-module=shared --nofollow-import-to=numpy --nofollow-import-to=matplotlib --nofollow-import-to=setuptools launcher.py
```

The exe will be in the project root as `launcher.exe`.

Or just push a `v*` tag — GitHub Actions builds and uploads automatically.
