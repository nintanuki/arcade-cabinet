# Change Log

This file is an append-only record of every code change made to **Fishy**
by a human, AI assistant, or copilot tool. Read it before making changes so you know the current state of the codebase.

## Format

Each entry covers one logical change (which may touch multiple files). Use the
template below, with one `**File:** ... **Why:** ...` block per file touched.

    ## YYYY-MM-DD HH:MM — short summary

    **File:** path/to/file.py
    **Lines (at time of edit):** 38-52 (modified)
    **Before:**
        [old code]
    **After:**
        [new code]
    **Why:** explanation

## Conventions

* Line numbers reflect the file as it existed at the moment of the edit. Edits
  above shift line numbers below, so older entries will not match the current
  file. Never go back and "fix" old line numbers.
* Entries are append-only. Never delete history. If a later edit reverts an
  earlier one, write a new entry that references the original.
* For new files, write `(new file)` instead of a line range. The "Before"
  block can be omitted or marked `(file did not exist)`.
* For deletes, write `(deleted)` and put the removed code in "Before" with no
  "After" block.
* Keep "Before" / "After" blocks short. If a change is huge, summarize with a
  diff-style excerpt of the most important lines plus a sentence describing the
  rest, instead of pasting the entire file.
* New Entries should be BELOW this line, do not add new log entries to the top. These instructions must stay on top.

---

## 2026-05-07 — Generic-template cleanup pass

**File:** main.py
**Lines (at time of edit):** 12-31 (modified)
**Before:** `__init__` docstring referenced "the first dungeon level"; kept an unused `self.game_active = False`; called `set_mode((ScreenSettings.RESOLUTION), pygame.SCALED)` with redundant parens.
**After:** Generic docstring, no `game_active`, `set_mode(ScreenSettings.RESOLUTION, pygame.SCALED)`.
**Why:** Template was copy-pasted from a dungeon project; needed to be neutral so it can seed any new pygame project.
**Editor:** Bryan (Claude Opus 4.7)

**File:** main.py
**Lines (at time of edit):** 45-51 (modified)
**Before:** `reset_game` docstring was a 7-line block.
**After:** Tightened to a 4-line block with the same intent.
**Why:** Cosmetic; matches the docstring style of the rest of the file.
**Editor:** Bryan (Claude Opus 4.7)

**File:** main.py
**Lines (at time of edit):** 80-87 (modified)
**Before:** `_handle_keydown` only handled `F11`.
**After:** Added an `Esc` quit branch above the `F11` branch.
**Why:** So the template runs without a controller for development.
**Editor:** Bryan (Claude Opus 4.7)

**File:** settings.py
**Lines (at time of edit):** 22 (modified)
**Before:** `TITLE = "Mimic Dice"`
**After:** `TITLE = "Pygame Template"  # Replace with your project's name.`
**Why:** Generic placeholder for the template.
**Editor:** Bryan (Claude Opus 4.7)

**File:** settings.py
**Lines (at time of edit):** 58-66 (modified)
**Before:** `AssetPaths.TV = "assets/graphics/effects/tv.png"`; `DebugSettings.MUTE = False` duplicated `AudioSettings.MUTE`.
**After:** `AssetPaths.TV` is now `__file__`-relative via `os.path.join(os.path.dirname(__file__), ...)`; the duplicate `DebugSettings.MUTE` was removed.
**Why:** Cwd-relative paths break when launched via the arcade cabinet; duplicate mute flags caused ambiguity.
**Editor:** Bryan (Claude Opus 4.7)

**File:** crt.py
**Lines (at time of edit):** 1-3 (modified)
**Before:** `from settings import *`
**After:** `from settings import ScreenSettings, ColorSettings, AssetPaths`
**Why:** Explicit imports match `main.py` and make dependencies obvious.
**Editor:** Bryan (Claude Opus 4.7)

**File:** core/__init__.py
**Lines (at time of edit):** (new file)
**After:** `"""Core data classes and state machines for the game."""`
**Why:** Empty folders weren't tracked by git; gives the package a docstring and a stable home.
**Editor:** Bryan (Claude Opus 4.7)

