"""Unit tests for selection, shuffling, and session flow."""

import random
import unittest

from quiz.engine import (QuestionResult, run_session, select_questions,
                         shuffle_choices, summarize)
from quiz.loader import Question


def make_question(qid, language="python", topic="misc", difficulty="easy"):
    return Question(
        id=qid, language=language, topic=topic, difficulty=difficulty,
        question=f"Question {qid}?",
        choices=("alpha", "beta", "gamma", "delta"),
        answer_index=2,
        explanation="Because gamma.",
    )


POOL = [
    make_question("py-a"),
    make_question("py-b", difficulty="hard"),
    make_question("py-c", topic="strings"),
    make_question("ja-a", language="java"),
    make_question("ja-b", language="java", difficulty="hard"),
]


class TestSelect(unittest.TestCase):

    def test_filters_by_language(self):
        picked = select_questions(POOL, language="java", count=10,
                                  rng=random.Random(1))
        self.assertEqual({q.language for q in picked}, {"java"})
        self.assertEqual(len(picked), 2)

    def test_filters_by_difficulty_and_topic(self):
        picked = select_questions(POOL, difficulty="hard", count=10,
                                  rng=random.Random(1))
        self.assertEqual({q.id for q in picked}, {"py-b", "ja-b"})
        picked = select_questions(POOL, topic="strings", count=10,
                                  rng=random.Random(1))
        self.assertEqual([q.id for q in picked], ["py-c"])

    def test_respects_count(self):
        picked = select_questions(POOL, count=3, rng=random.Random(1))
        self.assertEqual(len(picked), 3)

    def test_only_ids_filter(self):
        picked = select_questions(POOL, only_ids={"py-a", "ja-b"}, count=10,
                                  rng=random.Random(1))
        self.assertEqual({q.id for q in picked}, {"py-a", "ja-b"})

    def test_seeded_selection_is_reproducible(self):
        first = select_questions(POOL, count=3, rng=random.Random(42))
        second = select_questions(POOL, count=3, rng=random.Random(42))
        self.assertEqual([q.id for q in first], [q.id for q in second])


class TestShuffle(unittest.TestCase):

    def test_answer_index_is_remapped(self):
        q = make_question("py-x")
        for seed in range(20):
            choices, correct_pos = shuffle_choices(q, random.Random(seed))
            self.assertEqual(sorted(choices), sorted(q.choices))
            self.assertEqual(choices[correct_pos], q.answer_text)


class TestSession(unittest.TestCase):

    def run_scripted(self, questions, answers):
        answers = iter(answers)
        lines = []
        results = run_session(questions, random.Random(0),
                              ask=lambda _prompt: next(answers),
                              out=lines.append)
        return results, "\n".join(lines)

    def test_correct_and_incorrect_are_scored(self):
        q = make_question("py-x")
        choices, correct_pos = shuffle_choices(q, random.Random(0))
        right = "abcd"[correct_pos]
        wrong = next(c for c in "abcd" if c != right)

        # run_session re-shuffles with the same seeded rng, so the mapping
        # above matches what the session shows for a single question.
        results, _ = self.run_scripted([q], [right])
        self.assertTrue(results[0].correct)

        results, output = self.run_scripted([q], [wrong])
        self.assertFalse(results[0].correct)
        self.assertIn("Incorrect", output)
        self.assertIn(q.explanation, output)

    def test_quit_ends_session_early(self):
        results, _ = self.run_scripted([make_question("a1"),
                                        make_question("a2")], ["q"])
        self.assertEqual(results, [])

    def test_invalid_input_reprompts(self):
        q = make_question("py-x")
        results, output = self.run_scripted([q], ["zz", "", "a"])
        self.assertEqual(len(results), 1)
        self.assertIn("Please enter one of", output)

    def test_summarize_reports_score(self):
        q = make_question("py-x")
        lines = []
        summarize([QuestionResult(q, 2, True),
                   QuestionResult(q, 0, False)], out=lines.append)
        text = "\n".join(lines)
        self.assertIn("Score: 1/2 (50%)", text)
        self.assertIn("python/misc: 1/2", text)


if __name__ == "__main__":
    unittest.main()
