# Ms. Fishy — Roadmap & TODO

Move completed items from `[ ]` to `[x]`. Do not delete entries.

The roadmap is grouped into **passes**. A pass is a focused batch of work
where every item is at a similar level of architectural depth. Earlier
passes lay foundation that later passes depend on, so finish a pass before
starting the next one even if a later item looks individually easier.
Within a pass, items are ordered low-to-high difficulty.

---

## Completed

- [x] **Ms. Fishy rebrand** — renamed game from *Fishy* to *Ms. Fishy* (à la Ms. Pac-Man) to match the cute voice samples used for the gulp/scream SFX. Player fish now wears a pink bow above the body apex.
- [x] `GameManager` frame loop (events → update → render → flip).
- [x] Keyboard and controller input routing.
- [x] `F11` / `BACK` fullscreen toggle (now via shared `_toggle_fullscreen` helper).
- [x] `Esc` keyboard quit.
- [x] `START + SELECT + L1 + R1` controller quit chord.
- [x] CRT overlay (scanlines + flicker, windowed only).
- [x] `Player` sprite with arrow-key and left-stick movement, screen-boundary clamping.
- [x] `Fish` sprite spawning from left/right edges, scrolling across, self-destructing off-screen.
- [x] `FishManager` spawn timer and eat-or-be-eaten collision logic.
- [x] Player grows when eating a smaller fish (`FishSettings.PLAYER_GROWTH_COEFFICIENT`).
- [x] Session ends when a larger fish hits the player.
- [x] **Pixel-perfect (mask) collision** for fish-vs-player.
- [x] Game-over screen instead of abrupt `sys.exit()` when eaten.
- [x] Pause feature — keyboard (Enter) and controller (START); pauses world + music; plays pause-in/out SFX.
- [x] Underwater inertia movement (acceleration, drag, counter-acceleration, sub-pixel accumulators).
- [x] Retro visual pass: ocean gradient bg, fish drop shadows, gradient player, palette-randomized fish.
- [x] Player fish polygon shape (replaced the yellow square placeholder).
- [x] Player distinction (gradient + bow) so it stands out from enemies.
- [x] Fish eyes — small black square positioned half-way between body center and nose.
- [x] Audio system (`AudioManager`) with data-driven sound registry, music randomizer, mute, pause/resume.
- [x] **Player spawn centered correctly** at startup (was anchored topleft).
- [x] **Architecture rule**: keyboard/controller parity for every action.
- [x] **Architecture rule**: input handlers must not call each other; share via action methods.
- [x] **Architecture rule**: prefer updating an existing function over creating a near-duplicate name.
- [x] **Architecture rule**: never add/remove/modify in-game UI without explicit user request.
- [x] **Code-health items inherited from the template** — explicit imports in `crt.py`, deduped mute flags, `__file__`-relative asset paths, removed unused `game_active`, all `__init__.py` files present, `Esc` wired, title set, no `sys.exit()` in `FishManager`, joystick list cached.
- [x] **Pass 1.1** — Pygame-primitive visuals rule added to `ARCHITECTURE.md` and `copilot-instructions.md`.
- [x] **Pass 1.2** — `utils/text.py` `draw_centered_text` helper; refactored overlay rendering in `main.py`.
- [x] **Pass 1.3** — `Scene` base class (`core/scene.py`), `SceneManager` (`systems/scene_manager.py`), `ui/scenes/` package; `main.py` refactored to scene graph; `ARCHITECTURE.md` updated.
- [x] **Pass 1.4** — `TitleScene` with ocean gradient background, background fish via `FishManager(player=None)`, title + prompt text, Enter/START starts game; `utils/graphics.py` `build_gradient_surface` helper extracted.
- [x] **Pass 1.5** — `PlayScene` with `DROPPING_IN` / `ACTIVE` / `PAUSED` substates, player drop-in animation, `PlayerSettings.DROP_IN_VELOCITY`, HUD wired.
- [x] **Pass 1.6** — `GameOverScene` as a proper `Scene` subclass.
- [x] **Pass 2.1** — `Score` model in `core/score.py`; `PlayScene` tracks `fish_eaten` and `size_eaten`, passes score to `GameOverScene`.
- [x] **Pass 2.2** — `Hud` widget in `ui/hud.py`; top-left fish count, top-right score, top-center hi-score line; `UiSettings.HUD_FONT_SIZE` and `HUD_PADDING` constants.
- [x] **Pass 2.3** — `Leaderboard` in `systems/leaderboard.py`; top-10 JSON persistence with atomic save, initials dedup rule, `qualifies`/`submit`/`top` API; `AssetPaths.LEADERBOARD` constant.

