# Student Games

This folder is where students drop their pygame games so they show up in
the arcade cabinet's launcher menu. Every folder in here that contains a
`main.py` becomes a menu entry the next time the launcher starts.

**This folder is gitignored.** Anything you add inside `games/student/`
stays on the local cabinet only -- it will not appear on GitHub. The one
exception is this README, which is whitelisted in `.gitignore` so the
convention is documented for anyone cloning the repo.

## Adding a game (the minimum)

1. Make a new folder with a short, lowercase, hyphenated name. Example:
   `games/student/snake-clone/`.
2. Put your game's entry point inside it as `main.py`.
3. Run the launcher (`python main.py` from the repo root) and your game
   appears at the bottom of the carousel.

That's it. With no extra files, the launcher will:

* Use the folder name (title-cased, hyphens become spaces) as the menu label.
  `snake-clone` becomes `Snake Clone`.
* Show the attribution `CREATED BY UNKNOWN STUDENT`.
* Skip the preview screenshot (the launcher draws "PREVIEW NOT AVAILABLE"
  in the panel instead).

For a working zero-config example, see [`red-square/`](red-square/).

## Customizing the menu entry (optional `game.json`)

Drop a `game.json` next to your `main.py` to override any of the
defaults. Every field is optional -- skip the ones you don't need.

```json
{
    "label": "Snake Clone Deluxe",
    "attribution": "CREATED BY ALEX RIVERA",
    "preview": "preview.png",
    "limited_controller_support": true,
    "no_controller_support": false,
    "wonky_physics": false,
    "under_construction": false
}
```

| Field | What it does | Default |
|-------|--------------|---------|
| `label` | Menu name shown in the carousel. | Folder name, title-cased. |
| `attribution` | Blue text under the preview panel. Use `CREATED BY <YOUR NAME>` so Mr. Navarro knows who made it. | `CREATED BY UNKNOWN STUDENT` |
| `preview` | Path to a PNG/JPG screenshot, **relative to your game folder**. The launcher scales it into the preview panel. | No preview. |
| `no_controller_support` | Show the red "NO CONTROLLER SUPPORT" warning under the preview. | `false` |
| `limited_controller_support` | Show the red "LIMITED CONTROLLER SUPPORT" warning. Mutually exclusive with the above. | `false` |
| `wonky_physics` | Show the red "EXPECT WONKY PHYSICS" warning. | `false` |
| `under_construction` | Stamp "UNDER CONSTRUCTION" across the preview. | `false` |

For a working example with a manifest, see [`blue-circle/`](blue-circle/).

## What the launcher does at startup

1. Loads the curated sponsor games from `settings.GameSettings.OPTIONS`.
2. Creates `games/student/` if it doesn't exist (so a fresh GitHub clone
   runs without errors even with no student games installed).
3. Scans every subdirectory of `games/student/`. Any directory containing
   `main.py` becomes a menu entry; the optional `game.json` overrides
   metadata as documented above.
4. Appends the discovered games to the carousel in alphabetical folder
   order.

If a manifest is malformed (bad JSON, wrong types), the launcher silently
falls back to the defaults rather than crashing. Watch the launcher's
console output if you expect a customization to apply but don't see it.

## Running your game directly

From the repo root:

```
python games/student/your-folder/main.py
```

The launcher uses the same invocation under the hood, just with the game
folder as the working directory. If your game can find its assets when
run directly from the repo root, the launcher will be able to launch it
too.

## Tips

* Make sure ESC (or a pygame `QUIT` event) cleanly closes your window.
  The launcher waits for your subprocess to exit before redrawing the
  menu.
* Keep file paths relative to your `main.py` (use
  `Path(__file__).resolve().parent` as the base). Don't hard-code
  absolute paths -- they'll break on the cabinet.
* If you want to ship your game to GitHub eventually, ask Mr. Navarro to
  promote it into `games/sponsor/` and add an entry to
  `settings.GameSettings.OPTIONS`.
