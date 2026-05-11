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

## 2026-05-09 — roadmap rewrite + documentation-truth rule

**File:** .github/copilot-instructions.md
**Lines (at time of edit):** Architecture rules section (added)
**After:**
    Added a "Documentation truth rules" subsection: code is the source of
    truth; the only legitimate doc-vs-code contradiction is an unfinished
    `[ ]` item in TODO.md; never change code to match a stale doc claim.
**Why:** Codifies the rule the user articulated — prevents future passes
from "fixing" code to match outdated documentation (e.g. a TESTING smoke
check that no longer reflects the actual game).

**File:** docs/TODO.md
**Lines (at time of edit):** Pass 1 through Pass 7 (rewritten)
**Before:** Pass 1-7 were short bullet outlines; included a Pass 3 with a
difficulty ramp, fish size tiers / palette tiering, ecosystem-destroyed
fail-state, and player-growth diminishing returns.
**After:**
    - Pass 1 expanded into spec-grade implementation notes for an LLM
      implementer (Scene base class, SceneManager, TitleScene with
      background fish, PlayScene with player drop-in animation,
      GameOverScene as a real scene, utils/text.py helper, Pygame-primitive
      visuals rule).
    - Pass 2 expanded with a full Score model, HUD widget, Leaderboard
      with strict initials-deduplication semantics, InitialsEntryScene
      (keyboard-typing AND arrow/D-pad letter cycling), LeaderboardScene
      that replaces the old GAME OVER screen.
    - Pass 3 reframed from "difficulty curve" to a "Levels" placeholder
      because the user wants difficulty to come from level design, not
      stat scaling. Player growing huge is the intended reward.
    - Removed: difficulty ramp, fish size tiers, ecosystem-destroyed end,
      growth diminishing returns. Screen-wrap moved to ideas/parking lot.
    - Renumbered downstream passes (Visuals → Pass 4, Audio polish → 5,
      Settings → 6).
**Why:** User clarified that a flat power curve is part of the appeal and
that difficulty should be designed per-level, not interpolated globally.
Pass 1+2 needed implementer-grade detail because a weaker LLM will be
doing the actual implementation.

**Editor:** GitHub Copilot (Claude Opus 4.7)

---


## 2026-05-09 — review pass: spawn-center fix, fullscreen-toggle DRY, doc refresh

**File:** core/sprites.py
**Lines (at time of edit):** Player.__init__ (anchor positioning)
**Before:**
    self.rect = self.image.get_rect()
    self.rect.topleft = (x, y)
    ...
    self._pos_x = float(x)
    self._pos_y = float(y)
**After:**
    self.rect = self.image.get_rect(center=(x, y))
    ...
    self._pos_x = float(self.rect.x)
    self._pos_y = float(self.rect.y)
**Why:** Caller (`GameManager._create_gameplay_entities`) passes screen-center coordinates and TESTING.md states the player should be centered at startup, but topleft anchoring offset the body by half its width/height plus the bow padding. `Player.grow` already re-anchors on center, so initial setup now matches.

**File:** main.py
**Lines (at time of edit):** new `_toggle_fullscreen`, `_handle_keydown`, `_handle_joybuttondown`
**Before:**
    # F11 fullscreen toggle is global and intentionally falls through so
    # other handlers still see the press.
    if event.key == pygame.K_F11:
        pygame.display.toggle_fullscreen()
        self.full_screen = not self.full_screen
    ...
    # BACK is the global fullscreen toggle and falls through.
    if event.button == InputSettings.JOY_BUTTON_BACK:
        pygame.display.toggle_fullscreen()
        self.full_screen = not self.full_screen
**After:**
    def _toggle_fullscreen(self) -> None:
        pygame.display.toggle_fullscreen()
        self.full_screen = not self.full_screen
    ...
    if event.key == pygame.K_F11:
        self._toggle_fullscreen()
    ...
    if event.button == InputSettings.JOY_BUTTON_BACK:
        self._toggle_fullscreen()
**Why:** Two identical two-line blocks were drifting risks for the `full_screen` flag. The "intentionally falls through" comments were also stale — neither handler has anything below the F11/BACK branch to fall through to.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** Section 5 (Input)
**Why:** Documents the new `_toggle_fullscreen` helper and that both keyboard and controller paths share it.

**Editor:** GitHub Copilot (Claude Opus 4.7)

---


## 2026-05-09 — code-health bug fixes: type annotation, collision logic, joystick caching, dead constants

**File:** core/sprites.py
**Lines (at time of edit):** build_fish_surface signature, Player.__init__, Player.input, Player.update
**Before:**
    ) -> tuple[pygame.Surface, int]:   # missing third return value
    self.size = float(PlayerSettings.SIZE[0])  # SIZE was a tuple; only index 0 used
    def input(self) -> None: ...  # re-queried pygame.joystick.Joystick(i) every frame
    def update(self) -> None: self.input()
**After:**
    ) -> tuple[pygame.Surface, int, int]:   # all three return values documented
    self.size = float(PlayerSettings.SIZE)   # SIZE is now a scalar int
    def input(self, joysticks: list) -> None: ...  # uses caller-supplied cached list
    def update(self, joysticks: list | None = None) -> None: self.input(joysticks or [])
**Why:** Incorrect annotation would mislead callers. Repeated Joystick(i) construction each frame was the open TODO item. SIZE tuple was redundant — only the width was ever used.

**File:** systems/fish_manager.py
**Lines (at time of edit):** check_collisions, collision size comparison
**Before:**
    player_area = player.rect.width * player.rect.height
    fish_area = fish.size * fish.size
    if player_area > fish_area:
**After:**
    if player.size > fish.size:
**Why:** The rect height includes the bow pixels, inflating the player's apparent area relative to enemies. Both player.size and fish.size are the same unit (body width in px), so the comparison is now apples-to-apples.

**File:** settings.py
**Lines (at time of edit):** FishSettings, PlayerSettings, UiSettings, DebugSettings
**Before:**
    EYE_NOSE_OFFSET_RATIO = 0.25   # defined but never read anywhere in the codebase
    SIZE = (16, 16)                 # tuple; only index [0] used
    DRAG = 0.95  # comment said "0.88 brings fish to zero in ~35 frames" — stale
    class DebugSettings:  # body was empty — no pass
        """..."""
**After:**
    EYE_NOSE_OFFSET_RATIO removed
    SIZE = 16
    DRAG = 0.95  # comment corrected: "0.95 brings fish to zero in ~60 frames"
    class DebugSettings:
        """..."""
        pass
**Why:** Dead constants and stale comments. DebugSettings without a body is a syntax edge-case that some linters flag.

**File:** main.py
**Lines (at time of edit):** _update_world
**Before:**
    self.all_sprites.update()
**After:**
    self.all_sprites.update(joysticks=self.connected_joysticks)
**Why:** Passes the cached joystick list so Player.input() no longer re-queries pygame.joystick.

**File:** docs/TESTING.md
**Lines (at time of edit):** items 3, 10, 13
**Before:**
    "Background is `ColorSettings.BG_COLOR` (blue)."
    "The player (yellow fish polygon with a black eye)..."
    "Fish (red fish polygons with black eyes)..."
**After:**
    Descriptions updated to match the current visual: ocean gradient background,
    yellow-to-orange gradient player with pink bow, retro-palette enemies with shadows.
**Why:** Smoke-check descriptions were stale after the retro visual pass.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** Section 5, Input
**Before:**
    "Player movement from the analog stick is polled directly in Player.input() each frame..."
**After:**
    Added that GameManager passes connected_joysticks to all_sprites.update(joysticks=...) so
    Player.input() no longer re-queries pygame.joystick internally.
**Why:** Architecture doc must reflect the joystick-caching fix.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)


## 2026-05-09 — bug fixes, function consolidation, guardrail rules

## 2026-05-09 — Initials/leaderboard UI polish + HUD redesign

**File:** settings.py
**Lines (at time of edit):** ColorSettings, UiSettings (modified)
**Before:**
    HIGH_SCORE_LABEL = "HI: " in UiSettings; no GRAY color; no INITIALS_* layout constants; no HUD_FONT_SIZE_SMALL.
**After:**
    Removed HIGH_SCORE_LABEL (dead after HUD center change).
    Added ColorSettings.GRAY = (140, 140, 140).
    Added UiSettings.HUD_FONT_SIZE_SMALL = 16.
    Added initials entry layout constants: INITIALS_TITLE_Y_RATIO, INITIALS_SCORE_Y_RATIO,
    INITIALS_PROMPT_Y_RATIO, INITIALS_SLOTS_Y_RATIO, INITIALS_SLOT_GAP.
**Why:** User requested tunable Y positions and font sizes for each line of the initials
    entry screen. Smaller HUD font needed for compact in-game display.

**File:** ui/scenes/initials_entry_scene.py
**Lines (at time of edit):** render, _draw_slots (modified)
**Before:**
    Rendered "SCORE: NNNNN" label and "PRESS START WHEN DONE" footer.
    Active slot highlighted with a white box outline (pygame.draw.rect width=2).
    Y positions were hardcoded offsets from screen center.
**After:**
    Score line shows the number only (no "SCORE:" prefix).
    "PRESS START WHEN DONE" line removed.
    Active slot uses color + underline: active letter in WHITE with a 3px underline bar;
    inactive letters in GRAY. No box drawn.
    Y positions driven by INITIALS_*_Y_RATIO constants from settings.
**Why:** User found the box cluttered and the footer redundant; wanted tunable layout.

**File:** ui/scenes/leaderboard_scene.py
**Lines (at time of edit):** render, _draw_entries (modified)
**Before:**
    Rendered "SCORE: NNNNN" subheader at y=130; entries started at y=175.
    Highlighted row used a white background rect (white box) with black text.
**After:**
    "SCORE: NNNNN" subheader removed. Entries start at y=120 to close the gap.
    White box removed; highlighted row now uses YELLOW text.
**Why:** User found the score text was obscured by the highlight box; wanted both removed.

**File:** ui/hud.py
**Lines (at time of edit):** entire file (modified)
**Before:**
    Center: HI score from leaderboard. Right: SCORE. No timer. Leaderboard dependency.