**File:** systems/__init__.py
**Lines (at time of edit):** (new file)
**After:** `"""Gameplay systems (physics, AI, scoring, etc.)."""`
**Why:** Same as `core/__init__.py`.
**Editor:** Bryan (Claude Opus 4.7)

**File:** ui/__init__.py
**Lines (at time of edit):** (new file)
**After:** `"""User-interface widgets, screens, and HUD elements."""`
**Why:** Same as `core/__init__.py`.
**Editor:** Bryan (Claude Opus 4.7)

---

## 2026-05-08 — Documentation and docstring pass

**File:** README.md
**Lines (at time of edit):** 6 (modified)
**Before:** `"Sprites are placeholder colored squares — no art yet. No score, no title screen, no game-over screen."`
**After:** `"Fish are rendered as polygon shapes (diamond body + triangle tail) with a black square eye — no imported sprite art yet. No score or title screen."`
**Why:** Status section was outdated; polygon fish, eyes, and game-over screen have all been implemented.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** ~44 (modified)
**Before:** Eye "placed at `FishSettings.EYE_NOSE_OFFSET_RATIO` from the nose toward the body."
**After:** Eye "placed at the midpoint between the diamond body center and the nose tip."
**Why:** `EYE_NOSE_OFFSET_RATIO` is defined in `FishSettings` but is not used by `build_fish_surface`; the actual implementation computes the midpoint of `diamond_center_x` and `nose_x`.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** docs/TODO.md
**Lines (at time of edit):** ~68 (modified)
**Before:** `[ ] ScreenSettings.TITLE is still "Pygame Template"`
**After:** `[x] ScreenSettings.TITLE is still "Pygame Template"`
**Why:** `settings.py` already has `TITLE = "Fishy"`.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** settings.py
**Lines (at time of edit):** ~68 (modified)
**Before:** `# Add this to settings.py` comment above `class FishSettings`.
**After:** Comment removed.
**Why:** Stale scaffolding note left over from when the class was first written; inaccurate since `FishSettings` is already in `settings.py`.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** core/sprites.py
**Lines (at time of edit):** ~175 (modified)
**Before:** `def update(self):` with no docstring.
**After:** Added `"""Advance enemy fish position and remove it once it clears the screen."""`.
**Why:** Every function must have a docstring per coding conventions.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** main.py
**Lines (at time of edit):** ~182, ~190 (modified)
**Before:** `_update_world` and `_render_frame` had no docstrings.
**After:** Added one-line summary docstrings to both.
**Why:** Every function must have a docstring per coding conventions.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** utils/__init__.py
**Lines (at time of edit):** (new file)
**After:** `"""Pure helper functions and small utilities."""`
**Why:** Same as `core/__init__.py`.
**Editor:** Bryan (Claude Opus 4.7)

**File:** README.md, docs/ARCHITECTURE.md, docs/TESTING.md, docs/TODO.md
**Why:** Reflected the code changes above (Esc now wired, `__init__.py` files exist) and added a "first-run setup, delete this block afterwards" section to README + a delete-this-section instruction on the first-run checklist in docs/TODO.md.
**Editor:** Bryan (Claude Opus 4.7)

## 2026-05-07 — Initial gameplay implementation

**File:** core/sprites.py
**Lines (at time of edit):** (new file)
**After:** `Player` sprite (yellow square, arrow-key + left-stick movement, boundary clamping) and `Fish` sprite (red square, random size/speed, spawns from left or right edge, self-destructs off-screen).
**Why:** First gameplay pass — player and enemy sprites for the eat-or-be-eaten mechanic.
**Editor:** Bryan

**File:** systems/fish_manager.py
**Lines (at time of edit):** (new file)
**After:** `FishManager` with `spawn_fish`, `check_collisions` (eat smaller fish → grow player; eaten by larger fish → exit), and `grow_player`.
**Why:** Centralizes all fish lifecycle logic, keeping `GameManager` thin.
**Editor:** Bryan

