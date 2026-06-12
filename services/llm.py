"""Language model loading, generation, retries, and JSON validation."""

from __future__ import annotations

import json
import os
import re
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, TypeVar

import requests
from pydantic import BaseModel, ValidationError

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
except Exception:  # pragma: no cover - optional until local model mode is used
    torch = None
    AutoModelForCausalLM = None
    AutoTokenizer = None
    BitsAndBytesConfig = None


SchemaT = TypeVar("SchemaT", bound=BaseModel)

DEFAULT_MODEL_ID = "Qwen/Qwen3-8B"
DEFAULT_TIMEOUT_SECONDS = 90
DEFAULT_GPU_MEMORY_LIMIT = "13GiB"
DEFAULT_CPU_MEMORY_LIMIT = "48GiB"


class LLMError(RuntimeError):
    """Raised when generation or validation fails after retries."""


class LLMClient:
    """Generate JSON with Qwen3-8B via local Transformers or HF API."""

    def __init__(
        self,
        model_id: str | None = None,
        provider: str | None = None,
        hf_token: str | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.model_id = model_id or os.getenv("MODEL_ID", DEFAULT_MODEL_ID)
        self.provider = (provider or os.getenv("LLM_PROVIDER", "auto")).lower()
        self.hf_token = hf_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.timeout_seconds = timeout_seconds
        self._local_tokenizer: Any | None = None
        self._local_model: Any | None = None

    def generate_validated_json(
        self,
        prompt: str,
        schema: type[SchemaT],
        *,
        max_new_tokens: int = 1200,
        retries: int = 2,
    ) -> SchemaT:
        """Generate JSON text and validate it against a Pydantic schema."""
        errors: list[str] = []
        raw_text = ""
        for attempt in range(retries + 1):
            try:
                raw_text = self.generate_text(prompt, max_new_tokens=max_new_tokens)
                json_payload = extract_json_object(raw_text)
                return schema.model_validate(json_payload)
            except (LLMError, ValidationError, ValueError, requests.RequestException) as exc:
                errors.append(f"attempt {attempt + 1}: {exc}")
                _write_debug_output(raw_text, errors)
                if attempt < retries:
                    time.sleep(0.8 * (attempt + 1))
        raise LLMError("Model output could not be validated. " + " | ".join(errors[-3:]))

    def generate_text(self, prompt: str, *, max_new_tokens: int = 1200) -> str:
        """Generate raw text using the configured provider."""
        if self.provider == "hf_api":
            return self._generate_hf_api(prompt, max_new_tokens=max_new_tokens)
        if self.provider == "local":
            return self._generate_local(prompt, max_new_tokens=max_new_tokens)
        if self.hf_token:
            return self._generate_hf_api(prompt, max_new_tokens=max_new_tokens)
        return self._generate_local(prompt, max_new_tokens=max_new_tokens)

    def _generate_hf_api(self, prompt: str, *, max_new_tokens: int) -> str:
        """Call Hugging Face Inference API."""
        if not self.hf_token:
            raise LLMError("HF_TOKEN is required when LLM_PROVIDER=hf_api.")

        url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {
            "inputs": self._chat_prompt(prompt),
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "do_sample": False,
                "return_full_text": False,
            },
            "options": {"wait_for_model": True},
        }
        response = requests.post(url, headers=headers, json=payload, timeout=self.timeout_seconds)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and data:
            generated = data[0].get("generated_text")
            if isinstance(generated, str):
                return generated
        if isinstance(data, dict) and isinstance(data.get("generated_text"), str):
            return data["generated_text"]
        if isinstance(data, dict) and "error" in data:
            raise LLMError(str(data["error"]))
        raise LLMError("Unexpected Hugging Face API response format.")

    def _generate_local(self, prompt: str, *, max_new_tokens: int) -> str:
        """Run local Transformers generation."""
        if AutoTokenizer is None or AutoModelForCausalLM is None:
            raise LLMError("Transformers local runtime is unavailable. Install requirements or use HF_TOKEN.")

        tokenizer, model = self._get_local_model()
        messages = [
            {
                "role": "system",
                "content": (
                    "You return valid JSON only. You do not provide therapy, diagnosis, "
                    "advice, judgment, or sides."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        chat_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        chat_text = f"{chat_text}{{\n"
        model_inputs = tokenizer(
            [chat_text],
            return_tensors="pt",
        ).to(model.device)

        try:
            with torch.inference_mode():
                generated_ids = model.generate(
                    **model_inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                    use_cache=True,
                )
            output_ids = generated_ids[0][model_inputs["input_ids"].shape[-1] :]
            return "{\n" + str(tokenizer.decode(output_ids, skip_special_tokens=True)).strip()
        except torch.cuda.OutOfMemoryError as exc:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            raise LLMError(
                "CUDA ran out of memory during generation. Try restarting the app, "
                "installing bitsandbytes for 4-bit loading, or setting MODEL_ID=Qwen/Qwen3-4B."
            ) from exc

    def _get_local_model(self) -> tuple[Any, Any]:
        """Lazily load the local Qwen model once per process."""
        if self._local_tokenizer is not None and self._local_model is not None:
            return self._local_tokenizer, self._local_model

        if torch is None:
            raise LLMError("PyTorch is unavailable.")

        tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
        model_kwargs = self._local_model_kwargs()
        model = AutoModelForCausalLM.from_pretrained(self.model_id, **model_kwargs)
        self._local_tokenizer = tokenizer
        self._local_model = model
        return tokenizer, model

    def _local_model_kwargs(self) -> dict[str, Any]:
        """Build memory-aware local model loading options."""
        offload_folder = Path(os.getenv("MODEL_OFFLOAD_DIR", "/tmp/through-their-eyes-offload"))
        offload_folder.mkdir(parents=True, exist_ok=True)

        kwargs: dict[str, Any] = {
            "device_map": "auto",
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
            "offload_folder": str(offload_folder),
        }

        if torch is not None and torch.cuda.is_available():
            kwargs["max_memory"] = {
                0: os.getenv("GPU_MEMORY_LIMIT", DEFAULT_GPU_MEMORY_LIMIT),
                "cpu": os.getenv("CPU_MEMORY_LIMIT", DEFAULT_CPU_MEMORY_LIMIT),
            }

        load_in_4bit = os.getenv("LOAD_IN_4BIT", "auto").lower()
        should_quantize = load_in_4bit in {"1", "true", "yes"} or (
            load_in_4bit == "auto" and torch is not None and torch.cuda.is_available()
        )

        if should_quantize:
            if BitsAndBytesConfig is None:
                raise LLMError("4-bit loading requires bitsandbytes. Run: pip install -U bitsandbytes")
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                bnb_4bit_use_double_quant=True,
            )
        else:
            kwargs["torch_dtype"] = "auto"

        return kwargs

    @staticmethod
    def _chat_prompt(prompt: str) -> str:
        """Wrap the task in a simple instruction-tuned chat format."""
        return (
            "<|im_start|>system\n"
            "You return valid JSON only. You do not provide therapy, diagnosis, advice, judgment, or sides.\n"
            "<|im_end|>\n"
            "<|im_start|>user\n"
            f"{prompt}\n"
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
        )


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract the first valid JSON object from model text."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    direct_parse_error: json.JSONDecodeError | None = None
    try:
        payload = json.loads(cleaned)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError as exc:
        direct_parse_error = exc

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        detail = f" Direct parse error: {direct_parse_error}" if direct_parse_error else ""
        raise ValueError(f"No JSON object found in model output.{detail}")

    json_text = cleaned[start : end + 1]
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError:
        payload = json.loads(_repair_json_text(cleaned[start:]))
    if not isinstance(payload, dict):
        raise ValueError("Model output JSON must be an object.")
    return payload


def _repair_json_text(text: str) -> str:
    """Repair common model JSON issues such as truncation and trailing commas."""
    repaired = text.strip()
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)

    stack: list[str] = []
    in_string = False
    escaped = False
    for char in repaired:
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char in "{[":
            stack.append(char)
        elif char == "}" and stack and stack[-1] == "{":
            stack.pop()
        elif char == "]" and stack and stack[-1] == "[":
            stack.pop()

    if in_string:
        repaired += '"'
    repaired = re.sub(r",\s*$", "", repaired)
    while stack:
        opener = stack.pop()
        repaired += "}" if opener == "{" else "]"
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    return repaired


def _write_debug_output(raw_text: str, errors: list[str]) -> None:
    """Persist the latest invalid model text for local debugging."""
    try:
        output_dir = Path(__file__).resolve().parents[1] / "outputs"
        output_dir.mkdir(exist_ok=True)
        debug_payload = {
            "errors": errors[-3:],
            "raw_text": raw_text,
        }
        (output_dir / "last_model_error.json").write_text(
            json.dumps(debug_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        return


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / name
    return prompt_path.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    """Return the shared LLM client for the Gradio process."""
    return LLMClient()
