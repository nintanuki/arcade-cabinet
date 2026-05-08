# Copilot Instructions for the Arcade Cabinet Launcher

These rules apply to **every** editor of this codebase, human or AI. They are not suggestions. Read this file before each session.

This file governs the **launcher** at the repo root. Each game under `games/sponsor/` and `games/student/` is its own standalone project with its own copilot-instructions file; when editing a game, follow that game's instructions instead. **The launcher must never reach into game folders, and game code is agnostic to the launcher.**

---

## Required reading order (before any change)

1. [README.md](../README.md) — what the project is and how to run it.
2. [docs/TODO.md](../docs/TODO.md) — current phase and roadmap.
3. [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) — how the launcher actually works.
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

## Boundary rules (launcher vs. games)

- **Never touch game folders from a launcher change.** Games under `games/sponsor/` and `games/student/` are standalone projects. If a launcher change appears to need game-side support, the launcher must adapt instead — games stay agnostic.
- **Never assume a game's internal layout.** The launcher knows only the game's `main.py` path (from `GameSettings.OPTIONS` for sponsor games, or `<folder>/main.py` for student games) and any manifest fields documented in [games/student/README.md](../games/student/README.md).
- **Never load game assets in-process.** Games are launched as subprocesses with their own working directory; do not import game modules from the launcher.

---

## Code style

- All Python code must be PEP-8 compliant.
- Less code is better; clean and readable is best.
- Prefer clear names over short ones. New class and function names must clearly describe their purpose.
- Do not change function or variable names unless the role has *completely* changed.
- Keep code free of dead imports, unused variables, unused functions, and legacy code.

## Architecture rules

- `ArcadeLauncher` ([launcher/manager.py](../launcher/manager.py)) must stay thin. Offload responsibilities to dedicated classes (rendering → `LauncherRenderer`, discovery → `discover_student_games`, CRT → `LauncherCRT`, data → `MenuNode` / `MenuFrame` / `StudentGameRecord`).
- Classes should communicate through `ArcadeLauncher` where possible. Avoid systems reaching directly into each other.
- Keep middlemen minimal: if A calls B and B only calls C, have A call C directly.
- All constants live in [settings.py](../settings.py). **No magic numbers anywhere else.** When adding a constant, include a comment explaining its units and effect.
- Prefer adding a new `*Settings` class in `settings.py` over expanding an existing one when the new field is not closely related to its neighbors.

## File and function layout

- Inside a class, group functions by role (init, audio, navigation, status, game launch, input handling, run loop, etc.).
- `update` and `run` go **last** and should only call other functions on the class.
- Separate logical sections inside a file with an all-caps banner comment, exactly this style:

  ```python
      # ------------------------------------------------------------------
      # SECTION NAME
      # ------------------------------------------------------------------
  ```

  Match the leading indentation of the surrounding class body. Keep the dashes the same length and the name in ALL CAPS.

## Comments and docstrings

- Every class and function must have a docstring with a one-line summary, plus `Args:` / `Returns:` blocks when applicable.
- Do not remove docstrings. Update them in place if behavior changes.
- Do not remove comments unless they are inaccurate; prefer updating them.
- Comments must explain **why**, not just what.
- Do not leave comments noting that a change was made, unless they explain a non-obvious bug fix or unconventional code.

## UI text

- ALL text displayed to the user in the launcher UI (menu titles, footers, warnings, status messages) must be **ALL CAPS**. The pixel font (`Pixeled`) is designed for caps-style retro display.
- Documentation files stay in normal sentence case.

---

## Mental testing checklist (run after major changes)

- The launcher boots (`python main.py`) without console errors.
- The root menu shows Student Games and Mr. Navarro's Games.
- Submenus push and pop cleanly; back at root, `Esc` quits.
- The carousel renders for menus with more than `MenuSettings.CAROUSEL_THRESHOLD` items; smaller menus render as a static list.
- Move SFX plays on cursor change; select SFX plays on enter; both fail silently if the audio file is missing.
- Mouse hover highlights menu items; click launches.
- A game launches in its own subprocess and the launcher restores cleanly when the game exits.
- The CRT overlay still renders in windowed mode and at fullscreen.
- No new magic numbers leaked outside `settings.py`.

For the actionable run-through, see [docs/TESTING.md](../docs/TESTING.md).