---

## In progress

*(nothing active)*

---

## Pass 2 — Score, leaderboard, persistence (remaining)

### 2.4 Initials-entry scene

- [x] Create [ui/scenes/initials_entry_scene.py](../ui/scenes/initials_entry_scene.py).
- Reached **only** from `GameOverScene` when `leaderboard.qualifies(score)` is true. If the score doesn't qualify, `GameOverScene` skips this scene and shows the regular game-over layout straight away.
- Layout (centered column on a black background):
  - Line 1 (top, large): **"NEW HIGH SCORE"** at `UiSettings.OVERLAY_FONT_SIZE`.
  - Line 2: **"SCORE: NNNNN"**.
  - Line 3: **"ENTER YOUR INITIALS"** at `UiSettings.HUD_FONT_SIZE`.
  - Line 4 (large, the editor): three letter slots **"_ _ _"** with the currently-selected slot highlighted (white box outline, 2 px). Letters fill in as the player commits each slot.
  - Line 5: **"PRESS START WHEN DONE"** at `UiSettings.HUD_FONT_SIZE`.
- Input model — three editable slots, current slot index `0..2`:
  - **Keyboard typing**: pressing any A–Z key sets that letter into the current slot and advances the cursor. After the third letter is committed, the cursor stops at slot 2 (any further A–Z keys overwrite slot 2).
  - **Backspace**: clears the current slot (or steps back to the previous slot if the current is already empty) and moves the cursor to that slot.
  - **Up arrow / D-pad up**: cycle the current slot's letter up alphabetically (`A → B → ... → Z → A`). If empty, start at `A`.
  - **Down arrow / D-pad down**: cycle down (`A → Z → Y → ...`).
  - **Left arrow / D-pad left**: move cursor to the previous slot (clamped at 0).
  - **Right arrow / D-pad right**: move cursor to the next slot (clamped at 2).
  - **Enter / START**: commit. If any slot is empty, fill it with `A`. Call `leaderboard.submit(initials, score)` and `leaderboard.save()`. Transition to `LeaderboardScene` (next item).
- Acceptance: a qualifying run is followed by an editable 3-letter prompt that accepts both keyboard typing and arrow/controller stepping, persists the result, and moves on.

### 2.5 Leaderboard display scene

- [x] Create [ui/scenes/leaderboard_scene.py](../ui/scenes/leaderboard_scene.py).
- Reached from:
  - `InitialsEntryScene` after submit.
  - `GameOverScene` after a non-qualifying death (no initials prompt — this scene replaces the bare "GAME OVER" screen for non-qualifying runs once the leaderboard exists).
- Layout (centered column on a black background):
  - Header: **"GAME OVER"** at `UiSettings.OVERLAY_FONT_SIZE`.
  - Subheader: **"SCORE: NNNNN"** at `UiSettings.HUD_FONT_SIZE`.
  - Then the leaderboard, one row per entry, e.g.:

    ```
     1.  BRY    12345
     2.  AAA     9000
    ...
    ```

  - If the player just submitted, **highlight their row** (white background, black text, or just bold/underlined) using their initials + score as the match key.
  - Footer: **"PRESS START TO RETURN TO TITLE"**.
- Input: `Enter` / `START` returns to `TitleScene` (which now reads the updated high score for its HI line).
- Acceptance: every game-over now ends here; a qualifying run highlights the player's row; pressing start returns to the title.

### 2.6 Wire it all together

- [x] `GameOverScene.on_enter` routes to `InitialsEntryScene` when qualifies, else `LeaderboardScene`.
- [x] `Hud.draw` reads `game.leaderboard.top()[0]` for the HI center label.
- [x] End-of-run messaging flow: cause text first (`YOU WERE EATEN BY A BIGGER FISH` or `YOU'VE EATEN ALL THE FISH!`), then delayed stat tally, then leaderboard routing.
- [x] Added victory end condition when player width exceeds screen width.
- Note: `TitleScene` intentionally has no HI line per the title-screen lock rule in `copilot-instructions.md`.

