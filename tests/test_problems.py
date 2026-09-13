"""Validate the shipped problem files and card banks."""

import unittest

from quiz.cards import load_cards
from quiz.problems import REVEAL_HEADING, load_problems


class TestProblems(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.problems = load_problems()

    def test_problems_load(self):
        self.assertGreaterEqual(len(self.problems), 3)

    def test_ids_unique_and_categories_match_folders(self):
        ids = [p.id for p in self.problems]
        self.assertEqual(len(ids), len(set(ids)))
        for p in self.problems:
            self.assertEqual(p.path.parent.name, p.category)

    def test_statement_solution_split(self):
        for p in self.problems:
            with self.subTest(id=p.id):
                self.assertIn("## Problem", p.statement)
                self.assertNotIn(REVEAL_HEADING, p.statement)
                self.assertTrue(p.solution.startswith(REVEAL_HEADING))
                # The reveal side must carry actual solutions.
                self.assertIn("```python", p.solution)
                self.assertIn("```java", p.solution)

    def test_required_meta(self):
        for p in self.problems:
            with self.subTest(id=p.id):
                self.assertTrue(p.title and p.trigger and p.pattern)
                self.assertIn(p.difficulty, ("easy", "medium", "hard"))
                self.assertGreater(p.time_target_min, 0)


class TestCards(unittest.TestCase):

    def test_cards_load_with_unique_ids(self):
        cards = load_cards()
        self.assertGreaterEqual(len(cards), 10)
        ids = [c.id for c in cards]
        self.assertEqual(len(ids), len(set(ids)))
        for c in cards:
            self.assertTrue(c.trigger and c.pattern and c.category)


if __name__ == "__main__":
    unittest.main()
