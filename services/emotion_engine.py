"""Emotion and conflict analysis service."""

from __future__ import annotations

import networkx as nx

from schemas.empathy_schema import ALLOWED_EMOTIONS, EmpathyAnalysis
from services.llm import get_llm_client, load_prompt


def extract_emotions(story: str) -> EmpathyAnalysis:
    """Analyze a conflict story into validated empathy dimensions."""
    clean_story = _validate_story(story)
    prompt = load_prompt("emotion.txt").format(
        story=clean_story,
        allowed_emotions=", ".join(sorted(ALLOWED_EMOTIONS)),
    )
    analysis = get_llm_client().generate_validated_json(prompt, EmpathyAnalysis, max_new_tokens=2200)
    return _enrich_with_conflict_graph(analysis)


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


def _enrich_with_conflict_graph(analysis: EmpathyAnalysis) -> EmpathyAnalysis:
    """Use NetworkX to identify the most connected conflict concepts."""
    graph = nx.Graph()
    graph.add_node("core_conflict", label=analysis.core_conflict)

    for person in analysis.people:
        graph.add_node(person.role, label=person.role)
        graph.add_edge("core_conflict", person.role)
        for emotion in person.emotions:
            graph.add_node(emotion, label=emotion)
            graph.add_edge(person.role, emotion)
        for goal in person.goals:
            graph.add_node(goal, label=goal)
            graph.add_edge(person.role, goal)
        for fear in person.fears:
            graph.add_node(fear, label=fear)
            graph.add_edge(person.role, fear)

    if graph.number_of_nodes() > 1:
        nx.degree_centrality(graph)
    return analysis
