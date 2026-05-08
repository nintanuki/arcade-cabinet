# Copilot Instructions for Air Hockey

These rules apply to **every** editor of this codebase, human or AI. They are not suggestions. Read this file before each session.

This game is a **standalone project**. It happens to live inside the Arcade Cabinet repo, but its code is agnostic to the launcher: running `python main.py` from this folder must always work on its own. Do not import launcher modules, do not assume the launcher exists, and do not edit files outside this folder from an Air Hockey change.

---

## Required reading order (before any change)

1. [README.md](../README.md) — what the project is and how to run it.
2. [docs/TODO.md](../docs/TODO.md) — current phase, known bugs, roadmap.
3. [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) — how the code actually works.
4. [docs/CHANGELOG.md](../docs/CHANGELOG.md) — most recent changes.
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

- The `Game` class ([main.py](../main.py)) is the runtime coordinator. It is currently larger than ideal and the long-term goal is to split it into smaller helpers (input, update, render). When adding to it, prefer creating a new method or a new helper class over inlining more logic into `run()`.
- `Audio` ([audio.py](../audio.py)) owns all mixer state. Do not call `pygame.mixer` directly from `main.py`; route through `Audio`.
- `CRT` ([crt.py](../crt.py)) owns the post-process. The CRT pass is always the last thing drawn each frame, before `pygame.display.flip()`.
- All constants live in [settings.py](../settings.py). **No magic numbers anywhere else.** When adding a constant, include a comment explaining its units and effect.
- `settings.py` currently uses module-level constants and `from settings import *` at the call site. New constants should still go there; grouping them into `*Settings` classes is a pending refactor — see [docs/TODO.md](../docs/TODO.md).

## File and function layout

- Inside a class, group functions by role (init / setup, input, gameplay update, render, lifecycle).
- `update`-style and `run` methods go **last** and should only call other functions on the class.
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

- ALL text displayed to the player in-game (title screen, score labels, pause text, countdown, hints) must be **ALL CAPS**. The pixel font (`Pixeled.ttf`) is designed for caps-style retro display.
- Documentation files stay in normal sentence case.

---

## Mental testing checklist (run after major changes)

- The game launches (`python main.py`) without console errors.
- The title screen appears with both **MOUSE** and **CONTROLLER** options, and the selector cycles with arrows or D-pad.
- Selecting **MOUSE** then `Enter` starts a match where the paddle follows the cursor.
- Selecting **CONTROLLER** then `Start` starts a match where the paddle follows the left analog stick.
- The puck bounces off walls and paddles, and crossing into a goal increments the score and triggers a 3-second countdown.
- `Enter` / `Start` pauses the game; the same key resumes.
- `M` mutes and unmutes audio.
- `F11` / `Back` toggles fullscreen; the CRT overlay still renders in windowed mode.
- The quit combo (`Start + Back + L1 + R1`) and `Esc` both exit cleanly.
- No new magic numbers leaked outside `settings.py`.

For the actionable run-through, see [docs/TESTING.md](../docs/TESTING.md).
