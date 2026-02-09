def DOCUMENT_EXTRACTION_PROMPT() -> str:
    """
    Returns the formatted prompt template used for Gemini AI.
    """
    return (
        "You are an AI document extraction assistant.\n\n"
        "Your task is to extract structured JSON data from Indian identity documents.\n\n"

        "You MUST identify the document type.\n"
        "Allowed values for document_type:\n"
        "- Aadhaar\n"
        "- PAN\n"
        "- Passport\n"
        "- Unknown\n\n"

        "Rules:\n"
        "- If a field is missing or unreadable, return 'MISSING'.\n"
        "- Do NOT guess sensitive fields.\n"
        "- document_type must NEVER be 'MISSING' or 'INVALID'.\n"
        "- If unsure about document type, return 'Unknown'.\n\n"

        "Extract the following fields:\n"
        "- document_type\n"
        "- name\n"
        "- date_of_birth\n"
        "- document_number\n"
        "- address\n\n"

        "Return ONLY valid JSON. No markdown. No explanation."
    )

# DOCUMENT_EXTRACTION_PROMPT = """
# You are an AI document extraction assistant.
# Your task is to extract structured JSON data from documents such as Aadhaar, PAN, Passport, etc.

# Important Notes:
# - HITL (Human in the Loop) Required: {hitl_required}
#   - If HITL is True, prioritize marking missing fields and do not guess sensitive information.
#   - If HITL is False, extract all fields as accurately as possible.
# - Always return valid JSON with the following fields based on document type.

# Required fields by document type:
# - Aadhaar: name, date_of_birth, document_number, address
# - PAN: name, date_of_birth, pan_number
# - Passport: name, date_of_birth, passport_number, nationality, expiry_date

# Rules:
# - Do not invent data.
# - Mark fields missing or null if uncertain.
# - Use double quotes for JSON keys and string values.

# Respond ONLY with JSON.
# HITL Required: {hitl_required}
# Document Type: {document_type}

# Document Content: 
# {document_text}
# """



# """
# Professional document extraction prompt template for Gemini Flash.
# This can be tuned for different document types (Aadhaar, PAN, Passport, etc.)
# """

# PROMPT_TEMPLATE = """
# You are a highly accurate document extraction AI. 

# Task:
# 1. Identify the type of the document: Aadhaar, PAN, Passport, or Other.
# 2. Extract all visible fields relevant to the document type:
#    - Aadhaar: name, date_of_birth, aadhar_number, address
#    - PAN: name, date_of_birth, pan_number
#    - Passport: name, date_of_birth, passport_number, nationality, expiry_date
# 3. Return results strictly in JSON format. 
# 4. If a field is not visible or invalid, return null.
# 5. Respond only in JSON, do not include extra text.

# Example response for Aadhaar:

# {
#   "document_type": "Aadhaar",
#   "name": "John Doe",
#   "date_of_birth": "YYYY-MM-DD",
#   "aadhar_number": "XXXX XXXX XXXX",
#   "address": "Full address string"
# }

# Use this prompt consistently for all document uploads.
# """