# Jackbox Party Pack Launcher

A clean, no-frills launcher for all 10 Jackbox Party Packs. Pick a game, hit Play — that's it.

![Launcher screenshot](screenshot.png)

## Download

Head to [**Releases**](https://github.com/kimxnas/Jackbox-Partypack-Launcher/releases) and grab the latest `JackboxPartypackLauncher.exe`. No install, no dependencies — just run it.

## Features

- **Game cover art** — shows the box art for whichever pack you've selected
- **Auto-detect** — point it at your games folder and it finds all the exes automatically
- **Per-game path config** — set or override any path individually via the ⚙ settings menu
- **Settings persist** — your paths and preferences are saved between sessions
- **Close after launch** — optionally close the launcher once the game starts
- **Launch confirmation** — optional popup confirming the game launched (can be turned off)

## How to use

1. Download `JackboxPartypackLauncher.exe` from [Releases](https://github.com/kimxnas/Jackbox-Partypack-Launcher/releases)
2. Run it — no install needed
3. Click **⚙** → **Auto-detect from folder…** and select your Jackbox games folder
4. Select a pack from the dropdown and hit **Play!**

> Settings (including game paths) are saved automatically in the background.

## Planned

- **Game recommendations** — suggest which pack to play based on player count or mood
- **Modernized UI** — optional sleek dark theme to replace the default look
- **Recently played** — track and quickly relaunch your most played packs
- **Custom banners** — let users swap in their own header image

## Build from source

```
pip install pillow pyinstaller
pyinstaller launcher.spec --noconfirm
```

The exe will be in `dist/JackboxPartypackLauncher.exe`.
