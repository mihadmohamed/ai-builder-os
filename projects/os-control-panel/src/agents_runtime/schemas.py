from typing import Literal

from pydantic import BaseModel


class WorkflowReviewOutput(BaseModel):
    recommended_role: Literal[
        "Product Director",
        "PM",
        "Experience Designer",
        "UI Designer",
        "Architect",
        "Engineer",
        "QA",
        "None",
    ]
    recommended_action: str
    rationale: str
    agrees_with_deterministic: bool
    uncertainty: str = ""
