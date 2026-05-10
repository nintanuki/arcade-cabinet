# Packaging the Launcher — Handoff Notes

Status as of 2026-05-09: **Dev (`python main.py`) works. Packaged build is ~95% there but not yet verified end-to-end.** Last known blocker is fixed in code; one rebuild + test is needed to confirm.

This document records what was tried, what works, and what to try next so a future session can resume without re-deriving everything.

---

## What's in place

### Source code changes (all dev-safe)

- [main.py](../main.py) — when `sys.frozen` is True (PyInstaller), anchors `root_dir` to the exe's folder. Source runs unchanged.
- [settings.py](../settings.py) — `LauncherSettings.GAME_PYTHON = Path("runtime") / "python" / "python.exe"`. Source runs fall back to `sys.executable` because `_resolve_game_interpreter` checks `.exists()`.
- [launcher/manager.py](../launcher/manager.py) — new `_resolve_game_interpreter()` helper. Game launch goes through `runpy.run_path` with explicit `sys.path.insert` to handle the embeddable distribution's `_pth` restrictions.

### Build artifacts

- [arcade.spec](../arcade.spec) — PyInstaller recipe. Bundles **only** the launcher Python code into `_internal/`. Does NOT bundle `assets/`, `games/`, `runtime/`, or `settings.py` — those are copied next to the exe.
- [build.ps1](../build.ps1) — clean + PyInstaller + copy `assets/` + `settings.py` + `games/` + `runtime/` into `dist/ArcadeCabinet/`.
- [scripts/setup_runtime.ps1](../scripts/setup_runtime.ps1) — provisions `runtime/python/` (embeddable Python 3.11.9 + pygame). Verified working as of last run; pygame imports successfully in the bundled interpreter.
- [requirements.txt](../requirements.txt) — `pygame>=2.5`.
- [requirements-build.txt](../requirements-build.txt) — `-r requirements.txt` plus `pyinstaller>=6.0`.
- [.gitignore](../.gitignore) — keeps `arcade.spec` tracked, ignores `runtime/`.

---

## Workflow

### One-time setup (build machine)
```powershell
pip install -r requirements-build.txt
.\scripts\setup_runtime.ps1
```

### Build
```powershell
.\build.ps1
```

### Test
```powershell
.\dist\ArcadeCabinet\ArcadeCabinet.exe
```

---

## What to try first when resuming

The user did `setup_runtime.ps1 -Force` (succeeded, pygame imports in the embedded interpreter) but did NOT rerun `build.ps1` afterward. The `dist/` folder still contains the old broken runtime AND the old launcher code (without the `sys.path.insert` fix in `manager.py`).

```powershell
cd C:\Users\bryan\Desktop\code\repos\arcade-cabinet
.\build.ps1
.\dist\ArcadeCabinet\ArcadeCabinet.exe
```

Pick a small game (Pong) to test first.

If a game launches and pong runs: **success**, document the workflow in README/ARCHITECTURE if anything is missing.

If a game still fails silently, run this to see the error:
```powershell
cd dist\ArcadeCabinet
.\runtime\python\python.exe -c "import sys, runpy; sys.path.insert(0, r'games\sponsor\tutorial\pong'); runpy.run_path(r'games\sponsor\tutorial\pong\main.py', run_name='__main__')"
```

---

## Issues encountered and resolutions

### 1. Assets not found at first launch
**Symptom:** `FileNotFoundError: ...assets\font\Pixeled.ttf`
**Cause:** Spec bundled `assets/` *inside* `_internal/`, but `main.py` anchors `root_dir` to the exe's folder.
**Fix:** Removed `("assets", "assets")` and `("settings.py", ".")` from `datas` in `arcade.spec`. `build.ps1` now copies them as real folders next to the exe. Same root_dir resolves everything in source AND frozen mode.

### 2. `ModuleNotFoundError: No module named 'settings'`
**Symptom:** Game subprocess crashes immediately.
**Cause #1 (red herring):** Embeddable Python's `_pth` file disables `PYTHONPATH` and the auto-prepend-script-dir behavior. Setting `env["PYTHONPATH"]` had zero effect.
**Cause #2 (real fix):** `runpy.run_path("foo.py")` does NOT add the script's directory to sys.path the way `python foo.py` does. Must do `sys.path.insert(0, game_dir)` explicitly.
**Fix:** In `launcher/manager.py`, the runner now does:
```python
runner = (
    "import sys, runpy; "
    f"sys.path.insert(0, r'{game_dir}'); "
    f"runpy.run_path(r'{game_main}', run_name='__main__')"
)
subprocess.run([interpreter, "-c", runner], cwd=str(game_dir), check=False)
```

