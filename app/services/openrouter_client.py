import requests
import json
from typing import Dict
from app.core.config import settings


class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not set")

        self.api_key = settings.OPENROUTER_API_KEY
        self.model = "qwen/qwen-2.5-7b-instruct"

    def extract_fields(self, ocr_text: str) -> Dict:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an OCR post-processing engine. Output JSON only."
                },
                {
                    "role": "user",
                    "content": self._build_prompt(ocr_text)
                }
            ],
            "temperature": 0.0,
            "max_tokens": 512   # 🔥 REQUIRED
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "OCR-Application",
            "Accept": "application/json"
        }

        try:
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                return self._fail(
                    f"HTTP {response.status_code}: {response.text}"
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            return self._parse_json(content)

        except Exception as e:
            return self._fail(str(e))

    # ------------------ helpers ------------------

    def _build_prompt(self, text: str) -> str:
        return f"""
You are given raw OCR text extracted from an Indian identity document.

The OCR text may contain noise, spelling mistakes, or missing lines.

Your task:
- Identify the document type (Aadhaar, PAN, Passport, or Unknown)
- Extract:
  - name
  - date_of_birth
  - document_number
  - address

Rules:
- If missing or unreadable → "MISSING"
- Do NOT guess
- Output VALID JSON ONLY
- No markdown, no explanation

OCR TEXT:
{text}
"""

    def _parse_json(self, text: str) -> Dict:
        try:
            cleaned = (
                text.strip()
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )
            parsed = json.loads(cleaned)

            return {
                "document_type": parsed.get("document_type", "Unknown"),
                "name": parsed.get("name", "MISSING"),
                "date_of_birth": parsed.get("date_of_birth", "MISSING"),
                "document_number": parsed.get("document_number", "MISSING"),
                "address": parsed.get("address", "MISSING"),
            }

        except Exception:
            return self._fail(f"Invalid JSON from LLM: {text}")

    def _fail(self, reason: str) -> Dict:
        return {
            "document_type": "Unknown",
            "name": "MISSING",
            "date_of_birth": "MISSING",
            "document_number": "MISSING",
            "address": "MISSING",
            "error": reason
        }