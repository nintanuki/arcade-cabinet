# Arcade Cabinet Launcher — Architecture

This document explains **how the launcher code is put together and why**. It is meant for anyone touching the launcher — human or AI. It deliberately skips things any Pygame project does (open a window, fill a background, flip the buffer) and focuses on the parts that are specific to this launcher.

> **Maintenance rule:** every pass that meaningfully changes a system must update the matching section here. Out-of-date architecture docs are worse than none.

---

## 1. The shape of the program

```
                            +-------------------+
                            |   main.py         |
                            |   ArcadeLauncher  |   (thin coordinator)
                            +---------+---------+
                                      |
       +-----------------+------------+------------+--------------------+
       |                 |                         |                    |
       v                 v                         v                    v
  LauncherRenderer   LauncherCRT          discover_student_games    Input handlers
   (renderer.py)      (crt.py)               (discovery.py)         (in manager.py)
       |
       v
  fonts, logo, preview
  surfaces, hitboxes

  Data:  MenuNode  MenuFrame  StudentGameRecord  (models.py)
  Game launch: subprocess.run([python, game_main], cwd=game_folder)
```

`ArcadeLauncher` ([launcher/manager.py](../launcher/manager.py)) is intentionally thin. Its only jobs are:

- own the Pygame display, clock, audio, and connected controllers,
- build and walk the menu tree,
- drain the event queue and route each event to a small handler,
- launch a game by spawning a subprocess and restore the runtime when the game exits.

Anything that has its *own* state (rendering, CRT, student discovery, menu data) lives in its own module. `ArcadeLauncher` stitches them together; it does not implement them.

---

## 2. The frame loop

Each frame, in [`ArcadeLauncher.run`](../launcher/manager.py):

1. **Drain `pygame.event.get()`** and dispatch by event type:
   - `QUIT` → exit the loop.
   - `JOYBUTTONDOWN` → `handle_controller_buttons` (A/Start enter, B back, Select toggles fullscreen).
   - `JOYHATMOTION` → `handle_hat_navigation` (D-pad vertical).
   - `JOYAXISMOTION` → `handle_axis_navigation` (left-stick vertical with edge-triggered debounce).
   - `MOUSEMOTION` / `MOUSEBUTTONDOWN` → `handle_mouse` (hover highlights, click launches).
   - `KEYDOWN` → `handle_keyboard` (arrows/WS, Enter/Space, Esc, F11).
2. **`renderer.draw(...)`** paints background, header, current menu, preview panel, footer, status message (if active), and the CRT overlay on top.
3. **`clock.tick(ScreenSettings.FPS)`** caps the frame rate.

There is no separate `update()` step — the launcher is event-driven and renders per frame. The status-message timer is checked inside `draw_footer` and naturally falls back to the default footer when expired.

---

## 3. The menu tree

The menu is a tree of `MenuNode` objects (see [launcher/models.py](../launcher/models.py)) walked through a stack of `MenuFrame` objects. The shape of the tree is **declared as data** in [settings.py](../settings.py) under `MenuTreeSettings.ROOT`, so adding a new category is purely a settings change.

### 3.1 Building the tree

`ArcadeLauncher._build_games` produces a `dict[label, MenuNode]` of every available game by:

1. Iterating `GameSettings.OPTIONS` for sponsor games and inferring the category from the folder name (`games/sponsor/<category>/<game>/main.py`).
2. Calling `discover_student_games(games/student/)` for student games.
3. Attaching per-game metadata: preview image path, attribution caption, input-scheme key, free-form note, and under-construction flag.

`_build_root_items` then walks `MenuTreeSettings.ROOT` recursively. Each spec is either:

- `KIND_CATEGORY` → a leaf submenu whose children are all games matching the category key (filtered alphabetically via `_filter_games_by_category`).
- `KIND_GROUP` → a non-leaf submenu whose children are produced by recursing through `spec["children"]`.

### 3.2 Walking the tree

`menu_stack: list[MenuFrame]` is the navigation stack. `current_frame()` is the top, `current_node()` is the highlighted item inside it.

- `enter_selected_node` either launches the game or pushes a new `MenuFrame(items=node.children)`.
- `back_to_previous` pops one level. At the root, it returns `False` so `handle_keyboard` knows `Esc` should now quit.
- `_set_selected_index` wraps the index with modulo and plays the move SFX **only when the index actually changes**.

This is why backing out of a submenu and re-entering it lands on the same row: each `MenuFrame` carries its own `selected_index`.

