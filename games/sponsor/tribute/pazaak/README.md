# Pazaak

A Pygame tribute to the Pazaak card game from *Star Wars: Knights of the Old Republic*. Pazaak is a side-deck blackjack variant: each player draws from a shared deck of `+1`–`+10` cards, racing to a hand total **as close to 20 as possible without going over**, while playing tactical side-deck cards (`+/-` swings, doubles, etc.) from a four-card sideboard.

## Status

**Phase: Scaffold.** Only the project shell exists today: a `GameManager` that opens an `1280 × 720` window, drains events, applies the CRT overlay, and supports the cabinet's quit combo. The card game itself is not yet implemented. See [docs/TODO.md](docs/TODO.md) for the build-out roadmap.

## Requirements

- Python 3.10+
- Pygame 2.5+

## Run

From this folder:

```powershell
python main.py
```

Or via the cabinet launcher: repo root → `python main.py` → **Mr. Navarro's Games → Tribute Games → Pazaak**.

## Rules (target gameplay)

1. Each player has a side-deck of 10 cards and brings 4 to the table per match.
2. Players alternate drawing from the shared `+1`–`+10` main deck. After each draw, the active player may optionally play one of their side-deck cards (`+/-` value cards, doubles, flips).
3. Either player may **stand** at any time. A standing player no longer draws.
4. If a hand total exceeds 20 the player **busts** that hand.
5. Best of 5 hands wins the match.

## Controls (placeholder)

| Action | Keyboard | Controller |
| --- | --- | --- |
| Quit | `Esc` (planned) | `Start + Back + L1 + R1` |

In-game controls (draw, stand, end turn, side-deck card play) will be defined as gameplay is built; see [docs/TODO.md](docs/TODO.md).

## Documentation

Read these in order before contributing:

1. **[README.md](README.md)** — *(this file)* what the project is and how to run it.
2. **[docs/TODO.md](docs/TODO.md)** — phased roadmap and open questions.
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the code actually works.
4. **[docs/CHANGELOG.md](docs/CHANGELOG.md)** — append-only history of every change.
5. **[docs/TESTING.md](docs/TESTING.md)** — manual smoke-test checklist after changes.
6. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — required reading for every editor, human or AI.