**After:**
    Center: SCORE (player's current run score). Right: TIME MM:SS (counts up).
    leaderboard parameter and _high_score_text removed.
    draw() accepts a seconds: int = 0 parameter for the timer display.
**Why:** User requested score in center and a running timer on the right.

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** __init__, update, render (modified)
**Before:**
    HUD font used HUD_FONT_SIZE (24pt). Hud constructed with leaderboard kwarg.
    hud.draw(screen) called with no arguments.
**After:**
    HUD font uses HUD_FONT_SIZE_SMALL (16pt). Hud constructed without leaderboard.
    _elapsed_frames counter increments each ACTIVE frame.
    hud.draw(screen, self._elapsed_frames // ScreenSettings.FPS) passes elapsed seconds.
**Why:** Smaller HUD text; wires the new timer into the draw call.

**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** main.py
**Lines (at time of edit):** ~118-128 (reset_game consolidated), ~183 (enter key), ~190 (start button), ~248 (game-over render), ~255-262 (_draw_centered_overlay)
**Before:**
    reset_game() raised NotImplementedError; restart_session() held the real logic.
    _handle_enter_key / _handle_start_button called self.restart_session().
    game-over render: self._draw_centered_overlay(GAME_OVER_TEXT, RESTART_PROMPT_TEXT)
    _draw_centered_overlay accepted an optional subtitle_text and loaded subtitle_font.
**After:**
    reset_game() now holds the real restart logic (dead stub and restart_session removed).
    Call sites updated to self.reset_game().
    game-over render: self._draw_centered_overlay(GAME_OVER_TEXT) — no prompt.
    _draw_centered_overlay simplified back to a single centered line.
    subtitle_font removed from _load_fonts.
**Why:** restart_session was created by a previous AI session instead of updating the existing reset_game function — violating the project rule about not renaming things without cause. Restart prompt was added by a previous AI session without being asked for.

**File:** settings.py
**Lines (at time of edit):** UiSettings class (modified)
**Before:**
    RESTART_PROMPT_TEXT = "PRESS ENTER TO RESTART"
    SUBTITLE_FONT_SIZE = 20
**After:**
    (both removed)
**Why:** Only existed to support the unwanted restart prompt.

**File:** docs/TESTING.md
**Lines (at time of edit):** item 16 (modified)
**Before:**
    "...`GAME OVER` + restart prompt text..."
**After:**
    "...`GAME OVER` text (no abrupt process exit, no additional prompt)."
**Why:** Documentation was stale; reflected the removed restart prompt.

**File:** .github/copilot-instructions.md
**Lines (at time of edit):** Code style section and UI text section (modified)
**Before:**
    No rule about checking for existing functions before creating new ones.
    No rule about not adding unrequested UI elements.
**After:**
    Added: "Before creating a new function, search the file for an existing function with a similar purpose..."
    Added: "Do not add, remove, or modify any in-game UI element, text string, or screen layout unless the user explicitly asks for it."
**Why:** Two guardrail rules added to prevent recurrence of the restart_session renaming and unwanted restart prompt patterns.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

---

## 2026-05-09 — retro visual pass: gradient background, fish shadow, player gradient, retro palette

**File:** settings.py
**Lines (at time of edit):** 3-16 (modified ColorSettings), 104-107 (modified PlayerSettings), 127-131 (modified FishSettings)
**Before:**
    DARK_TURQUOISE = (5, 195, 221)
    BG_COLOR = DARK_TURQUOISE
    ...
    COLOR = (255, 255, 0)
**After:**
    DARK_TURQUOISE = (5, 195, 221)
    RETRO_CORAL/MINT/LAVENDER/PEACH/LIME/SKY palette constants added
    FISH_PALETTE list added
    BG_COLOR_TOP = (60, 180, 210) / BG_COLOR_BOTTOM = (10, 30, 70) added
    BG_COLOR = DARK_TURQUOISE (kept for fallback)
    COLOR replaced by COLOR_TOP = (255,240,60) / COLOR_BOTTOM = (255,130,0)
    SHADOW_OFFSET = 2 added to FishSettings
**Why:** All visual constants live in settings.py per architecture rules. New gradient colors needed named constants rather than magic numbers.

**File:** core/sprites.py
**Lines (at time of edit):** 1 (new import), 6-61 (build_fish_surface rewritten), 74 (Fish color), 120-122 (Player init), 268-270 (Player.grow)
**Before:**
    def build_fish_surface(size, color) — flat fill, no shadow
    Fish: ColorSettings.RED
    Player: PlayerSettings.COLOR (solid yellow)
**After:**
    def build_fish_surface(size, color, color2=None) — drop shadow always; gradient fill when color2 given
    Fish: random.choice(ColorSettings.FISH_PALETTE)
    Player: PlayerSettings.COLOR_TOP, COLOR_BOTTOM (yellow→orange gradient)
**Why:** Drop shadow separates fish from background without changing the polygon silhouette. Gradient player is visually unique vs solid-color enemies. Retro palette gives each enemy distinct color without tying color to size.

**File:** main.py
**Lines (at time of edit):** 17 (new function), 51-54 (bg_surface init), 197 (render)
**Before:**
    self.screen.fill(ColorSettings.BG_COLOR)
**After:**
    build_gradient_surface() pre-renders an ocean depth gradient once at startup.
    _render_frame blits self.bg_surface instead of filling with a flat color.
**Why:** Vertical gradient (sunlit aqua → deep navy) adds depth cue and makes the retro look easier on the eyes without any sprite art.

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

## 2026-05-09T17:24:51-04:00 — Pass 2.2 HUD widget implementation

**File:** ui/hud.py
**Lines (at time of edit):** (new file)
**After:**
    Added `Hud` class with `draw(screen)` and top-line layout:
    - left: `FISH: NN`
    - center: `HI: NNNNN  XYZ` or `HI: -----`
    - right: `SCORE: NNNNN`
**Why:** Implements the next unchecked roadmap task (Pass 2.2) with a dedicated gameplay HUD widget.

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** 10-18 (imports), 34-47 (HUD init), 187-191 (HUD render call)
**Before:**
    PlayScene rendered only background + sprites during active play.
**After:**
    PlayScene now creates a HUD font + `Hud` instance and calls
    `self.hud.draw(screen)` only while in `ACTIVE` state.
**Why:** Ensures the HUD appears during gameplay while remaining hidden during pause and non-play scenes.

**File:** settings.py
**Lines (at time of edit):** 52-60 (UiSettings constants)
**Before:**
    No dedicated HUD font or padding constants.
**After:**
    Added:
    - `HIGH_SCORE_LABEL = "HI: "`
    - `HUD_FONT_SIZE = 24`
    - `HUD_PADDING = 16`
**Why:** Keeps HUD text labels and spacing tunables centralized in settings and avoids magic numbers.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** PlayScene render notes, Score/Hud section, settings table, source tree, extension points
**Before:**
    HUD was listed as a future extension point and not described as a system.
**After:**
    Documented `Hud` ownership, layout, and draw order, and updated architecture references to match implementation.
**Why:** Maintains architecture docs as source-of-truth after a system-level change.

**File:** docs/TODO.md
**Lines (at time of edit):** Pass 2.2 checkbox
**Before:**
    `- [ ] Create ui/hud.py ...`
**After:**
    `- [x] Create ui/hud.py ...`
**Why:** Marks completion of the implemented roadmap item.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-11T14:00:00-04:00 — ratio-based time bonus to fix trivial late-game hunger

**File:** settings.py
**Lines (at time of edit):** 222-231 (modified)
**Before:**
    # Base seconds added per pixel of fish width when the player eats it.
    SECONDS_PER_FISH_PIXEL = 0.4
    # Minimum ratio ... value of 0.1 ...
    TIMER_MIN_RATIO = 0.05
**After:**
    # Seconds added for eating a fish exactly the player's own size.
    SECONDS_PER_EAT = 6
    # Minimum ratio ... value of 0.05 ...
    TIMER_MIN_RATIO = 0.05
**Why:** The old formula multiplied the absolute fish-size in pixels by SECONDS_PER_FISH_PIXEL, so a large player eating a large peer could gain 80+ seconds per eat, making the hunger meter trivial. The new constant is ratio-only: bonus = effective_ratio × SECONDS_PER_EAT. Eating a peer always gives the same seconds regardless of size, keeping the timer meaningful in the late game. Lowering TIMER_MIN_RATIO alone did not fix this because it only affects the floor for tiny fish, not the absolute-size explosion.

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** 227-234 (modified)
**Before:**
    self._remaining_time_seconds += (
        fish_size * TimerSettings.SECONDS_PER_FISH_PIXEL * effective_ratio
    )
**After:**
    self._remaining_time_seconds += (
        effective_ratio * TimerSettings.SECONDS_PER_EAT
    )
**Why:** Implements the ratio-only formula — absolute fish size no longer appears in the bonus calculation.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 77 (modified)
**Before:**
    Time bonus formula referenced SECONDS_PER_FISH_PIXEL and said TIMER_MIN_RATIO default was 0.1.
**After:**
    Updated to describe ratio-only formula and correct TIMER_MIN_RATIO default of 0.05.
**Why:** Keep docs in sync with code.

**Editor:** GitHub Copilot (Claude Sonnet 4.6)

---

## 2026-05-11T12:40:42-04:00 — prevent tally lines from shifting during reveal

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** 171-179 in `render` (modified)
**Before:**
    `block_width` was computed from only currently visible lines, so when a
    wider line appeared later, `block_left_x` changed and previously drawn
    lines appeared to jump left.
**After:**
    `block_width` is computed from all tally lines up front (including rows not
    yet visible), then a fixed `block_left_x` is used for every reveal step.
**Why:** Keeps the centered left-justified tally block visually stable while rows pop in one-by-one.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-11T12:37:18-04:00 — centered outcome restored; centered left-justified tally block

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** 148-187 (modified)
**Before:**
    Outcome text used a left-edge anchor (`midleft`) and appeared left-aligned.
    Tally lines also used a left-edge anchor tied to generic HUD padding.
    Final score row shared the same vertical rhythm as the tally rows.
**After:**
    Outcome text now uses a true centered anchor (`center=(WIDTH//2, HEIGHT//2)`).
    Tally lines are rendered into a centered block with a shared computed left
    edge (`block_left_x`), so each line is left-justified while the whole
    group remains centered on-screen.
    Added an explicit extra gap before the final TOTAL SCORE row.
**Why:** User requested a centered composition with left-justified tally text shape, while restoring centered outcome messaging and adding clearer separation before the final score.

**File:** settings.py
**Lines (at time of edit):** 87-90 (modified)
**Before:**
    TALLY_LINE_START_Y_RATIO = 0.34
    (no dedicated extra-gap constant before total row)
**After:**
    TALLY_LINE_START_Y_RATIO = 0.30
    TALLY_TOTAL_TOP_GAP = 24
**Why:** Moves the tally block upward and adds tunable spacing between the stat lines and the final total line.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-11T12:33:19-04:00 — left-aligned tally text, non-padded values, and larger total row

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** 17-187 (modified)
**Before:**
    from utils.text import draw_centered_text
    ...
    f"+ NUMBER OF FISH EATEN: ... ({fish_points:05d})"
    ...
    f"TOTAL SCORE = {self.score.total:05d}!"
    ...
    draw_centered_text(... center=(ScreenSettings.WIDTH // 2, ...))
**After:**
    (removed centered-text helper import from this scene)
    ...
    f"+ NUMBER OF FISH EATEN: ... ({fish_points})"
    ...
    f"TOTAL SCORE = {self.score.total}!"
    ...
    Outcome and tally lines are rendered via font surfaces with `midleft`
    anchors using `UiSettings.HUD_PADDING` so all text is left-aligned.
    Final total row uses `self._tally_total_font` for larger text.
**Why:** Requested UI polish for the new tally scene: left alignment, no trailing zero padding in numeric output, and stronger visual emphasis on the final TOTAL SCORE line.

**File:** settings.py
**Lines (at time of edit):** 89 (modified)
**Before:**
    (no dedicated total-row font-size setting for game-over tally)
**After:**
    TALLY_TOTAL_FONT_SIZE = 36
**Why:** Keeps the larger final-score row size configurable in settings and avoids hardcoded font-size values in scene code.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T23:44:00-04:00 — outcome text colors for loss/win messaging

**File:** settings.py
**Lines (at time of edit):** 51-52 (modified)
**Before:**
    EATEN_BY_BIGGER_FISH_TEXT = "YOU WERE EATEN BY A BIGGER FISH"
    ATE_ALL_FISH_TEXT = "YOU'VE EATEN ALL THE FISH!"
**After:**
    EATEN_BY_BIGGER_FISH_TEXT = "YOU WERE EATEN BY A BIGGER FISH"
    ATE_ALL_FISH_TEXT = "YOU'VE EATEN ALL THE FISH!"
    EATEN_BY_BIGGER_FISH_COLOR = ColorSettings.RED
    ATE_ALL_FISH_COLOR = ColorSettings.GREEN
**Why:** Adds dedicated UI color settings so end-of-run outcome text can be styled by outcome without hardcoding colors in scene logic.

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** 88-95, 129 (modified)
**Before:**
    draw_centered_text(..., color=ColorSettings.WHITE, ...)
**After:**
    Added `_current_message_color()` to return:
    - white for GAME OVER phase
    - `UiSettings.ATE_ALL_FISH_COLOR` for victory
    - `UiSettings.EATEN_BY_BIGGER_FISH_COLOR` for loss
    and render now uses `color=self._current_message_color()`.
**Why:** Implements requested behavior: loss message in red and victory message in green while preserving white GAME OVER text.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T23:35:00-04:00 — debug toggle for large player start (end-game testing)

**File:** settings.py
**Lines (at time of edit):** 260-268 (modified)
**Before:**
    class DebugSettings:
        """Settings related to debugging features."""
        pass
**After:**
    class DebugSettings:
        """Settings related to debugging features."""

        START_LARGE_PLAYER = False
        LARGE_PLAYER_SIZE = 640
**Why:** Adds a single debug switch and tunable size so testers can spawn as a larger fish and reach the end-game flow faster without changing normal gameplay defaults.

**File:** core/sprites.py
**Lines (at time of edit):** 6-13 (imports), 160-169 (`Player.__init__`) (modified)
**Before:**
    from settings import ColorSettings, FishSettings, InputSettings, PlayerSettings, ScreenSettings
    ...
    self.size = float(PlayerSettings.SIZE)
**After:**
    from settings import (..., DebugSettings, ...)
    ...
    starting_size = (
        DebugSettings.LARGE_PLAYER_SIZE
        if DebugSettings.START_LARGE_PLAYER
        else PlayerSettings.SIZE
    )
    self.size = float(starting_size)
**Why:** Wires the new debug settings into player initialization so the larger start is opt-in and isolated to debug configuration.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 192 (modified)
**Before:**
    | `DebugSettings`  | Debug-only toggles.                                                   |
**After:**
    | `DebugSettings`  | Debug-only toggles (including optional large-player start for end-game testing). |
**Why:** Keeps architecture docs aligned with runtime behavior after adding the new debug toggle.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T22:10:00-04:00 — initials/leaderboard readability pass (requested UI polish)

**File:** ui/scenes/initials_entry_scene.py
**Lines (at time of edit):** `render`, `_draw_slots` (modified)
**Before:**
    Header used large "NEW HIGH SCORE" on one line with score on a separate line.
    "ENTER YOUR INITIALS" rendered in white.
    Active slot was white with an extra underline bar.
**After:**
    Header now uses HUD-size text and renders as one row: `NEW HIGH SCORE:` + score value.
    Score value is yellow; prompt text `ENTER YOUR INITIALS` is light blue.
    Active slot highlight is yellow text only; underline removed.
**Why:** Reduce clutter and improve visual hierarchy while keeping active-character focus clear.

**File:** settings.py
**Lines (at time of edit):** `UiSettings` (modified)
**Before:**
    No constant for title/score inline spacing or leaderboard first-row spacing.
**After:**
    Added `INITIALS_TITLE_SCORE_GAP` and `LEADERBOARD_ENTRIES_START_Y`.
    Removed unused `INITIALS_SCORE_Y_RATIO` after moving to a single-line header row.
**Why:** Keep layout tuning in settings and avoid dead constants.

**File:** ui/scenes/leaderboard_scene.py
**Lines (at time of edit):** `_draw_entries` (modified)
**Before:**
    First leaderboard entry started at fixed y=120.
**After:**
    First leaderboard entry now starts at `UiSettings.LEADERBOARD_ENTRIES_START_Y` (150 default).
**Why:** Adds more padding between `GAME OVER` and the first leaderboard row.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T21:05:00-04:00 — architecture guardrail: lock title screen layout

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 281-284 (modified)
**Before:**
    Project rules only documented the no-imported-visual-assets rule.
**After:**
    Added explicit title-screen lock rule: keep `TitleScene` to exactly two centered lines
    (`MS. FISHY` and `PRESS START TO PLAY`) over ocean background + background fish,
    and do not add score/high-score/extra prompts unless explicitly requested by the user.
**Why:** Mirrors the same guardrail already added to copilot instructions so future changes do not reintroduce unwanted title-screen text.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T17:43:19-04:00 — title screen lock: remove HI line and document guardrail

**File:** ui/scenes/title_scene.py
**Lines (at time of edit):** 54-61, 108-123 (modified)
**Before:**
    Title scene included `_high_score_text()` and rendered a third line below the start prompt,
    showing either `HI: NNNNN  XYZ` or `HI: -----`.
**After:**
    Removed `_high_score_text()` and removed the third centered draw call.
    Title scene now renders only `MS. FISHY` and `PRESS START TO PLAY`.
**Why:** User explicitly requested removing `HI: -----` from the title screen and keeping the title layout minimal.

**File:** settings.py
**Lines (at time of edit):** 54 (modified)
**Before:**
    `UiSettings` included `TITLE_HIGH_SCORE_OFFSET_RATIO` for the title-screen HI row.
**After:**
    Removed `TITLE_HIGH_SCORE_OFFSET_RATIO`.
**Why:** Constant became unused after removing the title-screen HI row.

**File:** .github/copilot-instructions.md
**Lines (at time of edit):** 76 (modified)
**Before:**
    General UI-change guardrail existed, but no explicit title-screen lock.
**After:**
    Added explicit rule: keep `TitleScene` to exactly two centered lines (`MS. FISHY` and
    `PRESS START TO PLAY`) over ocean background + background fish unless user explicitly requests otherwise.
**Why:** Prevents future Copilot sessions from reintroducing title-screen extras without direct user instruction.

---

## 2026-05-09T18:47:18-04:00 — settings CRT toggle for testing and pybag

**File:** settings.py
**Lines (at time of edit):** 264-272 (modified)
**Before:**
    class DebugSettings:
        """Settings related to debugging features."""
        START_LARGE_PLAYER = False
        LARGE_PLAYER_SIZE = 640
**After:**
    class DebugSettings:
        """Settings related to debugging features."""

        ENABLE_CRT = True
        START_LARGE_PLAYER = False
        LARGE_PLAYER_SIZE = 640
**Why:** Adds a single settings-level switch to disable the CRT overlay for pybag runs or quick testing without changing runtime code.

**File:** main.py
**Lines (at time of edit):** 11-17, 47-50, 175-176 (modified)
**Before:**
    from settings import (...)
    self.crt = CRT(self.screen)
    if not self.full_screen:
        self.crt.draw()
**After:**
    from settings import (..., DebugSettings, ...)
    self.crt_enabled = DebugSettings.ENABLE_CRT
    self.crt = CRT(self.screen) if self.crt_enabled else None
    if self.crt_enabled and not self.full_screen and self.crt is not None:
        self.crt.draw()
**Why:** Keeps the CRT decision at the game-manager render boundary and skips loading the overlay asset entirely when disabled.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 174, 192 (modified)
**Before:**
    CRT section described windowed-only rendering but not a settings kill switch.
    DebugSettings was documented only as a large-player testing bucket.
**After:**
    CRT section now documents `DebugSettings.ENABLE_CRT` as the construction gate.
    DebugSettings is documented as owning both CRT and large-player debug toggles.
**Why:** Architecture documentation now matches the runtime control point for the CRT overlay.

**File:** docs/TESTING.md
**Lines (at time of edit):** 18, 22 (modified)
**Before:**
    CRT overlay is visible (scanlines + slight flicker).
    `F11` toggles fullscreen. CRT overlay disappears in fullscreen, reappears in windowed.
**After:**
    CRT visibility checks are conditional on `DebugSettings.ENABLE_CRT`.
    Fullscreen CRT expectations are only asserted when the CRT toggle is enabled.

---

## 2026-05-11T12:30:14-04:00 — game-over stat tally reveal and direct leaderboard handoff

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** 20-178 (modified)
**Before:**
    class GameOverScene(Scene):
        """Two-step end-of-run scene before leaderboard routing.

        Step 1 displays the outcome text (loss or victory). After confirm, step 2
        displays GAME OVER. A second confirm routes to InitialsEntryScene or
        LeaderboardScene based on leaderboard qualification.
        """

    def _advance_flow_action(self) -> None:
        if self._phase == self._PHASE_OUTCOME_MESSAGE:
            self._phase = self._PHASE_GAME_OVER_MESSAGE
            return
        self._route_to_post_game_scene()

    def _route_to_post_game_scene(self) -> None:
        if self.score is not None and self.game.leaderboard.qualifies(self.score.total):
            from ui.scenes.initials_entry_scene import InitialsEntryScene
            self.game.scenes.change_to(InitialsEntryScene(self.game, self.score))
        else:
            from ui.scenes.leaderboard_scene import LeaderboardScene
            self.game.scenes.change_to(LeaderboardScene(self.game, self.score))
**After:**
    class GameOverScene(Scene):
        """Outcome message then timed stat tally before leaderboard routing."""

    def _advance_flow_action(self) -> None:
        if self._phase == self._PHASE_OUTCOME_MESSAGE:
            self._phase = self._PHASE_TALLY
            self._tally_elapsed_ms = 0
            return
        if self._phase == self._PHASE_TALLY and self._all_tally_lines_visible():
            self._route_to_post_game_scene()

    def _tally_lines(self) -> list[str]:
        return [
            "+ NUMBER OF FISH EATEN: ...",
            "+ TOTAL WEIGHT EATEN: ...",
            "+ MS. FISHY'S FINAL WEIGHT: ...",
            "+ SECONDS LEFT ON THE TIMER: ...",
            "= TOTAL SCORE! ...",
        ]

    def _route_to_post_game_scene(self) -> None:
        from ui.scenes.leaderboard_scene import LeaderboardScene
        self.game.scenes.change_to(LeaderboardScene(self.game, self.score))
**Why:** Implements requested end-of-run pacing: remove the standalone GAME OVER interstitial, reveal each stat line one-by-one, and only allow confirm-to-leaderboard after the tally is fully shown.

**File:** settings.py
**Lines (at time of edit):** 86-88 in `UiSettings` (modified)
**Before:**
    (no game-over tally reveal timing/layout constants)
**After:**
    TALLY_LINE_REVEAL_DELAY_MS = 700
    TALLY_LINE_START_Y_RATIO = 0.34
    TALLY_LINE_ROW_GAP = 60
**Why:** Keeps reveal cadence and tally layout tunable from settings, avoiding magic numbers in scene code.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 85-102 (modified)
**Before:**
    GameOverScene phase 2 was documented as centered `GAME OVER` text,
    with routing to InitialsEntryScene when leaderboard qualification passed.
**After:**
    GameOverScene phase 2 is documented as delayed stat tally reveal using
    `UiSettings.TALLY_LINE_REVEAL_DELAY_MS`, with routing directly to
    LeaderboardScene after tally confirmation.
**Why:** Documentation truth update to match actual runtime flow.

**File:** docs/TODO.md
**Lines (at time of edit):** 108, 118-122 (modified)
**Before:**
    - [x] End-of-run messaging flow ... then `GAME OVER` on confirm, then leaderboard routing.
    - [ ] Add a timer ... Seconds left on timer add to the score
    - [ ] # of fish adds to score
    - [ ] player's final weight adds to score
    - [ ] Display all statistics at the end ... and add to final score
**After:**
    - [x] End-of-run messaging flow ... then delayed stat tally, then leaderboard routing.
    - [x] Add a timer ... Seconds left on timer add to the score
    - [x] # of fish adds to score
    - [x] player's final weight adds to score
    - [x] Display all statistics at the end ... and add to final score
**Why:** Marks completed roadmap items and updates the completed messaging description to the new tally flow.

**Editor:** GitHub Copilot (GPT-5.3-Codex)
**Why:** The smoke checklist must reflect that CRT is now an optional debug setting rather than always-on behavior.

**Editor:** GitHub Copilot (GPT-5.4)

---

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 62, 111 (modified)
**Before:**
    `TitleScene` render bullet included the high-score line.
    `Leaderboard` consumer bullet listed both `TitleScene` and `Hud`.
**After:**
    `TitleScene` render bullet now lists title + start prompt only.
    `Leaderboard` consumers now list `Hud` only.
**Why:** Documentation-truth update so architecture matches runtime behavior.

**File:** docs/TODO.md
**Lines (at time of edit):** 114, 119-122 (modified)
**Before:**
    Completed title-scene spec still required a high-score line below the prompt and referenced
    `HIGH_SCORE_LABEL` under title-scene settings.
**After:**
    Removed the high-score line requirement from TitleScene visuals and removed that title-specific
    `HIGH_SCORE_LABEL` note.
**Why:** Removes stale completed-spec text that contradicted the user-approved title layout.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T17:36:00-04:00 — pass 2.3 leaderboard model + persistence

**File:** systems/leaderboard.py
**Lines (at time of edit):** (new file)
**After:**
    Added `Leaderboard` service with `load`, `save` (atomic replace),
    `qualifies`, `submit`, and `top` methods.
    Implemented initials validation (exactly 3 letters A-Z), initials-dedup
    score-update rule, top-10 sort/truncate behavior, and JSON persistence.
**Why:** Completes the next roadmap item (Pass 2.3) by adding a process-wide leaderboard model.

**File:** settings.py
**Lines (at time of edit):** 55, 196 (modified)
**Before:**
    No title high-score offset ratio setting.
    No `AssetPaths.LEADERBOARD` path.
**After:**
    Added `UiSettings.TITLE_HIGH_SCORE_OFFSET_RATIO`.
    Added `AssetPaths.LEADERBOARD = os.path.join(BASE_DIR, 'leaderboard.json')`.
**Why:** Keeps title layout and leaderboard file path centralized in settings.

**File:** main.py
**Lines (at time of edit):** 7, 41-42 (modified)
**Before:**
    `GameManager` did not own a leaderboard instance.
**After:**
    Imported `Leaderboard`, created `self.leaderboard`, and called `load()` during boot.
**Why:** Makes leaderboard state process-wide and available to all scenes.

**File:** ui/scenes/title_scene.py
**Lines (at time of edit):** 54-61, 110-123 (modified)
**Before:**
    Title scene rendered only title and start prompt.
**After:**
    Added `_high_score_text()` and rendered a centered high-score line below the prompt using leaderboard top entry or `HI: -----` fallback.
**Why:** Implements title-scene leaderboard read path required by Pass 2.3.

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** 25, 29-35 (modified)
**Before:**
    Game-over scene did not query leaderboard qualification.
**After:**
    Added `qualifies_for_leaderboard` state and `_score_qualifies_for_leaderboard()` helper called on enter.
**Why:** Prepares the game-over flow to branch into initials-entry logic in the next roadmap task.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 30, 65, 85, 104-111, 204, 271 (modified)
**Before:**
    Architecture doc described leaderboard integration as future work.
**After:**
    Documented GameManager leaderboard ownership, title high-score rendering,
    game-over qualification read, and added a dedicated `Leaderboard` subsystem section.
**Why:** Keeps architecture docs aligned with implemented systems.

**File:** docs/TODO.md
**Lines (at time of edit):** 187 (modified)
**Before:**
    `- [ ] Create [systems/leaderboard.py](../systems/leaderboard.py):`
**After:**
    `- [x] Create [systems/leaderboard.py](../systems/leaderboard.py):`
**Why:** Marks Pass 2.3 as completed.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

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

---

## 2026-05-09T11:37:07-04:00 — pass 1.1 visual-asset rule documented

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** end of file (added new section `## 12. Project rules`)
**Before:** No explicit project-level rule banning newly imported image assets.
**After:** Added the rule that visuals must be runtime-drawn with pygame primitives/surface operations, with audio/fonts allowed and `assets/graphics/effects/tv.png` as the only grandfathered image exception.
**Why:** Completes TODO Pass 1 item 1.1 and makes the rendering constraint explicit in architecture docs.

**File:** .github/copilot-instructions.md
**Lines (at time of edit):** Code style section (added one bullet)
**Before:** Code style rules did not explicitly ban new imported visual assets.
**After:** Added the same no-imported-visual-assets rule under Code style, including the CRT overlay exception.
**Why:** Enforces the project rule at implementation-time for both human and AI editors.

**File:** docs/TODO.md
**Lines (at time of edit):** Pass 1, item 1.1 checklist line
**Before:** `- [ ] Add this rule ...`
**After:** `- [x] Add this rule ...`
**Why:** Marks Pass 1 item 1.1 as completed after both required doc updates were made.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

## 2026-05-09T19:55:00-04:00 — title-only UI + gameplay-only background music

**File:** ui/scenes/title_scene.py
**Lines (at time of edit):** `on_enter`, removed `_high_score_text`, `render`
**Before:** Title scene resumed music on enter and rendered a centered high-score fallback line (`HI: -----`) below the start prompt.
**After:** Title scene now stops music on enter and renders only `MS. FISHY` plus `PRESS START TO PLAY`.
**Why:** User requested a minimal title screen and no background music outside gameplay.

**File:** systems/audio_manager.py
**Lines (at time of edit):** `__init__` docstring/body tail
**Before:** `AudioManager` started background music during initialization.
**After:** `AudioManager` only initializes audio state; music now starts when gameplay enters `PlayScene`.
**Why:** Ensures background music plays during gameplay only.

**File:** settings.py
**Lines (at time of edit):** `UiSettings` constants
**Before:** `HIGH_SCORE_LABEL` remained in settings for title-screen fallback text.
**After:** Removed `HIGH_SCORE_LABEL` because the title screen no longer renders a high-score line.
**Why:** Keeps settings aligned with current UI behavior and avoids dead constants.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** `TitleScene` scene description bullets
**Before:** Stated that title scene resumed music and rendered high-score text.
**After:** Updated to reflect silent title behavior and title+prompt-only layout.
**Why:** Keeps architecture docs in sync with code.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T19:35:00-04:00 — title centered + smaller start prompt constants

**File:** settings.py
**Lines (at time of edit):** `UiSettings` constants block
**Before:** Title screen used `TITLE_FONT_SIZE` and `OVERLAY_FONT_SIZE`, with no dedicated constants for prompt size or title/prompt vertical anchors.
**After:** Added `START_PROMPT_FONT_SIZE`, `TITLE_CENTER_Y_RATIO`, and `START_PROMPT_CENTER_Y_RATIO`.
**Why:** Makes title-screen layout and CTA size tunable from settings instead of hardcoding values in scene code.

**File:** ui/scenes/title_scene.py
**Lines (at time of edit):** `__init__` font setup + `render` text placement
**Before:** Prompt used `OVERLAY_FONT_SIZE`; title and prompt Y positions were hardcoded ratios in the render call.
**After:** Prompt now uses dedicated `prompt_font` from `UiSettings.START_PROMPT_FONT_SIZE`, and text placement uses `UiSettings.TITLE_CENTER_Y_RATIO` / `UiSettings.START_PROMPT_CENTER_Y_RATIO`.
**Why:** Centers the title via settings-driven anchor and makes `PRESS START TO PLAY` visibly smaller, as requested.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

**File:** systems/fish_manager.py
**Lines (at time of edit):** (new file)
**After:** `FishManager` with `spawn_fish`, `check_collisions` (eat smaller fish → grow player; eaten by larger fish → exit), and `grow_player`.
**Why:** Centralizes all fish lifecycle logic, keeping `GameManager` thin.
**Editor:** Bryan

---

## 2026-05-09 — Pass 2.4/2.5/2.6 — initials entry, leaderboard display, game-over routing

**File:** ui/scenes/initials_entry_scene.py
**Lines (at time of edit):** (new file)
**After:**
    `InitialsEntryScene` class with three-slot letter editor.
    Keyboard: A-Z types a letter and advances cursor; Backspace clears/steps back; arrows
    cycle letters up/down and move cursor left/right; Enter commits.
    Controller: START commits; D-pad hat up/down cycles; D-pad left/right moves cursor.
    On commit, empty slots fill with 'A', initials are submitted to `game.leaderboard`,
    leaderboard is saved, then scene transitions to `LeaderboardScene`.
**Why:** Implements Pass 2.4 — the qualifying high-score initials prompt.

**File:** ui/scenes/leaderboard_scene.py
**Lines (at time of edit):** (new file)
**After:**
    `LeaderboardScene` class that renders: "GAME OVER" header, run score, up-to-10 ranked
    rows from `game.leaderboard.top()`, an optional white-background highlight for the
    player's just-submitted row, and a "PRESS START TO RETURN TO TITLE" footer.
    Enter/START transitions back to `TitleScene`.
**Why:** Implements Pass 2.5 — the post-game leaderboard display replacing the old bare GAME OVER screen.

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** 1-75 (replaced)
**Before:**
    Rendered a black screen with "GAME OVER" text; Enter/START restarted directly to PlayScene.
    Had `qualifies_for_leaderboard` flag and `_score_qualifies_for_leaderboard` helper but
    did not act on them.
**After:**
    `GameOverScene` is now a zero-frame router. `on_enter` immediately calls
    `game.leaderboard.qualifies(score)` and routes to `InitialsEntryScene` or
    `LeaderboardScene` accordingly. `render` is a no-op.
    Removed: `_score_qualifies_for_leaderboard`, `handle_event`, `_restart`, and the
    "GAME OVER" render path (now owned by `LeaderboardScene`).
**Why:** Implements Pass 2.6 wiring — game-over state now dispatches into the correct post-game scene.

**File:** docs/TODO.md
**Lines (at time of edit):** Pass 2 section (modified)
**Before:** Items 2.4, 2.5, 2.6 marked `[ ]`.
**After:** Items 2.4, 2.5, 2.6 marked `[x]`. Pass 1 and completed Pass 2 items moved to the Completed section; Pass 1 section removed; Pass 2 header updated to "(remaining)".
**Why:** Reflects all completed work and cleans up the active roadmap.

**Editor:** GitHub Copilot (Claude Sonnet 4.6)

---

## 2026-05-09T16:30:00-04:00 — pass 1.3 scene refactoring: Scene base class and SceneManager

**File:** core/scene.py
**Lines (at time of edit):** (new file)
**After:**
    Base `Scene` class with lifecycle hooks: on_enter, on_exit, handle_event, update, render.
    Subclasses override the methods they need.
**Why:** Replaces string-based game_state with first-class scene objects (Pass 1.3).

**File:** systems/scene_manager.py
**Lines (at time of edit):** (new file)
**After:**
    `SceneManager` class with current property and change_to(scene) method.
    Calls on_exit on the old scene and on_enter on the new scene during transitions.
**Why:** Coordinates scene transitions and lifecycle. GameManager now holds a SceneManager instance instead of managing state strings.

**File:** ui/scenes/__init__.py
**Lines (at time of edit):** (new file)
**After:** Empty package docstring.
**Why:** Enables the scenes package and future scene subclasses.

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** (new file)
**After:**
    PlayScene class encapsulates all gameplay logic.
    Owns: player, all_sprites, enemy_sprites, fish_manager, bg_surface, and local PLAYING/PAUSED state.
    Handles Enter/START for pause toggle; Enter/START trigger pause/resume with SFX and music control.
    update() advances sprites and FishManager; on game-over transitions to GameOverScene.
    render() draws ocean gradient + sprites when PLAYING, or black + "PAUSED" text when PAUSED.
**Why:** Extracts gameplay from GameManager into a dedicated scene. Moves gradient generation (build_gradient_surface) into this scene.

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** (new file)
**After:**
    GameOverScene class for the game-over state.
    render() draws black background + centered "GAME OVER" text.
    handle_event() listens for Enter/START to restart by transitioning to a fresh PlayScene.
**Why:** Wraps the current game-over state as a real scene.

**File:** main.py
**Lines (at time of edit):** 1-19 (imports), 48-63 (__init__), 97-104 (setup), 107-135 (input handling), 159-176 (main loop)
**Before:**
    Imports: core.sprites, systems.fish_manager, utils.text, GameStateSettings
    __init__: called _create_gameplay_entities(), held player/all_sprites/enemy_sprites/fish_manager/bg_surface/game_state
    _create_gameplay_entities, reset_game methods
    Input handlers: _handle_pause_action, _handle_enter_key, _handle_start_button called reset_game or toggled game_state
    _update_world: checked game_state and updated sprites/FishManager
    _render_frame: rendered by game_state string
    _draw_centered_overlay helper method
**After:**
    Imports: removed core.sprites and systems.fish_manager; added systems.scene_manager
    __init__: creates SceneManager and transitions to PlayScene(self)
    Removed: _create_gameplay_entities, reset_game, _draw_centered_overlay
    Input handlers: global handlers (Esc, F11, quit-combo, BACK) stay in GameManager; scene-specific input (Enter, START) forwarded to scenes.current.handle_event(event)
    _update_world: calls scenes.current.update()
    _render_frame: calls scenes.current.render(screen) then applies CRT pass
    Removed build_gradient_surface from main.py (moved to PlayScene)
**Why:** Refactors GameManager to be a thin coordinator; all gameplay state and logic now live in scenes (Pass 1.3 requirement).

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 1-60 (sections 1-3 rewritten), 63-123 (renamed sections 3-5 to 4-5), 191-217 (sections 8-11 updated with new source tree and extension points)
**Before:**
    Section 1 diagram showed GameManager with events/state/render inputs.
    Section 2 described frame loop with game_state string management.
    Section 3 was Sprites; input routing mentioned specific handler methods by name.
    Sections 4+ covered fish manager, input, CRT, settings, etc.
**After:**
    Section 1 diagram updated to show SceneManager in the middle with Scene subclasses.
    Section 2 explains frame loop delegates to scenes; global input handled by GameManager, scene input forwarded.
    New Section 3 introduces Scene base class, lifecycle hooks, and current scene implementations (PlayScene, GameOverScene).
    Section 4+ (formerly 3+) Sprites, fish manager, input, CRT, settings adjusted for new architecture.
    Section 9 source tree updated with core/scene.py, systems/scene_manager.py, ui/scenes/ package.
    Section 11 extension points updated: scene/state machine done; score/HUD and sprite art remain.
**Why:** Documents the new scene-based architecture as the source of truth for future work.

**File:** docs/TODO.md
**Lines (at time of edit):** Pass 1, item 1.3 checklist line
**Before:** `- [ ] Scene base class + SceneManager`
**After:** `- [x] Scene base class + SceneManager`
**Why:** Marks Pass 1 item 1.3 as completed.

**Editor:** GitHub Copilot (Claude Haiku 4.5)


**File:** settings.py
**Lines (at time of edit):** 50-55 (added)
**After:** Added `PlayerSettings` (SPEED, SIZE) and `FishSettings` (SPAWN_RATE, MIN_SIZE, MAX_SIZE, MIN_SPEED, MAX_SPEED, PLAYER_GROWTH_RATE).
**Why:** New gameplay systems need tunables; all magic numbers must live in settings.py.
**Editor:** Bryan

---

## 2026-05-09T11:39:00-04:00 — testing docs-only exception added

**File:** docs/TESTING.md
**Lines (at time of edit):** 5-7 (added)
**Before:** Checklist stated to run after non-trivial changes, with no explicit docs-only exception.
**After:** Added a docs-only exception: when changes touch documentation files only (`README.md`, `docs/*.md`, `.github/copilot-instructions.md`) and do not modify runtime code, gameplay smoke checks are not required.
**Why:** Aligns testing expectations with documentation-only edits to avoid unnecessary runtime checks.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

**File:** main.py
**Lines (at time of edit):** 1-170 (modified)
**After:** `GameManager.__init__` now creates `Player`, `all_sprites`, `enemy_sprites`, and `FishManager`. `_update_world` drives all three. `_render_frame` draws both sprite groups.
**Why:** Wire the new sprites and manager into the frame loop.

---

## 2026-05-09T18:51:59-04:00 — web-safe exit toggle for pybag/browser runs

**File:** settings.py
**Lines (at time of edit):** 264-282 (modified)
**Before:**
    class DebugSettings:
        """Settings related to debugging features."""

        ENABLE_CRT = False
        START_LARGE_PLAYER = False
        LARGE_PLAYER_SIZE = 640
**After:**
    class DebugSettings:
        """Settings related to debugging features."""

        ENABLE_CRT = False
        WEB_SAFE_EXIT = False
        START_LARGE_PLAYER = False
        LARGE_PLAYER_SIZE = 640
**Why:** Adds a dedicated settings toggle so browser-safe builds can avoid `sys.exit()` while keeping existing desktop shutdown behavior available.

**File:** main.py
**Lines (at time of edit):** 1-4, 42-51, 82-89, 185-197 (modified)
**Before:**
    Imported `sys`.
    `close_game()` always called `pygame.quit()` followed by `sys.exit()`.
    `run()` loop was `while True`, so there was no clean loop-exit path.
**After:**
    Removed the unused `sys` import.
    Added `self.running` and `self.web_safe_exit` state to `GameManager`.
    `close_game()` now clears `self.running` and returns when `WEB_SAFE_EXIT` is enabled; otherwise it keeps desktop-style `SystemExit` shutdown.
    `run()` now uses `while self.running`, breaks immediately after quit requests, and calls `pygame.quit()` after loop exit.
**Why:** Keeps shutdown behavior controlled at the owning game-loop abstraction and makes pybag/browser exits stop the frame loop cleanly instead of raising a browser-console "clean crash".

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 25, 37-42, 192 (modified)
**Before:**
    `GameManager` ownership list did not mention the loop-running flag.
    Frame-loop docs ended at `flip()` and `tick()`.
    `DebugSettings` docs did not include any exit-mode toggle.
**After:**
    Documented the `running` flag on `GameManager`.
    Documented the shutdown path after loop exit and the `WEB_SAFE_EXIT` behavior split.
    `DebugSettings` docs now include the web-safe exit toggle.
**Why:** Architecture docs now match the actual shutdown control flow.

**File:** docs/TESTING.md
**Lines (at time of edit):** 23 (modified)
**Before:**
    `Esc` exits cleanly.
**After:**
    `Esc` exits cleanly, and with `DebugSettings.WEB_SAFE_EXIT = True` it should do so by leaving the loop without a `sys.exit()` traceback.
**Why:** The manual smoke test now reflects the optional web-safe shutdown mode.

**Editor:** GitHub Copilot (GPT-5.4)
**Editor:** Bryan

## 2026-05-08 — Docs rewritten for Fishy

**File:** README.md
**Lines (at time of edit):** 1-60 (replaced)
**Before:** Template scaffold description with first-run setup instructions.
**After:** Describes Fishy — the eat-or-be-eaten game, its current status, controls, and links.
**Why:** Docs reflected the template origin, not the actual game.
**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

---

## 2026-05-09T18:30:00-04:00 — dedicated font size for pre-game-over outcome messages

**File:** settings.py
**Lines (at time of edit):** 59 (modified)
**Before:**
    Pre-`GAME OVER` outcome messages and `GAME OVER` shared `UiSettings.OVERLAY_FONT_SIZE`.
**After:**
    Added `UiSettings.OUTCOME_MESSAGE_FONT_SIZE = 36` for the two pre-game-over outcome messages.
**Why:** User requested the lose/win condition messages to share their own smaller size without shrinking other overlay text.

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** 50-54, 108-117 (modified)
**Before:**
    `GameOverScene` used a single `_overlay_font` for both phase-1 outcome text and phase-2 `GAME OVER`.
**After:**
    Added `_outcome_font` built from `UiSettings.OUTCOME_MESSAGE_FONT_SIZE`.
    `render()` now selects `_outcome_font` for phase 1 and `_overlay_font` for phase 2.
**Why:** Keeps `GAME OVER` visual scale intact while ensuring long outcome lines fit on screen.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 86-89 (modified)
**Before:**
    Game-over phase description did not specify phase-specific font settings.
**After:**
    Documented phase-1 font as `UiSettings.OUTCOME_MESSAGE_FONT_SIZE` and phase-2 font as `UiSettings.OVERLAY_FONT_SIZE`.
**Why:** Keeps architecture documentation aligned with runtime behavior.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T18:26:00-04:00 — custom end screens + screen-width victory condition

**File:** settings.py
**Lines (at time of edit):** 49-50 (modified)
**Before:**
    `UiSettings` only had generic `GAME OVER` text for end-of-run messaging.
**After:**
    Added:
    - `EATEN_BY_BIGGER_FISH_TEXT = "YOU WERE EATEN BY A BIGGER FISH"`
    - `ATE_ALL_FISH_TEXT = "YOU'VE EATEN ALL THE FISH!"`
**Why:** Keeps new end-screen strings centralized in settings and avoids magic strings in scene code.

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** 31-32, 91-106, 198-204 (modified)
**Before:**
    PlayScene had one game-over path from FishManager collision (`GAME OVER` flow only).
**After:**
    Added explicit outcomes (`LOSS_EATEN_BY_BIGGER_FISH`, `WIN_ATE_ALL_FISH`) and `_end_run(...)` helper.
    Collision loss now transitions through `GameOverScene(..., outcome=loss)`.
    Added win condition: if `player.rect.width > ScreenSettings.WIDTH`, transition through `GameOverScene(..., outcome=win)`.
**Why:** Implements requested custom loss/victory endings while keeping transition logic DRY.

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** 13-112 (modified)
**Before:**
    Scene was a zero-frame router in `on_enter`, immediately jumping to initials-entry or leaderboard.
**After:**
    Scene now has a two-step flow:
    1) show outcome message (`YOU WERE EATEN BY A BIGGER FISH` or `YOU'VE EATEN ALL THE FISH!`)
    2) show `GAME OVER`
    Third confirm routes to initials-entry or leaderboard.
    Confirm inputs: Enter, controller A, controller START.
**Why:** Matches requested UX: custom cause message first, then GAME OVER.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 76-89 (modified)
**Before:**
    PlayScene described only collision-based game-over; GameOverScene described immediate routing only.
**After:**
    Documented screen-width win condition and the two-phase GameOverScene message flow with routing behavior.
**Why:** Keeps architecture docs truthful after gameplay-state changes.

**File:** docs/TODO.md
**Lines (at time of edit):** 108-109 (modified)
**Before:**
    No completed roadmap bullets for the new custom end-message flow or width-based victory condition.
**After:**
    Added completed bullets for both features under Pass 2.6 wiring.
**Why:** Required roadmap maintenance for completed work.

**File:** docs/TESTING.md
**Lines (at time of edit):** 38-43 (modified)
**Before:**
    Checklist expected immediate `GAME OVER` screen and restart behavior.
**After:**
    Checklist now validates two-step message flow (custom message -> `GAME OVER` -> post-run routing) and the new width-based victory ending.
**Why:** Updates manual smoke checks to match implemented behavior.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

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

**Editor:** Bryan (GitHub Copilot — Claude Sonnet 4.6)

## 2026-05-09 — Underwater velocity-based player movement

**File:** settings.py
**Lines (at time of edit):** 75-82 (modified)
**Before:**
    class PlayerSettings:
        """Player-specific settings like movement speed."""
        SPEED = 2
        SIZE = (16, 16)
        COLOR = (255, 255, 0)
        # % of the eaten fish's size is added to the player
        PLAYER_GROWTH_COEFFICIENT = 0.05
**After:** Removed `SPEED`; added `MAX_SPEED = 5.0`, `ACCELERATION = 0.5`, `DRAG = 0.88`,
    `STOP_THRESHOLD = 0.05`, `FLIP_THRESHOLD = 0.1` with explanatory comments on units and behaviour.
**Why:** Velocity-based movement requires separate physics tunables. `SPEED` was a fixed
    per-frame offset; the new constants govern acceleration, water-resistance drag, and
    anti-flicker thresholds independently.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** core/sprites.py
**Lines (at time of edit):** 60-175 (modified)
**Before:** `Player.__init__` stored no velocity; `input()` applied `PlayerSettings.SPEED`
    directly to `rect.x/y` each frame; releasing a key caused instant stop;
    direction flip read the raw `move_x` delta.
**After:**
    - `__init__` adds `self.velocity_x`, `self.velocity_y` (float, px/frame) and
      `self._pos_x`, `self._pos_y` (float sub-pixel position accumulators).
    - `input()` accelerates velocity by `ACCELERATION` when input is held (clamped to
      `MAX_SPEED`), and multiplies by `DRAG` when released; snaps to zero below
      `STOP_THRESHOLD`. Commits velocity via the float accumulators so sub-pixel
      velocities accumulate instead of being discarded by `int()` truncation.
      Direction flip uses velocity sign and only fires above `FLIP_THRESHOLD`.
    - `enforce_boundaries()` zeroes velocity on any clamped axis and resyncs the
      float accumulators so the fish doesn't fight the wall each frame.
    - `grow()` resyncs the float accumulators after the rect topleft shifts from
      the increased sprite size.
**Why:** Gives the player underwater inertia — gradual acceleration and a natural
    coast-to-stop on key release — without any visible position snap artefacts.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** ~50-51 (modified)
**Before:** "Speed is `PlayerSettings.SPEED` px/frame." and one-line boundary note.
**After:** Updated to describe the velocity model, DRAG/ACCELERATION/STOP_THRESHOLD/FLIP_THRESHOLD
    roles, sub-pixel accumulators, and boundary velocity zeroing.
**Why:** Architecture must reflect the current movement system.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

## 2026-05-09 — Fix right/down movement bug; add active counter-acceleration

**File:** core/sprites.py
**Lines (at time of edit):** ~215-225 (enforce_boundaries, modified)
**Before:** `self._pos_x = float(self.rect.x)` / `self._pos_y = float(self.rect.y)` ran
    unconditionally at the end of `enforce_boundaries` every frame.
**After:** Accumulator resync is guarded by a `clamped` flag and only runs when a
    wall actually moved the rect.
**Why:** The unconditional reset destroyed the sub-pixel fractional part before it
    could accumulate.  For negative-direction motion (left/up), Python's `int()`
    truncation happens to move the rect by 1 px on the very first frame (e.g.
    `int(99.97) = 99`), so those directions felt responsive.  For positive-direction
    motion (right/down), the fractional part was wiped before ever crossing an
    integer boundary, so the fish appeared not to respond at all.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** settings.py
**Lines (at time of edit):** ~83 (added COUNTER_ACCELERATION)
**After:** Added `COUNTER_ACCELERATION = 0.12` with explanatory comment.
**Why:** Active braking needs a separate constant so players can override passive
    drag; the value is higher than ACCELERATION so opposing input decelerates
    faster than coasting does.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

**File:** core/sprites.py
**Lines (at time of edit):** ~143-175 (input velocity physics, modified)
**Before:** `input_x != 0` branch always used `ACCELERATION` regardless of whether
    the input was in the same or opposite direction as current velocity.
**After:** Detects `input_x * self.velocity_x < 0` (opposing signs) and uses
    `COUNTER_ACCELERATION` in that case; same direction still uses `ACCELERATION`.
    Applied identically to the vertical axis.
**Why:** Without this, pressing the opposite direction felt nearly identical to
    releasing the key — both just bled off momentum at roughly the same rate.
    Counter-acceleration lets the player noticeably brake and reverse faster.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

## 2026-05-09 — Controller pause support; keyboard/controller parity rule

**File:** main.py
**Lines (at time of edit):** ~187-200 (_handle_joybuttondown, modified)
**Before:**
    def _handle_joybuttondown(self, event) -> None:
        if self.quit_combo_pressed():
            self.close_game()
        if event.button == InputSettings.JOY_BUTTON_BACK:
            pygame.display.toggle_fullscreen()
            self.full_screen = not self.full_screen
**After:**
    def _handle_joybuttondown(self, event) -> None:
        if self.quit_combo_pressed():
            self.close_game()
        if event.button == InputSettings.JOY_BUTTON_BACK:
            pygame.display.toggle_fullscreen()
            self.full_screen = not self.full_screen
        # START mirrors the Enter key: pause/resume/restart.
        if event.button == InputSettings.JOY_BUTTON_START:
            self._handle_enter_key()
**Why:** Pressing START alone now calls `_handle_enter_key`, giving the controller
    the same pause/resume/restart capability as the Enter key on the keyboard.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** §5 Input (modified)
**Before:** No parity rule; §5 listed Enter only under KEYDOWN, START not mentioned.
**After:** Added "Parity rule: every action available on the keyboard must also be
    reachable on the controller." Updated KEYDOWN and JOYBUTTONDOWN bullet points
    to reflect Enter ↔ START parity explicitly.
**Why:** Establishes and documents the keyboard/controller parity requirement so
    future contributors maintain it.

**File:** docs/TODO.md
**Lines (at time of edit):** ~54, ~90 (modified)
**Before:** `[ ] Controller needs to be able to pause too` unchecked; no Rules section.
**After:** Item marked `[x]`; new Rules section added with the parity rule entry.
**Why:** Reflect completed work and capture the new project rule.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

## 2026-05-09 — Extract _handle_pause_action; separate Enter and START handlers

**File:** main.py
**Lines (at time of edit):** ~169-210 (_handle_enter_key, _handle_joybuttondown, modified/new)
**Before:**
    `_handle_enter_key` contained all pause/resume/restart logic inline.
    `_handle_joybuttondown` called `self._handle_enter_key()` from the START branch.
**After:**
    New `_handle_pause_action()` holds the shared pause/resume logic.
    `_handle_enter_key()` calls `_handle_pause_action()` for playing/paused states and
        handles restart separately for game_over.
    New `_handle_start_button()` calls `_handle_pause_action()` only.
    `_handle_joybuttondown` START branch calls `_handle_start_button()`.
    Input handlers no longer call each other.
**Why:** Input handlers should never delegate to each other; shared behaviour belongs
    in a dedicated action method so each handler remains self-contained and doesn't
    silently inherit unrelated side-effects of another.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** §5 Input (modified)
**Before:** Parity rule only; handlers listed without design constraint.
**After:** Added "Handler design rule" explaining that handlers must not call each other
    and shared behaviour must be extracted into action methods.
**Why:** Codify the design constraint so future contributors follow the same pattern.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

## 2026-05-09 — START button restarts from game-over screen

**File:** main.py
**Lines (at time of edit):** ~190-195 (_handle_start_button, modified)
**Before:**
    def _handle_start_button(self) -> None:
        self._handle_pause_action()
**After:**
    def _handle_start_button(self) -> None:
        if self.game_state == GameStateSettings.GAME_OVER:
            self.restart_session()
            return
        self._handle_pause_action()
**Why:** START should have full parity with Enter, including restart from game-over.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

## 2026-05-09 — Add gulp and Wilhelm scream sound effects; route pause sounds through fixed channels

**File:** settings.py
**Lines (at time of edit):** 186-187 (added)
**Before:**
    PAUSE_IN_SOUND = ...
    PAUSE_OUT_SOUND = ...
**After:**
    PAUSE_IN_SOUND = ...
    PAUSE_OUT_SOUND = ...
    GULP_SOUND = os.path.join(AUDIO_DIR, 'sound', 'gulp.ogg')
    SCREAM_SOUND = os.path.join(AUDIO_DIR, 'sound', 'wilhelm_scream.ogg')
**Why:** New SFX asset paths must live in AssetPaths per architecture rules.

**File:** systems/audio_manager.py
**Lines (at time of edit):** 8-11, 26-34, 59-72, 162-177 (modified)
**Before:** `CHANNEL_IDS` was commented out; pause sounds loaded with `_safe_load_sound` and played via `.play()` directly; no `_loud_sound` helper; no gulp/scream loading.
**After:** `CHANNEL_IDS = {'gulp': 0, 'scream': 1, 'pause_in': 2, 'pause_out': 3}` active; all four sounds loaded via `_loud_sound`; channels dict built from `CHANNEL_IDS`; all four play functions route through `self.channels[name].play(sound)`.
**Why:** Fixed channels prevent any sound from being cut off by a simultaneous effect. Routing pause sounds through the same architecture keeps all SFX consistent.

**File:** systems/fish_manager.py
**Lines (at time of edit):** 14-29, 52-76 (modified)
**Before:** `update` and `check_collisions` returned `bool` (game_over only).
**After:** Both return `tuple[bool, int]` — `(game_over, ate_count)` — so the caller can trigger the gulp sound once per frame when any fish was eaten.
**Why:** The caller needs to know whether an eat happened this frame to fire the sound without reaching into FishManager internals.

**File:** main.py
**Lines (at time of edit):** ~220-225 (_update_world, modified)
**Before:** `if self.fish_manager.update(self.player): ...`
**After:** `game_over, ate_count = ...; if ate_count > 0: audio.play_gulp_sound(); if game_over: audio.play_game_over_scream_sound()`
**Why:** Wire the two new sounds at their natural trigger points in the game loop.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

## 2026-05-09 10:14 -04:00 � refactor: data-driven audio manager + portable template

**File:** systems/audio_manager.py
**Lines (at time of edit):** entire file (rewrite)
**Before:**
    ~250 lines: per-sound attributes, four bespoke `play_X_sound` methods,
    reserved CHANNEL_IDS for each cue, three nested loaders
    (`_load_sound`, `_safe_load_sound`, `_loud_sound`), commented-out
    legacy from a previous game (`SOUND_BINDINGS`, chase music,
    repellent), unused `_music_mode` state.
**After:**
    ~140 lines: dict `self.sounds` populated from
    `AudioSettings.SOUND_EFFECTS`, single `play(name)` entry point using
    pygame's default channel pool, one `_load_sound` helper, music API
    unchanged in shape (`play_random_music`/`pause_music`/`resume_music`/
    `stop_music`/`toggle_mute`).
**Why:** The inherited architecture was half-finished and not DRY (every new
    sound required an attribute, a path constant, and a custom method).
    A data-driven registry collapses that to one line in settings and
    removes ~110 lines of dead/duplicated code.

**File:** settings.py
**Lines (at time of edit):** AudioSettings + AssetPaths blocks
**Before:**
    `AudioSettings` held only mute flags + music volume; `AssetPaths` held
    `PAUSE_IN_SOUND`, `PAUSE_OUT_SOUND`, `GULP_SOUND`, `SCREAM_SOUND`,
    `NORMAL_MUSIC_TRACKS`, and `MUSIC_TRACKS`.
**After:**
    `AssetPaths` keeps only the directory roots + `SOUND_DIR`. Audio
    registry moved to `AudioSettings.SOUND_EFFECTS` (dict) and
    `AudioSettings.MUSIC_TRACKS` (list). Added `SFX_VOLUME = 1.0`.
**Why:** Centralises the audio contract in one class so the manager has a
    single dependency surface and adding a sound is one line.

**File:** main.py
**Lines (at time of edit):** `_handle_pause_action` and `_update_world`
**Before:**
    `self.audio.play_pause_in_sound()`, `play_pause_out_sound()`,
    `play_gulp_sound()`, `play_game_over_scream_sound()`.
**After:**
    `self.audio.play("pause_in" | "pause_out" | "gulp" | "scream")`.
**Why:** Use the unified entry point.

**File:** systems/audio_manager_template.py (new file)
**Why:** Heavily-commented portable copy of the manager intended to be
    lifted into other pygame projects. Documents the `AudioSettings`
    contract, mixer-init requirement, and the dedicated-channel opt-in
    for sounds that must never be cut off.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** added new section 10 "Audio"; renumbered
    extension points to section 11; removed the obsolete "Audio:
    initialize pygame.mixer..." extension-point bullet.
**Why:** Architecture doc must reflect the new system.

## 2026-05-09 — Ms. Fishy rebrand: title change + pink bow on player

**File:** settings.py
**Lines (at time of edit):** 40 (modified TITLE), 117-134 (added bow constants in PlayerSettings)
**Before:**
    TITLE = "Fishy"
    ...
    PLAYER_GROWTH_COEFFICIENT = 0.05
**After:**
    TITLE = "Ms. Fishy"
    ...
    PLAYER_GROWTH_COEFFICIENT = 0.05

    # MS. FISHY BOW
    BOW_WIDTH_RATIO = 0.55
    BOW_HEIGHT_RATIO = 0.40
    BOW_GAP_RATIO = 0.15
    BOW_COLOR = (255, 105, 180)
**Why:** The voice-recorded gulp/scream SFX sound like a cute girl, so the
    fish is now Ms. Fishy (à la Ms. Pac-Man). Bow constants live in
    `PlayerSettings` because only the player wears one; sized by ratios
    so the bow scales with the fish as it grows.

**File:** core/sprites.py
**Lines (at time of edit):** 8-135 (build_fish_surface extended), 196-201 and 264-271 (Player __init__/grow now request bow=True)
**Before:** `build_fish_surface(size, color, color2=None)` — fish-only canvas.
**After:** `build_fish_surface(size, color, color2=None, bow=False)` — when
    `bow=True`, the canvas is grown vertically by `bow_offset_y`, all body/
    tail/eye points are shifted down by that offset, and two mirrored
    triangles (▷◁) meeting at a central apex are drawn above the body's top
    point in `PlayerSettings.BOW_COLOR` with a matching drop shadow. `Player`
    passes `bow=True` from both `__init__` and `grow()`.
**Why:** Give the player a unique, readable visual marker (also closes the
    "Player distinction" TODO item). The bow ships with the player surface so
    flipping for facing direction (`pygame.transform.flip`) keeps the bow
    correctly positioned without extra bookkeeping.

**File:** README.md, docs/ARCHITECTURE.md, docs/TODO.md, docs/TESTING.md
**Lines (at time of edit):** title headers updated; ARCHITECTURE Player
    appearance bullet now mentions the pink bow; TODO Completed list gained
    a "Ms. Fishy rebrand" entry and the "Player distinction" Visuals item is
    marked `[x]`.
**Why:** Required-actions rule — docs must reflect the rebrand and the new
    visual element.
**Editor:** GitHub Copilot (Claude Opus 4.7)

## 2026-05-09 — Bow: halve gap, exclude from collision and screen boundary

**File:** settings.py
**Lines (at time of edit):** BOW_GAP_RATIO line in PlayerSettings (modified)
**Before:**
    BOW_GAP_RATIO = 0.15
**After:**
    BOW_GAP_RATIO = 0.075
**Why:** User found the bow floated too high above the head; halving the ratio
    cuts the visual distance to the body apex in half.

**File:** core/sprites.py
**Lines (at time of edit):** build_fish_surface return (modified); Player.__init__,
    _build_mask (new), _set_facing_direction, grow, enforce_boundaries (modified);
    Fish.__init__ unpack (modified).
**Before:**
    return image, body_height
    ...
    self.mask = pygame.mask.from_surface(self.image)   # bow pixels included
    ...
    if self.rect.top < 0:                              # bow constrained by screen
        self.rect.top = 0
**After:**
    return image, body_height, bow_offset_y
    ...
    self.mask = self._build_mask()   # bow rows zeroed out in mask copy
    ...
    # Allow the bow to float above y=0; clamp on the body's top edge instead.
    if self.rect.top + self.bow_offset_y < 0:
        self.rect.top = -self.bow_offset_y
**Why:** Bow contact must not trigger growth or game-over, and the bow should
    not be constrained by the screen edge. build_fish_surface now returns
    bow_offset_y as a third value so Player can zero those rows when building
    the mask and use the offset to clamp only the body's top against y=0.
    Fish unpacks with _ so the existing non-bow path is unaffected.
**Editor:** GitHub Copilot (Claude Sonnet 4.6)

---

## 2026-05-09T11:40:47-04:00 — add music and per-sfx volume toggles

**File:** settings.py
**Lines (at time of edit):** 201-238 (modified)
**Before:**
    MUSIC_VOLUME = 1.0
    SFX_VOLUME = 1.0
**After:**
    MUSIC_VOLUME = 1.0
    SFX_VOLUME = 1.0
    MUSIC_VOLUME_TOGGLE = 1.0
    SFX_VOLUME_PAUSE_IN = 1.0
    SFX_VOLUME_PAUSE_OUT = 1.0
    SFX_VOLUME_GULP = 1.0
    SFX_VOLUME_SCREAM = 1.0
    SOUND_EFFECT_VOLUMES = {
        "pause_in": SFX_VOLUME_PAUSE_IN,
        "pause_out": SFX_VOLUME_PAUSE_OUT,
        "gulp": SFX_VOLUME_GULP,
        "scream": SFX_VOLUME_SCREAM,
    }
**Why:** Adds explicit constants to toggle music and each registered sound effect by multiplier (`0.0` off, `1.0` on) without changing call sites.

**File:** systems/audio_manager.py
**Lines (at time of edit):** 23-126 (modified)
**Before:**
    sound.set_volume(AudioSettings.SFX_VOLUME)
    ...
    pygame.mixer.music.set_volume(AudioSettings.MUSIC_VOLUME)
**After:**
    sound.set_volume(self._get_sfx_volume(name))
    ...
    pygame.mixer.music.set_volume(self._get_music_volume())
    ...
    sound.set_volume(self._get_sfx_volume(name))
**Why:** Applies the new settings constants at playback time so per-sfx and music toggles are actually enforced.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 154, 193-197 (modified)
**Before:**
    `AudioSettings` | Mute toggles + music volume.
**After:**
    `AudioSettings` | Mute toggles + music volume + per-sound volume toggles.
    Added note describing `MUSIC_VOLUME_TOGGLE` and `SOUND_EFFECT_VOLUMES`.
**Why:** Keeps architecture documentation aligned with the updated audio-settings contract.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T11:51:35-04:00 — extract centered text helper for overlays

**File:** utils/text.py
**Lines (at time of edit):** (new file)
**After:**
    def draw_centered_text(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        center: tuple[int, int],
    ) -> pygame.Rect:
        """Render `text` with `font` and blit it centered at `center`.
        Returns the blitted rect (useful for stacking lines)."""
**Why:** Implements TODO 1.2 by introducing a reusable, importable centered-text helper with the required docstring and return type.

**File:** main.py
**Lines (at time of edit):** 10 (modified import), 259-271 (modified)
**Before:**
    title_surface = self.overlay_font.render(title_text, True, ColorSettings.WHITE)
    title_rect = title_surface.get_rect(center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2))
    self.screen.blit(title_surface, title_rect)
**After:**
    draw_centered_text(
        surface=self.screen,
        text=title_text,
        font=self.overlay_font,
        color=ColorSettings.WHITE,
        center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2),
    )
