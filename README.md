# Jackbox Party Pack Launcher

A clean, no-frills launcher for all 10 Jackbox Party Packs. Pick a pack, hit Play — that's it. Now with game suggestions based on player count and style.

![Launcher screenshot](screenshot.png)

## Download

Head to [**Releases**](https://github.com/kimxnas/Jackbox-Partypack-Launcher/releases) and grab the latest `JackboxPartypackLauncher.exe`. No install, no dependencies — just run it.

> ⚠️ Windows may show a "SmartScreen" warning since the exe isn't code-signed.
> Click **More info → Run anyway**. The source is open if you want to inspect it.

## Features

- **🎲 Find a Game** — slide-out panel that recommends specific Jackbox games based on player count and style (Trivia, Drawing, Comedy, Bluffing, Social, Music). List all matches or let it randomly pick one for you
- **Classic & Modern UI** — toggle between the original look and a sleek dark Jackbox-themed theme in settings
- **Game cover art** — shows the box art for whichever pack you've selected
- **Auto-detect** — point it at your games folder and it finds all the exes automatically
- **Per-game path config** — set or override any path individually via the ⚙ settings menu
- **Settings persist** — your paths and preferences live in `%APPDATA%\JackboxLauncher` and survive moves/updates
- **Close after launch** — optionally close the launcher once the game starts
- **Launch confirmation** — optional popup confirming the game launched

## How to use

1. Download `JackboxPartypackLauncher.exe` from [Releases](https://github.com/kimxnas/Jackbox-Partypack-Launcher/releases)
2. Run it — no install needed
3. Click **⚙** → **Auto-detect from folder…** and select your Jackbox games folder
4. (Optional) Switch to the modern UI and try **🎲 Find a Game** to get suggestions
5. Select a pack from the dropdown and hit **Play!**

> Settings are saved automatically in `%APPDATA%\JackboxLauncher`.

## Planned

- **Recently played** — track and quickly relaunch your most played packs
- **Check for updates** — built-in notification when a new release lands
- **Custom banners** — let users swap in their own header image

## Build from source

```
pip install pillow customtkinter nuitka
python -m nuitka --standalone --onefile --windows-disable-console --enable-plugin=tk-inter --windows-icon-from-ico=icon.ico --onefile-tempdir-spec="%CACHE_DIR%/JackboxLauncher" --include-data-dir=game_images=game_images --include-data-files=icon.ico=icon.ico launcher.py
```

The exe will be in the project root as `launcher.exe`.
