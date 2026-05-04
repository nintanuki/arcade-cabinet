# Change Log

This file is an append-only record of every code change made to Mr. Navarro's
Arcade by a human, AI assistant, or copilot tool. Read it before making changes
so you know the current state of the codebase.

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

* The newest entry is added immediately below the `---` separator, so the
  file reads newest-first. Older entries shift down as new ones are
  prepended; never insert a new entry above the header or in the middle of
  the timeline.
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

## 2026-05-04 — Split monolithic main.py into launcher package; main.py becomes entry point only (Claude Sonnet 4.6)

**File:** main.py
**Lines (at time of edit):** entire file replaced (~1200 lines → 9 lines)
**Before:**
    Module-level docstring + all imports + StudentGameRecord, MenuNode,
    MenuFrame dataclasses + _read_student_manifest + discover_student_games
    functions + LauncherCRT class + ArcadeLauncher class (all rendering,
    input handling, navigation, audio, and game-launch logic).
**After:**
    ```python
    """Entry point for the Coding Club Arcade launcher."""
    from pathlib import Path
    from launcher.manager import ArcadeLauncher
    if __name__ == "__main__":
        ArcadeLauncher(Path(__file__).resolve().parent).run()
    ```
**Why:** main.py was doing everything. Separating responsibilities makes each
    file easier to read, test, and extend.

**File:** settings.py
**Lines (at time of edit):** LauncherSettings block (added 3 lines)
**Before:**
    JIL_LOGO_SIZE = (59, 69)
    # Horizontal gap between...
**After:**
    JIL_LOGO_SIZE = (59, 69)
    # Maximum pixel dimensions for scaled preview screenshots.
    PREVIEW_MAX_WIDTH = 296
    PREVIEW_MAX_HEIGHT = 216
**Why:** The preview image max dimensions were computed inline in
    _load_preview_images. Constants belong in settings.py.

**File:** launcher/__init__.py (new file)
**Why:** Makes `launcher/` a Python package.

**File:** launcher/models.py (new file)
**Why:** Extracted StudentGameRecord, MenuNode, MenuFrame dataclasses from
    main.py. Pure data — no pygame, no logic.

**File:** launcher/crt.py (new file)
**Why:** Extracted LauncherCRT from main.py. Self-contained visual component.

**File:** launcher/discovery.py (new file)
**Why:** Extracted _read_student_manifest and discover_student_games from
    main.py. Pure functions with no dependency on the launcher class.

**File:** launcher/renderer.py (new file)
**Why:** All draw_* methods, text-wrap helpers, and font/logo loading moved
    out of ArcadeLauncher into LauncherRenderer. Renderer owns menu_option_hitboxes
    (written during draw, read by manager for mouse input). Added draw_loading_frame
    so show_loading_screen in the manager delegates drawing cleanly.

**File:** launcher/manager.py (new file)
**Why:** ArcadeLauncher now only coordinates: runtime init, audio, menu-tree
    building, navigation state, game launching, input dispatch, and the run loop.
    The run() method only calls other functions — no inline input logic.
    _restore_runtime() added to cleanly rebuild the renderer after a game exits
    (previously the renderer would have held a stale screen reference).

## 2026-05-02 — Nested launcher menus, per-game captions, input-scheme + note warning system, demo expansion (Claude Opus 4.7)

**File:** settings.py
**Lines (at time of edit):** entire file restructured (~225 → ~370 lines)
**Before:**
    Flat config classes. GameSettings carried OPTIONS, PREVIEW_IMAGES,
    GAME_ATTRIBUTIONS, LIMITED_/NO_CONTROLLER_SUPPORT_GAMES,
    WONKY_PHYSICS_GAMES, UNDER_CONSTRUCTION_GAMES. MenuSettings carried
    NO_CONTROLLER_SUPPORT_TEXT, LIMITED_CONTROLLER_SUPPORT_TEXT,
    WONKY_PHYSICS_TEXT. StudentGameSettings exposed
    MANIFEST_KEY_NO_CONTROLLER / MANIFEST_KEY_LIMITED_CONTROLLER /
    MANIFEST_KEY_WONKY_PHYSICS.
