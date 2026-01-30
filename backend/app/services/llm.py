import os
import json
from typing import Any, Dict, Union, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client using environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Default model (good balance of speed/cost/quality)
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def call_llm(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
    json_mode: bool = True,
) -> Union[str, Dict[str, Any]]:
    """
    Call OpenAI with a prompt.

    - If json_mode=True: forces the model to return VALID JSON and returns a dict.
    - If json_mode=False: returns plain text string.

    This is safer for production apps, especially for demo stability.
    """
    if not prompt or not isinstance(prompt, str):
        raise ValueError("prompt must be a non-empty string")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "If asked for JSON, output ONLY valid JSON and nothing else."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    # JSON Mode (recommended for your question generation + scoring)
    if json_mode:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},  # forces valid JSON
        )
        content = resp.choices[0].message.content or "{}"
        return json.loads(content)

    # Normal text mode
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def safe_json(text: str) -> Dict[str, Any]:
    """
    Backward-compatible helper:
    If you still call safe_json() in other files, it won't break.
    But when using json_mode=True, you usually won't need this.
    """
    if not text:
        return {}

    try:
        return json.loads(text)
    except Exception:
        # fallback extraction if any extra text exists
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])

        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            # wrap array into object to keep consistent return type
            return {"data": json.loads(text[start : end + 1])}

        raise ValueError("Could not parse JSON from model output.")