**Why:** Refactors `GameManager._draw_centered_overlay` to call the new helper instead of duplicating render/get_rect/blit logic.

**File:** docs/TODO.md
**Lines (at time of edit):** 75 (modified)
**Before:**
    - [ ] Create [utils/text.py](../utils/text.py) with one function:
**After:**
    - [x] Create [utils/text.py](../utils/text.py) with one function:
**Why:** Marks roadmap task 1.2 complete after implementing and wiring the helper.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T19:20:00-04:00 — pass 1.4 title scene with background fish

**File:** utils/graphics.py
**Lines (at time of edit):** (new file)
**After:** Added `build_gradient_surface(width, height, color_top, color_bottom)` as a shared helper.
**Why:** Title and play scenes both need the same ocean gradient; this removes duplicate rendering logic.

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** imports + removed local helper block
**Before:** `build_gradient_surface` was defined inside `play_scene.py`.
**After:** Scene imports `build_gradient_surface` from `utils/graphics.py`.
**Why:** Shares one canonical gradient helper across scenes.

**File:** ui/scenes/title_scene.py
**Lines (at time of edit):** (new file)
**After:** Added `TitleScene` with gradient background, background fish via `FishManager`, centered title/prompt text, high-score line fallback (`HI: -----`), and Enter/START transition to a fresh `PlayScene`.
**Why:** Implements TODO Pass 1 item 1.4 title-screen behavior.

