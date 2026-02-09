from app.services.openrouter_client import OpenRouterClient

client = OpenRouterClient()

ocr_text = """
GOVERNMENT OF INDIA
AADHAAR
Name: Rahul Sharma
DOB: 1971
1234 5678 9012
Pune Maharashtra
"""

print(client.extract_fields(ocr_text))