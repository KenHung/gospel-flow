#!/usr/bin/env python3
"""Check Recall decks beyond what card.schema.json can express.

Schema validation of every deck file lives here too, so one command covers it.
card.schema.json remains the schema; this script only adds the constraints
that schema cannot state.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

# Index-aligned translations. Same length, same type at each index,
# and for multiple-choice cards the same option count and answer index.
PAIRS = (("decks/gospel.json", "decks/gospel_zh.json"),)


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "card.schema.json").is_file() and (parent / "decks" / "manifest.json").is_file():
            return parent
    sys.exit("check_decks: cannot find repo root (card.schema.json + decks/manifest.json)")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: invalid JSON ({exc})") from exc


def deck_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in (root / "decks").glob("*.json")
        if path.name != "manifest.json"
    )


def check_schema(validator: Draft202012Validator, path: Path, data) -> list[str]:
    errors = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
        where = "/".join(str(part) for part in error.path) or "(deck)"
        errors.append(f"{path.name}: {where}: {error.message}")
    return errors


def check_answer_bounds(path: Path, data) -> list[str]:
    errors = []
    cards = data.get("cards") if isinstance(data, dict) else None
    if not isinstance(cards, list):
        return errors
    for index, card in enumerate(cards):
        if not isinstance(card, dict) or card.get("type") != "mc":
            continue
        options = card.get("options")
        answer = card.get("answer")
        if isinstance(options, list) and isinstance(answer, int) and not isinstance(answer, bool):
            if answer >= len(options):
                errors.append(
                    f"{path.name}: cards/{index}/answer: {answer} is past the last option ({len(options) - 1})"
                )
    return errors


def check_manifest(root: Path) -> list[str]:
    manifest_path = root / "decks" / "manifest.json"
    data = load_json(manifest_path)
    errors = []
    decks = data.get("decks") if isinstance(data, dict) else None
    if not isinstance(decks, list):
        return [f"{manifest_path.name}: expected an object with a decks array"]

    seen: set[str] = set()
    for index, entry in enumerate(decks):
        label = f"decks/{index}"
        if not isinstance(entry, dict):
            errors.append(f"{manifest_path.name}: {label}: expected an object")
            continue
        deck_id = entry.get("id")
        name = entry.get("name")
        file_value = entry.get("file")
        if not isinstance(deck_id, str) or not deck_id:
            errors.append(f"{manifest_path.name}: {label}: id must be a non-empty string")
        elif deck_id in seen:
            errors.append(f"{manifest_path.name}: {label}: duplicate id {deck_id!r}")
        else:
            seen.add(deck_id)
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{manifest_path.name}: {label}: name must be a non-empty string")
        if not isinstance(file_value, str) or not file_value:
            errors.append(f"{manifest_path.name}: {label}: file must be a path string")
            continue
        relative = file_value[2:] if file_value.startswith("./") else file_value
        target = root / relative
        if not target.is_file():
            errors.append(f"{manifest_path.name}: {label}: file does not exist: {file_value}")
    return errors


def check_pairs(root: Path) -> list[str]:
    errors = []
    for left_rel, right_rel in PAIRS:
        left_path = root / left_rel
        right_path = root / right_rel
        if not left_path.is_file() or not right_path.is_file():
            errors.append(f"translation pair missing: {left_rel} / {right_rel}")
            continue
        left = load_json(left_path).get("cards")
        right = load_json(right_path).get("cards")
        if not isinstance(left, list) or not isinstance(right, list):
            continue
        if len(left) != len(right):
            errors.append(
                f"{left_path.name} has {len(left)} cards and {right_path.name} has {len(right)}"
            )
        for index, (a, b) in enumerate(zip(left, right)):
            if not isinstance(a, dict) or not isinstance(b, dict):
                continue
            if a.get("type") != b.get("type"):
                errors.append(
                    f"card {index}: type {a.get('type')!r} in {left_path.name}, {b.get('type')!r} in {right_path.name}"
                )
                continue
            if a.get("type") != "mc":
                continue
            a_options = a.get("options") if isinstance(a.get("options"), list) else []
            b_options = b.get("options") if isinstance(b.get("options"), list) else []
            if len(a_options) != len(b_options):
                errors.append(
                    f"card {index}: {len(a_options)} options in {left_path.name}, {len(b_options)} in {right_path.name}"
                )
            if a.get("answer") != b.get("answer"):
                errors.append(
                    f"card {index}: answer {a.get('answer')!r} in {left_path.name}, {b.get('answer')!r} in {right_path.name}"
                )
    return errors


def main() -> int:
    root = repo_root()
    schema = load_json(root / "card.schema.json")
    validator = Draft202012Validator(schema)
    errors: list[str] = []

    for path in deck_files(root):
        data = load_json(path)
        errors.extend(check_schema(validator, path, data))
        errors.extend(check_answer_bounds(path, data))

    errors.extend(check_manifest(root))
    errors.extend(check_pairs(root))

    if errors:
        print(f"{len(errors)} deck check(s) failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    names = ", ".join(path.name for path in deck_files(root))
    print(f"ok: {names}; manifest; {len(PAIRS)} translation pair(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
