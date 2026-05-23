from __future__ import annotations

import unittest

from projects.parentmate.src.app import build_event_glance_summary


class BuildEventGlanceSummaryTests(unittest.TestCase):
    def test_includes_when_where_action_and_cost(self) -> None:
        summary = build_event_glance_summary(
            {
                "date": "2026-05-12",
                "start_time": "09:00",
                "end_time": "15:00",
                "location": "Museum",
                "action_required": True,
                "items_needed": ["packed lunch"],
                "cost": "GBP 12.00",
                "event_status": "scheduled",
            }
        )

        self.assertIn("When: 2026-05-12 from 09:00 to 15:00.", summary)
        self.assertIn("Where: Museum.", summary)
        self.assertIn("Action needed: bring or submit packed lunch.", summary)
        self.assertIn("Cost: GBP 12.00.", summary)
        self.assertNotIn("Deadline:", summary)

    def test_deadline_only_event_stays_concise(self) -> None:
        summary = build_event_glance_summary(
            {
                "deadline": "2026-05-03",
                "action_required": True,
                "event_status": "scheduled",
            }
        )

        self.assertEqual(summary, "Deadline: 2026-05-03. Action needed before the deadline.")

    def test_action_without_items_does_not_invent_details(self) -> None:
        summary = build_event_glance_summary(
            {
                "date": "2026-06-01",
                "action_required": True,
                "event_status": "scheduled",
            }
        )

        self.assertIn("When: 2026-06-01.", summary)
        self.assertIn("Action needed.", summary)
        self.assertNotIn("bring or submit", summary)
        self.assertNotIn("Where:", summary)

    def test_non_scheduled_status_is_visible(self) -> None:
        summary = build_event_glance_summary(
            {
                "date": "2026-06-25",
                "start_time": "11:00",
                "event_status": "cancelled",
            }
        )

        self.assertEqual(summary, "Status: cancelled. When: 2026-06-25 at 11:00.")


if __name__ == "__main__":
    unittest.main()
