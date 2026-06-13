---
title: Echoes Between Us
emoji: 🫂
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.34.2
app_file: app.py
pinned: false
---

# Echoes Between Us

Every conflict has three stories:

- Yours
- Theirs
- The story in between

An AI-powered empathy simulator that helps users explore perspectives, misunderstandings, hidden needs, and emotional worlds.

## ZeroGPU Deployment

Space settings:

```text
SDK: Gradio
Hardware: ZeroGPU
Python: 3.10 or 3.12
```

The app imports `spaces` and wraps local Transformers generation with `@spaces.GPU(duration=120)` in `services/llm.py`. The shared `LLMClient` caches the tokenizer and model so they are initialized once per process and reused across requests.

Recommended Space environment variables:

```bash
LLM_PROVIDER=local
MODEL_ID=Qwen/Qwen3-8B
LOAD_IN_4BIT=true
GPU_MEMORY_LIMIT=40GiB
CPU_MEMORY_LIMIT=64GiB
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```
