## 2026-04-29 — Split games into sponsor/student folders with auto-discovery (Claude Opus 4.7)

**File:** games/sponsor/ (rename from games/)
**Lines (at time of edit):** (folder rename, no content changes)
**Before:**
    games/air-hockey/, games/breakout/, games/dungeon-digger/, ... (13 more)
**After:**
    games/sponsor/air-hockey/, games/sponsor/breakout/, ... (all 14 sponsor games)
**Why:** Student-contributed games need a separate, .gitignored home so the
public GitHub copy of the launcher only ships the curated sponsor list.
Renaming the existing folders into a sponsor/ subfolder keeps everything
the launcher already references and leaves room for a sibling student/
folder discovered at runtime.

**File:** settings.py
**Lines (at time of edit):** 112-132 (modified), 184-214 (new)
**Before:**
    OPTIONS = [
        ("Air Hockey", Path("games") / "air-hockey" / "main.py"),
        ...
    ]
    # No StudentGameSettings class.
**After:**
    OPTIONS = [
        ("Air Hockey", Path("games") / "sponsor" / "air-hockey" / "main.py"),
        ...
    ]

    class StudentGameSettings:
        ROOT = Path("games") / "student"
        ENTRY_FILENAME = "main.py"
        MANIFEST_FILENAME = "game.json"
        DEFAULT_ATTRIBUTION = "CREATED BY UNKNOWN STUDENT"
        MANIFEST_KEY_LABEL = "label"
        ... (other manifest keys)
**Why:** Sponsor paths now live under sponsor/. New StudentGameSettings
holds every constant the discovery code needs so main.py keeps no magic
strings (per TESTING.md). DEFAULT_ATTRIBUTION uses the "CREATED BY ..."
phrasing the cabinet owner asked for.

**File:** main.py
**Lines (at time of edit):** 1-22 (modified imports), 27-130 (new dataclass + discovery), 198-235 (modified __init__), 254-265 (modified load_preview_images), 332-340 (modified collect_warning_lines), 351-353 (modified draw_preview_warnings), 320-322 (modified draw_preview_panel)
**Before:**
    # No discovery, options came straight from GameSettings.OPTIONS, every
    # warning/attribution lookup hit the GameSettings class directly.
**After:**
    @dataclass(frozen=True)
    class StudentGameRecord: ...

    def _read_student_manifest(manifest_path): ...

    def discover_student_games(student_root) -> list[StudentGameRecord]: ...

    # In __init__: copy GameSettings dicts/sets into instance state, then
    # merge in discovered student games. draw/collect_* methods now read
    # self.preview_paths, self.game_attributions, self.no_controller_games,
    # self.limited_controller_games, self.wonky_physics_games, and
    # self.under_construction_games instead of GameSettings.X.
**Why:** The launcher needs to be agnostic to whatever lives in
games/student/. A module-level discovery function keeps the scan logic
testable, and routing every menu lookup through instance state means the
sponsor + student data merges in one place. Bad manifests fail soft
(empty dict) so one student's typo can't crash the launcher.

