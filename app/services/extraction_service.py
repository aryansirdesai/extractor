from app.services.gemini_client import GeminiClient
from app.services.confidence_service import ConfidenceService


class ExtractionService:
    def __init__(self):
        self.client = GeminiClient()
        self.conf_service = ConfidenceService()

        self.required_fields_by_doc = {
            "Aadhaar": ["name", "date_of_birth", "document_number", "address"],
            "PAN": ["name", "date_of_birth", "pan_number"],
            "Passport": [
                "name",
                "date_of_birth",
                "passport_number",
                "nationality",
                "expiry_date"
            ],
        }

    def extract_document(self, file_path):
        extracted_text = self.client.extract_text(file_path)
        extracted_fields = self.parse_extracted_text(extracted_text)

        # Backend authority over document_type
        ai_doc_type = extracted_fields.get("document_type")
        if ai_doc_type in [None, "MISSING", "INVALID", "Unknown"]:
            extracted_fields["document_type"] = self.infer_document_type(
                extracted_fields
            )

        doc_type = extracted_fields.get("document_type", "Unknown")
        required_fields = self.required_fields_by_doc.get(doc_type, [])

        # ✅ REAL confidence calculation
        confidence = self.conf_service.calculate_confidence(
            extracted_fields,
            required_fields
        )

        hitl_required = self.determine_hitl(
            extracted_fields,
            confidence,
            required_fields
        )

        return {
            "data": extracted_fields,
            "confidence": confidence,
            "hitl_required": hitl_required
        }

    def parse_extracted_text(self, extracted_text):
        if not isinstance(extracted_text, dict):
            return {}

        return {
            "document_type": extracted_text.get("document_type"),
            "name": extracted_text.get("name"),
            "date_of_birth": extracted_text.get("date_of_birth"),
            "document_number": extracted_text.get("document_number"),
            "address": extracted_text.get("address"),
        }

    def infer_document_type(self, extracted_fields: dict) -> str:
        doc_no = extracted_fields.get("document_number", "")

        if doc_no:
            digits = doc_no.replace(" ", "")
            if digits.isdigit() and len(digits) == 12:
                return "Aadhaar"

        return "Unknown"

    def determine_hitl(self, extracted_fields, confidence, required_fields):
        # Missing or invalid fields
        for field in required_fields:
            value = extracted_fields.get(field)
            if not value or value in ["MISSING", "INVALID"]:
                return True

        # Low confidence
        return not self.conf_service.is_confident(confidence)