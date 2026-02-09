import re
from typing import Optional


class IDNumberService:
    """
    Extracts and normalizes document numbers from OCR text
    based on inferred document type.
    """

    AADHAAR_REGEX = re.compile(r"\b(\d{4}\s?\d{4}\s?\d{4})\b")
    PAN_REGEX = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b")
    PASSPORT_REGEX = re.compile(r"\b([A-Z][0-9]{7})\b")

    def extract(self, ocr_text: str, document_type: str) -> Optional[str]:
        if document_type == "Aadhaar":
            return self._extract_aadhaar(ocr_text)

        if document_type == "PAN":
            return self._extract_pan(ocr_text)

        if document_type == "Passport":
            return self._extract_passport(ocr_text)

        # Generic fallback (best-effort)
        return self._extract_generic(ocr_text)

    # ------------------ specific extractors ------------------

    def _extract_aadhaar(self, text: str) -> Optional[str]:
        match = self.AADHAAR_REGEX.search(text)
        if not match:
            return None
        return match.group(1).replace(" ", "")

    def _extract_pan(self, text: str) -> Optional[str]:
        match = self.PAN_REGEX.search(text.upper())
        return match.group(1) if match else None

    def _extract_passport(self, text: str) -> Optional[str]:
        match = self.PASSPORT_REGEX.search(text.upper())
        return match.group(1) if match else None

    # ------------------ generic fallback ------------------

    def _extract_generic(self, text: str) -> Optional[str]:
        """
        Last resort: find long alphanumeric tokens.
        Used for unknown / future IDs.
        """
        candidates = re.findall(r"\b[A-Z0-9]{8,16}\b", text.upper())
        return candidates[0] if candidates else None