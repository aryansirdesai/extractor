import requests

url = "http://127.0.0.1:8000/api/v1/documents/extract"
file_path = r"C:\\Users\\Admin\\Downloads\\Aadhar Card.jpg"

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print(response.json())