**File:** settings.py
**Lines (at time of edit):** 50-55 (added)
**After:** Added `PlayerSettings` (SPEED, SIZE) and `FishSettings` (SPAWN_RATE, MIN_SIZE, MAX_SIZE, MIN_SPEED, MAX_SPEED, PLAYER_GROWTH_RATE).
**Why:** New gameplay systems need tunables; all magic numbers must live in settings.py.
**Editor:** Bryan

**File:** main.py
**Lines (at time of edit):** 1-170 (modified)
**After:** `GameManager.__init__` now creates `Player`, `all_sprites`, `enemy_sprites`, and `FishManager`. `_update_world` drives all three. `_render_frame` draws both sprite groups.
**Why:** Wire the new sprites and manager into the frame loop.
**Editor:** Bryan

## 2026-05-08 — Docs rewritten for Fishy

**File:** README.md
**Lines (at time of edit):** 1-60 (replaced)
**Before:** Template scaffold description with first-run setup instructions.
**After:** Describes Fishy — the eat-or-be-eaten game, its current status, controls, and links.
**Why:** Docs reflected the template origin, not the actual game.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 1-100 (replaced)
**Before:** Generic scaffold architecture with stub update/render descriptions.
**After:** Documents Player, Fish, FishManager, collision logic, and all current settings classes.
**Why:** Architecture had not been updated after gameplay was added.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

**File:** docs/TODO.md
**Lines (at time of edit):** 1-60 (replaced)
**Before:** Template first-run checklist.
**After:** Real roadmap with completed items, core polish tasks, difficulty/feel, visuals, audio, and known code-health items.
**Why:** TODO reflected the template, not the game's actual state and goals.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

**File:** docs/CHANGELOG.md
**Lines (at time of edit):** 3 (modified)
**Before:** `<RENAME ME — your project name>`
**After:** `Fishy`
**Why:** Project name was never filled in.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

**File:** docs/TESTING.md
**Lines (at time of edit):** 1-30 (replaced)
**Before:** Template smoke checks (background color, title bar, CRT).
**After:** Added gameplay checks: player moves, fish spawn and scroll, player grows on eat, session ends on being eaten.
**Why:** No gameplay tests existed after the initial gameplay pass was added.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

## 2026-05-08 — Pixel-perfect mask collision

**File:** core/sprites.py
**Lines (at time of edit):** 12 (Player.__init__), 82 (Fish.__init__) (modified)
**Before:** Neither sprite built a mask; collision relied on bounding-box rect overlap.
**After:** Both `Player.__init__` and `Fish.__init__` call `pygame.mask.from_surface(self.image)` after the surface is ready, storing it as `self.mask`.
**Why:** Fish are now polygon shapes on transparent surfaces; the bounding box contains large empty corners that triggered false collisions.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

**File:** systems/fish_manager.py
**Lines (at time of edit):** 45, 64 (modified)
**Before:** `spritecollide(player, self.sprite_group, False)` used default rect collision. `grow_player` did not rebuild the mask after resizing.
**After:** `spritecollide(..., pygame.sprite.collide_mask)` for pixel-accurate hits. `grow_player` calls `pygame.mask.from_surface(player.image)` after resizing so the mask stays in sync.
**Why:** Required to make the new mask-based collision actually work end-to-end.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

## 2026-05-08 — Fix fish tail direction; rename cryptic variables; improve comments

**File:** core/sprites.py
**Lines (at time of edit):** 54-91 (modified Fish.__init__)
**Before:** `tail = [(0, cy), (tail_w, 0), (tail_w, body_h)]` — triangle point was on the left, so the tail looked like a backwards arrowhead for a right-facing fish. Single-letter/abbreviated locals (`body_h`, `tail_w`, `total_w`, `cy`). Minimal comments.
**After:** `tail_points = [(0, 0), (0, body_height), (tail_width, center_y)]` — wide fan on the left, tip pointing right into the diamond. All locals renamed to full words (`body_height`, `tail_width`, `total_width`, `center_y`). Block comment explains the layout and what each point represents.
**Why:** Tail geometry was mirrored; variable names violated the project's readability rules; comments were not sufficient for a non-coder to follow the math.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