---

## Pass 3 — Score and Endgame

End game is not challenging when player reaches a certain size, and final scores will always be close to the same. Let's add other stats to thes core

- [x] Add a timer, test it so that it gets close to zero when the player gets to a size that they are unbeatable, this effectively treats the invincible stage as a bonus round. Seconds left on timer add to the score
- [x] # of fish adds to score
- [ ] eating multiple fish at a time adds to score.
- [x] player's final weight adds to score
- [x] Display all statistics at the end (# of fish eaten, player weight, time left, etc) and add to final score

---

## Pass 4 — Levels and level design *(placeholder — design TBD)*

Difficulty in Ms. Fishy will come from **level design**, not from a global
difficulty ramp or fish-stat scaling. The base loop where the player
eventually grows into an unstoppable juggernaut is intentional and is the
reward — do not nerf it.

Concrete level-design plans will be added here once the foundation passes
land. Likely directions to revisit later:

- [ ] Hand-authored arenas with static obstacle layouts (coral walls,
  rocks, narrow tunnels) drawn from polygons.
- [ ] Per-level fish-pool overrides (specific size mixes, specific
  spawn-side weights) without changing the global `FishSettings`.
- [ ] Hazards that don't scale with the player: jellyfish (always lethal,
  drift vertically), shark (always lethal, chases). These remain
  threatening even when the player is huge — the only thing that does.

---

## Pass 5 — Visual polish (Pygame-primitive only)

Last pass. These items make the game prettier without affecting gameplay.
Everything here must be drawable with Pygame's draw API — no imported art.

- [X] **Black outline** on all fish (player and enemy) for legibility.
- [ ] **Polygon-tier player shape** — once the player fish exceeds some
  fraction of screen size, rebuild the body from more polygons (ellipse
  approximation, segmented diamond, or curved spine) so a giant fish
  doesn't look blocky. Diamond+triangle stays for small/medium sizes.
  This is a **visual** tier, not a difficulty tier — stats don't change.
- [ ] **Particle system** (`systems/particles.py`) — splash/bubbles when
  the player eats a fish.
- [ ] **Parallax background** — multiple gradient/silhouette layers (kelp
  silhouettes, distant fish dots) drawn from primitives.
- [ ] **Kelp / seaweed** drawn as wavy line strips, swayed by a low-freq
  sine so the world breathes.
- [ ] **Underwater waviness** — per-frame horizontal offset along scanlines
  for a shimmer effect.

---

## Pass 6 — Audio polish

Most of the audio system already exists; only thin gaps remain.

- [ ] **In-game audio toggle** — a controller button + keyboard key that
  calls `AudioManager.toggle_mute`. Surface the current mute state in the
  pause overlay.
- [ ] **Distinct SFX** for: title-screen confirm, leaderboard-entry
  qualify celebration, leaderboard scroll/select.

---

## Pass 7 — Settings menu

Now that there are scenes and persistence, give the player real knobs.

- [ ] **Options scene** reachable from the title — toggle CRT overlay,
  music volume, SFX volume.
- [ ] **Persist options** alongside the leaderboard (separate JSON file
  next to `main.py`, e.g. `options.json`).

---

## Ideas / parking lot

Things to consider but not yet planned into a pass.

- [ ] **Combo system** — eating fish quickly in succession multiplies score.
- [ ] **Cosmetic ecosystem events** — occasionally a non-player big fish
  eats a non-player small fish nearby (purely visual, but sells the
  ecosystem).
- [ ] **Screen-wrap movement option** as an alternative to boundary
  clamping (player exits left → enters right). Toggleable in the options
  scene from Pass 6 if revisited.
- [ ] **Imported sprite art** — explicitly *off the table* per the
  Pygame-primitive rule from Pass 1.

---

## Documentation maintenance

Every pass that meaningfully changes a system must:

1. Update [docs/ARCHITECTURE.md](ARCHITECTURE.md).
2. Append entries to [docs/CHANGELOG.md](CHANGELOG.md).
3. Move completed items here from `[ ]` to `[x]` (do not delete).
