from __future__ import annotations

import unittest

from projects.parentmate.src.extractor import extract_email_from_payload


class ExtractorDeterministicTests(unittest.TestCase):
    def test_normalizes_pound_symbol_cost(self) -> None:
        result = extract_email_from_payload(
            email_subject="Breakfast Club confirmation",
            email_body="This session costs £4.50.",
            payload={
                "school_name": None,
                "email_subject": "Breakfast Club confirmation",
                "events": [
                    {
                        "title": "Breakfast Club",
                        "event_type": "club",
                        "event_status": "scheduled",
                        "date": "5 May 2026",
                        "start_time": "7:45 AM",
                        "end_time": "8:45 AM",
                        "location": "school hall",
                        "child_specific": False,
                        "action_required": False,
                        "deadline": None,
                        "items_needed": None,
                        "cost": "£4.50",
                        "confidence": 1.0,
                    }
                ],
            },
        )

        self.assertEqual(result.events[0].cost, "GBP 4.50")
        self.assertEqual(result.events[0].date, "2026-05-05")
        self.assertEqual(result.events[0].start_time, "07:45")
        self.assertEqual(result.events[0].end_time, "08:45")

    def test_infers_rescheduled_status_from_email_language(self) -> None:
        result = extract_email_from_payload(
            email_subject="Change to swimming lesson",
            email_body="The Year 2 swimming lesson has been moved to 25 June 2026 at 11:00.",
            payload={
                "school_name": None,
                "email_subject": "Change to swimming lesson",
                "events": [
                    {
                        "title": "Year 2 swimming lesson",
                        "event_type": "swimming lesson",
                        "event_status": "scheduled",
                        "date": "25 June 2026",
                        "start_time": "11:00",
                        "end_time": None,
                        "location": None,
                        "child_specific": True,
                        "action_required": False,
                        "deadline": None,
                        "items_needed": None,
                        "cost": None,
                        "confidence": 0.9,
                    }
                ],
            },
        )

        self.assertEqual(result.events[0].event_status, "rescheduled")
        self.assertEqual(result.events[0].event_type, "lesson")

    def test_merges_payment_admin_event_into_primary_event(self) -> None:
        result = extract_email_from_payload(
            email_subject="Choir trip payment",
            email_body="Please pay GBP 8 by 1 June 2026 for the choir trip.",
            payload={
                "school_name": None,
                "email_subject": "Choir trip payment",
                "events": [
                    {
                        "title": "Choir performance at the town hall",
                        "event_type": "trip",
                        "event_status": "scheduled",
                        "date": "12 June 2026",
                        "start_time": None,
                        "end_time": None,
                        "location": "town hall",
                        "child_specific": True,
                        "action_required": False,
                        "deadline": None,
                        "items_needed": None,
                        "cost": None,
                        "confidence": 0.95,
                    },
                    {
                        "title": "Trip payment",
                        "event_type": "payment",
                        "event_status": "scheduled",
                        "date": None,
                        "start_time": None,
                        "end_time": None,
                        "location": None,
                        "child_specific": True,
                        "action_required": True,
                        "deadline": "1 June 2026",
                        "items_needed": None,
                        "cost": "GBP 8",
                        "confidence": 0.9,
                    },
                ],
            },
        )

        self.assertEqual(len(result.events), 1)
        event = result.events[0]
        self.assertEqual(event.title, "Choir performance at the town hall")
        self.assertEqual(event.cost, "GBP 8")
        self.assertEqual(event.deadline, "2026-06-01")
        self.assertTrue(event.action_required)

    def test_filters_payment_phrases_from_items_needed(self) -> None:
        result = extract_email_from_payload(
            email_subject="Drama club fee",
            email_body="Please pay GBP 15 before the first session.",
            payload={
                "school_name": None,
                "email_subject": "Drama club fee",
                "events": [
                    {
                        "title": "Drama club start",
                        "event_type": "club",
                        "event_status": "scheduled",
                        "date": "9 September 2026",
                        "start_time": None,
                        "end_time": None,
                        "location": "hall",
                        "child_specific": False,
                        "action_required": True,
                        "deadline": None,
                        "items_needed": ["deposit payment", "water bottle"],
                        "cost": "15",
                        "confidence": 0.9,
                    }
                ],
            },
        )

        event = result.events[0]
        self.assertEqual(event.items_needed, ["water bottle"])
        self.assertEqual(event.cost, "GBP 15")


if __name__ == "__main__":
    unittest.main()