---

## 4. Game discovery

Sponsor games and student games are merged into one dict, but the path to get there is intentionally different.

### 4.1 Sponsor games — declarative

Sponsor games are listed in `GameSettings.OPTIONS` as `(label, relative_path)` tuples. Their preview image, caption, input scheme, free-form note, and under-construction flag are all keyed by the same label in sibling dicts (`PREVIEW_IMAGES`, `GAME_DESCRIPTIONS`, `GAME_INPUT_SCHEMES`, `GAME_NOTES`, `UNDER_CONSTRUCTION_GAMES`). Adding a new sponsor game is a single edit to `settings.py`.

### 4.2 Student games — discovered

Student games live in `games/student/<folder>/`, which is **gitignored** so each cabinet keeps its own students' work. The launcher scans it at startup via [`discover_student_games`](../launcher/discovery.py) and produces one `StudentGameRecord` per folder containing a `main.py`. An optional `game.json` next to `main.py` overrides the auto-derived metadata; the schema and behavior is documented in [games/student/README.md](../games/student/README.md).

The launcher is **defensive** about student manifests: a missing or malformed `game.json` falls back to defaults rather than crashing, because one student's broken file must not brick the cabinet for everyone else. A typo in `input_scheme` is silently dropped (`InputSchemeSettings.LABELS` membership check). A missing preview file shows "PREVIEW NOT AVAILABLE" instead of an error.

---

## 5. Rendering

[`LauncherRenderer`](../launcher/renderer.py) owns every drawing concern: fonts, the JIL logo, preview surfaces, and the per-frame `menu_option_hitboxes` list used by mouse routing.

### 5.1 Layout

- **Header.** JIL logo + title + subtitle, centered as a single horizontal unit so the gap between the logo and the title (`LauncherSettings.JIL_LOGO_TITLE_SPACING`) stays constant regardless of title length.
- **Menu.** Either a vertical **carousel** (when `len(items) > MenuSettings.CAROUSEL_THRESHOLD`) or a static **list** with a `>` cursor (smaller menus). The threshold prevents two- to five-item submenus from wasting the on-screen real estate the carousel illusion needs.
- **Preview panel.** Right side, ~320 × 240 with rounded border. For game nodes it shows the scaled preview screenshot plus an "UNDER CONSTRUCTION" stamp when applicable; for submenu nodes it shows a wrapped description.
- **Caption + warning slots.** Two stacked slots under the preview. The optional input-scheme label (red, e.g. `LIMITED CONTROLLER SUPPORT`) takes slot 1; the optional free-form note takes slot 2. If only the note is present, it promotes into slot 1.
- **Footer.** Two hint lines at the bottom. When a status message is active, it temporarily replaces the second line.

### 5.2 Hitboxes

`menu_option_hitboxes` is rebuilt every frame to the size of the current frame's items so only currently visible items react to the mouse. Each hitbox is the rendered text rect inflated horizontally enough to cover the cursor.

### 5.3 Description highlights

`MenuSettings.DESCRIPTION_HIGHLIGHTS` is a phrase → color map (e.g. `"Mr. Navarro": LIGHT_PURPLE`, `"Clear Code": CYAN`). The renderer walks each description, prefers longer phrase matches when overlapping, and renders matched spans in their color and the rest in white. Source descriptions stay in sentence case and are uppercased only at render time.

---

## 6. Audio

Two SFX clips, both optional. `_load_sound_if_available` handles a missing file or absent mixer by returning `None`; `_play_move_sfx` / `_play_select_sfx` then silently no-op. This means the launcher never crashes on a missing audio file. The select SFX has a list of fallback candidates (`MENU_SELECT_SOUND_CANDIDATES`) so swapping the file for a new one is just a settings tweak.

The move SFX fires only on actual cursor movement (the index check inside `_set_selected_index` prevents repeated notes when navigation is held). The select SFX fires on every confirm, including on empty submenus, so players get audio feedback even when a category has no games yet.

---

## 7. Game launch and runtime restore

Launching a game is a four-step sequence inside `launch_selected_game`:

