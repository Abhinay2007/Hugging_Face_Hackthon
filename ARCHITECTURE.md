# Through Their Eyes - Technical Architecture & Improvements

## System Architecture

### High-Level Flow

```
User Input (Story)
        ↓
    Validation
    (20-4000 chars)
        ↓
    ┌─────────────────────────────────┐
    │  Parallel Processing            │
    ├─────────────────────────────────┤
    │  1. extract_emotions()          │
    │     → LLM call with prompt      │
    │     → Pydantic validation       │
    │     → NetworkX graph building   │
    │                                 │
    │  2. generate_perspectives()     │
    │     → LLM call with prompt      │
    │     → Pydantic validation       │
    │     → Format perspectives       │
    └─────────────────────────────────┘
        ↓
    ┌─────────────────────────────────┐
    │  Data Combination               │
    │  (analysis + perspectives)      │
    └─────────────────────────────────┘
        ↓
    ┌─────────────────────────────────┐
    │  HTML Rendering (9 outputs)     │
    ├─────────────────────────────────┤
    │  1. _core_conflict_html()       │
    │  2. _perspectives_html()        │
    │  3. _misunderstanding_layer()   │
    │  4. _hidden_needs_html()        │
    │  5. _if_you_were_them_html()    │
    │  6. _future_echoes_html()       │
    │  7. _emotion_bubbles_html()     │
    │  8. _emotional_universe_html()  │
    │  9. raw_json (Developer Mode)   │
    └─────────────────────────────────┘
        ↓
    Frontend Rendering + Interactivity
        ↓
    User Experience
```

---

## Service Layer Architecture

### 1. LLM Service (`services/llm.py`)

#### Responsibilities
- Model loading (Qwen3-8B, Transformers or HF API)
- Text generation with configurable parameters
- JSON extraction from raw output
- Pydantic validation
- Retry logic with exponential backoff
- Timeout handling

#### Key Methods
```python
generate_validated_json(prompt, schema, max_tokens, retries)
    → Type-checked generation + validation
    → Returns typed Pydantic model
    → Raises LLMError on failure
```

#### Error Handling
- Network errors: Retry with backoff
- Timeout errors: User-friendly message
- JSON validation errors: Retry with different temperature
- Token limit exceeded: Clear error message

### 2. Emotion Engine (`services/emotion_engine.py`)

#### Responsibilities
- Story validation
- Emotion extraction via LLM
- Conflict graph building with NetworkX
- Data enrichment

#### Processing
```
Story Input
    ↓
Clean & Validate
    ↓
Load emotion.txt prompt
    ↓
Fill template with:
    - Story
    - Allowed emotions list
    ↓
Call LLM
    ↓
Extract JSON
    ↓
Validate against EmpathyAnalysis
    ↓
Build NetworkX graph
    ↓
Return validated EmpathyAnalysis
```

#### Graph Building
Nodes:
- conflict (central)
- person (participants)
- emotion
- goal
- fear
- assumption

Edges:
- conflict → person
- person → emotion/goal/fear/assumption

### 3. Perspective Engine (`services/perspective_engine.py`)

