"""Local study UI server (stdlib only): python -m quiz.server, or study.cmd.

Serves the single-page app in ui/ and a small JSON API. Question banks,
cards, and problems are re-read on every bootstrap request, so edits to the
data files show up on browser refresh without restarting the server.
"""

from __future__ import annotations

import argparse
import json
import threading
import webbrowser
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import srs
from .cards import load_cards
from .loader import load_questions
from .problems import load_problems

UI_DIR = Path(__file__).resolve().parent.parent / "ui"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}
DEFAULT_PORT = 8765

_state_lock = threading.Lock()


def item_keys(questions, cards) -> list[str]:
    return [f"q:{q.id}" for q in questions] + [f"c:{c.id}" for c in cards]


class StudyHandler(BaseHTTPRequestHandler):
    server_version = "quiz-study/0.1"

    def log_message(self, fmt, *args):  # quiet the per-request console noise
        pass

    def _send_json(self, obj, status: int = 200) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, message: str, status: int = 400) -> None:
        self._send_json({"error": message}, status)

    def do_GET(self):  # noqa: N802 (http.server API)
        parsed = urlparse(self.path)
        if parsed.path in STATIC_FILES:
            filename, content_type = STATIC_FILES[parsed.path]
            data = (UI_DIR / filename).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif parsed.path == "/api/bootstrap":
            self._handle_bootstrap()
        elif parsed.path == "/api/problem":
            self._handle_problem(parse_qs(parsed.query))
        else:
            self._send_error_json("not found", 404)

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._send_error_json("invalid JSON body")
            return

        if parsed.path == "/api/review":
            self._handle_review(payload)
        elif parsed.path == "/api/postmortem":
            self._handle_postmortem(payload)
        else:
            self._send_error_json("not found", 404)

    # -- handlers ---------------------------------------------------------

    def _handle_bootstrap(self):
        questions = load_questions()
        cards = load_cards()
        problems = load_problems()
        with _state_lock:
            state = srs.load_state()
            queue = srs.build_daily_queue(item_keys(questions, cards), state)
        self._send_json({
            "questions": [asdict(q) for q in questions],
            "cards": [asdict(c) for c in cards],
            "problems": [p.meta() for p in problems],
            "state": state,
            "daily": queue,
        })

    def _handle_problem(self, query):
        problem_id = (query.get("id") or [""])[0]
        for p in load_problems():
            if p.id == problem_id:
                self._send_json({"meta": p.meta(), "statement": p.statement,
                                 "solution": p.solution})
                return
        self._send_error_json(f"unknown problem id: {problem_id}", 404)

    def _handle_review(self, payload):
        key = payload.get("key", "")
        correct = payload.get("correct")
        if not key or not isinstance(correct, bool):
            self._send_error_json("expected {key: str, correct: bool}")
            return
        with _state_lock:
            state = srs.load_state()
            entry = srs.record_review(state, key, correct)
            srs.save_state(state)
        self._send_json({"key": key, "entry": entry})

    def _handle_postmortem(self, payload):
        try:
            with _state_lock:
                state = srs.load_state()
                entry = srs.record_postmortem(
                    state,
                    problem_id=payload["problem_id"],
                    outcome=payload["outcome"],
                    cause=payload["cause"],
                    minutes=payload.get("minutes", 0),
                )
                srs.save_state(state)
        except (KeyError, ValueError) as exc:
            self._send_error_json(str(exc))
            return
        self._send_json({"entry": entry})


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="quiz.server",
                                     description="Run the local study UI.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true",
                        help="do not open a browser tab on start")
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), StudyHandler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Study UI running at {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
