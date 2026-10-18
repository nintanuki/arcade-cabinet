"""Stand-ins for the pygame calls the browser build of pygame lacks.

``scripts/web_build.py`` copies this file into each game's web copy, and the
game imports it only when running as a web page (``sys.platform ==
"emscripten"``). The desktop games never load it.

``pygame.time.set_timer`` raises NotImplementedError on WebAssembly, so it is
replaced with one that remembers each timer, and ``pygame.event.get`` posts
the timers that are due before handing back the queue.

``keep_files`` keeps a game's save files across visits (see Saves below).
"""

import json
import os
import platform  # pygbag's: platform.window is the browser's window

import pygame

# event type -> [the event to post, interval in ms, next due time, posts left (0 = forever)]
_timers = {}


def set_timer(event, millis, loops=0):
    """Post ``event`` every ``millis`` ms, ``loops`` times (0 = forever); 0 ms stops it."""
    if not isinstance(event, pygame.event.EventType):
        event = pygame.event.Event(event)
    millis = int(millis)
    if millis <= 0:
        _timers.pop(event.type, None)
        return
    _timers[event.type] = [event, millis, pygame.time.get_ticks() + millis, loops]


def _post_due_timers():
    """Post every timer event whose time has come."""
    now = pygame.time.get_ticks()
    for event_type, timer in list(_timers.items()):
        event, millis, due, loops = timer
        if now < due:
            continue
        pygame.event.post(pygame.event.Event(event.type, event.dict))
        if loops == 1:
            del _timers[event_type]
            continue
        timer[2] = max(due + millis, now)
        if loops > 1:
            timer[3] = loops - 1


_event_get = pygame.event.get


def _get(*args, **kwargs):
    """``pygame.event.get``, with the due timer events posted and changed saves stored first."""
    _post_due_timers()
    _store_changed_files()
    return _event_get(*args, **kwargs)


pygame.time.set_timer = set_timer
pygame.event.get = _get


# -------- Saves --------
# A web page's files vanish when it closes, so the files a game saves are
# copied into the browser's storage (localStorage) whenever they change and
# copied back when the game starts.

_kept = []  # [storage key, paths, last stored text]
_KEEP_CHECK_MS = 500
_next_keep_check = 0


def _snapshot(paths):
    """Return {path: text} for the kept files, and every file in kept folders."""
    files = {}
    for path in paths:
        if os.path.isdir(path):
            for folder, _, names in os.walk(path):
                for name in names:
                    full = os.path.join(folder, name)
                    with open(full, encoding="utf-8") as kept_file:
                        files[full] = kept_file.read()
        elif os.path.isfile(path):
            with open(path, encoding="utf-8") as kept_file:
                files[path] = kept_file.read()
    return files


def keep_files(key, *paths):
    """Keep ``paths`` (files or folders, relative to the game folder) across visits."""
    storage = platform.window.localStorage
    stored = storage.getItem(key)
    if stored:
        for path, text in json.loads(stored).items():
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as kept_file:
                kept_file.write(text)
    _kept.append([key, paths, stored or json.dumps({})])


def _store_changed_files(now=False):
    """Copy kept files into browser storage if they changed since last time.

    Checks every ``_KEEP_CHECK_MS`` ms, or at once when ``now`` is True.
    """
    global _next_keep_check
    ticks = pygame.time.get_ticks()
    if ticks < _next_keep_check and not now:
        return
    _next_keep_check = ticks + _KEEP_CHECK_MS
    for kept in _kept:
        key, paths, last = kept
        text = json.dumps(_snapshot(paths), sort_keys=True)
        if text != last:
            platform.window.localStorage.setItem(key, text)
            kept[2] = text


def leave_game():
    """Store the saves and go back to the games menu (a web page cannot close itself)."""
    _store_changed_files(now=True)
    platform.window.location.assign("../")
