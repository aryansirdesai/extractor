class ConfidenceService:
    """
    Computes confidence using field-level weighting.
    """

    FIELD_WEIGHTS = {
        "document_number": 0.35,
        "date_of_birth": 0.20,
        "name": 0.15,
        "address": 0.15,
        "document_type": 0.15,
    }

    CONFIDENCE_THRESHOLD = 0.65

    def calculate_confidence(self, data, required_fields, ocr_result=None):
        if not required_fields:
            return 0.0

        score = 0.0
        max_score = 0.0

        for field in required_fields:
            weight = self.FIELD_WEIGHTS.get(field, 0.1)
            max_score += weight

            value = data.get(field)

            if value and value != "MISSING":
                score += weight

        # OCR quality bonus (important)
        if ocr_result:
            if ocr_result.get("char_count", 0) > 300:
                score += 0.05
            if ocr_result.get("line_count", 0) > 5:
                score += 0.05

        final_confidence = min(score / max_score, 1.0)
        return round(final_confidence, 2)

    def is_confident(self, confidence: float) -> bool:
        return confidence >= self.CONFIDENCE_THRESHOLD