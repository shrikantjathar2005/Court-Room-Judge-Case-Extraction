from fastapi.testclient import TestClient
from app.main import app
import traceback

client = TestClient(app)
try:
    response = client.post("/api/auth/register", json={
        "email": "test5@example.com",
        "password": "password123",
        "full_name": "Test",
        "role": "user"
    })
    print("Status:", response.status_code)
    try:
        print(response.json())
    except:
        print(response.text)
except Exception as e:
    traceback.print_exc()