**File:** systems/fish_manager.py
**Lines (at time of edit):** `update` signature/body
**Before:** `update` required a player and always ran collision checks.
**After:** `update(player=None)` now skips collisions and returns `(False, 0)` when no player is provided.
**Why:** Lets `TitleScene` reuse fish spawning/movement without gameplay collisions.

**File:** settings.py
**Lines (at time of edit):** `UiSettings` constants
**Before:** No title text/prompt/high-score label or title font size constants.
**After:** Added `TITLE_TEXT`, `START_PROMPT_TEXT`, `HIGH_SCORE_LABEL`, and `TITLE_FONT_SIZE`.
**Why:** Moves title-scene UI strings and sizing into settings per architecture rules.

**File:** main.py
**Lines (at time of edit):** scene bootstrap in `GameManager.__init__`
**Before:** Boot scene was `PlayScene`.
**After:** Boot scene is now `TitleScene`.
**Why:** Game now launches to title as required by Pass 1.4.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** scene descriptions, fish-manager section, source tree, state-machine scope, extension points
**Before:** Document still listed `TitleScene` as not implemented and described fish collisions as always active.
**After:** Documented `TitleScene` behavior, optional-collision fish updates, new `utils/graphics.py`, and updated active/not-yet-implemented scene list.
**Why:** Keeps architecture docs aligned with code.

