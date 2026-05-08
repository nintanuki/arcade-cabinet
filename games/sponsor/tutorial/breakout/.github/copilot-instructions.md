# Copilot Instructions for Breakout

These rules apply to **every** editor of this codebase, human or AI. Read this file before each session.

This game is a **standalone project** living inside the Arcade Cabinet repo. Running `python main.py` from this folder must always work on its own. Do not import launcher modules and do not edit files outside this folder from a Breakout change.

## Required reading order (before any change)

1. [README.md](../README.md)
2. [docs/TODO.md](../docs/TODO.md)
3. [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
4. [docs/CHANGELOG.md](../docs/CHANGELOG.md)
5. The source files relevant to your task.

If a question is asked about *why* code was written a certain way, that is a request for an **explanation**, not a request for a code change.

## Required actions (after any change)

- Append an entry to [docs/CHANGELOG.md](../docs/CHANGELOG.md) per the format at the top of that file (ISO 8601 timestamp, file path, line numbers at time of edit, before/after, why, editor name including AI model).
- Update [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) if your change altered how a system works.
- Update [docs/TODO.md](../docs/TODO.md) if your change completed or added a roadmap item.
- Run the manual smoke checks in [docs/TESTING.md](../docs/TESTING.md).

## Code style

- PEP-8. Less code is better; clean and readable is best.
- Prefer clear names over short ones.
- Do not change function or variable names unless the role has *completely* changed.
- Keep code free of dead imports, unused variables, and legacy code.

## Architecture rules

- `Game` ([main.py](../main.py)) is the coordinator. Sprites (`Player`, `Ball`, `Block`, `Upgrade`, `Projectile`) live in [sprites.py](../sprites.py); brick faces and paddle surfaces are built by `SurfaceMaker` in [surfacemaker.py](../surfacemaker.py).
- All constants live in [settings.py](../settings.py). **No magic numbers anywhere else.**
- Sprite groups are `all_sprites`, `block_sprites`, `upgrade_sprites`, `projectile_sprites`. Add new sprites to the matching group; do not invent ad-hoc collections.

## File and function layout

- Group functions in classes by role. `update` and `run` go **last**.
- Use ALL-CAPS section banners between logical groupings:

  ```python
      # -------------------------
      # SECTION NAME
      # -------------------------
  ```

## Comments and docstrings

- Every class and function gets a docstring with a one-line summary plus `Args:` / `Returns:` when applicable.
- Comments explain **why**, not what.

## UI text

- Player-facing text should be **ALL CAPS**. Documentation files stay in normal sentence case.

## Mental testing checklist

- `python main.py` boots without console errors.
- Paddle moves on keyboard and controller.
- Ball launches, bounces, and clears bricks.
- Power-ups drop and apply. Laser projectiles fire.
- Hearts decrement when the ball drops.
- `Esc` and the controller quit combo exit cleanly.
- No new magic numbers leaked outside `settings.py`.
