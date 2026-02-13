from typing import List, Optional
from app.services.ocr_service import OCRService
from app.services.openrouter_client import OpenRouterClient
from app.services.confidence_service import ConfidenceService
from app.services.document_type_service import DocumentTypeService
from app.services.id_number_service import IDNumberService


class ExtractionService:
    def __init__(self):
        self.ocr = OCRService()
        self.llm = OpenRouterClient()
        self.conf_service = ConfidenceService()
        self.doc_type_service = DocumentTypeService()
        self.id_number_service = IDNumberService()

    def extract_document(self, file_path: str, required_fields: Optional[List[str]] = None):

        required_fields = required_fields or []

        # ------------------ OCR ------------------
        ocr_result = self.ocr.extract_text(file_path)

        if ocr_result["status"] != "ok" or ocr_result["char_count"] < 30:
            return {
                "data": self._empty_result(),
                "confidence": 0.0,
                "hitl_required": False,
                "source": "ocr_failed",
                "fallback_reason": "low_ocr_quality"
            }

        # ------------------ LLM (pass required fields) ------------------
        llm_result = self.llm.extract_fields(
            ocr_text=ocr_result["text"],
            required_fields=required_fields
        )

        data = self._normalize_fields(llm_result)

        # ------------------ Document Type ------------------
        doc_type = self.doc_type_service.infer(
            ocr_text=ocr_result["text"],
            llm_doc_type=data.get("document_type")
        )
        data["document_type"] = doc_type

        # ------------------ ID Number Rule Override ------------------
        ocr_id_number = self.id_number_service.extract(
            ocr_text=ocr_result["text"],
            document_type=doc_type
        )

        if ocr_id_number:
            data["document_number"] = ocr_id_number

        # ------------------ Confidence ------------------
        confidence = self.conf_service.calculate_confidence(
            data,
            required_fields,
            ocr_result=ocr_result
        )

        # ------------------ HITL Decision ------------------
        hitl_required, fallback_reason = self.determine_hitl(
            data=data,
            confidence=confidence,
            required_fields=required_fields
        )

        return {
            "data": data,
            "confidence": confidence,
            "hitl_required": hitl_required,
            "source": "ocr_llm",
            "fallback_reason": fallback_reason
        }

    # ------------------ HITL Logic ------------------

    def determine_hitl(self, data, confidence, required_fields):

        if not required_fields:
            return False, None

        missing_fields = [
            field for field in required_fields
            if data.get(field) in [None, "", "MISSING"]
        ]

        # If ALL required fields missing → OCR likely failed
        if len(missing_fields) == len(required_fields):
            return False, "low_ocr_quality"

        # Partial missing → ask human
        if missing_fields:
            return True, "partial_fields"

        # Low confidence → ask human
        if not self.conf_service.is_confident(confidence):
            return True, "low_confidence"

        return False, None

    # ------------------ Normalization ------------------

    def _normalize_fields(self, data):
        return {
            "document_type": data.get("document_type", "Unknown"),
            "name": data.get("name", "MISSING"),
            "date_of_birth": data.get("date_of_birth", "MISSING"),
            "document_number": data.get("document_number", "MISSING"),
            "address": data.get("address", "MISSING"),
        }

    def _empty_result(self):
        return {
            "document_type": "Unknown",
            "name": "MISSING",
            "date_of_birth": "MISSING",
            "document_number": "MISSING",
            "address": "MISSING",
        }