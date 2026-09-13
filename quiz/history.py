"""Track missed questions across sessions in results/missed.json (gitignored)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from .engine import QuestionResult

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
MISSED_FILE = RESULTS_DIR / "missed.json"


def load_missed_ids(path: Path = MISSED_FILE) -> set[str]:
    if not path.is_file():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data) if isinstance(data, list) else set()
    except (json.JSONDecodeError, OSError):
        return set()


def update_missed(results: Sequence[QuestionResult],
                  path: Path = MISSED_FILE) -> None:
    """Add newly missed ids; drop ids that were just answered correctly."""
    missed = load_missed_ids(path)
    for r in results:
        if r.correct:
            missed.discard(r.question.id)
        else:
            missed.add(r.question.id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(missed), indent=2) + "\n",
                    encoding="utf-8")