**After:**
    Added InputSchemeSettings (STANDARD / LIMITED_CONTROLLER /
    NO_CONTROLLER / MOUSE_ONLY / MOUSE_AND_KEYBOARD / KEYBOARD_ONLY +
    LABELS dict). Added CategorySettings (STUDENT / ORIGINAL / TRIBUTE
    / TUTORIAL with LABELS / DESCRIPTIONS / ATTRIBUTIONS). Added
    GroupSettings (MR_NAVARRO with LABELS / DESCRIPTIONS). Added
    MenuTreeSettings (KIND_CATEGORY / KIND_GROUP / ROOT — the
    navigation tree as data).

    GameSettings: dropped GAME_ATTRIBUTIONS, the two CONTROLLER sets,
    and WONKY_PHYSICS_GAMES; added GAME_CATEGORIES,
    GAME_INPUT_SCHEMES, GAME_NOTES, GAME_DESCRIPTIONS. Pazaak and
    Puzzle League added across OPTIONS / PREVIEW_IMAGES /
    GAME_CATEGORIES (TRIBUTE) / GAME_DESCRIPTIONS;
    UNDER_CONSTRUCTION_GAMES gains Pazaak.

    MenuSettings: dropped NO_CONTROLLER_SUPPORT_TEXT /
    LIMITED_CONTROLLER_SUPPORT_TEXT / WONKY_PHYSICS_TEXT; added
    CAROUSEL_THRESHOLD, LIST_ITEM_SPACING, LIST_CURSOR_TEXT,
    DESCRIPTION_LINE_SPACING, DESCRIPTION_HIGHLIGHTS,
    CAPTION_LINE_SPACING.

    ControlSettings: added CONTROLLER_BUTTON_B = 1.
    ColorSettings: added ORANGE.
    FontSettings: added DESCRIPTION_SIZE = 10.
    StudentGameSettings: dropped the three legacy controller / physics
    manifest keys; added MANIFEST_KEY_INPUT_SCHEME and
    MANIFEST_KEY_NOTE.
**Why:** The flat menu didn't scale once we wanted students to author
their own games and Mr. Navarro's lineup to be split by
"original / tribute / tutorial". Categories + a navigation-tree
constant solve that, and replacing the binary controller flags +
hardcoded "wonky physics" string with an input-scheme enum and a
free-form note slot lets every game (sponsor or student) carry
variable warning copy without a code change.

**File:** main.py
**Lines (at time of edit):** entire file restructured (~755 → ~960 lines)
**Before:**
    Flat self.options list, single carousel renderer, attribution
    rendered in light blue, controller / wonky-physics warnings
    derived from GameSettings sets. ESC quit immediately, no B button
    binding.
**After:**
    Added MenuNode dataclass (kind: "game" | "submenu", with game-only
    fields like main_path / preview_path / attribution /
    input_scheme_key / note / under_construction / category_key) and
    MenuFrame (items + cursor index). __init__ walks
    MenuTreeSettings.ROOT to build the tree, attaching games to
    category leaves via _filter_games_by_category.

    Navigation: forward (A / Start / Enter / Space) launches games or
    pushes submenus; back (B / Esc) pops a level; Esc at the root
    still quits. Per-level cursor memory survives push/pop. Empty
    submenu (e.g. an empty Student Games folder) plays the select SFX
    and stays put.

    draw_menu picks between draw_carousel_menu and a new
    draw_list_menu (vertical list, `>` cursor on the selected row,
    yellow / white) based on CAROUSEL_THRESHOLD. draw_preview_panel
    routes to _draw_game_preview for game nodes and _draw_description
    for submenu nodes; descriptions wrap (_wrap_description_with_colors)
    and render with per-phrase color runs driven by
    _build_description_color_map and DESCRIPTION_HIGHLIGHTS.

    Caption under the preview is now node.attribution rendered in
    white (was light blue), wraps against PREVIEW_BOX_WIDTH via the
    new _wrap_simple helper, and pushes the warning slots down only
    when wrapped. Sponsor games source the caption from
    GameSettings.GAME_DESCRIPTIONS; student games still use the
    manifest's attribution field. collect_warning_lines reads
    node.input_scheme_key (looked up in InputSchemeSettings.LABELS)
    and node.note instead of the removed GameSettings sets.

    discover_student_games reads MANIFEST_KEY_INPUT_SCHEME (validated
    against the known scheme keys; unknown values are silently ignored
    so a typo never bricks the menu) and MANIFEST_KEY_NOTE.
    StudentGameRecord fields renamed accordingly:
    no_controller / limited_controller / wonky_physics →
    input_scheme_key + note.
