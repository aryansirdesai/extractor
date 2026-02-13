import os
import tempfile
from fastapi import APIRouter, UploadFile, Form
from typing import Optional
from app.services.extraction_service import ExtractionService

router = APIRouter()
extraction_service = ExtractionService()


@router.post("/extract")
async def extract_document(
    file: UploadFile,
    required_fields: Optional[str] = Form(None),

    # HITL inputs (dynamic usage)
    hitl_name: str = Form(None),
    hitl_date_of_birth: str = Form(None),
    hitl_document_number: str = Form(None),
    hitl_address: str = Form(None),
):
    tmp_file_path = None

    try:
        # ------------------ Parse required fields ------------------
        parsed_required_fields = []
        if required_fields:
            parsed_required_fields = [
                field.strip()
                for field in required_fields.split(",")
                if field.strip()
            ]

        # ------------------ Save uploaded file ------------------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(await file.read())
            tmp_file_path = tmp.name

        # ------------------ First-pass AI extraction ------------------
        result = extraction_service.extract_document(
            file_path=tmp_file_path,
            required_fields=parsed_required_fields
        )

        # ------------------ HITL merge (if provided) ------------------
        hitl_fields = {
            "name": hitl_name,
            "date_of_birth": hitl_date_of_birth,
            "document_number": hitl_document_number,
            "address": hitl_address,
        }

        if any(value for value in hitl_fields.values()):

            # Overwrite AI output with human inputs
            for key, value in hitl_fields.items():
                if value:
                    result["data"][key] = value

            # Recalculate confidence using UPDATED required fields
            confidence = extraction_service.conf_service.calculate_confidence(
                result["data"],
                parsed_required_fields,
                {"status": "ok"}  # minimal safe OCR placeholder
            )

            hitl_required, _ = extraction_service.determine_hitl(
                data=result["data"],
                confidence=confidence,
                required_fields=parsed_required_fields
            )

            result["confidence"] = confidence
            result["hitl_required"] = hitl_required

        return result

    finally:
        # ------------------ Cleanup temp file ------------------
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)