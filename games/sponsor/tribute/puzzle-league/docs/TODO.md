# Puzzle League — Roadmap & TODO

The build is a **scaffold**. The window opens, the title/game-over screen renders, the controller plumbing works, and the CRT overlay applies; gameplay is stubbed. Items are ordered so a contributor can ship a playable run roughly in this order.

---

## Phase 1 — Block rendering

- [ ] Render the `Board.grid` to the playfield rect (one rounded rectangle per non-empty cell using `ColorSettings.BLOCK_COLORS[type]` and `BlockSettings.INNER_PADDING`).
- [ ] Render the buffer row at the bottom, dimmed, scrolling up by `rise_offset_px`.
- [ ] Render the 1×2 cursor outline at the cursor anchor.

## Phase 2 — Cursor + swap

- [ ] Cursor movement on arrow keys / D-pad with `CursorSettings.INITIAL_DELAY_MS` and `REPEAT_INTERVAL_MS` auto-repeat.
- [ ] Swap action (`Space` / A) animates the two cells over `BlockSettings.SWAP_DURATION_MS` and updates the grid on completion.
- [ ] Cursor is clamped so the right half stays inside the grid.

## Phase 3 — Match resolution

- [ ] Match detection: ≥ 3 of the same `type` horizontally or vertically.
- [ ] Flash matched blocks for `BlockSettings.FLASH_DURATION_MS`.
- [ ] Sequential pop staggered by `BlockSettings.POP_INTERVAL_MS`.
- [ ] Falling blocks accelerate at `BlockSettings.FALL_SPEED_PX_PER_FRAME`.
- [ ] Re-check matches after a fall settles; increment chain depth.

## Phase 4 — Scoring

- [ ] Award `ScoreSettings.POINTS_PER_BLOCK` per popped block.
- [ ] Add `COMBO_BONUS` for clears of 4+.
- [ ] Add `CHAIN_BONUS[depth]` for each chained match.
- [ ] HUD: render score, high score, level above the playfield.

## Phase 5 — Rise + top-out

- [ ] Integrate `rise_offset_px` against `RiseSettings.BASE_RISE_SPEED_PX_PER_SEC`.
- [ ] Rush button (`Shift` / R1) overrides with `RUSH_RISE_SPEED_PX_PER_SEC` while held.
- [ ] When score crosses `DIFFICULTY_STEP_SCORE`, bump base rise by `SPEED_INCREMENT_PX_PER_SEC` (capped at `MAX_RISE_SPEED_PX_PER_SEC`).
- [ ] When the top row becomes non-empty, start the `TOPOUT_GRACE_MS` timer; if it elapses without a clear, transition to game-over.

## Phase 6 — Audio

- [ ] Background music track that loops while `game_active`.
- [ ] SFX: cursor move, swap, match (size-tiered), chain (depth-tiered), top-out warning, game-over.

## Phase 7 — Persistence + leaderboard

- [ ] `ScoreManager.save_scores` writes JSON to `ScoreSettings.HIGH_SCORE_FILE`.
- [ ] Defensive load (mirrors jezz-ball): bad/missing file falls back to defaults without crashing.
- [ ] Initials entry on game-over for top-N qualifying scores.

## Phase 8 — Polish

- [ ] Title screen artwork.
- [ ] Particle effects on big chains.
- [ ] Difficulty-level select on title screen (start speed).
- [ ] Hot-seat 2-player mode (eventually).

---

## Code health

- [ ] `from settings import *` is **not** used here — settings are imported explicitly. Keep it that way.
- [ ] Empty handler bodies (`_handle_joyhatmotion`, `_handle_joyaxismotion`) are intentional placeholders. Fill them rather than reshaping the dispatch.

---

## Open questions

- Is the cursor anchor cell the **left** or **right** half of the 1×2 selection? Settings imply left; confirm during Phase 2.
- Should the rush button instantly raise one row, or scroll continuously while held? `RiseSettings.RUSH_RISE_SPEED_PX_PER_SEC` implies continuous; verify against source-game feel.
- Block sprite art or solid rounded rectangles? Solid rectangles keep the project shippable; sprite art is Phase 8 polish.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
