import re
from typing import Optional


class DocumentTypeService:
    """
    Deterministic document type inference using OCR text + ID patterns.
    LLM output is advisory only.
    """

    AADHAAR_KEYWORDS = [
        "aadhaar",
        "uidai",
        "your aadhaar",
        "government of india"
    ]

    PAN_KEYWORDS = [
        "income tax department",
        "permanent account number",
        "pan"
    ]

    PASSPORT_KEYWORDS = [
        "passport",
        "republic of india",
        "nationality",
        "place of issue"
    ]

    AADHAAR_REGEX = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
    PAN_REGEX = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
    PASSPORT_REGEX = re.compile(r"\b[A-Z][0-9]{7}\b")

    def infer(self, ocr_text: str, llm_doc_type: Optional[str] = None) -> str:
        text = ocr_text.lower()

        # ---------- Layer 1: Keyword signatures ----------
        if self._contains_any(text, self.AADHAAR_KEYWORDS):
            return "Aadhaar"

        if self._contains_any(text, self.PAN_KEYWORDS):
            return "PAN"

        if self._contains_any(text, self.PASSPORT_KEYWORDS):
            return "Passport"

        # ---------- Layer 2: Number structure ----------
        if self.AADHAAR_REGEX.search(ocr_text):
            return "Aadhaar"

        if self.PAN_REGEX.search(ocr_text):
            return "PAN"

        if self.PASSPORT_REGEX.search(ocr_text):
            return "Passport"

        # ---------- Layer 3: LLM fallback ----------
        if llm_doc_type:
            llm_doc_type = llm_doc_type.lower()
            if "aadhaar" in llm_doc_type:
                return "Aadhaar"
            if "pan" in llm_doc_type:
                return "PAN"
            if "passport" in llm_doc_type:
                return "Passport"

        return "Unknown"

    def _contains_any(self, text: str, keywords: list[str]) -> bool:
        return any(k in text for k in keywords)