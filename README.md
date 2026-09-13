# code_assessment

Practice toolkit for big-tech style general coding assessments (CodeSignal
GCA and similar). Covers **Python** and **Java**. Pure Python standard
library — no dependencies to install. Requires Python 3.10+.

Two ways to practice:

- **Study UI** (`study.cmd`): a local web app with a Quizlet-style daily
  routine — spaced-repetition (Leitner) review queue, trigger→pattern
  flashcards, multiple-choice quizzes, timed long-form problems with a
  post-mortem log (misread / unknown pattern / slow recall / implementation
  bug), and per-category stats.
- **Quiz CLI** (`quiz.cmd`): quick multiple-choice sessions in the terminal.

## Study UI

```
study.cmd                    # starts http://127.0.0.1:8765/ and opens a browser
python -m quiz.server        # any OS; --port N, --no-browser
```

Tabs:

- **Daily** — everything due today plus up to 10 new items. Wrong answers
  drop back to box 1 and reappear; correct answers climb boxes with growing
  intervals (1/2/4/8/16 days).
- **Flashcards** — trigger→pattern cards ("sorted array, pair sum" → "two
  pointers"), browsable by category.
- **Quiz** — on-demand multiple-choice sessions; results feed the same boxes.
- **Problems** — long-form problems by category: read the statement, run the
  timer, reveal the solution, then log the outcome and the *cause* of any
  failure. The cause log tells you what to train.
- **Stats** — box distribution, accuracy per category, post-mortem causes.

Study state lives in `results/study_state.json` (gitignored, per-machine).

## Quiz CLI

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
quiz/               package (stdlib only)
  __main__.py       quiz CLI entry point (python -m quiz)
  loader.py         loads/validates JSON question banks
  engine.py         selection, choice shuffling, session loop, scoring
  history.py        missed-question log for the CLI --review
  server.py         study UI server (python -m quiz.server)
  srs.py            Leitner spaced-repetition state
  problems.py       loads problems/<category>/*.md
  cards.py          loads cards/*.json flashcards
ui/                 study UI single-page app (vanilla HTML/CSS/JS)
questions/
  python/*.json     Python MCQ banks
  java/*.json       Java MCQ banks
cards/*.json        trigger→pattern flashcards
problems/
  _TEMPLATE.md      problem format + rewrite rules
  <category>/*.md   long-form timed problems (statement + solutions)
tests/              unittest suite
quiz.cmd            quiz CLI launcher (Windows)
study.cmd           study UI launcher (Windows)
```

## Adding problems

Long-form problems live one per file in `problems/<category>/<id>.md`; the
folder name is the category. Copy `problems/_TEMPLATE.md` and follow the
rules embedded in it — most importantly: problems practiced on other
platforms must be **rewritten** (new story, names, values, and recomputed
examples), never pasted verbatim, and every example must be verified by
actually running the solution code. Everything above the `## Approach`
heading is shown while the timer runs; everything below appears after
"Reveal solution".

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