#### Responsibilities
- Multi-perspective generation
- User view (from their perspective)
- Other view (from the other person's perspective)
- Observer view (neutral third party)

#### Processing
Similar validation and generation flow as emotion engine.

---

## Data Schema Architecture

### Core Entities

#### Person
```python
class Person(BaseModel):
    role: str                    # "Father", "Child", etc.
    emotions: list[Emotion]      # ["fear", "hope", ...]
    fears: list[str]            # ["losing my child", ...]
    goals: list[str]            # ["make them safe", ...]
    assumptions: list[str]      # ["they don't respect me", ...]
```

#### Misunderstanding
```python
class Misunderstanding(BaseModel):
    speaker: str                # "Father"
    intention: str              # "I want you to be safe"
    interpretation: str         # "You don't trust me"
```

#### HiddenNeed
```python
class HiddenNeed(BaseModel):
    person: str                 # "Father"
    surface_position: str       # "Become an engineer"
    deep_need: str             # "Security"
```

#### FutureEcho
```python
class FutureEcho(BaseModel):
    choice: str                # "Choice A"
    response_style: str        # "Respond defensively"
    timeline: FutureTimeline   # 1 week, 1 month, 1 year
```

#### EmpathyAnalysis (Complete Output)
```python
class EmpathyAnalysis(BaseModel):
    situation: str              # Short label
    core_conflict: str          # "Security vs Freedom"
    people: list[Person]        # All participants
    observer_view: str          # Neutral perspective
    misunderstandings: list[Misunderstanding]  # Communication gaps
    hidden_needs: list[HiddenNeed]             # Deep needs
    future_echoes: list[FutureEcho]            # 3 futures
    if_you_were_them: str                      # 150-word narration
```

---

## LLM Prompt Engineering

### Prompt Structure (`prompts/emotion.txt`)

#### 1. System Context
- Non-therapy framing
- Non-judgmental stance
- Perspective-taking focus

#### 2. Task Definition
- Identify people
- Extract emotions/fears/goals/assumptions
- Compress core conflict
- Generate misunderstandings
- Identify hidden needs
- Create future echoes
- Write empathy narration

#### 3. Constraints
- Fixed emotion vocabulary (no hallucinations)
- Specific output format (JSON schema)
- Field length limits
- Archetype format for core_conflict
- 3 response styles for future echoes

#### 4. JSON Template
Shows exact expected structure with field constraints.

#### 5. Examples
- Good core_conflict examples
- Field requirement examples
- Good emotion vocabulary

### Quality Guarantees
- ✅ Pydantic validation ensures schema compliance
- ✅ Max length fields prevent verbose output
- ✅ Required fields always present
- ✅ Fixed emotions prevent hallucinations
- ✅ Retries handle occasional failures

---

## Frontend Architecture

### Rendering Pipeline

```
analyze_story() [Python/Gradio]
    ↓ (returns 9 HTML strings)
├─ core_conflict_html
├─ perspectives_html
├─ misunderstanding_layer_html
├─ hidden_needs_html
├─ if_you_were_them_html
├─ future_echoes_html
├─ emotion_cards_html
├─ emotional_universe_html
└─ raw_json
    ↓
Gradio renders HTML components
    ↓
CSS applies styling
    ↓
JavaScript wires interactivity
    ↓
User interaction
```

### Styling Architecture (`static/style.css`)

#### CSS Variables
```css
--tte-bg: #050816               /* Main background */
--tte-secondary: #0f172a        /* Secondary background */
--tte-accent: #7dd3fc           /* Highlight color */
--tte-glow: #38bdf8             /* Glow effect */
--tte-text: #f8fafc             /* Text color */
--tte-muted: #94a3b8            /* Muted text */
--tte-glass: rgba(...)          /* Glassmorphism */
--tte-border: rgba(...)         /* Border color */
--tte-shadow: (...)             /* Shadow */
```

#### Animation Library
- `starDrift` - Background animation
- `beamFloat` - Light beam floating
- `orbFloat` - Orb floating
- `capsuleFloat` - Input capsule floating
- `revealMind` - Standard reveal (used everywhere)
- `ringPulse` - Pulsing rings
- `slowRotate` - Orbit ring rotation
- `planetPulse` - Planet glow pulsing
- `bubblePulse` - Bubble saturation pulse
- `edgeFlow` - Animated edge dashes
- `glowPulse` - Glow point pulsing (NEW)
- `cardExpand` - Card expansion (NEW)
- `timelineReveal` - Timeline reveal (NEW)

#### Component Styling
- `.core-node` - Central conflict display
- `.planet` - Perspective selector
- `.misread-card` - Misunderstanding card
- `.need-card` - Hidden need card
- `.embodied-perspective` - Wow moment section
- `.future-card` - Timeline card
- `.emotion-bubble` - Emotion display
- `.tte-flow-node` - Graph nodes

### Interactivity Architecture (`static/app.js`)

#### Wire Functions (Progressive Enhancement)

1. **`wireAnalyzeButton()`** - Existing
   - Shows journey status while analyzing

2. **`wirePlanets()`** - Existing
   - Switches between perspectives

3. **`wireEmotionBubbles()`** - Existing
   - Expands emotion details

4. **`wireMisunderstandingCards()`** - NEW
   - Makes misunderstanding cards clickable
   - Toggles `is-open` class
   - Triggers reveal animation

5. **`wireFutureEchoes()`** - NEW
   - Makes future echo cards clickable
   - Manages active state
   - Expands timeline with animation

#### Graph Rendering

Two-tier approach:
1. **Try React Flow** - Full interactive graph
2. **Fallback to SVG** - Works without JavaScript
3. **Feature Detection** - Auto-selects based on environment

#### Event Handling
- Event delegation for dynamic content
- MutationObserver watches for new elements
- requestAnimationFrame optimizes reflows
- Passive event listeners for scroll/wheel

---

## State Management

### Backend State
- Input story (transient)
- Generated analysis (in memory)
- Output JSON (saved to disk)

### Frontend State
- Active perspective (stored in DOM class)
- Active future echo (stored in DOM class)
- Expanded emotion bubble (stored in DOM class)
- Graph state (maintained by React Flow or canvas)

No global JavaScript state—all state is DOM-based.

---

## Error Handling Strategy

### Validation Errors
```
User Input Validation
    ↓ (if invalid)
Friendly Error Message
    ↓
Show suggestions (e.g., "Please add more context")
```

### LLM Errors
```
LLM Generation
    ↓ (if invalid JSON)
Retry with backoff
    ↓ (if still invalid)
Friendly Error Message
    ↓
Show "Try again with shorter story"
```

### Network Errors
```
API Call
    ↓ (if timeout)
Retry (up to 3 times)
    ↓ (if still failing)
Friendly Error Message
    ↓
Show "Model is busy, try again"
```

### Rendering Errors
```
HTML Generation
    ↓ (if exception)
Show error card
    ↓
Don't crash page
    ↓
Return empty JSON for Developer Mode
```

---

## Performance Optimization

### Backend
- ✅ No database calls (stateless)
- ✅ Minimal memory footprint
- ✅ Efficient JSON parsing
- ✅ NetworkX graph is lightweight
- ✅ Parallelizable inference

### Frontend
- ✅ CSS animations use GPU (transform, opacity)
- ✅ No layout thrashing (batch DOM updates)
- ✅ Lazy loading of React Flow library
- ✅ SVG fallback avoids JavaScript overhead
- ✅ Event delegation minimizes listeners

### Network
- ✅ Single page load (no redirects)
- ✅ CSS inlined in HTML
- ✅ JavaScript inlined in HTML
- ✅ CDN-hosted libraries (React Flow)
- ✅ Local caching of model weights

---

## Security Considerations

### XSS Prevention
- ✅ All user input HTML-escaped with `html.escape()`
- ✅ JSON safely embedded: `html.escape(json.dumps())`
- ✅ No eval() or dynamic code execution
- ✅ No innerHTML assignment in JavaScript

### Injection Prevention
- ✅ Pydantic validation on all inputs
- ✅ Field length limits prevent buffer overflows
- ✅ Prompt is static (no user injection)
- ✅ No SQL queries (stateless)

### CSRF/SSRF Prevention
- ✅ No state-changing operations
- ✅ No external API calls to user-supplied URLs
- ✅ Model ID is fixed in configuration

---

## Testing Strategy

### Unit Testing
- Pydantic schema validation
- HTML escape functions
- Conflict split logic
- Graph payload generation

### Integration Testing
- End-to-end story analysis
- LLM integration with retries
- Frontend rendering
- Interactive features

### Manual Testing
- Multiple stories with different conflicts
- Interactive element clicking
- Graph interactions
- Mobile responsiveness

### Edge Cases
- Very short stories (error message)
- Very long stories (truncation)
- Multiple people involved
- Complex emotions
- Network timeouts

---

## Deployment Architecture

### Single-Process Deployment
```
User Request
    ↓
Gradio Server
    ├─ Load model (first time)
    ├─ Generate analysis
    ├─ Render HTML
    └─ Return response
```

### Multi-Process Deployment (Future)
```
Load Balancer
    ↓
├─ Worker 1 (model inference)
├─ Worker 2 (model inference)
└─ Worker 3 (model inference)
    ↓
Shared Cache (model weights)
```

### Cloud Deployment
- ✅ Gradio Cloud compatible
- ✅ Docker containerizable
- ✅ Environment variable configuration
- ✅ Stateless (horizontal scaling ready)

---

## Configuration

### Environment Variables
```bash
HF_TOKEN              # Hugging Face API token
LLM_PROVIDER          # "hf_api" or "local"
MODEL_ID              # Model identifier
HF_HUB_OFFLINE        # Offline mode
TRANSFORMERS_OFFLINE  # Offline transformers
```

### Configurable Constants
```python
DEFAULT_MODEL_ID = "Qwen/Qwen3-8B"
DEFAULT_TIMEOUT_SECONDS = 90
MAX_STORY_LENGTH = 4000
MIN_STORY_LENGTH = 20
```

---

## Monitoring & Debugging

### Logging Points
- Story validation
- LLM call start/end
- JSON parsing
- Pydantic validation
- Error messages

### Output Files
- `outputs/latest_analysis.json` - Last analysis

### Debug Mode Ideas
- Verbose LLM output
- Intermediate analysis states
- Response timing
- Token usage

---

## Future Architectural Improvements

### Phase 2
1. **Caching** - Cache analyses for repeated stories
2. **Analytics** - Track common conflicts
3. **Batch Processing** - Analyze multiple stories
4. **API Layer** - RESTful API for integration
5. **Database** - Persist analyses

### Phase 3
1. **Real-time Collaboration** - Multi-user analysis
2. **Resolution Module** - Path to understanding
3. **Voice Interface** - Spoken interaction
4. **Mobile App** - Native mobile experience
5. **Integration** - Mediation platform integration

---

## Technology Stack

### Backend
- **Python 3.11+** - Core language
- **Gradio 4.44+** - Web interface
- **Pydantic 2.7+** - Data validation
- **Transformers 4.51+** - LLM inference
- **Torch 2.2+** - Deep learning
- **Requests** - HTTP client
- **NetworkX 3.3+** - Graph algorithms

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling
- **JavaScript (Vanilla)** - Interactivity
- **React 18** - Graph rendering (optional)
- **React Flow 11** - Graph visualization (optional)

### Infrastructure
- **Gradio** - Deployment (local or cloud)
- **Hugging Face Hub** - Model hosting
- **CDN** - Library delivery (React, React Flow)

---

## Conclusion

The architecture successfully transforms emotional analysis into an empathy experience through:

1. **Thoughtful Data Flow** - From story to structured analysis to beautiful visualization
2. **Robust Validation** - Pydantic ensures data integrity at every step
3. **Beautiful Design** - CSS and animations create contemplative space
4. **Intelligent Interactivity** - JavaScript enables discovery
5. **Intelligent Error Handling** - Graceful degradation and user-friendly messages
6. **Scalable Foundation** - Ready for future phases

The system prioritizes user experience while maintaining technical excellence.