**Why:** Mirrors the settings refactor. The menu-stack model keeps the
draw and input handlers oblivious to depth, the colored description
rendering keeps category screens visually distinct from games, and
the caption rewrite removes the redundant "ORIGINAL BY MR. NAVARRO"
line whose info is now advertised by the menu location and the
preview-box description.

**File:** games/student/README.md
**Lines (at time of edit):** several modified blocks
**Before:**
    Manifest table listed `no_controller_support`,
    `limited_controller_support`, `wonky_physics`,
    `under_construction`. Example JSON used those keys. Walk-through
    said new games "appear at the bottom of the carousel". Caption
    described as "Blue text under the preview panel". Demo links
    pointed at `red-square/` and `blue-circle/`.
**After:**
    Manifest table replaced controller / physics flags with
    `input_scheme` (sub-table of valid string values) and `note`
    (free-form red text) plus `under_construction`. Example JSON
    updated. Walk-through says new games "appear under Student Games
    on the main menu". Caption described as "White caption under the
    preview panel". Demo links point at `red-square-demo/` and
    `blue-circle-demo/`.
**Why:** Doc the schema and discovery flow that actually runs now.

**File:** README.md (top-level)
**Lines (at time of edit):** 49-58 (modified), 64 (modified)
**Before:**
    Controller list said "Select/Back: Toggle fullscreen", no B
    button. Catalog blurb cited UNDER_CONSTRUCTION_GAMES,
    LIMITED_CONTROLLER_SUPPORT_GAMES, NO_CONTROLLER_SUPPORT_GAMES,
    WONKY_PHYSICS_GAMES.
**After:**
    Controller list adds "B: Back to previous menu" and Esc described
    as "back, exits at the root". Catalog blurb cites
    GAME_CATEGORIES, GAME_INPUT_SCHEMES, GAME_NOTES,
    UNDER_CONSTRUCTION_GAMES.
**Why:** Match the new bindings and settings names.

**File:** games/sponsor/pazaak/main.py (new file)
**Before:** (file did not exist)
**After:**
    Minimal pygame placeholder: opens a 1280x720 SCALED window, paints
    "PAZAAK / UNDER CONSTRUCTION - PRESS ESC TO RETURN", exits on ESC,
    the L1+R1+SELECT+START quit chord, or the window's close button.
**Why:** Pazaak appears in the launcher under Tribute Games now and
needs a runnable entry point. Real gameplay can land later without
touching the launcher plumbing.

**File:** games/student/red-square-demo/main.py (new file)
**Before:** (file did not exist)
**After:**
    pygame demo: red square, movable via arrow keys / WASD / D-pad /
    left stick (deadzoned), bounded to the screen. Exits on ESC, the
    quit chord, or the close button.
**Why:** Tests the launcher's auto-discovery path -- no game.json
sits next to it, so the launcher must derive label and attribution
from defaults.

**File:** games/student/blue-circle-demo/main.py (new file)
**Before:** (file did not exist)
**After:**
    Same control + exit pattern as red-square-demo, draws a blue
    circle.