**File:** docs/TODO.md
**Lines (at time of edit):** Pass 1 item 1.4 checkbox
**Before:** `- [ ] Create [ui/scenes/title_scene.py](../ui/scenes/title_scene.py) ...`
**After:** `- [x] Create [ui/scenes/title_scene.py](../ui/scenes/title_scene.py) ...`
**Why:** Marks the next roadmap task as completed.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

## 2026-05-09T14:59:03-04:00 - pass 1.5 play-scene drop-in substate

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** class state constants + on_enter + update/render flow (modified)
**Before:** PlayScene used a two-state flow (PLAYING/PAUSED); fish spawning began immediately when entering play; player started centered with normal input active.
**After:** Added local substates `DROPPING_IN`, `ACTIVE`, `PAUSED`. `on_enter` now places the player above the screen with initial downward velocity. `update` runs a one-time drop-in auto-motion pass that ignores movement input and delays fish-manager updates until the player settles, then transitions to `ACTIVE`. Pause behavior remains unchanged in `PAUSED`.
**Why:** Completes TODO Pass 1.5 by adding the requested title-to-play drop-in animation and delaying fish spawn until after settle.

**File:** settings.py
**Lines (at time of edit):** PlayerSettings physics constants block (modified)
**Before:** No dedicated drop-in velocity constant.
**After:** Added `PlayerSettings.DROP_IN_VELOCITY = 2.0` with units and transition-specific comment.
**Why:** Centralizes the drop-in tunable in settings (no magic numbers).

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** Scene descriptions (PlayScene bullets) + section 9 state-machine scope (modified)
**Before:** Documented PlayScene as PLAYING/PAUSED only.
**After:** Documented `DROPPING_IN/ACTIVE/PAUSED` behavior, including delayed fish spawning and drop-in update flow.
**Why:** Keep architecture docs aligned with runtime behavior.