1. Play the select SFX, then run `show_loading_screen` for ~2.2 seconds with an animated `LOADING...` ellipsis. This both masks the perceived startup delay and lets the player feel the launcher acknowledged their input.
2. Validate that `node.main_path` exists and its parent folder exists. Failures call `show_status_message` and abort without tearing down the launcher.
3. `suspend_runtime` calls `pygame.display.quit() / pygame.joystick.quit() / pygame.quit()` so the child game has a clean slate to initialize Pygame on its own. The cabinet has only one display and audio device; we cannot share them.
4. `subprocess.run([sys.executable, game_main], cwd=game_main.parent, check=False)` runs the game in **its own folder as the working directory**. This is the contract that lets games use relative asset paths and stay agnostic to the launcher.

When the subprocess exits (game window closed, quit combo pressed, or the game crashes), control returns to the launcher and `_restore_runtime` rebuilds the display, joysticks, renderer, and preview cache. Previews must be reloaded because the old display context is gone — surfaces created against it would not blit correctly.

---

## 8. CRT overlay

[`LauncherCRT`](../launcher/crt.py) blits a TV-bezel image at a per-frame random alpha (`CRTSettings.ALPHA_RANGE`) for a subtle flicker, then draws horizontal scanlines on a *copy* of the bezel so the overlay does not accumulate between frames. It is the **last** thing drawn each frame, so scanlines sit on top of everything else, including the menu.

A missing bezel image falls back to a transparent surface so a missing-asset bug only loses the effect, not the launcher.

---

## 9. Settings as the only knob panel

[settings.py](../settings.py) is the single place every tunable lives. Each class groups one subsystem (`ScreenSettings`, `LauncherSettings`, `ColorSettings`, `FontSettings`, `MenuSettings`, `ControlSettings`, `CRTSettings`, `InputSchemeSettings`, `CategorySettings`, `GroupSettings`, `MenuTreeSettings`, `GameSettings`, `StudentGameSettings`). The rest of the codebase imports from here and never hard-codes a number.

Adding a new tunable? Put it in `settings.py` with a comment explaining its **units** and what changing it does. If a related cluster of new fields exists, prefer creating a new `*Settings` class over expanding an existing one with unrelated members.

---

## 10. Input model

Two parallel input paths share the same handlers, plus a mouse path:

- **Keyboard** events route through `handle_keyboard` (arrows/WS for navigation, Enter/Space to confirm, Esc for back-or-quit, F11 for fullscreen).
- **Controller** events split across `handle_controller_buttons`, `handle_hat_navigation`, and `handle_axis_navigation`. The axis handler uses an edge-triggered flag (`vertical_axis_engaged`) so holding the stick does not spam moves.
- **Mouse** events route through `handle_mouse`, which uses `LauncherRenderer.menu_option_hitboxes` to translate cursor position to a menu index. Hover sets the selection; left click sets the selection and confirms.

Connected controllers are cached once at `initialize_runtime` so frame handlers do not enumerate joysticks.

---

## 11. The game-folder contract

Games are **standalone** projects. The launcher's only assumptions about a game are:

- It has a `main.py` (sponsor games may use a different filename — see `GameSettings.OPTIONS` — but `main.py` is the convention).
- Running `python main.py` from the game's own folder starts the game.
- The game closes its window or `sys.exit()`s when the player wants to quit. Each game is also expected to implement its own `Start + Select + L1 + R1` quit combo for cabinet use.

Anything beyond that (engine, asset layout, save format, dependency choices) is the game's business. The launcher must never reach into a game folder.

---

## 12. Code conventions worth knowing

Most rules live in [.github/copilot-instructions.md](../.github/copilot-instructions.md). Two are worth surfacing here because they shape how files **look**:

**Section banners.** Inside any file with multiple logical groupings, sections are separated by an all-caps banner comment:

```python
    # ------------------------------------------------------------------
    # SECTION NAME
    # ------------------------------------------------------------------
```

This is what `manager.py` and `renderer.py` already use. Keep it consistent.

**Function order inside a class.** Functions are grouped by role (init, audio, menu construction, navigation, status, game launch, input handling, run loop). `update` and `run` go **last** and should only call other functions — they are coordinators, not implementations.

---

## 13. What's *not* here yet

The following systems will get their own sections in this document as they're built. If you're implementing one of these, please add the section as part of your pass:

- **Settings screen** (volume, CRT toggle, controller config, fullscreen default).
- **Attract mode** (idle demo loop after N seconds without input).
- **Per-game audio handoff** (currently each game manages its own audio device; consider a shared lock to prevent race conditions on cabinet hardware).
- **Hot reload of student games** (today the folder is scanned only at launcher startup; a periodic re-scan would let teachers add games without restarting the cabinet).
