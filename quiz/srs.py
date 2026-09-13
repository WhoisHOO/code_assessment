"""Leitner-box spaced repetition: review state shared by the study UI.

State lives in results/study_state.json (gitignored, per-machine).
Item keys are namespaced: "q:<question id>" for MCQs, "c:<card id>" for
flashcards.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

STATE_FILE = Path(__file__).resolve().parent.parent / "results" / "study_state.json"

# Days until the next review, per box. A wrong answer drops the item back to
# box 1 and makes it due again today.
BOX_INTERVAL_DAYS = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}
MAX_BOX = 5
DEFAULT_NEW_PER_DAY = 10

OUTCOMES = ("solved", "partial", "failed")
CAUSES = ("none", "misread", "unknown_pattern", "slow_recall", "implementation_bug")


def _empty_state() -> dict:
    return {"items": {}, "postmortems": [], "new_intro": {}}


def load_state(path: Path = STATE_FILE) -> dict:
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("items", {})
                data.setdefault("postmortems", [])
                data.setdefault("new_intro", {})
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return _empty_state()


def save_state(state: dict, path: Path = STATE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def record_review(state: dict, item_key: str, correct: bool,
                  today: date | None = None) -> dict:
    """Apply one review to an item and return its updated entry."""
    today = today or date.today()
    today_iso = today.isoformat()
    items = state.setdefault("items", {})

    entry = items.get(item_key)
    if entry is None:
        entry = {"box": 0, "due": today_iso, "seen": 0, "correct": 0}
        items[item_key] = entry
        intro = state.setdefault("new_intro", {})
        intro[today_iso] = intro.get(today_iso, 0) + 1

    entry["seen"] += 1
    if correct:
        entry["correct"] += 1
        entry["box"] = min(entry["box"] + 1, MAX_BOX)
        interval = BOX_INTERVAL_DAYS[entry["box"]]
        entry["due"] = (today + timedelta(days=interval)).isoformat()
    else:
        entry["box"] = 1
        entry["due"] = today_iso  # retry within the same session/day
    entry["last"] = today_iso
    return entry


def record_postmortem(state: dict, problem_id: str, outcome: str, cause: str,
                      minutes: float, today: date | None = None) -> dict:
    """Log the result of one timed long-form problem session."""
    if outcome not in OUTCOMES:
        raise ValueError(f"invalid outcome: {outcome!r}")
    if cause not in CAUSES:
        raise ValueError(f"invalid cause: {cause!r}")
    entry = {
        "problem_id": problem_id,
        "outcome": outcome,
        "cause": cause,
        "minutes": round(float(minutes), 1),
        "date": (today or date.today()).isoformat(),
    }
    state.setdefault("postmortems", []).append(entry)
    return entry


def build_daily_queue(all_keys: Iterable[str], state: dict,
                      today: date | None = None,
                      new_per_day: int = DEFAULT_NEW_PER_DAY) -> dict:
    """Split item keys into today's queue: due reviews plus a few new items.

    New (never-reviewed) items are capped at `new_per_day`, counting the ones
    already introduced today, so a long backlog cannot flood a session.
    """
    today_iso = (today or date.today()).isoformat()
    items = state.get("items", {})

    due = [k for k in all_keys
           if k in items and items[k]["due"] <= today_iso]
    introduced_today = state.get("new_intro", {}).get(today_iso, 0)
    budget = max(0, new_per_day - introduced_today)
    new = [k for k in all_keys if k not in items][:budget]
    return {"due": due, "new": new}