**Why:** Tests the launcher's full-manifest path; paired with the
game.json below.

**File:** games/student/blue-circle-demo/game.json (new file)
**Before:** (file did not exist)
**After:**
    {"label": "Blue Circle Demo", "attribution": "CREATED BY MR.
    NAVARRO (DEMO)", "input_scheme": "mouse_only", "note": "DEMO
    MANIFEST EXAMPLE"}
**Why:** Exercises every optional manifest field the launcher reads.

**File:** games/student/green-triangle-demo/main.py (new file)
**Before:** (file did not exist)
**After:**
    Same control + exit pattern as the other demos, draws a point-up
    equilateral triangle (circumscribed-radius bounds for clamping).
**Why:** Tests the launcher's "some fields set, others defaulted"
manifest path.

**File:** games/student/green-triangle-demo/game.json (new file)
**Before:** (file did not exist)
**After:**
    {"attribution": "CREATED BY MR. NAVARRO (PARTIAL DEMO)", "note":
    "PARTIAL MANIFEST EXAMPLE"}
**Why:** Only `attribution` and `note` are set -- `label` falls back
to the folder name, missing `input_scheme` means no warning line,
missing `preview` means "PREVIEW NOT AVAILABLE", and
`under_construction` defaults to false.

**File:** TODO.md
**Lines (at time of edit):** 1-2 (new section prepended)
**Before:**
    ## Game Ideas
    - [ ] Tetris Attack / Panel de Pon
**After:**
    ## Working agreements
    - After every code change ..., append a new entry to
      docs/CHANGELOG.md ...

    ## Game Ideas
    ...
**Why:** Make the changelog requirement visible to anyone (human, AI,
or copilot) opening the TODO so this session's miss (the entire
refactor landing without a single CHANGELOG entry) doesn't repeat.

## 2026-05-01 — Reorganize CHANGELOG header + extract logo-placeholder color constant (Claude Opus 4.7)

**File:** docs/CHANGELOG.md
**Lines (at time of edit):** 276-312 (deleted), 1-40 (new)
**Before:**
    The "# Change Log / ## Format / ## Conventions / ---" header was buried
    around line 276, between the 2026-04-29 "Shrink JIL logo" entry and the
    2026-04-29 "Tetris meets the four launcher criteria" entry. Some recent
    entries (including the 2026-05-01 entries above this one) had been
    prepended above the buried header; older entries sat below it. The
    header description still said "made to Dungeon Digger" — a leftover
    from when this CHANGELOG was the dungeon-digger per-game log before
    being adopted as the project-wide log.
**After:**
    Single header block at the top of the file (project-wide wording, not
    "Dungeon Digger"); entries follow newest-first directly below the
    `---` separator. New convention bullet at the top of the Conventions
    list explicitly says newest entries go right under `---`, so future
    copilot runs do not drift the header back into the middle of the file.
**Why:** A previous copilot pass started prepending new entries above the
header instead of below it, which buried the header further every time
and made the convention block effectively invisible. Pulling the header
back to the top and stating the ordering rule explicitly should keep
this from regressing.

**File:** settings.py
**Lines (at time of edit):** 31-34 (added)
**Before:**
    JIL_LOGO_TITLE_SPACING = 20
**After:**
    JIL_LOGO_TITLE_SPACING = 20
    # Color of the placeholder rect drawn when the JIL logo file is missing.
    # Deliberately hotter than ColorSettings.RED so a missing-asset bug
    # cannot be visually confused with a normal red UI element.
    JIL_LOGO_PLACEHOLDER_COLOR = (255, 0, 0)
**Why:** TESTING.md "no magic numbers" rule. The hardcoded `(255, 0, 0)`
in main.py's missing-logo fallback is now a named constant so the intent
("hotter than the UI red on purpose") is documented in settings.