**File:** docs/TODO.md
**Lines (at time of edit):** Pass 1 item 1.5 checkbox (modified)
**Before:** `- [ ] Create [ui/scenes/play_scene.py](../ui/scenes/play_scene.py).`
**After:** `- [x] Create [ui/scenes/play_scene.py](../ui/scenes/play_scene.py).`
**Why:** Marks Pass 1.5 complete after implementation.

**File:** docs/TESTING.md
**Lines (at time of edit):** Gameplay checklist items 10-20 (modified)
**Before:** Expected immediate centered player at gameplay start.
**After:** Updated checks to validate title-to-play drop-in and delayed fish spawn before active control.
**Why:** Documentation-truth update so smoke checks match current gameplay flow.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

## 2026-05-09T15:17:43.9273834-04:00 - title intro splash before gameplay music

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** 28-43, 53-62, 118-130 (modified)
**Before:**
    def __init__(self, game):
        ...
        self._state = self.DROPPING_IN

    def on_enter(self) -> None:
        ...
        self.player.velocity_y = PlayerSettings.DROP_IN_VELOCITY
        self.game.audio.resume_music()

    # on drop-in settle
    self.player.velocity_y = 0.0
    self._state = self.ACTIVE
**After:**
    def __init__(self, game, play_intro_splash: bool = False):
        ...
        self._state = self.DROPPING_IN
        self._play_intro_splash = play_intro_splash
        self._drop_in_splash_played = False

    def on_enter(self) -> None:
        ...
        self._drop_in_splash_played = False
        self.player.velocity_y = PlayerSettings.DROP_IN_VELOCITY

    # on drop-in settle
    self.player.velocity_y = 0.0
    if self._play_intro_splash and not self._drop_in_splash_played:
        self.game.audio.play("splash")
        self._drop_in_splash_played = True
    self.game.audio.resume_music()
    self._state = self.ACTIVE
