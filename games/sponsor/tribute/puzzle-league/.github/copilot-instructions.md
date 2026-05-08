# Copilot Instructions for Puzzle League

These rules apply to **every** editor of this codebase, human or AI. They are not suggestions. Read this file before each session.

This game is a **standalone project**. It happens to live inside the Arcade Cabinet repo, but its code is agnostic to the launcher: running `python main.py` from this folder must always work on its own. Do not import launcher modules, do not assume the launcher exists, and do not edit files outside this folder from a Puzzle League change.

The current state of the codebase is a **scaffold**. The folder layout, settings, and main loop mirror Star Hero and Dungeon Digger so the project feels familiar — preserve that pattern when filling in gameplay.

---

## Required reading order (before any change)

1. [README.md](../README.md) — what the project is and how to run it.
2. [docs/TODO.md](../docs/TODO.md) — current phase and roadmap.
3. [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) — how the code actually works.
4. [docs/CHANGELOG.md](../docs/CHANGELOG.md) — most recent changes, so you know the current state.
5. The source files relevant to your task.

If a question is asked about *why* code was written a certain way, that is a request for an **explanation**, not a request for a code change. Do not modify code unless the user explicitly asks for a change.

---

## Required actions (after any change)

- Append an entry to [docs/CHANGELOG.md](../docs/CHANGELOG.md) following the format defined at the top of that file (ISO 8601 timestamp with timezone, file path, line numbers at time of edit, before/after code, why, and editor name including the AI model used).
- If your change altered how a system works, update the matching section of [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md). Out-of-date architecture docs are worse than none.
- If your change completes or adds a roadmap item, update [docs/TODO.md](../docs/TODO.md) (mark `[x]`, do not delete).
- Run the manual smoke checks in [docs/TESTING.md](../docs/TESTING.md).

---

## Code style

- All Python code must be PEP-8 compliant.
- Less code is better; clean and readable is best.
- Prefer clear names over short ones. New class and function names must clearly describe their purpose.
- Do not change function or variable names unless the role has *completely* changed.
- Keep code free of dead imports, unused variables, unused functions, and legacy code.

## Architecture rules

- `GameManager` ([main.py](../main.py)) must stay thin. Push gameplay into `core/board.py` (board state machine) and dedicated rendering helpers under `ui/`.
- Classes should communicate through `GameManager` where possible. Avoid systems reaching directly into each other.
- Keep middlemen minimal: if A calls B and B only calls C, have A call C directly.
- All constants live in [settings.py](../settings.py). **No magic numbers anywhere else.** When adding a constant, include a comment explaining its units and effect.
- Per-system tunables live in their dedicated `*Settings` class (`BoardSettings`, `BlockSettings`, `CursorSettings`, `RiseSettings`, `ScoreSettings`, etc.) rather than overflowing one monolithic class.
- The `Board` model never touches `pygame.Surface` objects. Rendering reads the board's public state.

## File and function layout

- Inside a class, group functions by role (boot, lifecycle, controller plumbing, event handling, per-frame update, render, run loop). The scaffold establishes these section banners — keep them.
- `update` and `run` go **last** and should only call other functions on the class.
- Separate logical sections inside a file with an all-caps banner comment, exactly this style:

  ```python
      # -------------------------
      # SECTION NAME
      # -------------------------
  ```

  Match the leading indentation of the surrounding class body. Keep the dashes the same length and the name in ALL CAPS.

## Comments and docstrings

- Every class and function must have a docstring with a one-line summary, plus `Args:` / `Returns:` blocks when applicable.
- Do not remove docstrings. Update them in place if behavior changes.
- Do not remove comments unless they are inaccurate; prefer updating them.
- Comments must explain **why**, not just what.
- Do not leave comments noting that a change was made, unless they explain a non-obvious bug fix or unconventional code.

## UI text

- Player-facing text in the HUD, title screen, and overlays should be **ALL CAPS** to match the retro pixel aesthetic. Documentation files stay in normal sentence case.

---

## Mental testing checklist (run after major changes)

- The game launches (`python main.py`) without console errors.
- A LOADING card appears briefly during init.
- Title screen renders with the configured title and prompt copy.
- `Enter` (keyboard) or A/Start (controller) triggers `SessionStateManager.reset_for_new_game()`.
- The CRT overlay is visible.
- `F11` / Back toggles fullscreen.
- `Esc` and the controller quit combo both exit cleanly.
- No new magic numbers leaked outside `settings.py`.

For the actionable run-through, see [docs/TESTING.md](../docs/TESTING.md).
