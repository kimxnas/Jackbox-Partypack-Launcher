# Direct Game Launch — Research & Implementation Notes

> **Status:** Researched, not yet implemented. Planned for future versions.

## What we want

Skip the in-pack menu and boot the user straight into a chosen Jackbox game (e.g. open `Pack 5.exe` directly into `You Don't Know Jack Full Stream`, bypassing the Pack 5 menu).

---

## Two completely different approaches

The Jackbox pack format split between Pack 7 and Pack 8:

| Packs | Engine | Launch method | Difficulty |
|-------|--------|---------------|------------|
| **1–7** | Adobe AIR / Flash (`.swf` files) | Hidden CLI argument | Easy |
| **8–10** | HTML5 / Electron-style | File replacement loaders | Harder |

---

## Approach 1 — Packs 1 to 7 (Flash-based)

### How it works
The pack's exe accepts an **undocumented CLI argument** that lets you specify which `.swf` to boot into directly. Jackbox shipped this for internal dev/QA testing and never officially removed it.

### Command format

```
"{pack_exe_path}" -launchTo games/{InternalName}/{InternalName}.swf -jbg.config isBundle=false
```

### Example

```cmd
"C:\Games\Jackbox Party Pack 2\The Jackbox Party Pack 2.exe" ^
  -launchTo games/Bidiots/Bidiots.swf ^
  -jbg.config isBundle=false
```

Boots straight into Bidiots, skipping the pack menu.

### URL encoding note
Slashes can be URL-encoded:
```
-launchTo games%2FBidiots%2FBidiots.swf
```
Raw forward slashes also work. Use whichever Python's `subprocess.Popen` handles cleanly — forward slashes are simpler.

### Internal name mapping

Each game has an `InternalName` — usually matches the display name with no spaces or punctuation. Examples:

| Display name | Internal name |
|---|---|
| You Don't Know Jack | `YDKJ` (verify) |
| Fibbage XL | `Fibbage` |
| Drawful | `Drawful` |
| Word Spud | `WordSpud` |
| Lie Swatter | `LieSwatter` |
| Quiplash | `Quiplash` |
| Bidiots | `Bidiots` |
| Earwax | `Earwax` |
| Fibbage 2 | `Fibbage2` |
| Bomb Corp | `Bomb` |
| Trivia Murder Party | `TriviaMurderParty` |
| Tee K.O. | `TeeKO` |

**To get exact names:** in each pack's install folder, look in `{install}/games/` — the subfolder names are the internal names. We should script extracting them on first run, or hardcode the table.

### Implementation

```python
# In GAME_INFO, add internal_name for each Pack 1-7 game:
"The Jackbox Party Pack 2": [
    {"name": "Bidiots", "internal_name": "Bidiots", "min": 2, "max": 6, "tags": {"drawing"}},
    ...
]

def launch_specific_game(pack_path, pack_name, internal_name):
    pack_num = extract_pack_number(pack_name)  # 1-7
    if pack_num > 7:
        raise NotImplementedError("Packs 8-10 require the loader approach")
    args = [
        str(pack_path),
        "-launchTo", f"games/{internal_name}/{internal_name}.swf",
        "-jbg.config", "isBundle=false",
    ]
    subprocess.Popen(args, cwd=str(Path(pack_path).parent), shell=False)
```

### Risks
- **Pack updates may break it** — if Jackbox patches a pack and renames internal SWFs, our hardcoded table breaks for that game. Unlikely but possible.
- **Different versions** of the same pack across Steam/Epic/standalone may have slightly different internal names.

---

## Approach 2 — Packs 8 to 10 (HTML5)

### Why it's harder
Packs 8+ ship as Electron-style HTML5 apps. The pack menu is JavaScript rendered in a webview. The exe doesn't accept `-launchTo` because there's no hardcoded route to a specific SWF — the menu is dynamic and routes via internal JS state.

### The loader approach

The known technique is to temporarily replace the pack's launcher files with pre-patched versions that auto-boot a specific game:

