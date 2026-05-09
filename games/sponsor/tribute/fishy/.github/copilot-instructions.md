# Copilot Instructions for the Pygame Template

These rules apply to **every** editor of this codebase, human or AI. Read this file before each session.

This folder is a **starter template**. The conventions below are what new projects spawned from this scaffold should inherit. Once you copy the template into a real project, replace this header with the real game's name and tighten the rules to fit.

## Required reading order (before any change)

1. [README.md](../README.md)
2. [docs/TODO.md](../docs/TODO.md)
3. [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
4. [docs/CHANGELOG.md](../docs/CHANGELOG.md)
5. The source files relevant to your task.

If a question is asked about *why* code was written a certain way, that is a request for an **explanation**, not a request for a code change. Do not modify code unless the user explicitly asks for a change.

## Required actions (after any change)

- Append an entry to [docs/CHANGELOG.md](../docs/CHANGELOG.md) using the format at the top of that file (ISO 8601 timestamp with timezone, file path, line numbers at time of edit, before/after blocks, why, editor name including the AI model used).
- Update [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) if your change altered how a system works.
- Update [docs/TODO.md](../docs/TODO.md) if you completed or added a roadmap item (mark `[x]`, do not delete).
- Run the manual smoke checks in [docs/TESTING.md](../docs/TESTING.md).

## Code style

- All Python is PEP-8 compliant.
- Less code is better; clean and readable is best.
- Prefer clear names over short ones. New class and function names must clearly describe their purpose.
- Do not change function or variable names unless the role has *completely* changed.
- No dead imports, unused variables, unused functions, or legacy code.

## Architecture rules

- `GameManager` ([main.py](../main.py)) stays thin. Offload responsibilities to dedicated classes under `core/`, `systems/`, `ui/`, or `utils/`.
- Classes communicate through `GameManager` where possible. Avoid direct cross-system reach-arounds.
- Keep middlemen minimal: if A calls B and B only calls C, have A call C directly.
- All constants live in [settings.py](../settings.py). **No magic numbers anywhere else.** When adding a constant, include a comment explaining its units and effect.
- Prefer adding a new `*Settings` class in `settings.py` over expanding an existing one when the new field is not closely related to its neighbors.

## File and function layout

- Inside a class, group functions by role (init, input, update, render, etc.).
- `update` and `run` go **last** and should only call other functions on the class.
- Separate logical sections inside a file with an all-caps banner comment, exactly this style:

  ```python
      # ------------------------------------------------------------------
      # SECTION NAME
      # ------------------------------------------------------------------
  ```

  Match the leading indentation of the surrounding class body. Keep dashes the same length and the name in ALL CAPS.

## Comments and docstrings

- Every class and function has a docstring with a one-line summary, plus `Args:` / `Returns:` blocks where applicable.
- Do not remove docstrings — update them in place if behavior changes.
- Do not remove comments unless they are inaccurate; prefer updating them.
- Comments explain **why**, not what.
- Do not leave comments noting that a change was made unless they explain a non-obvious bug fix.

## UI text

- ALL text displayed to the user in-game must be **ALL CAPS**. The pixel font (`Pixeled`) is designed for caps-style retro display.
- Documentation files stay in normal sentence case.

## Mental testing checklist

- `python main.py` boots without console errors.
- The window opens at the resolution defined by `ScreenSettings`.
- `F11` and `BACK` toggle fullscreen.
- The quit chord (`START + SELECT + L1 + R1`) on any controller exits cleanly.
- The CRT overlay renders only in windowed mode.
- No new magic numbers leaked outside `settings.py`.

For the actionable run-through, see [docs/TESTING.md](../docs/TESTING.md).
