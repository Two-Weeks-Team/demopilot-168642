import os
import json
import re
from typing import Any, Dict, List
import httpx

# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------
INFERENCE_ENDPOINT = "https://inference.do-ai.run/v1/chat/completions"
API_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
DEFAULT_MODEL = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")

# ---------------------------------------------------------------------------
# Helper to pull JSON out of LLM markdown wrappers
# ---------------------------------------------------------------------------
def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

# ---------------------------------------------------------------------------
# Core inference driver – single reusable async function
# ---------------------------------------------------------------------------
def _coerce_unstructured_payload(raw_text: str) -> Dict[str, Any]:
    compact = raw_text.strip()
    tags = [part.strip(" -•\t") for part in re.split(r",|\\n", compact) if part.strip(" -•\t")]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact,
        "tags": tags[:6],
    }


async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "max_completion_tokens": max_tokens,
    }
    timeout = httpx.Timeout(90.0, read=90.0, write=90.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(INFERENCE_ENDPOINT, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            # Expecting a typical ChatCompletion format
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            raw_json = _extract_json(content)
            return json.loads(raw_json)
        except Exception as e:
            # Fallback – never propagate errors to route handlers
            return {"note": f"AI service unavailable: {str(e)}"}

# ---------------------------------------------------------------------------
# Public helpers used by route handlers
# ---------------------------------------------------------------------------
async def generate_feedback(recording_url: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": "You are an expert demo coach. Analyse the rehearsal recording at the provided URL and return feedback JSON with three categories: clarity, engagement, persuasion. Each category should contain a numeric score (0‑10) and a list of actionable suggestions. Use the following schema:\n{\n  \"clarity\": {\n    \"score\": number,\n    \"suggestions\": [string]\n  },\n  \"engagement\": {\n    \"score\": number,\n    \"suggestions\": [string]\n  },\n  \"persuasion\": {\n    \"score\": number,\n    \"suggestions\": [string]\n  }\n}\nDo NOT add any extra fields. Return ONLY the JSON."},
        {"role": "user", "content": f"Recording URL: {recording_url}"},
    ]
    return await _call_inference(messages)

async def generate_script(beats_text: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": "You are a pitch script writer. Using the supplied demo beats, generate a refined pitch script and a short list of key points. Return JSON with two fields: `script` (string) and `key_points` (list of strings). No extra fields."},
        {"role": "user", "content": f"Demo beats:\n{beats_text}"},
    ]
    return await _call_inference(messages)
