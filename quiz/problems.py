"""Load long-form practice problems from problems/<category>/*.md.

Each file starts with a simple `key: value` frontmatter block between two
`---` lines, followed by markdown. Everything up to (but not including) the
`## Approach` heading is the statement shown before the reveal; the rest is
the solution/notes shown after. See problems/_TEMPLATE.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"
REVEAL_HEADING = "## Approach"


class ProblemError(ValueError):
    """Raised when a problem file is malformed."""


@dataclass(frozen=True)
class Problem:
    id: str
    title: str
    category: str
    difficulty: str
    trigger: str
    pattern: str
    time_target_min: int
    path: Path
    statement: str = field(repr=False, default="")
    solution: str = field(repr=False, default="")

    def meta(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "difficulty": self.difficulty,
            "trigger": self.trigger,
            "pattern": self.pattern,
            "time_target_min": self.time_target_min,
        }


def parse_frontmatter(text: str, source: Path) -> tuple[dict, str]:
    """Return (frontmatter dict, markdown body)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ProblemError(f"{source}: file must start with a '---' frontmatter block")
    meta: dict[str, str] = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body = "\n".join(lines[i + 1:]).strip()
            return meta, body
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ProblemError(f"{source}: bad frontmatter line: {line!r}")
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"').strip("'")
    raise ProblemError(f"{source}: unterminated frontmatter block")


def _split_body(body: str, source: Path) -> tuple[str, str]:
    index = body.find(REVEAL_HEADING)
    if index < 0:
        raise ProblemError(f"{source}: missing required '{REVEAL_HEADING}' heading")
    return body[:index].strip(), body[index:].strip()


def load_problems(problems_dir: Path = PROBLEMS_DIR) -> list[Problem]:
    """Load every problems/<category>/*.md file (template excluded)."""
    problems: list[Problem] = []
    seen_ids: set[str] = set()
    if not problems_dir.is_dir():
        return problems

    for category_dir in sorted(p for p in problems_dir.iterdir() if p.is_dir()):
        category = category_dir.name
        for path in sorted(category_dir.glob("*.md")):
            if path.name.startswith("_"):
                continue
            meta, body = parse_frontmatter(path.read_text(encoding="utf-8"), path)

            for key in ("title", "difficulty", "trigger", "pattern"):
                if not meta.get(key):
                    raise ProblemError(f"{path}: frontmatter is missing {key!r}")
            if meta.get("category", category) != category:
                raise ProblemError(
                    f"{path}: frontmatter category {meta['category']!r} does not "
                    f"match folder {category!r}")

            problem_id = meta.get("id", path.stem)
            if problem_id in seen_ids:
                raise ProblemError(f"{path}: duplicate problem id {problem_id!r}")
            seen_ids.add(problem_id)

            statement, solution = _split_body(body, path)
            problems.append(Problem(
                id=problem_id,
                title=meta["title"],
                category=category,
                difficulty=meta["difficulty"],
                trigger=meta["trigger"],
                pattern=meta["pattern"],
                time_target_min=int(meta.get("time_target_min", 15)),
                path=path,
                statement=statement,
                solution=solution,
            ))
    return problems
