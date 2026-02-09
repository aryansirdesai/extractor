import base64
import requests
import json
from typing import Dict
from app.core.config import settings
from app.core.prompt_template import DOCUMENT_EXTRACTION_PROMPT


class GeminiClient:
    """
    Client to interact with Google Gemini Flash via
    the Generative Language API (multimodal image + text).
    """

    BASE_URL = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent"
    )

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env")
        self.api_key = settings.GEMINI_API_KEY

    def extract_text(self, file_path: str) -> Dict:
        """
        Uploads a document image to Gemini Flash and returns extracted JSON.
        """
        # Read and base64 encode image
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        image_b64 = base64.b64encode(image_bytes).decode()

        prompt = DOCUMENT_EXTRACTION_PROMPT()

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_b64
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        try:
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                return {
                    "error": f"Gemini API failed with status {response.status_code}",
                    "raw_response": response.text
                }

            response_data = response.json()

            if (
                "candidates" not in response_data
                or not response_data["candidates"]
            ):
                return {"error": "No candidates returned from Gemini"}

            extracted_content = (
                response_data["candidates"][0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )

            if not extracted_content:
                return {"error": "Empty content from Gemini"}

            # Strip markdown fences if present
            cleaned = extracted_content.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("```").strip("json").strip()

            try:
                extracted_json = json.loads(cleaned)
            except json.JSONDecodeError:
                return {
                    "error": "Failed to parse JSON from Gemini response",
                    "raw_text": cleaned
                }

            return extracted_json

        except requests.exceptions.RequestException as e:
            return {"error": f"Gemini request failed: {str(e)}"}