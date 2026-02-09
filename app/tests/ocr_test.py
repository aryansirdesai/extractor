# import pytest
# from app.services.ocr_service import OCRService


# def test_ocr_extraction():
#     """Test OCR extraction from document image."""
#     ocr = OCRService()
#     result = ocr.extract_text("Aadhar_Card.jpg")
#     assert result is not None
#     print(result)

from app.services.ocr_service import OCRService
from pathlib import Path

if __name__ == "__main__":
    ocr = OCRService()

    BASE_DIR = Path(__file__).resolve().parent
    image_path = BASE_DIR / "Aadhar_Card.jpg"

    result = ocr.extract_text(str(image_path))

    print("\n===== OCR STATUS =====")
    print(result.get("status"))

    print("\n===== OCR CHAR COUNT =====")
    print(result.get("char_count"))

    print("\n===== OCR RAW TEXT =====")
    print(result.get("text"))