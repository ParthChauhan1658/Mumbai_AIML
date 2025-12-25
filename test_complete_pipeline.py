import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from unittest.mock import AsyncMock, patch

# In E2E, we want to simulate the real application as much as possible.
# However, we still MUST mock the external Gemini/Vertex API calls 
# to avoid costs and flakiness. The rest of the system (FastAPI, Orchestrator, Classes)
# runs "for real".

@pytest.fixture
def mock_gemini_response():
    with patch("app.models.gemini_client.GeminiClient.analyze_text", new_callable=AsyncMock) as mock_analyze:
        # Default mock response for TextAnalyzer and ThreatScorer
        mock_analyze.return_value = {
            "text": """
            ```json
            {
                "threat_score": 85,
                "threat_confidence": 0.9,
                "summary": "Phishing detected",
                "indicators": ["urgent", "link"],
                "threat_level": "HIGH",
                "attack_type": "Phishing",
                "confidence": 0.9,
                "reasoning": "Detected urgent language",
                "recommended_actions": ["Alert"]
            }
            ```
            """
        }
        yield mock_analyze

@pytest.mark.asyncio
async def test_complete_pipeline_phishing_email(mock_gemini_response):
    """
    Simulate a user submitting a phishing email via API.
    Expect: Full analysis + Threat Detection + Defense Action
    """
    
    payload = {
        "content_type": "email", 
        "text_content": "URGENT: Click this link to verify your account now.",
        "sender": "attacker@evil.com",
        "subject": "Account Alert",
        "auto_respond": "true"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/analyze/complete", data=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # 1. Check Analysis ID
    assert "analysis_id" in data
    
    # 2. Check Perception/Scoring (driven by our mock but processed by the system)
    # The Scorer uses "HIGH" because our mock returns threat_level="HIGH"
    assert data["threat_category"] in ["HIGH", "CRITICAL"]
    
    # 3. Check Defense Actions
    # High threat should trigger actions like 'quarantine' or 'alert_user' (from DefenseAgent logic)
    assert len(data["actions_taken"]) > 0
    assert "quarantine" in data["actions_taken"] or "alert_user" in data["actions_taken"]
    
    # 4. Check Detailed Report
    assert "detailed_report" in data