**File:** main.py
**Lines (at time of edit):** 593-599 (modified)
**Before:**
    pygame.draw.rect(self.screen, (255, 0, 0), (start_x, logo_y, *LauncherSettings.JIL_LOGO_SIZE), 2)
**After:**
    pygame.draw.rect(
        self.screen,
        LauncherSettings.JIL_LOGO_PLACEHOLDER_COLOR,
        (start_x, logo_y, *LauncherSettings.JIL_LOGO_SIZE),
        2,
    )
**Why:** Mirrors settings.py change. Wrapped onto multiple lines because
the call exceeded a reasonable line length once the constant name went
in; lines up with the rest of the file's PEP-8 wrapping conventions.

## 2026-05-01 — main.py cleanup: indentation, cite artifacts, debug prints, magic spacing (Claude Opus 4.7)

**File:** settings.py
**Lines (at time of edit):** 24-30 (modified)
**Before:**
    JIL_LOGO_PATH = Path("assets") / "graphics" / "jil_logo.webp"
    JIL_LOGO_POS = (50, 110)
    JIL_LOGO_SIZE = (59, 69)
**After:**
    JIL_LOGO_PATH = Path("assets") / "graphics" / "jil_logo.webp"
    JIL_LOGO_POS = (50, 110)
    JIL_LOGO_SIZE = (59, 69)
    # Horizontal gap between the JIL logo and the launcher title text. ...
    JIL_LOGO_TITLE_SPACING = 20
**Why:** TESTING.md mandates that constants live in settings.py (no magic
numbers). Pulls the logo/title gap out of `draw()` into a named constant so
the layout knob is discoverable next to the other JIL logo settings.

**File:** main.py
**Lines (at time of edit):** 191-199 (modified)
**Before:**
    print(f"[DEBUG] Loaded JIL logo: {self.jil_logo_path} size={...}")
    ...
    print(f"[DEBUG] Failed to load JIL logo: {self.jil_logo_path} error={e}")
    self.jil_logo_surface = None
**After:**
    # Comment block explaining why the logo loads after initialize_runtime;
    # both [DEBUG] print statements removed; silent fallback to None on error.
**Why:** [DEBUG] prints leaked to stdout on every launch even in production.
Behavior on missing/corrupt logo is unchanged (still falls back to the
placeholder rect in draw()), the prints were the only thing removed.

**File:** main.py
**Lines (at time of edit):** 460-481 (modified)
**Before:**
    Mixed tabs+spaces indentation throughout draw_preview_warnings; numbered
    "# 1. Always Draw Attribution" / "# 2. Draw Warnings" comments with
    [cite: 1] artifacts; trailing-whitespace-only blank lines between blocks.
**After:**
    Function is fully tab-indented; comments rewritten to explain *why*
    (slot ordering) rather than restate the code; [cite: 1] artifacts and
    whitespace-only blank lines removed.
