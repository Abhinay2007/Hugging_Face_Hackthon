# Through Their Eyes

An AI-powered empathy simulator for understanding perspectives during conflict.

This project is not therapy. It does not provide mental health advice, diagnosis, judgment, or instructions about what anyone should do. It helps users inspect possible perspectives: the user's story, the other person's story, and the story in between.

## Features

- User perspective, other person perspective, and neutral observer perspective
- Structured conflict analysis with emotions, fears, goals, and assumptions
- JSON-only model contract validated with Pydantic
- Fixed emotion vocabulary so the model cannot invent new emotions
- Local Transformers support for `Qwen/Qwen3-8B`
- Hugging Face Inference API support
- NetworkX-based lightweight conflict concept graph enrichment
- Modern responsive Gradio Blocks UI with custom dark CSS
- Friendly handling for empty input, invalid JSON, model failure, and timeout

## Installation

```bash
cd through-their-eyes
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Setup

For Hugging Face Inference API mode:

```bash
export HF_TOKEN="your_hugging_face_token"
export LLM_PROVIDER="hf_api"
export MODEL_ID="Qwen/Qwen3-8B"
```

For local Transformers mode:

```bash
export LLM_PROVIDER="local"
export MODEL_ID="Qwen/Qwen3-8B"
export LOAD_IN_4BIT="auto"
export GPU_MEMORY_LIMIT="13GiB"
```

On a 16 GB GPU, keep 4-bit loading enabled. It leaves room for generation memory and avoids most CUDA out-of-memory failures.

`Qwen/Qwen3-8B` is the valid Hugging Face model identifier. The earlier `Qwen/Qwen3-8B-Instruct` name is not a published repo.

The first local run downloads the model weights into your Hugging Face cache. After the weights are cached, you can run from the local cache. To force offline loading later:

```bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
```

If you manually downloaded the model to a folder, point `MODEL_ID` at that folder:

```bash
export LLM_PROVIDER="local"
export MODEL_ID="/absolute/path/to/Qwen3-8B"
```

If `LLM_PROVIDER` is not set, the app uses Hugging Face Inference API when `HF_TOKEN` exists and local Transformers otherwise.

## Run Locally

```bash
python app.py
```

If you just installed the project or pulled a memory fix, update the venv first:

```bash
pip install -U -r requirements.txt
```

If CUDA memory is fragmented from an earlier run, stop the old Python process and restart the terminal command:

```bash
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export LLM_PROVIDER="local"
export MODEL_ID="Qwen/Qwen3-8B"
export LOAD_IN_4BIT="true"
export GPU_MEMORY_LIMIT="13GiB"
python app.py
```

For maximum stability on 16 GB GPUs, you can use the smaller local model:

```bash
export MODEL_ID="Qwen/Qwen3-4B"
```

Open:

```text
http://localhost:7860
```

## Project Architecture

```text
through-their-eyes/
├── app.py
├── requirements.txt
├── README.md
├── prompts/
│   ├── emotion.txt
│   └── perspective.txt
├── schemas/
│   └── empathy_schema.py
├── services/
│   ├── llm.py
│   ├── emotion_engine.py
│   └── perspective_engine.py
├── static/
│   └── style.css
├── outputs/
└── examples/
```

## Service Design

`services/llm.py` owns model selection, generation, retries, JSON extraction, and Pydantic validation.

`services/emotion_engine.py` turns a conflict story into an `EmpathyAnalysis` object and uses NetworkX to identify central conflict concepts.

`services/perspective_engine.py` generates the three perspective summaries as validated JSON.

`schemas/empathy_schema.py` defines the strict output contract:

- `Person`: `role`, `emotions`, `fears`, `goals`, `assumptions`
- `EmpathyAnalysis`: `situation`, `people`, `observer_view`, `core_conflict`

## Emotion Vocabulary

The app only allows these emotions:

```json
[
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
  "worry"
]
```

## Screenshots

Place screenshots in this section after running the app:

```text
docs/screenshots/home.png
docs/screenshots/results.png
```

## Example Stories

- Parent/Child: A parent wants a secure career path while the child wants to build a business.
- Teacher/Student: A teacher sees falling grades as low effort while the student feels overwhelmed.
- Friendship: A friend feels ignored after canceled plans while the other friend feels exhausted.
- Relationship: One partner wants more time together while the other needs quiet time.
- Workplace: A manager sees a project as growth while the employee feels overloaded.

## Production Notes

- Keep `temperature` low for structured output reliability.
- Use `HF_TOKEN` in deployment secrets rather than committing credentials.
- Monitor invalid JSON rates and model latency.
- The UI stores the latest successful result in `outputs/latest_analysis.json` for demo review.
- The project intentionally avoids advice generation because the product goal is perspective understanding only.
