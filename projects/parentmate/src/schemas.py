from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(
        default=None,
        description="Short event or action title taken directly from the email.",
    )
    event_type: Optional[str] = Field(
        default=None,
        description="Category such as meeting, deadline, trip, payment, reminder, or volunteer request.",
    )
    event_status: Literal["scheduled", "cancelled", "rescheduled"] = Field(
        default="scheduled",
        description="Whether the event is scheduled, cancelled, or rescheduled.",
    )
    date: Optional[str] = Field(
        default=None,
        description="Date string exactly as known from the email.",
    )
    start_time: Optional[str] = Field(
        default=None,
        description="Event start time if stated.",
    )
    end_time: Optional[str] = Field(
        default=None,
        description="Event end time if stated.",
    )
    location: Optional[str] = Field(
        default=None,
        description="Where the event happens.",
    )
    child_specific: Optional[bool] = Field(
        default=None,
        description="Whether the event applies to a specific child, grade, class, or group.",
    )
    action_required: Optional[bool] = Field(
        default=None,
        description="Whether a parent or student must do something.",
    )
    deadline: Optional[str] = Field(
        default=None,
        description="Deadline for a required action.",
    )
    items_needed: Optional[List[str]] = Field(
        default=None,
        description="Items parents or children need to bring, submit, or prepare.",
    )
    cost: Optional[str] = Field(
        default=None,
        description="Cost or fee if stated.",
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Model confidence from 0 to 1.",
    )


class EmailExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    school_name: Optional[str] = Field(
        default=None,
        description="Name of the school or sender organization if present.",
    )
    email_subject: Optional[str] = Field(
        default=None,
        description="Original email subject.",
    )
    events: List[Event] = Field(
        default_factory=list,
        description="All extracted school events and parent actions.",
    )
