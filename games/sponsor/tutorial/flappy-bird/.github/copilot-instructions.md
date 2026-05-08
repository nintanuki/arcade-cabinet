# Copilot Instructions for Flappy Bird

These rules apply to **every** editor of this codebase, human or AI. Read this file before each session.

This game is a **standalone project**. Running `python main.py` from this folder must always work on its own. Do not import launcher modules and do not edit files outside this folder from a Flappy Bird change.

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

- `Game` ([main.py](../main.py)) is the coordinator. Sprites (`BG`, `Ground`, `Plane`, `Obstacle`) live in [sprites.py](../sprites.py); the CRT overlay lives in [crt.py](../crt.py).
- All constants live in [settings.py](../settings.py). **No magic numbers anywhere else.**
- Sprites that scroll (`BG`, `Ground`, `Obstacle`) take a `scale_factor` so the playfield works at any window height.

## File and function layout

- Group functions in classes by role. `update` and `run` go **last**.
- Use ALL-CAPS section banners between logical groupings.

## Comments and docstrings

- Every class and function gets a one-line docstring plus `Args:` / `Returns:` blocks where applicable.
- Comments explain **why**, not what.

## UI text

- Player-facing text should be **ALL CAPS**. Documentation files stay in normal sentence case.

## Mental testing checklist

- `python main.py` boots without console errors.
- Title menu image renders and music starts.
- `Space` / A starts a run; the plane flaps and falls under gravity.
- Pipes spawn on the obstacle timer and scroll left.
- Score increments as pipes pass.
- Collision ends the run and shows the menu again.
- `P` / Start toggles pause (with pause-in / pause-out SFX).
- `Esc` and the controller quit combo exit cleanly.
