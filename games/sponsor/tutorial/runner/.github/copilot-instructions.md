# Copilot Instructions for Runner

These rules apply to **every** editor of this codebase, human or AI. Read this file before each session.

This game is a **standalone project**. Running `python main.py` from this folder must always work on its own. Do not import launcher modules and do not edit files outside this folder from a Runner change.

## Required reading order

1. [README.md](../README.md)
2. [docs/TODO.md](../docs/TODO.md)
3. [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
4. [docs/CHANGELOG.md](../docs/CHANGELOG.md)
5. The source files relevant to your task.

If a question is asked about *why* code was written a certain way, that is a request for an **explanation**, not a request for a code change.

## Required actions (after any change)

- Append an entry to [docs/CHANGELOG.md](../docs/CHANGELOG.md) per the format at the top of that file.
- Update [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) if you altered how a system works.
- Update [docs/TODO.md](../docs/TODO.md) if you completed or added a roadmap item.
- Run the manual smoke checks in [docs/TESTING.md](../docs/TESTING.md).

## Code style

- PEP-8. Less code is better; clean and readable is best.
- Prefer clear names over short ones.
- Do not change function or variable names unless the role has *completely* changed.
- Keep code free of dead imports, unused variables, and legacy code.

## Architecture rules

- The whole game lives in [main.py](../main.py): `Player`, `Obstacle`, helper functions for score and game-over, the event loop. Refactor into separate modules only when [docs/TODO.md](../docs/TODO.md) calls for it.
- All constants live in [settings.py](../settings.py) (grouped into `ScreenSettings`, `PlayerSettings`, `BackgroundSettings`, `AssetPaths`). **No magic numbers anywhere else.**
- The CRT overlay lives in [crt.py](../crt.py).

## File and function layout

- Group functions in classes by role. `update` goes **last**.
- Use ALL-CAPS section banners between logical groupings.

## Comments and docstrings

- Every class and function gets a one-line docstring plus `Args:` / `Returns:` blocks where applicable.
- Comments explain **why**, not what.

## UI text

- Player-facing text should be **ALL CAPS**. Documentation files stay in normal sentence case.

## Mental testing checklist

- `python main.py` boots without console errors.
- Player runs, jumps with `Space` / A, falls under gravity.
- Snail and fly obstacles spawn and scroll left.
- Collision ends the run; restart prompt appears.
- Score increments while alive.
- CRT overlay is visible.
- `Esc` and the controller quit combo exit cleanly.
