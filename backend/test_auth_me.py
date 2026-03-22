from fastapi.testclient import TestClient
from app.main import app
import traceback

client = TestClient(app)
try:
    # use the exact same token created in the previous step
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MmI5MzJiNC00NDU4LTQyZWYtYmExNC1iNTJmZTU1YzM5MjYiLCJyb2xlIjoidXNlciIsImV4cCI6MTc3NDEyMTUyMiwidHlwZSI6ImFjY2VzcyJ9.4YfuX842TcARzmL--RdMSUHcQlRv19BMAPTEUUB7RFE"
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    print("Status:", res.status_code)
    try:
        print(res.json())
    except:
        print(res.text)
except Exception as e:
    traceback.print_exc()
