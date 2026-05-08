# Game of the Amazons — Roadmap & TODO

The build is **playable end-to-end** with full move/shoot turn flow, win detection, animations, and a placeholder AI. Items are grouped by phase so contributors know where to push next.

---

## Phase 1 — Bugs to fix

- [ ] Arrow does not face the correct direction during animations. The fletching cycle plays but the sprite orientation is fixed regardless of flight angle. Fix in `ArrowAnimator` / `BoardView` arrow render.

## Phase 2 — AI

- [ ] Replace the random-move AI in `TurnManager.update_ai` with a strategic player. Minimum viable: prefer moves that maximize own legal-move count and minimize opponent legal-move count (one-ply heuristic). Stretch: shallow alpha-beta with a territory-count evaluator.
- [ ] Difficulty levels (easy = current random, medium = one-ply heuristic, hard = alpha-beta).

## Phase 3 — UX polish

- [ ] Highlight all legal destinations when a queen is selected (MOVE phase).
- [ ] Highlight all legal arrow tiles after the move animation lands (SHOOT phase).
- [ ] Sound effect on game-over.
- [ ] On-screen "press ENTER to play again" hint when `game_over` is True.

## Phase 4 — Two-player

- [ ] Hot-seat WHITE-vs-BLACK mode (no AI). Bind to a menu choice on the title screen.
- [ ] Title screen with mode select.

---

## Code health

- [ ] `from settings import *` is used in `main.py`. Acceptable historically; consider importing only the needed classes when the next major change touches the imports.
- [ ] The HUD font (`Pixeled.ttf`) is loaded from `FontSettings.FONT` but the comment notes "Doesn't look good... not used right now". Either re-enable it or remove the dead reference.

---

## Open questions

- Should arrow path validation share its line-walking implementation with queen-move validation in a single helper, or are the two divergent enough that the current `is_valid_path` reuse is the right call?
- Is the cursor-parking-on-queen behavior after the move animation desired, or should the cursor stay where it was?

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).