### 3. `ModuleNotFoundError: No module named 'pygame'`
**Symptom:** Even after the previous fix, `import pygame` failed in the bundled interpreter.
**Cause:** The original `setup_runtime.ps1` used `pip install -r requirements.txt` against the embedded interpreter, but pip silently put pygame somewhere unexpected (or the install didn't actually run against the embedded interpreter — exact root cause not fully diagnosed). `runtime/python/Lib/site-packages/` was empty.
**Fix:** Rewrote `setup_runtime.ps1` to:
  - Rewrite `_pth` explicitly with `Lib\site-packages` on the path list and `import site` enabled.
  - Use `pip install --target=...\Lib\site-packages` so the install location is unambiguous.
  - Verify `import pygame` succeeds at the end and fail loudly if not.
**Verified:** `setup_runtime.ps1 -Force` now ends with `pygame 2.6.1 (SDL 2.28.4, Python 3.11.9)` printed by the **embedded** interpreter. Confirmed working.

### 4. Locked DLLs during cleanup
**Symptom:** `Remove-Item: Cannot remove ... base.cp313-win_amd64.pyd: Access to the path ... is denied.`
**Cause:** A previous `ArcadeCabinet.exe` (or a child `python.exe` from a launched game) was still running.
**Fix:** Close the launcher window before rebuilding. If a process is hung, `Get-Process ArcadeCabinet, python | Stop-Process -Force`.

---

## Things that may need attention next session

### Probable next failures (when more games are tested)
- **Sponsor games using packages other than pygame.** Embedded runtime only has pygame. If any game imports `numpy`, `pillow`, etc., add to `requirements.txt` and re-run `setup_runtime.ps1 -Force`.
- **Games with hard-coded absolute paths.** Should be none, but if a game ignores `cwd` and uses `Path(__file__).parent` aggressively it should still work; if it uses absolute `C:\...` paths it would not.

### Polish items (out of scope but useful)
- Code-sign the exe to suppress Windows SmartScreen warning.
- Wrap `dist/ArcadeCabinet/` in an Inno Setup or NSIS installer for a "Next → Next → Finish" UX.
- Add a custom icon (`icon='path/to/icon.ico'` in the EXE() block of `arcade.spec`).
- Test with a student game in `games/student/` to confirm runtime discovery still works in a packaged build.

### Known cosmetic warnings (ignore unless they become problems)
- PyInstaller pulls Python 3.13.7 (the user's dev interpreter) into the launcher's `_internal/`, but the embedded runtime is 3.11.9. This is intentional — the launcher exe runs against the bundled 3.13 it shipped with, while game subprocesses use the bundled 3.11. They never share state, so the version skew is fine.

---

## Files that were modified or added

```
arcade.spec                       (new)
build.ps1                         (new)
scripts/setup_runtime.ps1         (new)
requirements.txt                  (was empty; now lists pygame)
requirements-build.txt            (new)
launcher/manager.py               (added _resolve_game_interpreter, runpy launch)
main.py                           (sys.frozen-aware root_dir)
settings.py                       (added GAME_PYTHON)
.gitignore                        (kept arcade.spec, ignored runtime/)
README.md                         (added "Packaging a distributable build")
docs/ARCHITECTURE.md              (updated section 7 + diagram)
docs/CHANGELOG.md                 (multiple entries)
```

---

## Reverting (if needed)

Nothing here breaks the dev workflow, but if you want to roll back the packaging effort entirely:

1. Delete `runtime/`, `dist/`, `build/`, `arcade.spec`, `build.ps1`, `scripts/setup_runtime.ps1`, `requirements-build.txt`.
2. Set `LauncherSettings.GAME_PYTHON = None` in [settings.py](../settings.py) (or delete the line — code falls back to `sys.executable`).
3. Optionally revert the `if getattr(sys, "frozen", False)` block in [main.py](../main.py).
4. Optionally revert `_resolve_game_interpreter` in [launcher/manager.py](../launcher/manager.py) and use `sys.executable` directly.

`requirements.txt` going from empty to `pygame>=2.5` should stay — it was a documented TODO and is correct regardless of packaging.
