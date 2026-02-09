import os
import tempfile
from fastapi import APIRouter, UploadFile, Form
from app.services.extraction_service import ExtractionService

router = APIRouter()
extraction_service = ExtractionService()


@router.post("/extract")
async def extract_document(
    file: UploadFile,
    hitl_name: str = Form(None),
    hitl_date_of_birth: str = Form(None),
    hitl_document_number: str = Form(None),
    hitl_address: str = Form(None),
):
    tmp_file_path = None

    try:
        # ------------------ Save uploaded file ------------------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(await file.read())
            tmp_file_path = tmp.name

        # ------------------ First-pass AI extraction ------------------
        result = extraction_service.extract_document(tmp_file_path)

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

            # 🔥 CRITICAL FIX:
            # Re-infer document type AFTER HITL (never trust old type)
            result["data"]["document_type"] = extraction_service.infer_document_type(
                result["data"]
            )

            doc_type = result["data"]["document_type"]
            required_fields = extraction_service.required_fields_by_doc.get(doc_type, [])

            # Recompute confidence
            confidence = extraction_service.conf_service.calculate_confidence(
                result["data"], required_fields
            )

            # Recompute HITL
            hitl_required = extraction_service.determine_hitl(
                result["data"], confidence, required_fields
            )

            result["confidence"] = confidence
            result["hitl_required"] = hitl_required

        return result

    finally:
        # ------------------ Cleanup temp file ------------------
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)