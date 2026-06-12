# Through Their Eyes - Emotional Intelligence Features

## Overview

**Through Their Eyes** is an AI-powered empathy simulator that transforms conflict analysis into an emotional understanding experience. Instead of reading an AI report, users walk through another person's emotional world.

The app answers the core question: **"Oh wow... I never thought they might see it that way."**

---

## Feature 1: Misunderstanding Engine

### What It Does
Reveals the gap between what one person means and what the other person hears.

### Example
**Father means:** "I want you to be safe."
**Child hears:** "You don't trust me."

### Why It Matters
Most conflicts aren't about disagreement—they're about misinterpretation. This layer exposes the invisible gap where understanding breaks down.

### Interactive Design
- **Left side:** What they mean underneath their words
- **Right side:** What the other person may hear
- **Animated connection line:** Shows the flow of misunderstanding
- **Click to expand:** Tap any card to explore deeper

---

## Feature 2: Hidden Needs Engine

### What It Does
Maps surface positions to the deep emotional needs beneath them.

### Example
**Father's surface position:** "Become an engineer"
**Father's deep need:** Security

**Child's surface position:** "Start a business"
**Child's deep need:** Freedom

### Why It Matters
People argue about positions, but conflicts are really about unmet needs. This layer reveals what each person actually needs—not what they're saying they want.

### Visual Design
- **BENEATH THE ARGUMENT** section
- **Position → Need** flow
- Large typography for emotional clarity
- Minimal, cinematic presentation

---

## Feature 3: Core Conflict Compression

### What It Does
Converts conflicts into archetypal emotional oppositions.

### Examples
- Security vs Freedom
- Stability vs Independence
- Control vs Trust
- Recognition vs Respect
- Belonging vs Authenticity

### Why It Matters
Instead of long conflict descriptions, this shows the emotional core at a glance. It's the DNA of the conflict.

### Visual Design
- **Center screen** with large typography
- Two opposing concepts
- Glowing, minimal presentation
- Serves as the thematic anchor for the entire analysis

---

## Feature 4: Future Echoes

### What It Does
Generates 3 possible futures based on different response styles:

1. **Choice A: Respond Defensively**
2. **Choice B: Respond with Curiosity**
3. **Choice C: Respond with Empathy**

For each choice, shows emotional consequences at:
- 1 Week Later
- 1 Month Later
- 1 Year Later

### Why It Matters
Users can see the long-term impact of different choices. Empathy isn't abstract—it has real consequences over time.

### Interactive Design
- **Click a card** to select a response path
- **Timeline expands** with emotional progression
- **Smooth animations** reveal future scenarios
- Magic moment: seeing how empathy compounds over time

---

## Feature 5: Emotional Universe (Constellation Map)

### What It Does
Transforms raw emotional data into a visual constellation network.

### Node Types and Colors
- **Emotion nodes:** Core feelings (cyan)
- **Fear nodes:** What they're afraid of (purple)
- **Hope nodes:** What they're hopeful about (cyan)
- **Anger nodes:** Frustration and rage (orange)
- **Love nodes:** Care and connection (pink)
- **Goal nodes:** What they're pursuing (green)
- **Assumption nodes:** Beliefs they hold (yellow)
- **Core conflict:** Central node (cyan glow)

### Why It Matters
Instead of a technical graph, this feels like exploring another person's emotional landscape. It's beautiful, interactive, and human.

### Interactive Features
- **Drag nodes** to explore
- **Pan and zoom** to navigate
- **Hover** to see connections
- **Visual hierarchy** shows what matters most
- **Glowing particles** create a constellation feel

---

## Feature 6: Judge Wow Moment - "If You Were Them"

### What It Does
Generates a 150-word vivid narration from the other person's perspective.

### Example
"You wake up tomorrow as them. The first thing you feel is the weight of expectations—not just from your father, but from yourself. You realize you've been interpreting his safety concerns as doubt in your abilities. You wish he knew that you're not rejecting his wisdom; you're trying to find your own way using what he taught you."

### Why It Matters
This is the empathy climax. Not academic understanding, but emotional recognition. It creates the "oh wow" moment.

### Tone Guidelines
- No therapy language
- No moral judgment
- No advice
- Pure emotional truth
- Second-person narration
- Maximum 150 words

---

## Feature 7: Developer Mode

### What It Does
Hides structured JSON output in a collapsed accordion.

### Why It Matters
Judges see the empathy experience first—the beautiful insights, the wow moments. Technical implementation details are available but not the default view.

### Access
Users can expand the "Developer Mode" accordion to see:
- Raw JSON output
- Validated data structures
- Implementation details

---

## The Empathy Journey

Users experience the app as a journey through another person's emotional world:

1. **Core Conflict** → Understand the central tension
2. **Misunderstandings** → See where communication breaks down
3. **Hidden Needs** → Discover what really matters
4. **Perspective Orbit** → Experience their emotional landscape
5. **Emotion Field** → Feel the emotional weather
6. **Future Echoes** → See long-term consequences
7. **Emotional Universe** → Explore the full emotional constellation
8. **If You Were Them** → The wow moment of recognition

---

## Architecture

### Backend Services
- **LLM Service** (`services/llm.py`): Model selection, generation, retries, JSON validation
- **Emotion Engine** (`services/emotion_engine.py`): Conflict analysis and emotion extraction
- **Perspective Engine** (`services/perspective_engine.py`): Multi-perspective generation

### Data Schemas
- **Person** - Conflict participant with emotions, fears, goals, assumptions
- **Misunderstanding** - Speaker intention vs interpretation gap
- **HiddenNeed** - Surface position vs deep need
- **FutureEcho** - Timeline for a response style
- **EmpathyAnalysis** - Complete structured output

### Frontend
- **Style** (`static/style.css`): Cosmic dark theme with glowing accents
- **Interactivity** (`static/app.js`): Cards, planets, bubbles, graph interactions
- **Gradio Interface** (`app.py`): Responsive layout with developer mode

---

## Key Design Principles

### 1. Empathy First
The UI prioritizes emotional understanding over technical accuracy.

### 2. Beautiful by Default
Cosmic dark theme, glowing accents, smooth animations.

### 3. Interactive Discovery
Click, expand, explore—don't just read.

### 4. Non-Judgmental
No advice, no diagnosis, no moral positioning.

### 5. Perspective-Neutral
Every view is equally valid and explored.

### 6. Minimal Text, Maximum Impact
Large typography, whitespace, focus on emotions.

---

## Prompts and Validation

The `prompts/emotion.txt` prompt ensures:
- Fixed emotion vocabulary (no invented words)
- Structured output validation with Pydantic
- Clear rules for each analysis layer
- Quality constraints (word limits, field requirements)
- No therapy language or advice

---

## Running the App

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
export HF_TOKEN="your_token"
python3 app.py

# Access
http://localhost:7860
```

---

## What Makes This Different

Traditional conflict analysis apps:
- Show data → User reads report
- Neutral and clinical
- Bottom-up (facts → emotions)

**Through Their Eyes:**
- Experience emotion → User feels understanding
- Beautiful and human
- Top-down (emotions → insights)

The goal isn't to be right. It's to **understand**.
