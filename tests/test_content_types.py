import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.parametrize("content_type", ["informational", "commercial", "transactional"])
def test_all_content_types_outline(content_type):
    payload = {
        "language": "English",
        "region": "USA English",
        "content_type": content_type,
        "product_name": f"Cloud CRM Solutions for {content_type}",
        "tone": "professional",
        "sense": f"Targeting {content_type} audience intent",
        "word_count": 600,
        "include_meta": True
    }
    response = client.post("/api/v1/outline", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["outline"]) > 10
