"""CLI entry point: python -m quiz (or quiz.cmd on Windows)."""

from __future__ import annotations

import argparse
import random
import sys

from . import __version__
from .engine import run_session, select_questions, summarize
from .history import load_missed_ids, update_missed
from .loader import DIFFICULTIES, LANGUAGES, BankError, load_questions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quiz",
        description="Random quiz for big-tech style general coding assessments "
                    "(Python & Java).",
    )
    parser.add_argument("-l", "--language", choices=(*LANGUAGES, "all"),
                        default="all", help="limit questions to one language")
    parser.add_argument("-n", "--count", type=int, default=10,
                        help="number of questions to ask (default: 10)")
    parser.add_argument("-d", "--difficulty", choices=DIFFICULTIES,
                        help="limit questions to one difficulty")
    parser.add_argument("-t", "--topic",
                        help="limit questions to one topic (see --list-topics)")
    parser.add_argument("--review", action="store_true",
                        help="only ask questions you previously missed")
    parser.add_argument("--seed", type=int,
                        help="random seed for a reproducible session")
    parser.add_argument("--list-topics", action="store_true",
                        help="list available topics per language and exit")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        questions = load_questions()
    except BankError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.list_topics:
        topics = sorted({(q.language, q.topic) for q in questions})
        for language, topic in topics:
            print(f"{language}: {topic}")
        return 0

    only_ids = None
    if args.review:
        only_ids = load_missed_ids()
        if not only_ids:
            print("Nothing to review - no missed questions on record.")
            return 0

    rng = random.Random(args.seed)
    selected = select_questions(
        questions,
        language=args.language,
        difficulty=args.difficulty,
        topic=args.topic,
        count=args.count,
        only_ids=only_ids,
        rng=rng,
    )
    if not selected:
        print("No questions match the given filters.")
        return 1

    print(f"Starting quiz: {len(selected)} question(s). Good luck!")
    results = run_session(selected, rng)
    summarize(results)
    if results:
        update_missed(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
