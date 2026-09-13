"""Unit tests for the Leitner spaced-repetition logic."""

import unittest
from datetime import date

from quiz import srs


class TestRecordReview(unittest.TestCase):

    def test_new_item_correct_goes_to_box_1_due_tomorrow(self):
        state = {"items": {}, "postmortems": [], "new_intro": {}}
        entry = srs.record_review(state, "q:x", True, today=date(2026, 9, 13))
        self.assertEqual(entry["box"], 1)
        self.assertEqual(entry["due"], "2026-09-14")
        self.assertEqual(state["new_intro"]["2026-09-13"], 1)

    def test_correct_climbs_boxes_with_growing_intervals(self):
        state = {"items": {}, "postmortems": [], "new_intro": {}}
        day = date(2026, 9, 13)
        srs.record_review(state, "q:x", True, today=day)   # box 1
        entry = srs.record_review(state, "q:x", True, today=day)  # box 2
        self.assertEqual(entry["box"], 2)
        self.assertEqual(entry["due"], "2026-09-15")
        for _ in range(10):
            entry = srs.record_review(state, "q:x", True, today=day)
        self.assertEqual(entry["box"], srs.MAX_BOX)
        self.assertEqual(entry["due"], "2026-09-29")  # today + 16

    def test_wrong_resets_to_box_1_due_today(self):
        state = {"items": {}, "postmortems": [], "new_intro": {}}
        day = date(2026, 9, 13)
        for _ in range(3):
            srs.record_review(state, "q:x", True, today=day)
        entry = srs.record_review(state, "q:x", False, today=day)
        self.assertEqual(entry["box"], 1)
        self.assertEqual(entry["due"], "2026-09-13")
        self.assertEqual(entry["seen"], 4)
        self.assertEqual(entry["correct"], 3)


class TestDailyQueue(unittest.TestCase):

    def test_due_and_new_split_with_budget(self):
        day = date(2026, 9, 13)
        state = {"items": {}, "postmortems": [], "new_intro": {}}
        srs.record_review(state, "q:due", False, today=day)      # due today
        srs.record_review(state, "q:later", True, today=day)     # due tomorrow
        all_keys = ["q:due", "q:later"] + [f"q:new{i}" for i in range(20)]

        queue = srs.build_daily_queue(all_keys, state, today=day, new_per_day=10)
        self.assertEqual(queue["due"], ["q:due"])
        # 2 items were introduced today already, so the new budget is 8.
        self.assertEqual(len(queue["new"]), 8)
        self.assertNotIn("q:later", queue["due"] + queue["new"])

    def test_overdue_items_are_due(self):
        state = {"items": {}, "postmortems": [], "new_intro": {}}
        srs.record_review(state, "q:x", True, today=date(2026, 9, 1))
        queue = srs.build_daily_queue(["q:x"], state, today=date(2026, 9, 13),
                                      new_per_day=0)
        self.assertEqual(queue["due"], ["q:x"])


class TestPostmortem(unittest.TestCase):

    def test_valid_entry_is_appended(self):
        state = {"items": {}, "postmortems": [], "new_intro": {}}
        entry = srs.record_postmortem(state, "booking-consolidation", "partial",
                                      "misread", 17.25, today=date(2026, 9, 13))
        self.assertEqual(state["postmortems"], [entry])
        self.assertEqual(entry["minutes"], 17.2)
        self.assertEqual(entry["date"], "2026-09-13")

    def test_invalid_values_are_rejected(self):
        state = {"items": {}, "postmortems": [], "new_intro": {}}
        with self.assertRaises(ValueError):
            srs.record_postmortem(state, "x", "aced", "none", 1)
        with self.assertRaises(ValueError):
            srs.record_postmortem(state, "x", "solved", "bad_luck", 1)
        self.assertEqual(state["postmortems"], [])


if __name__ == "__main__":
    unittest.main()
