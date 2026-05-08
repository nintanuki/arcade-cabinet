# Pazaak — Roadmap & TODO

The build is a **scaffold**. The render loop, controller plumbing, and CRT overlay exist; gameplay does not. Items are ordered so a contributor can ship a playable hand-to-hand match in roughly the order listed.

---

## Phase 0 — Wire up what already exists

- [ ] Call `self.crt.draw()` inside the render branch of `run()` so the CRT pass actually composites each frame.
- [ ] Add an `Esc` handler in `_process_events` that calls `close_game()` for keyboard parity with the controller quit combo.
- [ ] Add `F11` and Back (Select) fullscreen toggle for parity with other tribute games.

## Phase 1 — Card model

- [ ] `core/deck.py`: `Deck` with `draw()`, `shuffle()`, `__len__`, plus a constructor that builds the standard `+1`–`+10` main deck.
- [ ] `core/hand.py`: `Hand` with `add(card)`, `total`, `is_busted` (>20), `is_standing`, `stand()`.
- [ ] `core/side_deck.py`: `SideDeck` of 4 cards (initially just `+/-N` value cards). Track which card is selected and which have been played.
- [ ] `MatchSettings` in `settings.py`: `MAX_HAND_TOTAL = 20`, `HANDS_TO_WIN_MATCH = 3`, `SIDE_DECK_SIZE = 4`.

## Phase 2 — Turn loop

- [ ] `GameState(Enum)` with `TITLE`, `DEAL`, `PLAYER_TURN`, `OPPONENT_TURN`, `RESOLVE_HAND`, `MATCH_OVER`.
- [ ] In `PLAYER_TURN`: `Space` / A draws a card; `Enter` / Start stands; left/right + confirm plays a side-deck card.
- [ ] In `OPPONENT_TURN`: a deterministic AI that draws while < 17 and stands otherwise. Replace later with a real strategy.
- [ ] On `RESOLVE_HAND`, compare totals: closer-to-20 wins, ties → push, both-bust → push.

## Phase 3 — Presentation

- [ ] `ui/table_view.py`: render the table, the two hands, both totals, the side-deck row, the deck back, the turn indicator.
- [ ] Asset pass: card backs, value cards, side-deck card faces. Place them under `assets/graphics/cards/`.
- [ ] Pixel font for HUD totals.

## Phase 4 — Audio

- [ ] `systems/audio.py`: `AudioManager` matching the contract used in jezz-ball (silent on missing assets).
- [ ] SFX: deal, stand, side-deck-play, win-hand, lose-hand, win-match.
- [ ] Optional ambient track.

## Phase 5 — Polish

- [ ] Title screen with "Press Start".
- [ ] Match-over screen with rematch / back-to-launcher options.
- [ ] Side-deck builder before a match (eventually).
- [ ] More side-deck card types: `+/-` swing cards, double cards, tiebreaker cards, flip-2-and-4.

---

## Code health

- [ ] `from settings import *` is used in `main.py`. Replace with explicit imports once the settings module grows beyond a handful of names.
- [ ] Empty `GAMEPLAY ACTIONS` and `AUDIO / VOLUME ACTIONS` banners in `main.py` are placeholders — fill them rather than adding new sections.

---

## Open questions

- Hot-seat 2-player or always vs. AI?
- Match length (best of 3, best of 5, single hand)?
- Should the side deck be configurable from a title-screen builder, or always randomized for now?
- Will animations be pure tweening or sprite-sheet based?

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md) to reflect the new shape.
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md) per the format in that file.
3. Move completed items here from `[ ]` to `[x]` (do not delete — leave as a record).
