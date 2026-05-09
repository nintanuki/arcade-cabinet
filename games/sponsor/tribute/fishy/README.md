# Fishy

A classic eat-or-be-eaten arcade game. You are a fish. Eat fish smaller than you to grow. Get eaten by a fish bigger than you to lose. Keep growing as long as you can.

## Status

Early gameplay is working: the player moves around the screen, fish spawn from the left and right edges, collisions are detected, and eating a smaller fish grows the player. A larger fish hitting the player triggers a game-over screen with a restart prompt. Fish are rendered as polygon shapes (diamond body + triangle tail) with a black square eye — no imported sprite art yet. No score or title screen.

## Requirements

- Python 3.10+
- `pygame` 2.5+

## Run

```powershell
python main.py
```

## Controls

| Action            | Keyboard         | Controller           |
| ----------------- | ---------------- | -------------------- |
| Move              | Arrow keys       | Left stick           |
| Toggle fullscreen | `F11`            | `BACK`               |
| Quit              | `Esc`            | `START+SELECT+L1+R1` |

## Documentation

- [README.md](README.md) — this file.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how the systems fit together.
- [docs/TODO.md](docs/TODO.md) — roadmap and open tasks.
- [docs/TESTING.md](docs/TESTING.md) — manual smoke checks.
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — append-only change history.
- [.github/copilot-instructions.md](.github/copilot-instructions.md) — rules for human or AI editors.

## Asset credits

- `assets/font/Pixeled.ttf` — *Pixeled* by OmegaPC777 (free for personal & commercial use).
- `assets/graphics/effects/tv.png` — CRT overlay reused from the arcade cabinet asset set.