**Why:** Ensures the title-start drop-in can fire a one-shot splash cue and that gameplay music starts only after the drop-in has settled.

**File:** ui/scenes/title_scene.py
**Lines (at time of edit):** 49-52 (modified)
**Before:**
    self.game.scenes.change_to(PlayScene(self.game))
**After:**
    self.game.scenes.change_to(PlayScene(self.game, play_intro_splash=True))
**Why:** Limits the splash intro cue to the title -> play transition.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 63, 69, 73 (modified)
**Before:**
    TitleScene enter/start bullet only mentioned transitioning to PlayScene.
    PlayScene on-enter bullet said music resumes on enter.
**After:**
    TitleScene start bullet now notes the intro splash-enabled transition.
    PlayScene on-enter/update bullets now document deferred music start and the splash-before-music behavior when drop-in settles.
**Why:** Keeps architecture docs aligned with runtime behavior.

**File:** docs/TESTING.md
**Lines (at time of edit):** 30-41 (modified)
**Before:**
    Gameplay checklist covered drop-in settle before fish spawn, but had no audio ordering assertion.
**After:**
    Added checklist item verifying splash plays at title-start drop-in settle before gameplay music.
**Why:** Adds a direct smoke check for the requested behavior.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

## 2026-05-09T15:21:25.2946407-04:00 - move intro splash to top-edge entry moment

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** 84, 115-123, 129-138 (modified)
**Before:**
    Splash triggered when drop-in finished settling at center.
**After:**
    Splash now triggers during drop-in when the player first crosses from off-screen top into visible space:
    - capture `previous_bottom = self.player.rect.bottom`
    - after Y update, if `previous_bottom < 0` and `self.player.rect.bottom >= 0`, play `splash` once.
    Music start remains at drop-in settle (`resume_music()` in settle branch).
**Why:** User requested the cue to happen immediately when the player appears from the top, not at the end of the intro drift.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** PlayScene update bullets (modified)
**Before:**
    Documented splash firing on drop-in settle.
**After:**
    Documents splash firing at first visible top-edge entry and music starting on settle.
**Why:** Keep architecture docs aligned with updated runtime behavior.

**File:** docs/TESTING.md
**Lines (at time of edit):** Gameplay item 11 (modified)
**Before:**
    Splash assertion was tied to drop-in settle.
**After:**
    Splash assertion now verifies trigger at first top-edge appearance before gameplay music.
**Why:** Smoke test now checks the corrected timing requirement.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

## 2026-05-09T20:20:00-04:00 — pass 1.6 marked complete (docs sync)

**File:** docs/TODO.md
**Lines (at time of edit):** Pass 1, item 1.6 checklist line
**Before:** `- [ ] Create [ui/scenes/game_over_scene.py](../ui/scenes/game_over_scene.py).`
**After:** `- [x] Create [ui/scenes/game_over_scene.py](../ui/scenes/game_over_scene.py).`
**Why:** `GameOverScene` already exists and is wired as a real `Scene` subclass with centered `GAME OVER` rendering and Enter/START restart behavior. This update resolves a stale roadmap checkbox without changing runtime code.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T20:35:00-04:00 — pass 2.1 score model + scene wiring

**File:** core/score.py
**Lines (at time of edit):** (new file)
**After:**
    Added `Score` class with `fish_eaten`, `size_eaten`, `add(fish_size)`, and `total` property.
**Why:** Implements TODO Pass 2.1 run-scoped score model owned by `PlayScene`.

**File:** systems/fish_manager.py
**Lines (at time of edit):** `update`, `check_collisions` return contract and collision loop
**Before:**
    `update` / `check_collisions` returned `(game_over, ate_count)` as an integer fish count.
**After:**
    `update` / `check_collisions` now return `(game_over, eaten_fish_sizes)` where the second value is a list of eaten fish sizes.
    Title/background mode (`player=None`) now returns `(False, [])`.
**Why:** `PlayScene` needs per-fish size values to call `score.add(fish.size)` exactly as specified by Pass 2.1.

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** imports, `_create_gameplay_entities`, `update`, game-over transition
**Before:**
    Scene owned player + fish systems only; consumed only `ate_count`; transitioned with `GameOverScene(self.game)`.
**After:**
    Scene now owns `self.score = Score()`.
    `update()` loops through `eaten_sizes` from `FishManager.update(...)` and calls `self.score.add(fish_size)` for each eat.
    Game-over transition now passes run score via `GameOverScene(self.game, self.score)`.
**Why:** Wires scoring into active gameplay and forwards run data to the next scene.

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** constructor signature and fields
**Before:**
    Constructor accepted only `game`.
**After:**
    Constructor accepts optional `score: Score | None` and stores it on `self.score`.
**Why:** Prepares scene flow for upcoming leaderboard/initials tasks that need ended-run score data.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** Scene descriptions, FishManager section, source tree
**Before:**
    `PlayScene` ownership/update text did not mention score.
    `FishManager` documented `(False, 0)` in no-player mode.
    Core tree had no `score.py`.
