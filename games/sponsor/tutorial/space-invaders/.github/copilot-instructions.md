# Copilot Instructions for Space Invaders

These rules apply to **every** editor of this codebase, human or AI. Read this file before each session.

This game is a **standalone project**. Running `python main.py` from this folder must always work on its own. Do not import launcher modules and do not edit files outside this folder from a Space Invaders change.

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

- Coordination lives in [main.py](../main.py). Sprites split across [player.py](../player.py), [alien.py](../alien.py) (`Alien` + `Extra`), [laser.py](../laser.py), [obstacle.py](../obstacle.py).
- There is no centralized `settings.py` yet — magic numbers should move there during the next major refactor (see [docs/TODO.md](../docs/TODO.md)). Until then, keep new constants at the top of `main.py` with named identifiers.

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
- Player ship moves with `Left` / `Right` and on D-pad / analog.
- `Space` (or A) fires a laser; player lasers destroy aliens.
- Aliens march side-to-side, descend at the edge, and fire lasers down.
- Alien lasers chip the obstacles.
- The `Extra` UFO occasionally streaks across the top.
- Pause overlay works.
- `Esc` and the controller quit combo exit cleanly.
