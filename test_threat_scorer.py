import pytest
from unittest.mock import AsyncMock
from app.agents.threat_intelligence.threat_scorer import ThreatScorer, PerceptionResults, ThreatAssessment, ThreatContext

@pytest.fixture
def threat_scorer():
    scorer = ThreatScorer()
    # Mock Gemini
    scorer.gemini_client = AsyncMock()
    scorer.gemini_client.analyze_text.return_value = {
        "text": """
        ```json
        {
            "threat_level": "HIGH",
            "attack_type": "Phishing",
            "confidence": 0.9,
            "reasoning": "Test reasoning",
            "recommended_actions": ["Block"]
        }
        ```
        """
    }
    return scorer

@pytest.mark.asyncio
async def test_threat_score_calculation(threat_scorer):
    '''Test threat score calculation logic'''
    
    # Create input with high text risk
    perception_results = PerceptionResults(
        text_analysis={"linguistic_risk_score": 85},
        image_analysis={},
        video_analysis={},
        metadata_analysis={},
        sender_reputation=0.5
    )
    
    result = await threat_scorer.calculate_threat_score(
        perception_results=perception_results,
        context=ThreatContext(timestamp="now")
    )
    
    # Base weight for linguistic is 0.35 * 85 ~= 29
    # Plus sender risk (1-0.5)*100 = 50 * 0.15 = 7.5
    # Total > 30.
    # Gemini mock says "HIGH", so it might boost the score.
    
    assert result.overall_score > 25
    assert result.category in ["HIGH", "CRITICAL", "MEDIUM"] 
    # With Mock returning HIGH and score boosting logic, likely HIGH

@pytest.mark.asyncio
async def test_threat_categorization(threat_scorer):
    '''Test threat category assignment'''
    # Access private method or just test via public API if possible.
    # Testing private method directly for unit test coverage
    
    # Test LOW category
    assert threat_scorer._categorize_threat(20) == "LOW"
    
    # Test MEDIUM category
    assert threat_scorer._categorize_threat(40) == "MEDIUM"
    
    # Test HIGH category
    assert threat_scorer._categorize_threat(65) == "HIGH"
    
    # Test CRITICAL category
    assert threat_scorer._categorize_threat(90) == "CRITICAL"
