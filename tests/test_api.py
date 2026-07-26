import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_outline_endpoint():
    payload = {
        "language": "English",
        "region": "USA English",
        "content_type": "informational",
        "product_name": "AI Writing Tool",
        "tone": "professional",
        "sense": "Explain benefits of automated humanized writing",
        "word_count": 800,
        "include_meta": True
    }
    response = client.post("/api/v1/outline", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["outline"]) > 10
    assert "competitor_analysis" in data

def test_generate_endpoint():
    outline_text = "# Outline: AI Writing Guide\n## 1. Intro\n- Overview\n## 2. Benefits\n- Key advantages\n## 3. Conclusion"
    payload = {
        "language": "English",
        "region": "USA English",
        "content_type": "informational",
        "product_name": "AI Writing Tool",
        "tone": "professional",
        "sense": "Explain benefits of automated humanized writing",
        "word_count": 800,
        "confirmed_outline": outline_text,
        "competitor_summary": "Competitors focus on speed and ease of setup.",
        "include_meta": True
    }
    response = client.post("/api/v1/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["final_content"]) > 30
    assert "lint_report" in data
    assert data["meta_description"] is not None

def test_humanize_endpoint():
    payload = {
        "content_type": "informational",
        "target_audience": "Small business owners",
        "tone": "professional",
        "text": "This is some previously generated content that needs to be rewritten so it reads naturally and sounds human."
    }
    response = client.post("/api/v1/humanize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "humanized_content" in data
    assert len(data["humanized_content"]) > 0
