"""Quiz session logic: filtering, random selection, choice shuffling, scoring."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from .loader import Question

CHOICE_LABELS = "abcdefgh"


@dataclass
class QuestionResult:
    question: Question
    given_index: int | None  # index into the ORIGINAL choices; None = skipped/quit
    correct: bool


def select_questions(questions: Sequence[Question],
                     language: str = "all",
                     difficulty: str | None = None,
                     topic: str | None = None,
                     count: int = 10,
                     only_ids: Iterable[str] | None = None,
                     rng: random.Random | None = None) -> list[Question]:
    """Filter the pool, then pick up to `count` questions at random."""
    rng = rng or random.Random()
    id_filter = set(only_ids) if only_ids is not None else None

    pool = [
        q for q in questions
        if (language == "all" or q.language == language)
        and (difficulty is None or q.difficulty == difficulty)
        and (topic is None or q.topic == topic)
        and (id_filter is None or q.id in id_filter)
    ]
    if count >= len(pool):
        selected = list(pool)
        rng.shuffle(selected)
        return selected
    return rng.sample(pool, count)


def shuffle_choices(question: Question,
                    rng: random.Random) -> tuple[list[str], int]:
    """Return the choices in a random order plus the new index of the answer."""
    order = list(range(len(question.choices)))
    rng.shuffle(order)
    shuffled = [question.choices[i] for i in order]
    return shuffled, order.index(question.answer_index)


def _format_question(number: int, total: int, question: Question,
                     choices: Sequence[str]) -> str:
    lines = [
        f"[{number}/{total}] ({question.language} | {question.topic} "
        f"| {question.difficulty})",
        "",
        question.question,
    ]
    if question.code:
        lines += ["", "    " + question.code.replace("\n", "\n    ")]
    lines.append("")
    for label, choice in zip(CHOICE_LABELS, choices):
        lines.append(f"  {label}) {choice}")
    return "\n".join(lines)


def run_session(selected: Sequence[Question],
                rng: random.Random,
                ask: Callable[[str], str] = input,
                out: Callable[[str], None] = print) -> list[QuestionResult]:
    """Ask each question interactively. Returns one result per question asked.

    Typing 'q' (or hitting Ctrl+C / end-of-input) ends the session early;
    questions never shown are not counted.
    """
    results: list[QuestionResult] = []
    total = len(selected)

    for number, question in enumerate(selected, start=1):
        choices, correct_pos = shuffle_choices(question, rng)
        valid_labels = CHOICE_LABELS[:len(choices)]
        out("")
        out(_format_question(number, total, question, choices))
        out("")

        try:
            while True:
                raw = ask(f"Your answer [{valid_labels[0]}-{valid_labels[-1]}, "
                          f"q to quit]: ").strip().lower()
                if raw == "q":
                    return results
                if len(raw) == 1 and raw in valid_labels:
                    break
                out(f"  Please enter one of: {', '.join(valid_labels)} (or q)")
        except (EOFError, KeyboardInterrupt):
            out("")
            return results

        picked_pos = valid_labels.index(raw)
        correct = picked_pos == correct_pos
        if correct:
            out("  Correct!")
        else:
            out(f"  Incorrect. Answer: {CHOICE_LABELS[correct_pos]}) "
                f"{choices[correct_pos]}")
        out(f"  Why: {question.explanation}")

        # Map the picked position back to the original (unshuffled) index.
        original_index = question.choices.index(choices[picked_pos])
        results.append(QuestionResult(question, original_index, correct))

    return results


def summarize(results: Sequence[QuestionResult],
              out: Callable[[str], None] = print) -> None:
    if not results:
        out("No questions answered.")
        return

    score = sum(r.correct for r in results)
    total = len(results)
    out("")
    out("=" * 50)
    out(f"Score: {score}/{total} ({100 * score // total}%)")

    by_topic: dict[str, list[bool]] = {}
    for r in results:
        by_topic.setdefault(f"{r.question.language}/{r.question.topic}",
                            []).append(r.correct)
    out("By topic:")
    for topic in sorted(by_topic):
        marks = by_topic[topic]
        out(f"  {topic}: {sum(marks)}/{len(marks)}")

    missed = [r.question.id for r in results if not r.correct]
    if missed:
        out(f"Missed: {', '.join(missed)}  (retry with --review)")
    out("=" * 50)
