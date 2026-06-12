# Through Their Eyes - Implementation Guide

## What Was Added

### 1. Enhanced Visual Design

#### CSS Enhancements (`static/style.css`)
- **Glowing connection lines** for misunderstanding cards with pulse animation
- **Interactive card animations** for smooth expand/collapse
- **Gradient backgrounds** that activate on hover
- **Timeline reveal animation** for future echoes
- **Constellation styling** for emotional universe nodes
- **Color-coded nodes**: Purple (fear), Cyan (hope), Orange (anger), Pink (love), Green (goal), Yellow (assumption)

#### Key Animations Added
```css
@keyframes glowPulse - Continuous glow on connection points
@keyframes cardExpand - Smooth card expansion
@keyframes timelineReveal - Timeline content reveal
```

### 2. Interactive Features

#### JavaScript Enhancements (`static/app.js`)

**New Wire Functions:**

1. **`wireMisunderstandingCards()`**
   - Makes each misunderstanding card clickable
   - Toggles `is-open` class for expansion
   - Triggers reveal animation on click

2. **`wireFutureEchoes()`**
   - Makes future echo cards clickable
   - Manages active state across cards
   - Expands timeline content with animation
   - Ensures only one future path is selected at a time

**Updated Functions:**
- `enhance()` - Now calls the new wire functions
- All interactive elements are properly chained during DOM mutations

### 3. Data Structure (Already Complete)

#### Pydantic Schemas (`schemas/empathy_schema.py`)

All required data structures are already defined:

```python
class Misunderstanding(BaseModel):
    speaker: str              # Who is speaking
    intention: str            # What they mean underneath
    interpretation: str       # What other person hears

class HiddenNeed(BaseModel):
    person: str              # Who has the need
    surface_position: str    # What they're asking for
    deep_need: str          # What they actually need

class FutureEcho(BaseModel):
    choice: str              # "Choice A", "Choice B", "Choice C"
    response_style: str      # "Defensive", "Curious", "Empathic"
    timeline: FutureTimeline # 1 week, 1 month, 1 year

class EmpathyAnalysis(BaseModel):
    situation: str
    core_conflict: str              # "Need vs Need" format
    people: list[Person]
    observer_view: str
    misunderstandings: list[Misunderstanding]
    hidden_needs: list[HiddenNeed]
    future_echoes: list[FutureEcho]
    if_you_were_them: str          # 150-word narration
```

### 4. HTML Rendering (`app.py`)

All rendering functions already exist:

- `_core_conflict_html()` - Central conflict with archetype display
- `_perspectives_html()` - Clickable perspective planets
- `_misunderstanding_layer_html()` - Intention vs interpretation cards
- `_hidden_needs_html()` - Surface position vs deep need cards
- `_if_you_were_them_html()` - Empathy narration section
- `_future_echoes_html()` - Interactive timeline cards
- `_emotion_bubbles_html()` - Expandable emotion bubbles
- `_emotional_universe_html()` - React Flow graph with fallback
- `_emotion_kind()` - Color mapping for node types
- `_graph_payload()` - Graph data from conflict analysis

### 5. LLM Prompting (`prompts/emotion.txt`)

Comprehensive prompt already includes:

✅ Misunderstanding generation with clear guidelines
✅ Hidden needs extraction with human need vocabulary
✅ Core conflict compression into archetypes
✅ Future echoes for 3 response styles (defensive, curious, empathic)
✅ "If you were them" narration (max 150 words)
✅ Fixed emotion vocabulary (no invented words)
✅ Quality constraints and field limits
✅ Non-judgmental language requirements

### 6. Developer Mode

Already implemented in `app.py` build_app() function:

```python
with gr.Accordion("Developer Mode", open=False):
    raw_json = gr.Code(language="json", label="Validated output")
```

The JSON output is hidden by default and only shown when the accordion is expanded.

---

## How It All Works Together

### User Journey

1. **User enters story**
   ```
   "My father wants me to be an engineer, but I want to start a business..."
   ```

2. **Backend Analysis**
   - Emotion engine extracts: core conflict, people, emotions, fears, goals, assumptions
   - LLM generates: misunderstandings, hidden needs, future echoes, empathy narration
   - Perspective engine creates: user view, other view, observer view

3. **Frontend Rendering**
   ```
   analyze_story() returns 9 outputs:
   1. Core conflict (central tension)
   2. Perspectives (clickable planets)
   3. Misunderstandings (intention vs interpretation)
   4. Hidden needs (position vs need)
   5. If you were them (empathy narration)
   6. Future echoes (3 timelines)
   7. Emotion bubbles (expandable feelings)
   8. Emotional universe (interactive graph)
   9. Raw JSON (developer mode)
   ```

4. **User Interaction**
   - Reads core conflict
   - Clicks misunderstanding cards (they expand with animation)
   - Sees hidden needs beneath surface positions
   - Reads empathy narration (wow moment)
   - Clicks future echo cards to explore timelines
   - Explores emotional universe graph
   - Expands developer mode if interested in technical details

### Data Flow

