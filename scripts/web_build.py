"""Build the web versions of the cabinet's games into ``web/``.

pygbag (``pip install pygbag soundfile``) packs a pygame folder into a web
page that runs Python in the browser. Each game is packed on its own, from a
staging copy that leaves out what only the desktop uses, and lands in
``web/<game>/``. ``web/index.html`` is the menu, a card per game.

    python scripts/web_build.py              # every game, then the menu
    python scripts/web_build.py star-hero    # one game, then the menu

The game pages load pygbag's Python runtime from its CDN when they open.
To try it, serve the folder (``python -m http.server -d web 8123``) and open
http://127.0.0.1:8123/ (not localhost: there pygbag looks for its own
development server).
"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "web"

sys.path.insert(0, str(ROOT))
from settings import GameSettings  # noqa: E402

# The games on the website, in menu order: web folder -> (launcher name, kind).
# The kind is the launcher's folder (original or educational) and colors the card.
GAMES = {
    "star-hero": ("Star Hero", "original"),
    "dungeon-digger": ("Dungeon Digger", "original"),
    "typing-hero": ("Typing Hero", "educational"),
    "digital-logic-simulator": ("Digital Logic Simulator", "educational"),
}

# Left out of every browser copy: what only the desktop or a developer uses.
_SKIP = shutil.ignore_patterns(
    "__pycache__", "*.pyc", "tests", "docs", "tools", "build", ".github", ".gitignore", "legacy",
    "*.md", "high_score.txt", "leaderboard.txt", "saves", "projects", "*.ico",
)


def _source(name: str) -> Path:
    """Return the folder of the game the launcher lists as ``name``."""
    return ROOT / dict(GameSettings.OPTIONS)[name].parent  # type: ignore[arg-type]


def build_game(slug: str) -> None:
    """Stage one game, run pygbag on it, and copy the page to ``web/<slug>/``."""
    name = GAMES[slug][0]
    with tempfile.TemporaryDirectory() as tmp:
        app = Path(tmp) / slug
        shutil.copytree(_source(name), app, ignore=_SKIP)
        shutil.copy2(ROOT / "scripts" / "web_shims.py", app / "web_shims.py")
        # pygbag reads its last argument as the folder, relative to here.
        subprocess.run(
            [sys.executable, "-m", "pygbag", "--build", "--ume_block", "0", slug],
            check=True, cwd=tmp,
        )
        out = OUT / slug
        if out.exists():
            shutil.rmtree(out)
        # The .apk is only for itch.io.
        shutil.copytree(app / "build" / "web", out, ignore=shutil.ignore_patterns("*.apk"))
    shutil.copy2(ROOT / GameSettings.PREVIEW_IMAGES[name], out / "favicon.png")
    print("built", out)


def _sentence_case(text: str) -> str:
    """Turn the launcher's all-caps tagline into an ordinary sentence."""
    sentences = [part.capitalize() for part in text.split(". ")]
    words = ". ".join(sentences).split(" ")
    return " ".join(_SPELLINGS.get(word.upper(), word) for word in words)


# Words in the four taglines that keep their own spelling on the menu.
_SPELLINGS = {"I": "I", "GALAGA": "Galaga", "STAR": "Star", "FOX": "Fox", "RPG": "RPG", "SCIFI": "sci-fi"}


def _credits(slug: str) -> str:
    """Return one game's credits, from its ``attributions.md`` files, as HTML."""
    items = []
    for notes in sorted(_source(GAMES[slug][0]).glob("assets/*/attributions.md")):
        for line in notes.read_text(encoding="utf-8").splitlines():
            line = line.strip().lstrip("*-").strip()
            if not line:
                continue
            # Markdown links become HTML links.
            line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html.escape(line))
            items.append(f"        <li>{line}</li>")
    if not items:
        return ""
    return "\n".join([f"      <h3>{html.escape(GAMES[slug][0])}</h3>", "      <ul>", *items, "      </ul>"])


def _card(slug: str) -> str:
    """Return one game's menu card as HTML."""
    name, kind = GAMES[slug]
    blurb = _sentence_case(GameSettings.GAME_DESCRIPTIONS.get(name, ""))
    return "\n".join([
        f'      <a class="card {kind}" href="{slug}/">',
        f'        <img src="previews/{slug}.png" alt="">',
        '        <div class="body">',
        f'          <div class="kind">{kind}</div>',
        f"          <h2>{html.escape(name)}</h2>",
        f"          <p>{html.escape(blurb)}</p>",
        "        </div>",
        "      </a>",
    ])


def build_menu() -> None:
    """Write ``web/index.html``: a card per built game, linking to its page, and the credits."""
    previews = OUT / "previews"
    previews.mkdir(parents=True, exist_ok=True)
    built = [slug for slug in GAMES if (OUT / slug / "index.html").exists()]
    for slug in built:
        shutil.copy2(ROOT / GameSettings.PREVIEW_IMAGES[GAMES[slug][0]], previews / f"{slug}.png")
    page = (ROOT / "scripts" / "web_menu.html").read_text(encoding="utf-8")
    page = page.replace("{{cards}}", "\n".join(_card(slug) for slug in built))
    page = page.replace("{{credits}}", "\n".join(filter(None, (_credits(slug) for slug in built))))
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print("built", OUT / "index.html")


def main() -> None:
    """Build the games named on the command line (all of them by default), then the menu."""
    for slug in sys.argv[1:] or GAMES:
        build_game(slug)
    build_menu()


if __name__ == "__main__":
    main()
