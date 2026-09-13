"""Load and validate question banks from the questions/ directory.

Each bank is a JSON array of question objects. See README.md for the schema.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

QUESTIONS_DIR = Path(__file__).resolve().parent.parent / "questions"
LANGUAGES = ("python", "java")
DIFFICULTIES = ("easy", "medium", "hard")

REQUIRED_KEYS = {
    "id", "language", "topic", "difficulty",
    "question", "choices", "answer_index", "explanation",
}


class BankError(ValueError):
    """Raised when a question bank file is malformed."""


@dataclass(frozen=True)
class Question:
    id: str
    language: str
    topic: str
    difficulty: str
    question: str
    choices: tuple[str, ...]
    answer_index: int
    explanation: str
    code: str = ""

    @property
    def answer_text(self) -> str:
        return self.choices[self.answer_index]


def _parse_question(raw: dict, source: Path) -> Question:
    missing = REQUIRED_KEYS - raw.keys()
    if missing:
        raise BankError(f"{source}: question {raw.get('id', '<no id>')} "
                        f"is missing keys: {sorted(missing)}")

    choices = tuple(raw["choices"])
    if len(choices) < 2:
        raise BankError(f"{source}: question {raw['id']} needs at least 2 choices")

    answer_index = raw["answer_index"]
    if not isinstance(answer_index, int) or not 0 <= answer_index < len(choices):
        raise BankError(f"{source}: question {raw['id']} has an out-of-range "
                        f"answer_index: {answer_index!r}")

    if raw["difficulty"] not in DIFFICULTIES:
        raise BankError(f"{source}: question {raw['id']} has an invalid "
                        f"difficulty: {raw['difficulty']!r}")

    return Question(
        id=raw["id"],
        language=raw["language"],
        topic=raw["topic"],
        difficulty=raw["difficulty"],
        question=raw["question"],
        choices=choices,
        answer_index=answer_index,
        explanation=raw["explanation"],
        code=raw.get("code", ""),
    )


def load_questions(questions_dir: Path = QUESTIONS_DIR,
                   languages: tuple[str, ...] = LANGUAGES) -> list[Question]:
    """Load every *.json bank under questions/<language>/ and validate it."""
    questions: list[Question] = []
    seen_ids: set[str] = set()

    for language in languages:
        lang_dir = questions_dir / language
        if not lang_dir.is_dir():
            continue
        for path in sorted(lang_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise BankError(f"{path}: invalid JSON: {exc}") from exc
            if not isinstance(data, list):
                raise BankError(f"{path}: top-level value must be a JSON array")

            for raw in data:
                question = _parse_question(raw, path)
                if question.language != language:
                    raise BankError(
                        f"{path}: question {question.id} declares language "
                        f"{question.language!r} but lives under {language}/")
                if question.id in seen_ids:
                    raise BankError(f"{path}: duplicate question id {question.id!r}")
                seen_ids.add(question.id)
                questions.append(question)

    if not questions:
        raise BankError(f"No questions found under {questions_dir}")
    return questions
