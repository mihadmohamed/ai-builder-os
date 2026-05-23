from __future__ import annotations

import unittest
from urllib.parse import parse_qs, urlparse

from projects.parentmate.src.calendar import build_calendar_sync_plan


class CalendarSyncPlanTests(unittest.TestCase):
    def test_builds_timed_google_calendar_link(self) -> None:
        plan = build_calendar_sync_plan(
            {
                "title": "Year 3 Museum Trip",
                "date": "2026-05-12",
                "start_time": "09:00",
                "end_time": "15:00",
                "location": "City Museum",
                "event_status": "scheduled",
                "action_required": True,
                "items_needed": ["packed lunch"],
                "cost": "GBP 12.00",
            }
        )

        self.assertTrue(plan["syncable"])
        self.assertEqual(plan["mode"], "timed")
        self.assertEqual(plan["dates"], "20260512T090000/20260512T150000")

        query = parse_qs(urlparse(plan["url"]).query)
        self.assertEqual(query["action"], ["TEMPLATE"])
        self.assertEqual(query["text"], ["Year 3 Museum Trip"])
        self.assertEqual(query["location"], ["City Museum"])

    def test_builds_all_day_event_from_deadline_when_no_date_exists(self) -> None:
        plan = build_calendar_sync_plan(
            {
                "title": "Return permission slip",
                "date": None,
                "deadline": "2026-05-03",
                "event_status": "scheduled",
                "action_required": True,
            }
        )

        self.assertTrue(plan["syncable"])
        self.assertEqual(plan["mode"], "all_day")
        self.assertEqual(plan["dates"], "20260503/20260504")

    def test_builds_multi_day_all_day_event_from_date_range(self) -> None:
        plan = build_calendar_sync_plan(
            {
                "title": "Year 6 Camp",
                "date": "2026-09-14 to 2026-09-16",
                "event_status": "scheduled",
            }
        )

        self.assertTrue(plan["syncable"])
        self.assertEqual(plan["mode"], "all_day")
        self.assertEqual(plan["dates"], "20260914/20260917")

    def test_requires_both_start_and_end_time_for_timed_event(self) -> None:
        plan = build_calendar_sync_plan(
            {
                "title": "Swimming lesson",
                "date": "2026-06-25",
                "start_time": "11:00",
                "end_time": None,
                "event_status": "scheduled",
            }
        )

        self.assertFalse(plan["syncable"])
        self.assertIn("Both start and end time", plan["reason"])

    def test_does_not_offer_sync_for_cancelled_event(self) -> None:
        plan = build_calendar_sync_plan(
            {
                "title": "Swimming lesson",
                "date": "2026-06-25",
                "start_time": "11:00",
                "end_time": "12:00",
                "event_status": "cancelled",
            }
        )

        self.assertFalse(plan["syncable"])
        self.assertIn("Cancelled events", plan["reason"])


if __name__ == "__main__":
    unittest.main()