**After:**
    Added score ownership + update flow notes for `PlayScene`, score payload note for `GameOverScene`, a dedicated `Score` subsection, updated FishManager return semantics to `(False, [])`, and added `core/score.py` to source tree.
**Why:** Keeps architecture docs consistent with the new score pipeline.

**File:** docs/TODO.md
**Lines (at time of edit):** Pass 2 item 2.1 checkbox line
**Before:** `- [ ] Create [core/score.py](../core/score.py) with one class:`
**After:** `- [x] Create [core/score.py](../core/score.py) with one class:`
**Why:** Marks Pass 2.1 complete after implementation.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T20:50:00-04:00 — fix crash after splash intro (FishManager return path)

**File:** systems/fish_manager.py
**Lines (at time of edit):** `check_collisions` return at end of loop
**Before:**
    `return False, eaten_sizes` was indented inside the `for fish in collided_fish` loop.
    When there were zero collisions, the function fell through and returned `None`.
**After:**
    `return False, eaten_sizes` is now outside the loop so no-collision frames return a tuple.
**Why:** Fixes `TypeError: cannot unpack non-iterable NoneType object` in `PlayScene.update()` immediately after gameplay begins.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

---

## 2026-05-09T22:22:00-04:00 — initials screen equal-gap centered stack

**File:** settings.py
**Lines (at time of edit):** `UiSettings` initials layout constants (modified)
**Before:**
    Initials layout used independent Y-ratio constants:
    `INITIALS_TITLE_Y_RATIO`, `INITIALS_PROMPT_Y_RATIO`, `INITIALS_SLOTS_Y_RATIO`.
**After:**
    Replaced with centered-stack controls:
    `INITIALS_BLOCK_CENTER_Y_RATIO` and `INITIALS_BLOCK_ROW_GAP`.
**Why:** User requested row 1 (`NEW HIGH SCORE`), row 2 (`ENTER YOUR INITIALS`), and row 3 (initials slots) to have equal vertical spacing and be centered as a single block.

**File:** ui/scenes/initials_entry_scene.py
**Lines (at time of edit):** `render` layout math (modified)
**Before:**
    Title row, prompt row, and initials row each used separate Y ratios.
**After:**
    Layout now computes:
    - `block_center_y = h * INITIALS_BLOCK_CENTER_Y_RATIO`
    - row 1 at `block_center_y - INITIALS_BLOCK_ROW_GAP`
    - row 2 at `block_center_y`
    - row 3 at `block_center_y + INITIALS_BLOCK_ROW_GAP`
**Why:** Guarantees equal spacing between row 1->2 and 2->3 while centering the whole trio vertically.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

## 2026-05-10T10:38:00-04:00 — fix fish sticking at left screen edge

**File:** core/sprites.py
**Lines (at time of edit):** 445-452 (modified)
**Before:**
    def update(self):
        """Advance enemy fish position and remove it once it clears the screen."""
        self.rect.x += self.speed * self.direction

        # Kill if off-screen
        if self.rect.right < -50 or self.rect.left > ScreenSettings.WIDTH + 50:
            self.kill()
**After:**
    self._pos_x = float(self.rect.x)

    def update(self):
        """Advance enemy fish position and remove it once it clears the screen."""
        self._pos_x += self.speed * self.direction
        self.rect.x = int(self._pos_x)

        # Kill if off-screen
        if self.rect.right < -50 or self.rect.left > ScreenSettings.WIDTH + 50:
            self.kill()
**Why:** Fish speeds are floats, but `pygame.Rect` stores integers. Directly adding sub-pixel values to `rect.x` caused truncation artifacts that pinned right-moving fish at the left edge. A float accumulator preserves fractional movement and resolves the left-side sticking.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 137 (modified)
**Before:**
    - **Movement:** Constant horizontal speed in `[FishSettings.MIN_SPEED, FishSettings.MAX_SPEED]`. Self-destructs (`kill()`) once it clears the opposite edge by 50 px.
**After:**
    - **Movement:** Constant horizontal speed in `[FishSettings.MIN_SPEED, FishSettings.MAX_SPEED]`, integrated through a float x-position accumulator and then written to `rect.x` each frame so sub-pixel speeds move smoothly in both directions. Self-destructs (`kill()`) once it clears the opposite edge by 50 px.
**Why:** Architecture docs must reflect the runtime movement model used by `Fish`.

**File:** docs/CHANGELOG.md
**Lines (at time of edit):** (appended)
**After:**
    Added this change-log entry.
**Why:** Required append-only history update for this fix.

**Editor:** GitHub Copilot (GPT-5.3-Codex)

## 2026-05-11T12:00:00-04:00 — countdown timer, fish time bonus, starvation ending

**File:** settings.py
**Lines (at time of edit):** 45-53, 169-201 (modified)
**Before:**
    UiSettings defined only the bigger-fish and victory outcome text/colors.
    No dedicated timer settings block existed.
**After:**
    Added `UiSettings.STARVED_TO_DEATH_TEXT` and `UiSettings.STARVED_TO_DEATH_COLOR`.
    Added `TimerSettings` with `STARTING_SECONDS = 60` and `SECONDS_PER_FISH_PIXEL = 1`.
**Why:** Makes the countdown start time and per-fish time bonus easy to tune in one place.

**File:** ui/hud.py
**Lines (at time of edit):** 1-53 (modified)
**Before:**
    HUD formatted an elapsed-time counter from whole seconds.
**After:**
    HUD now formats a countdown using `math.ceil(remaining_seconds)` and still renders fish count and score.
**Why:** Top-right HUD label now shows time remaining instead of time elapsed.

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** 1-227 (modified)
**Before:**
    PlayScene tracked `_elapsed_frames`, passed elapsed seconds into the HUD, and only ended on bigger-fish or win conditions.
**After:**
    PlayScene now owns `_remaining_time_seconds`, decrements it during ACTIVE play, adds `fish.size * TimerSettings.SECONDS_PER_FISH_PIXEL` when fish are eaten, passes remaining time into the HUD, and ends the run with a starvation outcome when the timer reaches zero.
**Why:** Converts the timer from a passive elapsed counter into an active countdown that can end the run and reward eating fish with more time.

**File:** ui/scenes/game_over_scene.py
**Lines (at time of edit):** 19-131 (modified)
**Before:**
    Outcome text handled only bigger-fish loss and victory.
**After:**
    Added a starvation outcome branch that renders `YOU STARVED TO DEATH` in red with the same size and centered position as the other outcome messages.
**Why:** Gives the new countdown fail-state its own dedicated game-over card.

**File:** docs/ARCHITECTURE.md
**Lines (at time of edit):** 73-109 (modified)
**Before:**
    PlayScene docs described elapsed-time HUD behavior and only two loss/victory endings.
**After:**
    Docs now describe the countdown timer, fish-width time bonus, starvation routing, and the new top-right countdown HUD label.
**Why:** Keeps the architecture notes aligned with the new runtime behavior.

**File:** docs/TESTING.md
**Lines (at time of edit):** 18-25 (modified)
**Before:**
    Gameplay smoke checks covered bigger-fish loss, victory, and pause behavior but not the countdown timer.
**After:**
    Smoke checks now verify the one-minute starting timer, the fish-width time bonus, the starvation fail-state, and the updated red end-of-run message.
**Why:** Adds a manual check for the new countdown behavior.

**Editor:** GitHub Copilot (GPT-5.4 mini)

## 2026-05-11T13:30:00-04:00 — HUD redesign, diminishing-returns timer, compound score formula

**File:** settings.py
**Lines (at time of edit):** UiSettings (added HUD layout constants), TimerSettings (added TIMER_MIN_RATIO), new ScoreSettings class
**Before:**
    UiSettings had no HUD layout constants.
    TimerSettings had only STARTING_SECONDS and SECONDS_PER_FISH_PIXEL.
    No ScoreSettings class existed.
**After:**
    UiSettings: added HUD_LINE_SPACING, HUD_BAR_WIDTH, HUD_BAR_HEIGHT, HUNGER_WARNING_SECONDS.
    TimerSettings: added TIMER_MIN_RATIO = 0.1 (floor for diminishing-returns ratio).
    ScoreSettings: new class with WEIGHT_EATEN_FACTOR=1, FISH_EATEN_BONUS=10,
    FINAL_WEIGHT_FACTOR=3, TIME_LEFT_BONUS=20.
**Why:** Centralises all tunable constants for the new HUD and compound score formula.

**File:** core/score.py
**Lines (at time of edit):** 1-40 (modified)
**Before:**
    Tracked fish_eaten and size_eaten only; total returned size_eaten.
**After:**
    Added final_weight and time_left_seconds fields (default 0, set at run end).
    total property now returns the compound formula:
        size_eaten * WEIGHT_EATEN_FACTOR
        + fish_eaten * FISH_EATEN_BONUS
        + int(final_weight) * FINAL_WEIGHT_FACTOR
        + int(time_left_seconds) * TIME_LEFT_BONUS
**Why:** Score should reflect all run metrics, not just raw weight eaten.

**File:** ui/hud.py
**Lines (at time of edit):** 1-87 (rewritten)
**Before:**
    Three labels (FISH top-left, SCORE centre-top, TIME top-right); no hunger bar.
**After:**
    Four stacked top-left labels:
        TOTAL FISH EATEN: NN
        WEIGHT EATEN: NNNNN
        CURRENT WEIGHT: NNNNN   (reads player.size live)
        HUNGER TIMER: MM:SS     (turns red at <= HUNGER_WARNING_SECONDS)
    Hunger bar below timer: green->red RGB lerp, drains as fraction of STARTING_SECONDS.
    Score no longer shown in HUD; computed at run end.
    Constructor now accepts player argument to read live current weight.
**Why:** User requested this exact layout and hunger-bar visual.

**File:** ui/scenes/play_scene.py
**Lines (at time of edit):** Hud constructor call, update loop, _end_run (modified)
**Before:**
    Hud(score=..., font=...)
    Time bonus was fish_size * SECONDS_PER_FISH_PIXEL (no diminishing returns).
    _end_run did not set score.final_weight or score.time_left_seconds.
**After:**
    Hud(score=..., font=..., player=self.player)
    Time bonus now applies diminishing returns:
        effective_ratio = max(TIMER_MIN_RATIO, min(1.0, fish_size / player.size))
        bonus = fish_size * SECONDS_PER_FISH_PIXEL * effective_ratio
    _end_run sets score.final_weight = player.size and
        score.time_left_seconds = _remaining_time_seconds before transitioning.
**Why:** Near-peer fish give full time bonus; tiny fish give minimal time to a large player.
    Score.total must reflect all stats, so they must be captured before the scene change.

**Editor:** GitHub Copilot (Claude Sonnet 4.6)

## 2026-05-11T14:15:00-04:00 — HUD polish: font size, line gap, bar fix, color, no leading zeros

**File:** settings.py
**Lines (at time of edit):** UiSettings block (modified)
**Before:**
    HUD_FONT_SIZE_SMALL = 16
    HUD_LINE_SPACING = 22
    HUD_BAR_HEIGHT = 8          # (no HUD_BAR_TOP_GAP)
**After:**
    HUD_FONT_SIZE_SMALL = 13
    HUD_LINE_SPACING = 26
    HUD_BAR_HEIGHT = 8
    HUD_BAR_TOP_GAP = 4         # pixel gap between hunger timer text and hunger bar
**Why:** Smaller font and wider spacing improve readability; HUD_BAR_TOP_GAP ensures
    the bar never overlaps the timer text regardless of font size.

**File:** ui/hud.py
**Lines (at time of edit):** stat_rows, timer_color, bar_y (modified)
**Before:**
    f"TOTAL FISH EATEN: {self.score.fish_eaten:02d}"   # leading zeros
    f"WEIGHT EATEN: {self.score.size_eaten:05d}"
    f"CURRENT WEIGHT: {int(self.player.size):05d}"
    ColorSettings.WHITE (stat labels and timer default)
    bar_y = timer_y + line_h   # fixed offset -- overlapped timer text
**After:**
    f"TOTAL FISH EATEN: {self.score.fish_eaten}"       # plain integer, starts at 0
    f"WEIGHT EATEN: {self.score.size_eaten}"
    f"CURRENT WEIGHT: {int(self.player.size)}"
    ColorSettings.IN_GAME_HUD_TEXT (stat labels and timer default)
    bar_y = timer_y + timer_surf.get_height() + UiSettings.HUD_BAR_TOP_GAP
**Why:** User requested no leading zeros (values start at 0), TRINIDAD color for
    contrast against the aqua background, and the bar was visually overlapping the
    timer label -- fixed by anchoring to the actual rendered text height.

**Editor:** GitHub Copilot (Claude Sonnet 4.6)