1. **Pre-built loader files** — small ZIP archives containing patched versions of the pack's launcher JS. Each game has its own loader ZIP that, when extracted into the pack folder, makes the pack auto-launch that specific game on next start.
2. **Loader content** — typically a modified `main.js`, `launcher.html`, or game config that:
   - Skips the menu render
   - Auto-calls the "launch game" function with the chosen game's ID
3. **Storage** — loader ZIPs are small (~KB each), either bundled with the launcher or fetched on demand.

### Full flow

```
1. User picks a specific game from Pack 8+
2. Fetch / locate the loader ZIP for that game
3. Backup original pack files (the launcher's JS/HTML) to a temp folder
4. Extract loader ZIP into pack folder (overwrites launcher files)
5. Launch Pack.exe normally
6. Pack auto-boots into the chosen game
7. When Pack exe exits (poll via tasklist):
   8. Restore original launcher files from backup
   9. Delete temp backup
```

### What we'd need to ship this

1. **Source loader ZIPs** — either build them ourselves (reverse-engineer each pack's launcher JS per game), bundle ones derived from existing community work (with attribution + license check), or fetch from a remote API.
2. **File backup/restore** — careful enough not to corrupt the user's pack files if launcher crashes mid-launch.
3. **Process detection** — `tasklist` polling on Windows to know when the pack closes.
4. **Cleanup safety net** — on startup, check if any pack folders have leftover loader files and restore them (in case last session crashed before restoring).
5. **Loader version mismatch handling** — when Jackbox patches a pack, loaders break until updated.

### Risks (bigger than Packs 1-7)

- **Pack file corruption** — if backup/restore fails partway, user's pack is broken until they re-install.
- **Updates** — Jackbox patches a pack → all loaders for that pack break until we ship new ones.
- **Server dependency** — if loaders are fetched remotely, our server going down = feature broken.
- **Storage** — loader files are small but multiplied by ~30 games = a few MB of cached patches.
- **Antivirus** — modifying game files on the fly may trigger Windows Defender / SmartScreen heuristics.

---

## Phased rollout plan

### v1.8 — Direct launch for Packs 1-7 (low risk)
- Add `internal_name` field to `GAME_INFO` entries for Packs 1-7
- New launch path: `launch_specific_game(pack, internal_name)` using the `-launchTo` argument
- Wire into Find a Game's "Random Pick" — pick a specific game, launch directly
- Wire into a new "Quick launch game" UI in modern (compact list of games per pack)
- For Packs 8-10 games: show "Menu only — pick from in-game menu" badge

### v2.x — Direct launch for Packs 8-10 (high risk, opt-in)
- Settings toggle: "Experimental: direct launch for Packs 8-10"
- Add the backup/restore/poll machinery
- Stress test on every pack before each release

### Decision point
For Packs 8-10, the cleaner long-term move might be to stay focused on the Packs 1-7 case where we can ship without server infrastructure or file-modification fragility. Maintaining a loader infrastructure for HTML5 packs is a real ongoing burden — it'd mean tracking every Jackbox pack patch and re-shipping loaders.

---

## References & prior art

This research drew on the open-source [JackboxUtility](https://github.com/JackboxUtility/JackboxUtility) project (Flutter/Dart), which has been doing both approaches in production for years. Their reverse-engineering work surfaced the `-launchTo` argument and the loader-ZIP pattern publicly.

Relevant files in their repo if implementing:
- `lib/services/launcher/launchers/native_pack_launcher.dart` — the `-launchTo` argument usage for Packs 1-7
- `lib/services/launcher/launcher.dart` — the loader extract/launch/restore orchestration for Packs 8-10
- `documentation/server/schema/packs/loader.json` — loader manifest schema
- [JackboxUtility-Extras](https://github.com/JackboxUtility/Jackbox-Utility-Extras/tree/main/Individual%20Game%20Shortcuts/English/Shortcuts) — community-maintained `.bat` shortcuts per game

Reading their code is the fastest way to validate any implementation choices we make.
