"""Student game discovery and manifest parsing."""

import json
from pathlib import Path

from launcher.models import StudentGameRecord
from settings import InputSchemeSettings, StudentGameSettings


def _read_student_manifest(manifest_path: Path) -> dict:
    """
    Load a student game manifest, returning {} on any read or parse error.

    Args:
        manifest_path (Path): Absolute path to the candidate game.json file.

    Returns:
        dict: Parsed manifest dictionary, or an empty dict if the file is
        missing, unreadable, malformed JSON, or not a JSON object. The
        launcher must keep starting even if one student's manifest is broken.
    """
    if not manifest_path.is_file():
        return {}
    try:
        parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def discover_student_games(student_root: Path) -> list[StudentGameRecord]:
    """
    Scan student_root for game folders and return one record per game.

    Args:
        student_root (Path): Absolute path to the games/student/ directory.

    Returns:
        list[StudentGameRecord]: One record per discovered game, sorted by
        folder name so menu order stays stable across runs.
    """
    student_root.mkdir(parents=True, exist_ok=True)
    records: list[StudentGameRecord] = []
    for entry in sorted(student_root.iterdir()):
        # Skip hidden folders (e.g. .git, .vscode)
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        main_path = entry / StudentGameSettings.ENTRY_FILENAME
        if not main_path.is_file():
            continue
        default_label = entry.name.replace("-", " ").replace("_", " ").title()
        manifest = _read_student_manifest(entry / StudentGameSettings.MANIFEST_FILENAME)
        label_value = manifest.get(StudentGameSettings.MANIFEST_KEY_LABEL)
        label = label_value if isinstance(label_value, str) and label_value else default_label
        attribution_value = manifest.get(StudentGameSettings.MANIFEST_KEY_ATTRIBUTION)
        attribution = (
            attribution_value
            if isinstance(attribution_value, str) and attribution_value
            else StudentGameSettings.DEFAULT_ATTRIBUTION
        )
        preview_value = manifest.get(StudentGameSettings.MANIFEST_KEY_PREVIEW)
        preview_path = entry / preview_value if isinstance(preview_value, str) and preview_value else None
        input_scheme_value = manifest.get(StudentGameSettings.MANIFEST_KEY_INPUT_SCHEME)
        input_scheme_key = (
            input_scheme_value
            if isinstance(input_scheme_value, str) and input_scheme_value in InputSchemeSettings.LABELS
            else None
        )
        note_value = manifest.get(StudentGameSettings.MANIFEST_KEY_NOTE)
        note = note_value if isinstance(note_value, str) and note_value else None
        records.append(
            StudentGameRecord(
                label=label,
                main_path=main_path,
                attribution=attribution,
                preview_path=preview_path,
                input_scheme_key=input_scheme_key,
                note=note,
                under_construction=bool(manifest.get(StudentGameSettings.MANIFEST_KEY_UNDER_CONSTRUCTION)),
            )
        )
    return records