```
User Story
    ↓
extract_emotions()
    ↓
EmpathyAnalysis (validated Pydantic)
    ├─ situation
    ├─ core_conflict (archetype)
    ├─ people (with emotions, fears, goals, assumptions)
    ├─ misunderstandings[]
    ├─ hidden_needs[]
    ├─ future_echoes[]
    └─ if_you_were_them
    ↓
HTML Rendering Functions
    ├─ _core_conflict_html()
    ├─ _misunderstanding_layer_html()
    ├─ _hidden_needs_html()
    ├─ _if_you_were_them_html()
    ├─ _future_echoes_html()
    ├─ _emotion_bubbles_html()
    ├─ _emotional_universe_html()
    └─ JSON dump (Developer Mode)
    ↓
Frontend Display + JavaScript Interactivity
```

---

## Quality Assurance

### Schema Validation
- All outputs validated with Pydantic before rendering
- Fixed emotion vocabulary prevents hallucinations
- Field length limits ensure readability
- Required fields are always present

### Error Handling
- Friendly error messages for user
- Technical errors logged
- Timeout handling with user-friendly feedback
- JSON validation ensures structure

### Responsive Design
- Mobile-first CSS with media queries
- Breakpoints at 760px for tablet/mobile
- Cards stack vertically on mobile
- Universe graph resizes based on viewport

---

## Performance Considerations

### Frontend
- CSS animations use GPU acceleration
- No JavaScript libraries required except React Flow (optional)
- Lazy loading of React Flow libraries
- Fallback SVG graph if React Flow fails

### Backend
- LLM calls are cached in output directory
- Retries with exponential backoff
- JSON parsing with error recovery
- Network timeout of 90 seconds

---

## Testing the Implementation

### Quick Test
```bash
# Start the app
python3 app.py

# Use example stories
"My father wants me to become an engineer, but I want to start a business."

# Verify all sections render:
1. Core Conflict shows archetype (e.g., "Security vs Freedom")
2. Misunderstanding cards are clickable
3. Hidden needs show position → need flow
4. Future echoes let you click between 3 choices
5. Emotional universe graph renders or falls back to SVG
6. Developer mode accordion is collapsed by default
```

### Interactive Testing
- Click misunderstanding cards → they should expand smoothly
- Click future echo cards → timeline should reveal
- Explore emotional universe → should be draggable
- Expand developer mode → should show formatted JSON

---

## Files Modified

### Backend
- ✅ `schemas/empathy_schema.py` - Data structures (complete)
- ✅ `services/emotion_engine.py` - Emotion extraction (complete)
- ✅ `services/llm.py` - LLM integration (complete)
- ✅ `prompts/emotion.txt` - LLM prompt (complete)
- ✅ `app.py` - Gradio interface (enhanced)

### Frontend
- ✅ `static/style.css` - Visual design (enhanced)
- ✅ `static/app.js` - Interactivity (enhanced)

### Documentation
- ✅ `FEATURES.md` - Feature overview (created)
- ✅ `IMPLEMENTATION.md` - This file (created)

---

## Future Enhancements (Ideas)

1. **Voice Mode** - Read narrations aloud
2. **Comparison View** - Side-by-side person perspectives
3. **History** - Save and revisit previous analyses
4. **Sharing** - Share specific analyses (anonymized)
5. **Custom Archetypes** - User-defined conflict types
6. **Multi-language** - Analyze conflicts in any language
7. **Integration** - Embed in therapy/mediation apps

---

## Troubleshooting

### Misunderstanding cards don't expand
- Check browser console for JavaScript errors
- Verify CSS classes are applied correctly
- Test with fresh page reload

### Future echoes don't show timeline
- Ensure the timeline div has `future-timeline` class
- Check that Future Echo data is generated in LLM output
- Verify animation CSS includes `timelineReveal`

### Emotional universe doesn't render
- React Flow libraries may fail to load
- Check browser console for CDN errors
- SVG fallback should activate automatically

### JSON output is invalid
- LLM may not follow prompt structure
- Check retries are happening (retry count in error)
- Verify model supports JSON mode

---

## Code Quality Notes

### Best Practices Implemented
- ✅ Type hints on all functions
- ✅ HTML escaping prevents XSS
- ✅ Pydantic validation ensures data integrity
- ✅ Error handling with user-friendly messages
- ✅ CSS uses CSS variables for theming
- ✅ JavaScript uses event delegation
- ✅ Responsive design with mobile-first approach

### Security Considerations
- ✅ All HTML properly escaped with `html.escape()`
- ✅ JSON safely embedded with `html.escape(json.dumps())`
- ✅ No eval() or dynamic code execution
- ✅ Third-party scripts from CDN with SRI hashes recommended

---

## Deployment

### Local Development
```bash
export HF_TOKEN="your_token"
python3 app.py
```

### Production (Gradio Cloud or Similar)
- Set HF_TOKEN environment variable
- Set LLM_PROVIDER to "hf_api"
- Set MODEL_ID to "Qwen/Qwen3-8B"
- Scale inference timeout for large stories

### Docker (Optional)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV HF_TOKEN="set_in_environment"
CMD ["python3", "app.py"]
```

---

## Contact & Support

For questions about the implementation:
- Check FEATURES.md for feature documentation
- Review prompts/emotion.txt for LLM behavior
- Check schemas/empathy_schema.py for data structure
- Review app.py for rendering logic
- Check static/style.css for visual design
- Review static/app.js for JavaScript interactions
