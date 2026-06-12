"""Pydantic schemas for structured empathy analysis."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Emotion = Literal[
    "fear",
    "anger",
    "sadness",
    "guilt",
    "shame",
    "hope",
    "joy",
    "anxiety",
    "frustration",
    "confusion",
    "love",
    "worry",
]

ALLOWED_EMOTIONS: set[str] = set(Emotion.__args__)


class Person(BaseModel):
    """A conflict participant and their inferred perspective drivers."""

    model_config = ConfigDict(extra="forbid")

    role: str = Field(..., min_length=1, max_length=80)
    emotions: list[Emotion] = Field(default_factory=list, max_length=6)
    fears: list[str] = Field(default_factory=list, max_length=8)
    goals: list[str] = Field(default_factory=list, max_length=8)
    assumptions: list[str] = Field(default_factory=list, max_length=8)

    @field_validator("role")
    @classmethod
    def clean_role(cls, value: str) -> str:
        """Normalize whitespace in participant roles."""
        return " ".join(value.strip().split())

    @field_validator("fears", "goals", "assumptions")
    @classmethod
    def clean_string_list(cls, values: list[str]) -> list[str]:
        """Remove empty entries and normalize whitespace."""
        cleaned: list[str] = []
        for value in values:
            normalized = " ".join(str(value).strip().split())
            if normalized and normalized not in cleaned:
                cleaned.append(normalized)
        return cleaned

    @field_validator("emotions")
    @classmethod
    def deduplicate_emotions(cls, values: list[Emotion]) -> list[Emotion]:
        """Preserve emotion order while removing duplicates."""
        return list(dict.fromkeys(values))


class Misunderstanding(BaseModel):
    """What one person intends versus what the other person may hear."""

    model_config = ConfigDict(extra="forbid")

    speaker: str = Field(..., min_length=1, max_length=80)
    intention: str = Field(..., min_length=1, max_length=220)
    interpretation: str = Field(..., min_length=1, max_length=220)


class HiddenNeed(BaseModel):
    """A surface position mapped to the deeper need beneath it."""

    model_config = ConfigDict(extra="forbid")

    person: str = Field(..., min_length=1, max_length=80)
    surface_position: str = Field(..., min_length=1, max_length=180)
    deep_need: str = Field(..., min_length=1, max_length=80)


class FutureTimeline(BaseModel):
    """A short future timeline for one possible response pattern."""

    model_config = ConfigDict(extra="forbid")

    one_week_later: str = Field(..., min_length=1, max_length=280)
    one_month_later: str = Field(..., min_length=1, max_length=280)
    one_year_later: str = Field(..., min_length=1, max_length=280)


class FutureEcho(BaseModel):
    """A possible response path and its emotional echoes over time."""

    model_config = ConfigDict(extra="forbid")

    choice: str = Field(..., min_length=1, max_length=40)
    response_style: str = Field(..., min_length=1, max_length=80)
    timeline: FutureTimeline


class EmpathyAnalysis(BaseModel):
    """Validated JSON-only output for the empathy simulator."""

    model_config = ConfigDict(extra="forbid")

    situation: str = Field(..., min_length=1, max_length=160)
    people: list[Person] = Field(..., min_length=1, max_length=4)
    observer_view: str = Field(..., min_length=1, max_length=1200)
    core_conflict: str = Field(..., min_length=1, max_length=180)
    misunderstandings: list[Misunderstanding] = Field(default_factory=list, max_length=8)
    hidden_needs: list[HiddenNeed] = Field(default_factory=list, max_length=6)
    future_echoes: list[FutureEcho] = Field(default_factory=list, max_length=3)
    if_you_were_them: str = Field(default="", max_length=900)

    @field_validator("situation", "observer_view", "core_conflict", "if_you_were_them")
    @classmethod
    def clean_text(cls, value: str) -> str:
        """Normalize whitespace in top-level text fields."""
        return " ".join(value.strip().split())