## 2026-05-08 — Draw fish as polygon shape (diamond body + triangle tail)

**File:** settings.py
**Lines (at time of edit):** 65-66 (added to FishSettings)
**After:** Added `BODY_HEIGHT_RATIO = 0.5` and `TAIL_WIDTH_RATIO = 0.33`.
**Why:** Fish shape proportions belong in settings.py as named constants, not as inline magic numbers.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

**File:** core/sprites.py
**Lines (at time of edit):** 41-66 (replaced Fish.__init__)
**Before:** `pygame.Surface((size, size))` filled solid red.
**After:** Transparent surface drawn with two `pygame.draw.polygon` calls — a flat left-pointing triangle (tail) and a flat diamond (body). `pygame.transform.flip` mirrors the surface for left-facing fish. `self.size` stored for accurate area comparisons.
**Why:** Visual representation of fish as a recognizable shape instead of a square.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

**File:** systems/fish_manager.py
**Lines (at time of edit):** 47, 62 (modified)
**Before:** `fish_area = fish.rect.width * fish.rect.height`; `growth_amount = fish.rect.width * ...`
**After:** `fish_area = fish.size * fish.size`; `growth_amount = fish.size * ...`
**Why:** The polygon bounding box no longer equals the conceptual fish size, so the stored `fish.size` attribute is used instead for consistent area comparisons and growth calculation.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

## 2026-05-08T17:35:08.8120954-04:00 — Stop restarting music every frame

**File:** main.py
**Lines (at time of edit):** 149 (removed)
**Before:** `self.audio.play_random_bgm() # move to functions later` was called every loop iteration in `GameManager.run()`.
**After:** Removed the per-frame call so background music is started by `AudioManager` initialization instead of being continuously reloaded.
**Why:** Reloading and replaying music each frame effectively prevented audible playback even after the path issue was fixed.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

## 2026-05-08T18:04:00-04:00 — Add pause + game-over states and fish-shape polish

**File:** settings.py
**Lines (at time of edit):** 25-55, 84-111 (modified)
**Before:** Screen title was still `"Pygame Template"`; no state/UI constants; no fish-eye constants; no pause SFX paths.
**After:** Title is `"Fishy"`; added `UiSettings` and `GameStateSettings`; added `PlayerSettings.COLOR`; added fish eye constants (`EYE_SIZE_RATIO`, `EYE_NOSE_OFFSET_RATIO`); added pause SFX asset paths.
**Why:** Centralize new pause/game-over and fish-eye behavior in `settings.py` and remove remaining template title.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

**File:** core/sprites.py
**Lines (at time of edit):** 6-163 (modified)
**Before:** Player was a yellow square; fish body geometry existed only in `Fish`; no eye drawing helper shared between sprites.
**After:** Added `build_fish_surface(size, color)` helper that renders tail/body polygons plus a black square eye. `Player` now uses fish geometry and gains a `grow()` method that preserves center while rebuilding image/mask. `Fish` now uses the shared helper.
**Why:** Implement player-shape task and fish-eye task consistently for both player and enemies.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

**File:** systems/fish_manager.py
**Lines (at time of edit):** 6-89 (modified)
**Before:** On losing collision, `check_collisions` called `pygame.quit()` + `sys.exit()` directly; growth rebuilt a yellow square image manually.
**After:** `update()` / `check_collisions()` return a boolean game-over signal instead of exiting; growth now calls `player.grow(...)`.
**Why:** Remove abrupt process exit and route outcome through `GameManager` state handling.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

**File:** systems/audio_manager.py
**Lines (at time of edit):** 27-168 (modified)
**Before:** No pause/unpause helpers and no pause SFX loading/playback methods.
**After:** Added safe pause SFX loading, `pause_music()`, `resume_music()`, `play_pause_in_sound()`, and `play_pause_out_sound()`.
**Why:** Support Enter-based pause transitions that stop/resume music and play explicit in/out sounds.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

