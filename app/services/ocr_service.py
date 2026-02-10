import cv2
import pytesseract
from typing import Dict

# ✅ REQUIRED on Windows
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
)


class OCRService:
    """
    Offline OCR service using Tesseract.
    Responsible ONLY for extracting raw text + quality signals.
    """

    def extract_text(self, image_path: str) -> Dict:
        try:
            image = cv2.imread(image_path)
            if image is None:
                return self._fail("Unable to read image")

            # -------- Attempt 1: raw image --------
            text = self._run_tesseract(image)

            # -------- Attempt 2: grayscale fallback --------
            if not text.strip():
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                text = self._run_tesseract(gray)

            text = text.strip()

            if not text:
                return self._fail("No text detected by OCR")

            return {
                "text": text,
                "char_count": len(text),
                "line_count": len(text.splitlines()),
                "status": "ok",
            }

        except Exception as e:
            return self._fail(str(e))

    # ------------------ helpers ------------------

    def _run_tesseract(self, image) -> str:
        return pytesseract.image_to_string(
            image,
            lang="eng",
            config="--oem 3 --psm 4"
        )

    def _fail(self, reason: str) -> Dict:
        return {
            "text": "",
            "char_count": 0,
            "line_count": 0,
            "status": "failed",
            "reason": reason,
        }