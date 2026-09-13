"""Load trigger->pattern flashcards from cards/*.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CARDS_DIR = Path(__file__).resolve().parent.parent / "cards"
REQUIRED_KEYS = {"id", "category", "trigger", "pattern"}


class CardError(ValueError):
    """Raised when a card file is malformed."""


@dataclass(frozen=True)
class Card:
    id: str
    category: str
    trigger: str
    pattern: str
    notes: str = ""


def load_cards(cards_dir: Path = CARDS_DIR) -> list[Card]:
    cards: list[Card] = []
    seen_ids: set[str] = set()
    if not cards_dir.is_dir():
        return cards

    for path in sorted(cards_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CardError(f"{path}: invalid JSON: {exc}") from exc
        if not isinstance(data, list):
            raise CardError(f"{path}: top-level value must be a JSON array")

        for raw in data:
            missing = REQUIRED_KEYS - raw.keys()
            if missing:
                raise CardError(f"{path}: card {raw.get('id', '<no id>')} "
                                f"is missing keys: {sorted(missing)}")
            if raw["id"] in seen_ids:
                raise CardError(f"{path}: duplicate card id {raw['id']!r}")
            seen_ids.add(raw["id"])
            cards.append(Card(
                id=raw["id"],
                category=raw["category"],
                trigger=raw["trigger"],
                pattern=raw["pattern"],
                notes=raw.get("notes", ""),
            ))
    return cards
