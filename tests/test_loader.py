"""Validate that every shipped question bank loads cleanly."""

import unittest

from quiz.loader import DIFFICULTIES, LANGUAGES, load_questions


class TestLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.questions = load_questions()

    def test_banks_are_nonempty_per_language(self):
        for language in LANGUAGES:
            with self.subTest(language=language):
                count = sum(q.language == language for q in self.questions)
                self.assertGreater(count, 0)

    def test_ids_are_unique(self):
        ids = [q.id for q in self.questions]
        self.assertEqual(len(ids), len(set(ids)))

    def test_fields_are_valid(self):
        for q in self.questions:
            with self.subTest(id=q.id):
                self.assertIn(q.language, LANGUAGES)
                self.assertIn(q.difficulty, DIFFICULTIES)
                self.assertGreaterEqual(len(q.choices), 2)
                self.assertTrue(0 <= q.answer_index < len(q.choices))
                self.assertTrue(q.question.strip())
                self.assertTrue(q.explanation.strip())

    def test_choices_are_distinct(self):
        for q in self.questions:
            with self.subTest(id=q.id):
                self.assertEqual(len(q.choices), len(set(q.choices)),
                                 "duplicate choices break answer remapping")


if __name__ == "__main__":
    unittest.main()