**Why:** Mixed indentation is a TabError waiting to bite the next edit even
though it currently parses (the offending lines were comments / continuation
lines inside parens). The numbered "Step 1 / Step 2" comments were
copy-paste leftovers from a Notion/Gemini paste, hence the [cite: 1]
markers; replaced with intent comments per TESTING.md ("comments must
explain why, not just what").

**File:** main.py
**Lines (at time of edit):** 582-600 (modified)
**Before:**
    spacing = 20  # Adjust this to change the gap between logo and text
    ...
    # Uses ScreenSettings.WIDTH from settings.py[cite: 2]
    ...
    # Uses MenuSettings.TITLE_CENTER_Y to stay aligned with the text[cite: 2]
    ...
    # Fallback debug rect if logo missing[cite: 1]
**After:**
    Uses LauncherSettings.JIL_LOGO_TITLE_SPACING in both places the gap is
    referenced; the redundant "Uses X from settings.py" comments and their
    [cite: 2] / [cite: 1] artifacts are gone; trailing-whitespace blank
    lines collapsed.
**Why:** Same "no magic numbers" + "comments explain why, not what" rules
as the warning-block cleanup. The fallback rect color stays at (255, 0, 0)
deliberately — that hot-red flag is meant to be visually distinct from
ColorSettings.RED so a missing-asset bug can't be confused with normal UI.

## 2026-05-01 — README resync after sponsor/student split (Claude Opus 4.7)

**File:** README.md
**Lines (at time of edit):** 5-20 (modified), 62-126 (modified), 130-136 (modified), 138-145 (modified)
**Before:**
    Lineup listed "Dungeon Warrior"; per-game README links pointed at
    `games/<name>/README.md` (pre sponsor/student-split paths); status /
    input lines were stale (Air Hockey + Jezz Ball claimed "no controller
    support" though they're now in LIMITED_CONTROLLER_SUPPORT_GAMES;
    Breakout + Tetris claimed "keyboard only" despite their 2026-04-29
    controller-support work; Game of the Amazons listed Under Construction);
    Star Hero attributions linked to non-existent `games/star-hero/graphics/`
    paths (real files now sit under `games/sponsor/star-hero/assets/...`);
    Dungeon Warrior attributions section pointed at a deleted folder.
**After:**
    Lineup uses "Adventure" (matches settings.GameSettings.OPTIONS); every
    per-game README link rewritten with `games/sponsor/...` prefix; new
    sentence under the lineup explains the sponsor/student split and links
    to games/student/README.md; Status / Input lines for Adventure, Air
    Hockey, Breakout, Game of the Amazons, Jezz Ball, Ninja Frog, Tetris
    now agree with the LIMITED_CONTROLLER_SUPPORT_GAMES /
    NO_CONTROLLER_SUPPORT_GAMES / WONKY_PHYSICS_GAMES /
    UNDER_CONSTRUCTION_GAMES sets; Game of the Amazons promoted to
    Playable; quick-reference under-construction list trimmed to
    Adventure + Ninja Frog; Attributions section rewritten with
    sponsor/-prefixed paths and replaces Dungeon Warrior with Adventure's
    graphics/sound/music attributions.
**Why:** The 2026-04-29 sponsor/student-split CHANGELOG entry only renamed
the folders + updated settings.py; the top-level README was never resynced,
leaving every per-game link broken on GitHub. The same pass also picked up
the controller-support drift (status flags moved during the controller-work
sprint but the README was not updated). Source of truth for Status / Input
lines is `settings.GameSettings`; the README now mirrors it 1:1.

## 2026-04-29 — Clarify student README on relative paths and preview images (Claude Opus 4.7)

**File:** games/student/README.md
**Lines (at time of edit):** 47 (modified), 56-95 (new sections), 122-129 (modified)
**Before:**
    | `preview` | Path to a PNG/JPG screenshot, **relative to your game folder**. ...
    ...
    * Keep file paths relative to your `main.py` (use
      `Path(__file__).resolve().parent` as the base). Don't hard-code
      absolute paths -- they'll break on the cabinet.
**After:**
    | `preview` | Filename of a screenshot **relative to your game folder**
    (see "Preview screenshots" below). ...

    ## Preview screenshots
    [walkthrough of saving a PNG, pointing at it from game.json,
    panel size 320x240, missing-file fallback]

    ## File paths inside your game
    [explanation that the launcher sets cwd to the game folder, so
    `pygame.image.load("graphics/foo.png")` works without
    Path(__file__) gymnastics; advanced anchor-to-script tip is now
    optional and clearly framed as the "outside the launcher" case]

    * Don't hard-code absolute paths like `C:\Users\me\Desktop\sprite.png`.
      They will only work on your laptop. ...
**Why:** The first cut of the README told students to use
`Path(__file__).resolve().parent` as if it were required. It isn't --
the launcher runs each game with `cwd=game_dir` so plain relative paths
work. The new sections explain the cwd behavior, walk through how the
preview screenshot feature actually flows from game.json to the
preview panel, and reframe the script-anchored pattern as an optional
fallback for running games outside the launcher.

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