**File:** main.py
**Lines (at time of edit):** 8-235 (modified)
**Before:** Single always-playing loop; collisions could terminate process through `FishManager`; no pause or game-over overlays; no Enter behavior.
**After:** Added state machine (`playing`, `paused`, `game_over`), mixer init, overlay font loading, centered overlay text rendering, Enter-driven pause/resume/restart transitions, and world update gating by state.
**Why:** Implement no-abrupt-exit game-over screen and pause workflow requested in TODO.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

**File:** docs/TODO.md, docs/ARCHITECTURE.md
**Lines (at time of edit):** TODO visual/core task checkboxes + architecture flow sections (modified)
**Before:** Four requested items were unchecked; architecture described immediate-exit loss and square player/fish visuals.
**After:** Marked four implemented TODO tasks complete and updated architecture docs to reflect the current state-driven loop and fish visuals.
**Why:** Documentation maintenance is required for meaningful system changes.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

## 2026-05-08T18:22:00-04:00 — Tune overlay text, eye position, and player facing direction

**File:** core/sprites.py
**Lines (at time of edit):** 36-141 (modified)
**Before:** Player sprite always rendered in the default right-facing orientation; eye position used a fixed nose-offset formula; growth rebuilt only one orientation.
**After:** Added player facing state with `_set_facing_direction(...)`, orientation updates on horizontal movement, and orientation persistence across growth. Eye placement now uses the midpoint between diamond-body center and nose.
**Why:** Fix visual direction feedback while moving left/right and nudge eyes slightly backward to better match requested placement.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

**File:** settings.py
**Lines (at time of edit):** 29-35 (modified)
**Before:** Overlay config included prompt text and separate large/small font sizes.
**After:** Simplified overlay config to single-line text only and one smaller `OVERLAY_FONT_SIZE`.
**Why:** Pause and game-over screens now display only one centered word each.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

**File:** main.py
**Lines (at time of edit):** 60-230 (modified)
**Before:** Pause/game-over overlays rendered a title plus a secondary prompt with vertical offsets.
**After:** Overlays render a single centered title (`PAUSED` or `GAME OVER`) with one shared, slightly smaller font and exact horizontal/vertical centering.
**Why:** Match the simplified overlay UX request and ensure true center alignment.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

## 2026-05-08T18:24:00-04:00 — Silence pygame Group typing mismatch in entity setup

**File:** main.py
**Lines (at time of edit):** 66-67 (modified)
**Before:** `self.all_sprites = pygame.sprite.Group(self.player)` triggered a strict type-checker mismatch with pygame stubs.
**After:** Create empty group then add player: `self.all_sprites = pygame.sprite.Group(); self.all_sprites.add(self.player)`.
**Why:** Preserve runtime behavior while clearing static diagnostics.
**Editor:** Bryan (GitHub Copilot — GPT-5.3-Codex)

## 2026-05-08T18:30:00-04:00 — Fix player growth being silently discarded

**File:** core/sprites.py
**Lines (at time of edit):** 57, 136-138 (modified)
**Before:**
    self.size = PlayerSettings.SIZE[0]  # int
    ...
    new_size = max(1, int(self.size + growth_amount))
    self.size = new_size
    self.base_image, _ = build_fish_surface(self.size, PlayerSettings.COLOR)
**After:**
    self.size = float(PlayerSettings.SIZE[0])
    ...
    self.size = max(1.0, self.size + growth_amount)
    self.base_image, _ = build_fish_surface(int(self.size), PlayerSettings.COLOR)
**Why:** `PLAYER_GROWTH_COEFFICIENT` is 0.10, so eating a small fish (size 8) yields `growth_amount = 0.8`. `int(16 + 0.8) = 16` — the size never changed. Storing `self.size` as float lets fractional growth accumulate across multiple fish until it crosses a whole pixel boundary.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)
