from __future__ import annotations

import json

from projects.parentmate.src.schemas import EmailExtraction


EXTRACTION_SYSTEM_PROMPT = """
You extract school events and parent actions from school emails.

Return JSON only.
Do not wrap the JSON in markdown.
Do not include explanations or extra keys.
Never invent data.
Use null for any unknown scalar value.
Use null for items_needed when the email does not mention any items.
Only extract concrete school-related events or concrete parent/student actions.
Extract real-world school events.
Rules:
- Each real-world activity must be represented as ONE event.
- Do NOT create separate events for administrative tasks such as payments, deadlines, or permission slips.
- Attach all related actions (payments, deadlines, items needed) to the same event.
- Only create multiple events if there are clearly separate activities.
- Required payments and deposits must stay attached to the main event, even when the email mentions them separately.
- Optional donations, suggested contributions, and voluntary contributions must NOT become separate events; attach them to the related main event only.
Set event_status to "scheduled" by default.
Use event_status "cancelled" only when the email explicitly says the event is cancelled/canceled.
Use event_status "rescheduled" when the email explicitly says the event has moved, changed date/time, been postponed, or been rescheduled.
When an event is cancelled or rescheduled, still extract the event if the email provides a concrete event or action.
Do NOT include payments or money values in items_needed.
Cost must be stored only in the cost field.
If text says bring, pay, send, donate, or contribute money, store the money amount in cost and never in items_needed.
If payment is explicitly required, set action_required to true even when no payment deadline is given.
If payment is optional, voluntary, suggested, or only "appreciated", do not set action_required to true unless the email clearly requires payment.
Concrete parent/student actions with deadlines must be extracted even when there is no activity date.
For deadline-only actions, use event_type "deadline", put the due date in deadline, and leave date null.
Only create a deadline-only event when there is no related real-world activity in the same email.
If a deadline is for booking, paying for, consenting to, or preparing for a real-world activity, attach that deadline and action_required to the real-world activity instead.
If the email mentions vague future information without a concrete date, deadline, action, or activity, do not extract an event.
If the email contains no concrete events or actions, return an empty events array.
If the email subject is empty, set email_subject to null.
Set email_subject to the exact subject provided when it is not empty.
Extract school_name only when it is explicitly stated in the subject, body, sender/signature, or letterhead.
Do not infer school_name from generic references to school, class, pupils, or parents.
Normalise absolute dates to YYYY-MM-DD when possible.
Normalise times to HH:MM in 24-hour format when possible.
If a date or time cannot be confidently normalised, preserve the original string.
Set child_specific to true if the event applies to a specific group (e.g. Year 4, a class, or a named child).
Set child_specific to false if the event applies to all students or parents.
Words like children, pupils, students, parents, or families without a year group, class, team, or named child mean child_specific is false.
Set action_required to true only when the email clearly asks for a parent or student action.
Set action_required to false when the email describes an event but does not ask for an action.
Include permission slips, consent forms, and forms in items_needed when the email asks for them to be returned, submitted, or brought.
Requests to bring or wear specific clothing or equipment count as action_required true and should be listed in items_needed.
Confidence must be a number between 0 and 1.
""".strip()


def build_extraction_user_prompt(email_subject: str, email_body: str) -> str:
    schema = EmailExtraction.model_json_schema()
    return f"""
Extract structured school events and parent actions from the email below.

Output must be valid JSON matching this schema:
{json.dumps(schema, indent=2)}

EMAIL SUBJECT:
{email_subject.strip() or "(empty subject)"}

EMAIL BODY:
{email_body.strip()}
""".strip()
