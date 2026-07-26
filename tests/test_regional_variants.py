import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.parametrize("region", ["USA English", "UK English", "Australia English", "Canada English"])
def test_regional_variants(region):
    payload = {
        "language": "English",
        "region": region,
        "content_type": "informational",
        "product_name": "Smart Office Assistant",
        "tone": "casual",
        "sense": "Explain ease of use in localized context",
        "word_count": 500,
        "include_meta": True
    }
    response = client.post("/api/v1/outline", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["request_params"]["region"] == region
