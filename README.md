# code_assessment

Random-quiz CLI for practicing big-tech style general coding assessments.
Covers **Python** and **Java**. Multiple-choice questions with shuffled
choices, instant feedback, explanations, and a missed-question review mode.

Pure Python standard library — no dependencies to install.

## Quick start

Requires Python 3.10+.

```
quiz.cmd                 # Windows: 10 random questions from both languages
python -m quiz           # any OS, run from the repo root
```

Common options:

```
quiz.cmd -l python            # Python questions only
quiz.cmd -l java -n 5         # 5 Java questions
quiz.cmd -d hard              # hard questions only
quiz.cmd -t collections       # one topic (see --list-topics)
quiz.cmd --review             # retry questions you previously missed
quiz.cmd --seed 42            # reproducible session
quiz.cmd --list-topics        # show available language/topic pairs
```

During a session, answer with a letter (`a`-`d`) or type `q` to quit early.
Missed questions are tracked in `results/missed.json` (gitignored, per-machine)
and are cleared one by one as you answer them correctly in `--review` runs.

## Project layout

```
quiz/               CLI package (stdlib only)
  __main__.py       argparse entry point (python -m quiz)
  loader.py         loads/validates JSON question banks
  engine.py         selection, choice shuffling, session loop, scoring
  history.py        missed-question log for --review
questions/
  python/*.json     Python question banks
  java/*.json       Java question banks
tests/              unittest suite
quiz.cmd            Windows launcher
coding-problems.md  worked long-form problems (separate from the quiz tool)
```

## Adding questions

Add an object to an existing bank, or create a new `*.json` file under
`questions/python/` or `questions/java/` (any array of question objects is
picked up automatically). Schema:

```json
{
  "id": "py-011",
  "language": "python",
  "topic": "data-structures",
  "difficulty": "easy | medium | hard",
  "question": "What does this print?",
  "code": "print(1 + 1)",
  "choices": ["2", "11", "It raises an error", "None"],
  "answer_index": 0,
  "explanation": "Why the answer is correct (shown after each question)."
}
```

Notes:

- `id` must be unique across all banks; `language` must match the folder.
- `answer_index` is the 0-based index into `choices` **as written in the
  JSON** — the CLI shuffles choice order at runtime.
- `code` is optional. Choices must be distinct.
- Questions are written in US English.

The loader validates all of this on startup and fails with a clear error
message if a bank is malformed. The test suite checks it too:

## Running tests

```
python -m unittest discover -s tests -v
```
