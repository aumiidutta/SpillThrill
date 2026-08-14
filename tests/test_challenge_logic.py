import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from challenge_logic import pick_challenge  # noqa: E402


SAMPLE_ITEMS = [{"id": str(i), "text": f"Challenge {i}"} for i in range(1, 6)]  # 5 items


class TestPickChallenge(unittest.TestCase):
    def test_raises_on_empty_items(self):
        with self.assertRaises(ValueError):
            pick_challenge([], [])

    def test_returns_item_not_in_exclude_list(self):
        chosen, reset = pick_challenge(SAMPLE_ITEMS, ["1", "2", "3"])
        self.assertIn(chosen["id"], {"4", "5"})
        self.assertFalse(reset)

    def test_no_repeats_until_all_seen(self):
        """Simulate a full playthrough: every id should appear exactly once
        before anything repeats, matching the 'same challenge should not be
        viewed twice' requirement."""
        seen = []
        for _ in range(len(SAMPLE_ITEMS)):
            chosen, reset = pick_challenge(SAMPLE_ITEMS, seen)
            self.assertNotIn(chosen["id"], seen, "Got a repeat before the deck was exhausted")
            self.assertFalse(reset, "Should not reset before every item has been shown")
            seen.append(chosen["id"])
        self.assertEqual(sorted(seen), sorted(i["id"] for i in SAMPLE_ITEMS))

    def test_resets_once_exhausted(self):
        all_ids = [item["id"] for item in SAMPLE_ITEMS]
        chosen, reset = pick_challenge(SAMPLE_ITEMS, all_ids)
        self.assertTrue(reset)
        self.assertIn(chosen["id"], all_ids)

    def test_single_item_always_returned(self):
        one = [{"id": "42", "text": "Only one"}]
        chosen, reset = pick_challenge(one, [])
        self.assertEqual(chosen["id"], "42")
        self.assertFalse(reset)
        # Exclude it -> should reset and still return it (only option)
        chosen2, reset2 = pick_challenge(one, ["42"])
        self.assertEqual(chosen2["id"], "42")
        self.assertTrue(reset2)

    def test_exclude_ids_can_be_strings_or_mixed_types(self):
        items = [{"id": 1, "text": "a"}, {"id": 2, "text": "b"}]
        chosen, reset = pick_challenge(items, [1])  # int in exclude list
        self.assertEqual(str(chosen["id"]), "2")
        self.assertFalse(reset)


if __name__ == "__main__":
    unittest.main()
