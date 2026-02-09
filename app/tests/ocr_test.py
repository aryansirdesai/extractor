import pytest
from app.services.ocr_service import OCRService


def test_ocr_extraction():
    """Test OCR extraction from document image."""
    ocr = OCRService()
    result = ocr.extract_text("Aadhar_Card.jpg")
    assert result is not None
    print(result)