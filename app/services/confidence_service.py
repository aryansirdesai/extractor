class ConfidenceService:
    """
    Deterministic confidence scoring based on field completeness.
    """

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def calculate_confidence(self, extracted_fields: dict, required_fields: list) -> float:
        if not required_fields:
            return 0.0

        valid_count = 0

        for field in required_fields:
            value = extracted_fields.get(field)
            if value and value not in ["MISSING", "INVALID"]:
                valid_count += 1

        confidence = valid_count / len(required_fields)
        return round(confidence, 2)

    def is_confident(self, confidence: float) -> bool:
        return confidence >= self.threshold