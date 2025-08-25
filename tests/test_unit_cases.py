# tests/test_unit_cases.py

import pytest
from fastapi.testclient import TestClient
from api.main import app   # or your FastAPI entrypoint

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200 # 200 means okay
    assert "Document Portal" in response.text # title of our application, check index.html