**File:** .gitignore
**Lines (at time of edit):** 126-130 (modified)
**Before:**
    # Ignore all student game subfolders and files
    student_games/*
**After:**
    # Student-contributed games stay local to each cabinet ...
    games/student/*
    !games/student/README.md
**Why:** The orphaned student_games/* line referred to a folder that
never existed. The new games/student/* matches the launcher's actual
discovery path, and the negative re-include keeps the convention README
trackable on GitHub even though everything else stays local.

**File:** games/student/README.md
**Lines (at time of edit):** (new file)
**After:**
    Documentation of the discovery convention, the optional game.json
    schema, and worked examples pointing at red-square/ and blue-circle/.
**Why:** Students need a single document that explains how to add a game
without reading the launcher source. The README is the only file
whitelisted under games/student/, so it ships with the public repo.

**File:** games/student/red-square/main.py
**Lines (at time of edit):** (new file)
**After:**
    Tiny pygame demo: a red square that moves with the arrow keys, ESC
    exits. No game.json, exercises every default in the discovery path
    (folder name -> "Red Square", default attribution, no preview, no
    warnings).
**Why:** Smoke test for the no-manifest path and a copy-paste starting
point for students.

**File:** games/student/blue-circle/main.py
**Lines (at time of edit):** (new file)
**After:**
    Pygame demo: a blue circle that moves with the arrow keys, ESC exits.
    Has a sibling game.json that overrides the label and attribution.
**Why:** Smoke test for the manifest path. Demonstrates the
"CREATED BY <NAME>" attribution Mr. Navarro asked for.

**File:** games/student/blue-circle/game.json
**Lines (at time of edit):** (new file)
**After:**
    {
        "label": "Blue Circle Demo",
        "attribution": "CREATED BY ALEX EXAMPLE"
    }
**Why:** Minimal manifest illustrating the two most common overrides.
Other manifest keys are documented in games/student/README.md.

## 2026-04-29 Shrink JIL logo and move path/size to settings (GitHub Copilot GPT-4.1)

**File:** settings.py
**Lines (at time of edit):** LauncherSettings class (modified)
**Before:**
    # No JIL logo path/size constants
**After:**
    JIL_LOGO_PATH = Path("assets") / "graphics" / "graphics" / "jil_logo.webp"
    JIL_LOGO_POS = (20, 20)
    JIL_LOGO_SIZE = (72, 72)
**Why:** All file paths and constants must be in settings. Shrink logo for less visual dominance.

**File:** main.py
**Lines (at time of edit):** ArcadeLauncher __init__, draw (modified)
**Before:**
    self.jil_logo_path = self.root_dir / "assets" / "graphics" / "graphics" / "jil_logo.webp"
    ...
    self.screen.blit(self.jil_logo_surface, (20, 20))
**After:**
    self.jil_logo_path = self.root_dir / LauncherSettings.JIL_LOGO_PATH
    ...
    self.screen.blit(self.jil_logo_surface, LauncherSettings.JIL_LOGO_POS)
**Why:** Centralize all file paths and constants in settings, shrink logo, and ensure compliance with TESTING.md.
# Change Log

This file is an append-only record of every code change made to Dungeon Digger
by a human, AI assistant, or copilot tool. Read it before making changes so you
know the current state of the codebase.

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

---

## 2026-04-29 — Tetris meets the four launcher criteria (Claude Opus 4.7)

**File:** games/tetris/main.py
**Lines (at time of edit):** 1-90 (modified, full run loop and bootstrap)
**Before:**
        # ESC only exited fullscreen, no controller setup, no quit combo,
        # no SELECT-button fullscreen toggle.
        if event.key == pygame.K_F11:
            self.toggle_fullscreen()
        elif event.key == pygame.K_ESCAPE and self.fullscreen:
            self.toggle_fullscreen()
**After:**
        # F11 + SELECT toggle fullscreen, ESC + quit combo always exit.
        if event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
        elif event.key == pygame.K_ESCAPE:
            self.close_game()
        ...
        if event.button == SELECT_BUTTON:
            pygame.display.toggle_fullscreen()
**Why:** Tetris failed three of the four launcher criteria — ESC didn't exit
to the launcher, the controller had no fullscreen toggle, and the
L1+R1+START+SELECT quit combo was missing. Added `setup_controllers`,
`quit_combo_pressed`, and `close_game` so the file mirrors the helper
shape Dungeon Digger uses, then wired F11/SELECT/ESC/quit-combo into the
event loop.

## 2026-04-29 — Dungeon Warrior honors ESC exit (Claude Opus 4.7)

**File:** games/dungeon-warrior/main.py
**Lines (at time of edit):** 95-106 (modified)
**Before:**
        if event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
        elif event.key == pygame.K_F1:
            DebugSettings.SHOW_UI_FRAMES = not DebugSettings.SHOW_UI_FRAMES
**After:**
        if event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
        elif event.key == pygame.K_ESCAPE:
            self.close_game()
        elif event.key == pygame.K_F1:
            DebugSettings.SHOW_UI_FRAMES = not DebugSettings.SHOW_UI_FRAMES
**Why:** ESC was a no-op so the player had no keyboard exit shortcut. Hooking
it to the existing `close_game` keeps the keyboard exit consistent with the
controller's L1+R1+START+SELECT combo across the cabinet.

## 2026-04-29 — Ninja Frog gains ESC + quit combo (Claude Opus 4.7)

**File:** games/ninja-frog/main.py
**Lines (at time of edit):** 90-132 (modified)
**Before:**
        # No quit combo, no close_game helper, ESC silently ignored.
**After:**
        QUIT_COMBO_BUTTONS = (
            ControllerSettings.START_BUTTON,
            ControllerSettings.SELECT_BUTTON,
            ControllerSettings.L1_BUTTON,
            ControllerSettings.R1_BUTTON,
        )
        ...
        def quit_combo_pressed(self): ...
        def close_game(self): ...
        # ESC -> close_game, quit combo polled per-frame
**Why:** Ninja Frog ignored ESC and lacked the L1+R1+START+SELECT chord, so
players had no controller-only way back to the launcher. Added the standard
helpers using the existing ControllerSettings constants and wired ESC to
close_game so keyboard and controller exits behave the same.

## 2026-04-29 — Game of the Amazons stub adds keyboard/controller exit (Claude Opus 4.7)

**File:** games/game-of-the-amazons/graphics/audio/music/font/main.py
**Lines (at time of edit):** 71-94 (modified)
**Before:**
        # _process_events only handled QUIT; KEYDOWN/JOYBUTTONDOWN dispatch was commented out.
**After:**
        elif event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.JOYBUTTONDOWN:
            self._handle_joybuttondown(event)
        ...
        # _handle_keydown wires F11 + ESC; _handle_joybuttondown wires SELECT + quit-combo.
**Why:** The stub launched fine but offered no way out — F11/ESC/SELECT/
quit-combo were all dead. Even an under-construction game needs to honor the
four launcher criteria so testers aren't trapped.

## 2026-04-29 — Breakout: controller support + four launcher criteria (Claude Opus 4.7)

**File:** games/breakout/settings.py
**Lines (at time of edit):** 31-44 (added)
**Before:**
        UPGRADES = ['speed','laser','heart','size']
**After:**
        UPGRADES = ['speed','laser','heart','size']

        # Controller button mapping shared with the rest of the arcade ...
        A_BUTTON = 0
        SELECT_BUTTON = 6
        START_BUTTON = 7
        L1_BUTTON = 4
        R1_BUTTON = 5
        QUIT_COMBO_BUTTONS = (START_BUTTON, SELECT_BUTTON, L1_BUTTON, R1_BUTTON)
        LEFT_STICK_X_AXIS = 0
        CONTROLLER_DEADZONE = 0.15
**Why:** Per project convention all constants live in settings.py. Added the
controller mapping (and analog deadzone) needed to make Breakout playable
with a controller without sprinkling magic numbers through main.py / sprites.py.

**File:** games/breakout/sprites.py
**Lines (at time of edit):** 38-78 (modified)
**Before:**
        def __init__(self,groups,surfacemaker):
            ...
        def input(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
            else:
                self.direction.x = 0
**After:**
        def __init__(self,groups,surfacemaker,joysticks=None):
            ...
            self.joysticks = joysticks if joysticks is not None else []
        def controller_axis(self):
            # left-stick horizontal axis past the configured deadzone, signed.
            ...
        def input(self):
            axis_deflection = self.controller_axis()
            if axis_deflection != 0.0:
                self.direction.x = axis_deflection
                return
            # ... existing keyboard fallback ...
**Why:** Player needed to read the left analog stick to satisfy the new
"left analog stick to move" requirement. Storing a reference to the live
joystick list (instead of polling pygame.joystick directly) keeps the paddle
in sync with hot-plug refreshes that mutate Game.joysticks in place.

**File:** games/breakout/main.py
**Lines (at time of edit):** 1-209 (modified)
**Before:**
        # No joystick init, no quit combo, no F11/ESC/SELECT/A handling;
        # the only input was K_SPACE to fire and the keyboard arrows in
        # Player.input. Window opened in non-SCALED mode.
**After:**
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT), pygame.SCALED)
        ...
        self.setup_controllers()
        self.player = Player(self.all_sprites,self.surfacemaker,self.joysticks)
        ...
        def quit_combo_pressed(self): ...
        def close_game(self): ...
        def fire(self):
            self.ball.active = True
            if self.can_shoot: ...
        # Run loop now wires F11 + SELECT (fullscreen),
        # ESC + L1+R1+START+SELECT (exit), SPACE + A (fire).
**Why:** Breakout previously failed every one of the four launcher criteria
and had no controller support at all. Refactor follows Dungeon Digger's
shape — `setup_controllers`, `quit_combo_pressed`, `close_game`, and a
single `fire` helper that both SPACE and the A button call so keyboard and
controller bindings stay in lock step. SCALED display flag lets fullscreen
toggle render the playfield uniformly instead of in a top-left window.

## 2026-04-29 — Tetris D-pad mirrors arrow keys (Claude Opus 4.7)

**File:** games/tetris/main.py
**Lines (at time of edit):** 56-58 (modified)
**Before:**
        self.game = Game(self.get_next_shape, self.update_score)
**After:**
        self.game = Game(self.get_next_shape, self.update_score, self.connected_joysticks)
**Why:** Game needs a live reference to the joystick list so its per-frame
input poll picks up the same controllers Main tracks for the quit combo.

**File:** games/tetris/game.py
**Lines (at time of edit):** 9-20 (modified) and 101-126 (modified)
**Before:**
        def __init__(self, get_next_shape, update_score):
            ...
        def input(self):
            keys = pygame.key.get_pressed()
            if not self.timers['horizontal move'].active:
                if keys[pygame.K_LEFT]: ...
                if keys[pygame.K_RIGHT]: ...
            if not self.timers['rotate'].active:
                if keys[pygame.K_UP]: ...
            ...
**After:**
        def __init__(self, get_next_shape, update_score, joysticks=None):
            ...
            self.joysticks = joysticks if joysticks is not None else []
        def controller_dpad(self):
            # Return (hat_x, hat_y) of the first engaged D-pad, else (0, 0).
            ...
        def input(self):
            keys = pygame.key.get_pressed()
            hat_x, hat_y = self.controller_dpad()
            left_held = keys[pygame.K_LEFT] or hat_x == -1
            right_held = keys[pygame.K_RIGHT] or hat_x == 1
            up_held = keys[pygame.K_UP] or hat_y == 1
            down_held = keys[pygame.K_DOWN] or hat_y == -1
            # ... existing timer-debounced moves drive off the *_held booleans
**Why:** The D-pad now mimics the arrow keys exactly — left/right move,
up rotates, down soft-drops — by OR-ing the hat reading into the same
booleans the existing timer logic already gates on. No changes to the
debounce timers, no separate controller code path, so keyboard and D-pad
behavior stay identical.

## 2026-04-29 — Launcher: limited-controller category + global wonky-physics warning (Claude Opus 4.7)

**File:** settings.py
**Lines (at time of edit):** 78-85 (modified) and 139-156 (modified)
**Before:**
        NO_CONTROLLER_SUPPORT_TEXT = "NO CONTROLLER SUPPORT (KEYBOARD/MOUSE ONLY)"
        NO_CONTROLLER_SUPPORT_CENTER_Y = 585
        LIMITED_CONTROLLER_SUPPORT_TEXT = "LIMITED CONTROLLER SUPPORT"
        LIMITED_CONTROLLER_SUPPORT_CENTER_Y = 585
        AIR_HOCKEY_WARNING_TEXT = "STILL TUNING THE PHYSICS, EXPECT QUIRKS"
        AIR_HOCKEY_WARNING_CENTER_Y = 605
        ...
        LIMITED_CONTROLLER_SUPPORT_GAMES = {"Air Hockey"}
        NO_CONTROLLER_SUPPORT_GAMES = {"Jezz Ball"}
**After:**
        NO_CONTROLLER_SUPPORT_TEXT = "NO CONTROLLER SUPPORT (KEYBOARD/MOUSE ONLY)"
        LIMITED_CONTROLLER_SUPPORT_TEXT = "LIMITED CONTROLLER SUPPORT"
        WONKY_PHYSICS_TEXT = "STILL TUNING THE PHYSICS, EXPECT WONKINESS"
        WARNING_LINE_1_CENTER_Y = 585
        WARNING_LINE_2_CENTER_Y = 605
        ...
        LIMITED_CONTROLLER_SUPPORT_GAMES = {"Air Hockey", "Jezz Ball"}
        NO_CONTROLLER_SUPPORT_GAMES: set[str] = set()
        WONKY_PHYSICS_GAMES = {"Air Hockey", "Ninja Frog"}
**Why:** Two stacked warning slots replace the per-warning Y constants
because the duplicate 585s for NO/LIMITED were just aliases of the same
position, and the second slot needed to apply to wonky-physics in
general — not just Air Hockey. Renamed AIR_HOCKEY_WARNING → WONKY_PHYSICS
because the warning is now a global toggle, and changed the copy from
"QUIRKS" to "WONKINESS" per the requested wording. Jezz Ball moved from
NO to LIMITED controller support; NO_CONTROLLER_SUPPORT_GAMES is now an
empty set so the structure stays available for future games.

**File:** main.py
**Lines (at time of edit):** 228-272 (added) and 361-362 (modified)
**Before:**
        # Inline rendering of the no-controller line, then a hard-coded
        # `if selected_label == "Air Hockey":` second line.
**After:**
        def collect_warning_lines(self, selected_label):
            warnings = []
            if selected_label in GameSettings.NO_CONTROLLER_SUPPORT_GAMES:
                warnings.append(MenuSettings.NO_CONTROLLER_SUPPORT_TEXT)
            elif selected_label in GameSettings.LIMITED_CONTROLLER_SUPPORT_GAMES:
                warnings.append(MenuSettings.LIMITED_CONTROLLER_SUPPORT_TEXT)
            if selected_label in GameSettings.WONKY_PHYSICS_GAMES:
                warnings.append(MenuSettings.WONKY_PHYSICS_TEXT)
            return warnings

        def draw_preview_warnings(self, selected_label):
            slot_y_positions = (WARNING_LINE_1_CENTER_Y, WARNING_LINE_2_CENTER_Y)
            for slot_index, warning_text in enumerate(self.collect_warning_lines(...)):
                # render at slot_y_positions[slot_index]
**Why:** The user wanted controller and wonky warnings to flow into two
positional slots — wonky moves into slot 1 when alone and into slot 2
when stacked under a controller warning. Splitting collection from
rendering makes the slot logic obvious: collect ordered strings, then
render them into the corresponding slot Ys. The hard-coded "Air Hockey"
check is replaced with WONKY_PHYSICS_GAMES set membership so any game can
opt in.

## 2026-04-29 — Tetris: A/X rotates, D-pad up hard drops (Claude Opus 4.7)

**File:** games/tetris/settings.py
**Lines (at time of edit):** 53-58 (added)
**Before:**
        SCORE_DATA = {1: 40, 2: 100, 3: 300, 4: 1200}
**After:**
        SCORE_DATA = {1: 40, 2: 100, 3: 300, 4: 1200}

        A_BUTTON = 0
        X_BUTTON = 2
        ROTATE_BUTTONS = (A_BUTTON, X_BUTTON)
**Why:** Player wants either A or X to rotate. Both buttons live in
ROTATE_BUTTONS so the input-side just iterates the tuple.

**File:** games/tetris/game.py
**Lines (at time of edit):** 49-51 (added), 122-138 (added), 140-180 (modified), and 267-279 (added)
**Before:**
        # D-pad up rotated alongside K_UP via OR-merge; no hard drop.
        rotate_held = keys[pygame.K_UP] or hat_y == 1
        ...
        # Tetromino had no hard_drop method.
**After:**
        # __init__: self.previous_hat_y = 0  (edge-detection memory)
        def controller_rotate_held(self):
            for joystick in self.joysticks:
                for button in ROTATE_BUTTONS:
                    if joystick.get_button(button): return True
            return False
        ...
        # input(): D-pad up edge-triggers hard drop, A/X rotates
        if hat_y == 1 and self.previous_hat_y != 1:
            self.tetromino.hard_drop()
        self.previous_hat_y = hat_y
        rotate_held = keys[pygame.K_UP] or self.controller_rotate_held()
        ...
        # Tetromino.hard_drop: walks down until blocked, then locks +
        # spawns the next piece, mirroring move_down's lock-on-collide branch.
**Why:** D-pad up is now a one-shot hard drop, so a held hat doesn't
slam multiple pieces in a row — edge-detection on previous_hat_y enforces
"one tap, one drop." Rotate is detached from hat_y and reads A/X with the
existing rotate timer for debounce. K_UP keeps rotating because the
request only changed the controller binding. Tetromino.hard_drop reuses
move_down's lock-on-collide logic so the field bookkeeping path stays
identical to a piece dropping naturally.

## 2026-04-29 — Launcher: white outline around the WORK IN PROGRESS overlay (Claude Opus 4.7)

**File:** main.py
**Lines (at time of edit):** 228-271 (modified)
**Before:**
        if selected_label in GameSettings.UNDER_CONSTRUCTION_GAMES:
            construction_surface = self.option_font.render(
                MenuSettings.UNDER_CONSTRUCTION_TEXT,
                False,
                ColorSettings.RED,
            )
            construction_rect = construction_surface.get_rect(center=preview_rect.center)
            self.screen.blit(construction_surface, construction_rect)
**After:**
        if selected_label in GameSettings.UNDER_CONSTRUCTION_GAMES:
            self.draw_outlined_text(
                MenuSettings.UNDER_CONSTRUCTION_TEXT,
                self.option_font,
                ColorSettings.RED,
                ColorSettings.WHITE,
                preview_rect.center,
            )

        def draw_outlined_text(self, text, font, fg_color, outline_color, center):
            # Render the same text twice (outline color, then fg color) and
            # stamp the outline at the eight neighboring pixel offsets so the
            # red label stays legible on warm-toned previews.
            ...
**Why:** The red WORK IN PROGRESS overlay washed out against the dungeon
previews. Stamping the outline-colored render at the eight neighbors and
blitting the foreground last produces a 1-pixel white outline that traces
the full glyph silhouette. Factored into a reusable helper so other red
warnings can opt into the same treatment later without duplicating the
nine-blit sequence.

## 2026-04-29 — PEP-8 cleanup and remove unused import (GitHub Copilot GPT-4.1)

**File:** main.py
**Lines (at time of edit):** 7, 74-77 (modified)
**Before:**
import warnings
self.options = [(label, self.root_dir / relative_path) for label, relative_path in GameSettings.OPTIONS]
self.menu_option_hitboxes: list[pygame.Rect] = [pygame.Rect(0, 0, 0, 0) for _ in self.options]
**After:**
# (removed)
self.options = [
    (label, self.root_dir / relative_path)
    for label, relative_path in GameSettings.OPTIONS
]
self.menu_option_hitboxes: list[pygame.Rect] = [
    pygame.Rect(0, 0, 0, 0)
    for _ in self.options
]
**Why:** Remove unused import and wrap long lines for PEP-8 compliance per TESTING.md.