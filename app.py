"""Gradio app for Through Their Eyes, an AI-powered empathy simulator."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any

import gradio as gr
from pydantic import ValidationError

from schemas.empathy_schema import EmpathyAnalysis, FutureEcho, HiddenNeed, Misunderstanding, Person
from services.emotion_engine import extract_emotions
from services.llm import LLMError
from services.perspective_engine import generate_perspectives


APP_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = APP_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

EXAMPLES = [
    "My father wants me to become an engineer, but I want to start a business. He says I am risking my future, and I feel like he does not understand what I want.",
    "My teacher thinks I am not trying hard enough because my grades dropped, but I have been overwhelmed and scared to ask for help.",
    "My best friend is upset because I canceled plans twice, but I was exhausted from work and did not know how to explain it without sounding careless.",
    "My partner wants us to spend more time together, but I need quiet time after work. They think I am pulling away, and I feel pressured.",
    "My manager wants me to lead a new project, but I feel overloaded. They see it as a growth opportunity, while I worry I will fail publicly.",
]


def analyze_story(story: str) -> tuple[str, str, str, str, str, str, str, str, str]:
    """Run both analysis engines and return rendered UI fragments."""
    try:
        analysis = extract_emotions(story)
        perspectives = generate_perspectives(story)
        _save_output(story, analysis, perspectives)
        return (
            _core_conflict_html(analysis),
            _perspectives_html(perspectives),
            _misunderstanding_layer_html(analysis.misunderstandings),
            _hidden_needs_html(analysis.hidden_needs),
            _if_you_were_them_html(analysis.if_you_were_them),
            _future_echoes_html(analysis.future_echoes),
            _emotion_bubbles_html(analysis.people),
            _emotional_universe_html(analysis),
            json.dumps(analysis.model_dump(), indent=2, ensure_ascii=False),
        )
    except (ValueError, ValidationError, LLMError, TimeoutError) as exc:
        message = _friendly_error(exc)
        empty_json = json.dumps({"error": message}, indent=2)
        return (_error_html(message), "", "", "", "", "", "", "", empty_json)
    except Exception as exc:  # pragma: no cover - final UI safety net
        message = _friendly_error(exc)
        empty_json = json.dumps({"error": message}, indent=2)
        return (_error_html(message), "", "", "", "", "", "", "", empty_json)


def _save_output(story: str, analysis: EmpathyAnalysis, perspectives: dict[str, str]) -> None:
    """Persist the latest analysis for demos and debugging."""
    payload: dict[str, Any] = {
        "story": story,
        "analysis": analysis.model_dump(),
        "perspectives": perspectives,
    }
    output_path = OUTPUT_DIR / "latest_analysis.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _friendly_error(exc: Exception) -> str:
    """Convert technical failures into user-facing messages."""
    text = str(exc)
    if "timed out" in text.lower() or isinstance(exc, TimeoutError):
        return "The model took too long to respond. Please try again with a shorter story."
    if "could not be validated" in text.lower() or isinstance(exc, ValidationError):
        return "The model response was not valid JSON. Please try again."
    if "hf_token" in text.lower():
        return "Hugging Face API access is not configured. Set HF_TOKEN or use local model mode."
    if text:
        return text
    return "Something went wrong while analyzing the story. Please try again."


def _core_conflict_html(analysis: EmpathyAnalysis) -> str:
    """Render the core conflict section."""
    left, right = _conflict_poles(analysis)
    return f"""
    <section class="mind-reveal core-constellation">
      <div class="core-node" aria-label="Core conflict">
        <span class="node-label">Core Conflict</span>
        <div class="conflict-pair">
          <strong>{html.escape(left)}</strong>
          <span>vs</span>
          <strong>{html.escape(right)}</strong>
        </div>
        <p>{html.escape(analysis.situation)}</p>
      </div>
    </section>
    """


def _conflict_poles(analysis: EmpathyAnalysis) -> tuple[str, str]:
    """Return short cinematic poles for the central conflict node."""
    if len(analysis.hidden_needs) >= 2:
        left = _short_pole(analysis.hidden_needs[0].deep_need)
        right = _short_pole(analysis.hidden_needs[1].deep_need)
        if left and right and left != right:
            return left, right
    return _split_conflict(analysis.core_conflict)


def _perspectives_html(perspectives: dict[str, str]) -> str:
    """Render clickable perspective planets."""
    planet_data = [
        ("you", "YOU", perspectives["user_view"]),
        ("them", "THEM", perspectives["other_view"]),
        ("observer", "OBSERVER", perspectives["observer_view"]),
    ]
    planets = []
    panels = []
    for index, (key, label, text) in enumerate(planet_data):
        active = " active" if index == 0 else ""
        planets.append(
            f"""
            <button class="planet planet-{key}{active}" type="button" data-perspective="{key}">
              <span class="planet-glow"></span>
              <span class="planet-label">{html.escape(label)}</span>
            </button>
            """
        )
        panels.append(
            f"""
            <article class="perspective-panel{active}" data-perspective-panel="{key}">
              <p class="node-label">{html.escape(label)} Perspective</p>
              <p>{html.escape(text)}</p>
            </article>
            """
        )
    return f"""
    <section class="mind-reveal perspective-orbit" aria-label="Perspectives">
      <div class="orbit-ring"></div>
      <div class="planet-field">{''.join(planets)}</div>
      <div class="perspective-panels">{''.join(panels)}</div>
    </section>
    """


def _misunderstanding_layer_html(misunderstandings: list[Misunderstanding]) -> str:
    """Render intention versus interpretation cards."""
    if not misunderstandings:
        return ""

    cards = []
    for item in misunderstandings:
        cards.append(
            f"""
            <button class="misread-card" type="button">
              <div class="misread-side">
                <span class="node-label">What {html.escape(item.speaker)} may mean</span>
                <strong>{html.escape(item.intention)}</strong>
              </div>
              <div class="misread-link" aria-hidden="true"></div>
              <div class="misread-side">
                <span class="node-label">What the other person may hear</span>
                <strong>{html.escape(item.interpretation)}</strong>
              </div>
            </button>
            """
        )
    return f"""
    <section class="mind-reveal misunderstanding-layer" aria-label="Misunderstanding layer">
      <div class="section-heading">
        <p class="node-label">Misunderstanding Layer</p>
        <h2>MISUNDERSTANDING LAYER</h2>
      </div>
      <div class="misread-stack">{''.join(cards)}</div>
    </section>
    """


def _hidden_needs_html(hidden_needs: list[HiddenNeed]) -> str:
    """Render surface positions and deeper needs."""
    if not hidden_needs:
        return ""

    cards = []
    for need in hidden_needs:
        cards.append(
            f"""
            <article class="need-card">
              <span class="node-label">{html.escape(need.person)}</span>
              <strong>{html.escape(need.surface_position)}</strong>
              <i aria-hidden="true"></i>
              <em>{html.escape(need.deep_need)}</em>
            </article>
            """
        )
    return f"""
    <section class="mind-reveal hidden-needs" aria-label="Beneath the argument">
      <div class="section-heading">
        <p class="node-label">Beneath the Argument</p>
        <h2>BENEATH THE ARGUMENT</h2>
      </div>
      <div class="need-grid">{''.join(cards)}</div>
    </section>
    """


def _if_you_were_them_html(narration: str) -> str:
    """Render the embodied perspective narration."""
    if not narration:
        return ""

    return f"""
    <section class="mind-reveal embodied-perspective" aria-label="If you were them">
      <p class="node-label">If You Were Them</p>
      <h2>IF YOU WERE THEM</h2>
      <p>{html.escape(narration)}</p>
    </section>
    """


def _future_echoes_html(future_echoes: list[FutureEcho]) -> str:
    """Render interactive future echo timelines."""
    if not future_echoes:
        return ""

    cards = []
    for index, echo in enumerate(future_echoes):
        active = " active" if index == 1 else ""
        cards.append(
            f"""
            <button class="future-card{active}" type="button">
              <span class="node-label">{html.escape(echo.choice)}</span>
              <strong>{html.escape(echo.response_style)}</strong>
              <div class="future-timeline">
                <p><b>1 Week Later</b>{html.escape(echo.timeline.one_week_later)}</p>
                <p><b>1 Month Later</b>{html.escape(echo.timeline.one_month_later)}</p>
                <p><b>1 Year Later</b>{html.escape(echo.timeline.one_year_later)}</p>
              </div>
            </button>
            """
        )
    return f"""
    <section class="mind-reveal future-echoes" aria-label="Future echoes">
      <div class="section-heading">
        <p class="node-label">Future Echoes</p>
        <h2>FUTURE ECHOES</h2>
      </div>
      <div class="future-grid">{''.join(cards)}</div>
    </section>
    """


def _emotion_bubbles_html(people: list[Person]) -> str:
    """Render emotion bubbles with expandable context."""
    bubbles = []
    for person in people:
        details = _emotion_detail(person)
        for emotion in person.emotions:
            bubbles.append(
                f"""
                <button class="emotion-bubble" type="button">
                  <span>{html.escape(str(emotion).upper())}</span>
                  <small>{html.escape(person.role)}</small>
                  <em>{details}</em>
                </button>
                """
            )
    return f"""
    <section class="mind-reveal emotion-nebula" aria-label="Emotion bubbles">
      <h2>Emotion Field</h2>
      <div class="emotion-cloud">{''.join(bubbles)}</div>
    </section>
    """


def _emotional_universe_html(analysis: EmpathyAnalysis) -> str:
    """Render a React Flow mount point with graph data."""
    graph = _graph_payload(analysis)
    graph_json = html.escape(json.dumps(graph), quote=True)
    return f"""
    <section class="mind-reveal emotional-universe" aria-label="Emotional universe">
      <div class="universe-heading">
        <p class="node-label">Emotional Map</p>
        <h2>EMOTIONAL UNIVERSE</h2>
      </div>
      <div class="universe-shell" data-tte-graph="{graph_json}">
        <div class="react-flow-mount"></div>
        <div class="graph-fallback" aria-hidden="true"></div>
      </div>
    </section>
    """


def _emotion_detail(person: Person) -> str:
    """Build hidden detail text for an emotion bubble."""
    parts = [
        f"Fears: {', '.join(person.fears) or 'unclear'}",
        f"Goals: {', '.join(person.goals) or 'unclear'}",
        f"Assumptions: {', '.join(person.assumptions) or 'unclear'}",
    ]
    return html.escape(" | ".join(parts))


def _split_conflict(core_conflict: str) -> tuple[str, str]:
    """Split a conflict phrase into two visual poles."""
    lowered = core_conflict.lower()
    for separator in [" vs ", " versus ", " v. "]:
        if separator in lowered:
            index = lowered.index(separator)
            left = core_conflict[:index].strip(" :.-")
            right = core_conflict[index + len(separator) :].strip(" :.-")
            return _short_pole(left) or "SELF", _short_pole(right) or "OTHER"
    if ":" in core_conflict:
        before, after = core_conflict.split(":", 1)
        return _short_pole(before), _short_pole(after)
    return _short_pole(core_conflict), "UNDERSTANDING"


def _short_pole(value: str) -> str:
    """Compress one side of a conflict into a short visual label."""
    cleaned = " ".join(value.strip().replace("_", " ").split())
    if not cleaned:
        return ""
    stop_words = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "for",
        "from",
        "in",
        "of",
        "the",
        "their",
        "to",
        "vs",
        "with",
    }
    words = [word for word in cleaned.split() if word.lower() not in stop_words]
    return " ".join(words[:2]).upper()


def _graph_payload(analysis: EmpathyAnalysis) -> dict[str, list[dict[str, Any]]]:
    """Create graph nodes and edges for the emotional universe."""
    nodes: list[dict[str, Any]] = [
        {
            "id": "conflict",
            "label": analysis.core_conflict,
            "kind": "conflict",
            "description": analysis.observer_view,
            "x": 0,
            "y": 0,
        }
    ]
    edges: list[dict[str, Any]] = []
    y_offset = -160
    seen: set[str] = {"conflict"}

    for person_index, person in enumerate(analysis.people):
        person_id = f"person-{person_index}"
        nodes.append(
            {
                "id": person_id,
                "label": person.role,
                "kind": "person",
                "description": _person_summary(person),
                "x": -360 + person_index * 300,
                "y": y_offset,
            }
        )
        edges.append({"id": f"conflict-{person_id}", "source": "conflict", "target": person_id})
        concepts = [
            *[(emotion, _emotion_kind(str(emotion)), person.role, "Emotion") for emotion in person.emotions],
            *[(goal, "goal", person.role, "Goal") for goal in person.goals[:2]],
            *[(fear, "fear", person.role, "Fear") for fear in person.fears[:2]],
            *[(assumption, "assumption", person.role, "Assumption") for assumption in person.assumptions[:2]],
        ]
        for concept_index, (label, kind, owner, category) in enumerate(concepts):
            node_id = f"{person_id}-{kind}-{concept_index}"
            if node_id in seen:
                continue
            seen.add(node_id)
            nodes.append(
                {
                    "id": node_id,
                    "label": str(label),
                    "kind": kind,
                    "category": category,
                    "description": f"{owner} - {category.lower()}: {label}",
                    "x": -460 + person_index * 320 + (concept_index % 2) * 180,
                    "y": 70 + concept_index * 70,
                }
            )
            edges.append({"id": f"{person_id}-{node_id}", "source": person_id, "target": node_id})
    return {"nodes": nodes, "edges": edges}


def _person_summary(person: Person) -> str:
    """Build graph panel text for a person node."""
    parts = [
        f"Emotions: {', '.join(person.emotions) or 'unclear'}",
        f"Fears: {', '.join(person.fears) or 'unclear'}",
        f"Goals: {', '.join(person.goals) or 'unclear'}",
        f"Assumptions: {', '.join(person.assumptions) or 'unclear'}",
    ]
    return " | ".join(parts)


def _emotion_kind(emotion: str) -> str:
    """Map emotions to visual node categories."""
    if emotion == "hope":
        return "hope"
    if emotion in {"anger", "frustration"}:
        return "anger"
    if emotion in {"love", "joy"}:
        return "love"
    if emotion in {"fear", "anxiety", "worry", "shame", "guilt", "sadness", "confusion"}:
        return "fear"
    return "emotion"


def _error_html(message: str) -> str:
    """Render a visible error state."""
    return f"""
    <section class="mind-reveal error-card">
      <p class="node-label">Could not enter the memory</p>
      <h2>{html.escape(message)}</h2>
    </section>
    """


def build_app() -> gr.Blocks:
    """Create the Gradio Blocks interface."""
    css_path = APP_DIR / "static" / "style.css"
    js_path = APP_DIR / "static" / "app.js"
    custom_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    custom_js = js_path.read_text(encoding="utf-8") if js_path.exists() else ""
    custom_head = f"<script>{custom_js}</script>" if custom_js else ""

    with gr.Blocks(css=custom_css, head=custom_head, title="Through Their Eyes", theme=gr.themes.Base()) as demo:
        gr.HTML(
            """
            <div class="cosmic-stage" aria-hidden="true">
              <div class="star-field"></div>
              <div class="light-beam beam-one"></div>
              <div class="light-beam beam-two"></div>
              <div class="floating-orb orb-one"></div>
              <div class="floating-orb orb-two"></div>
              <div class="floating-orb orb-three"></div>
            </div>
            <header class="mind-landing">
              <p class="node-label">Explore another person's mind</p>
              <h1>THROUGH THEIR EYES</h1>
              <p class="subtitle">Every conflict has<br>your story,<br>their story,<br>and the story in between.</p>
            </header>
            """
        )

        with gr.Group(elem_classes=["memory-capsule"]):
            story = gr.Textbox(
                label="Memory Capsule",
                placeholder="Describe a moment you wish someone understood.",
                lines=8,
                max_lines=14,
                elem_classes=["story-box"],
            )

        analyze = gr.Button("ENTER THEIR WORLD", elem_classes=["analyze-button"], variant="primary")

        gr.Examples(
            examples=[[example] for example in EXAMPLES],
            inputs=story,
            label="Memory fragments",
            examples_per_page=5,
        )

        gr.HTML(
            """
            <section id="journey-status" class="journey-status" aria-live="polite">
              <span>Analyzing emotions...</span>
              <span>Understanding perspectives...</span>
              <span>Building emotional map...</span>
            </section>
            """
        )

        core_conflict = gr.HTML()
        perspectives = gr.HTML()
        misunderstanding_layer = gr.HTML()
        hidden_needs = gr.HTML()
        embodied_perspective = gr.HTML()
        future_echoes = gr.HTML()
        emotion_cards = gr.HTML()
        emotional_universe = gr.HTML()

        with gr.Accordion("Developer Mode", open=False):
            raw_json = gr.Code(language="json", label="Validated output")

        analyze.click(
            analyze_story,
            inputs=story,
            outputs=[
                core_conflict,
                perspectives,
                misunderstanding_layer,
                hidden_needs,
                embodied_perspective,
                future_echoes,
                emotion_cards,
                emotional_universe,
                raw_json,
            ],
        )

    return demo


if __name__ == "__main__":
    preferred_port = int(
        os.getenv("GRADIO_SERVER_PORT")
        or os.getenv("PORT", "7860")
    )

    app = build_app()

    for port in range(preferred_port, preferred_port + 10):
        try:
            app.launch(
                server_name="0.0.0.0",
                server_port=port,
                ssr_mode=False
            )
            break

        except OSError as exc:
            if "Cannot find empty port" not in str(exc) or port == preferred_port + 9:
                raise

            print(f"Port {port} is busy. Trying {port + 1}...")
