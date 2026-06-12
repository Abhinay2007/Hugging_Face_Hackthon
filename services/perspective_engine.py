"""Perspective generation service."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from services.llm import get_llm_client, load_prompt


class PerspectiveOutput(BaseModel):
    """Structured output for three conflict perspectives."""

    model_config = ConfigDict(extra="forbid")

    user_view: str = Field(..., min_length=1, max_length=1400)
    other_view: str = Field(..., min_length=1, max_length=1400)
    observer_view: str = Field(..., min_length=1, max_length=1400)


def generate_perspectives(story: str) -> dict[str, str]:
    """Generate user, other-person, and neutral observer perspectives."""
    clean_story = _validate_story(story)
    prompt = load_prompt("perspective.txt").format(story=clean_story)
    perspectives = get_llm_client().generate_validated_json(prompt, PerspectiveOutput, max_new_tokens=650)
    return perspectives.model_dump()


def _validate_story(story: str) -> str:
    """Validate and normalize the user-submitted conflict story."""
    clean_story = " ".join(story.strip().split())
    if not clean_story:
        raise ValueError("Please enter a conflict story first.")
    if len(clean_story) < 20:
        raise ValueError("Please add a little more context so the perspectives can be understood.")
    if len(clean_story) > 4000:
        raise ValueError("Please keep the story under 4,000 characters.")
    return clean_story
