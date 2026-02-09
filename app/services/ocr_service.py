import cv2
import pytesseract
from PIL import Image
from typing import Dict

# Windows-only: uncomment & set if needed
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class OCRService:
    """
    Offline OCR service using Tesseract.
    Responsible ONLY for extracting raw text + basic quality signals.
    """

    def extract_text(self, image_path: str) -> Dict:
        try:
            image = cv2.imread(image_path)
            if image is None:
                return self._fail("Unable to read image")

            processed = self._preprocess(image)

            text = pytesseract.image_to_string(
                processed,
                lang="eng",
                config="--psm 6"
            ).strip()

            if not text:
                return self._fail("No text detected")

            return {
                "text": text,
                "char_count": len(text),
                "line_count": len(text.splitlines()),
                "status": "ok"
            }

        except Exception as e:
            return self._fail(str(e))

    # ------------------ helpers ------------------

    def _preprocess(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blur,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        return thresh

    def _fail(self, reason: str) -> Dict:
        return {
            "text": "",
            "char_count": 0,
            "line_count": 0,
            "status": "failed",
            "reason": reason
        }