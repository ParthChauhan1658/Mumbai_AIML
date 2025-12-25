import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.perception.text_analyzer import TextAnalyzer, TextAnalysisResult, SuspiciousUrl

# Mocking GeminiClient inside TextAnalyzer
@pytest.fixture
def text_analyzer():
    analyzer = TextAnalyzer()
    # Mock the internal gemini client
    analyzer.gemini_client = AsyncMock()
    analyzer.gemini_client.analyze_text.return_value = {
        "text": """
        ```json
        {
            "linguistic_score": 85,
            "sentiment": "urgent",
            "intent": "credential_theft",
            "urgency_score": 90,
            "ai_generated_prob": 0.1
        }
        ```
        """
    }
    return analyzer

@pytest.mark.asyncio
async def test_detect_urgency_patterns(text_analyzer):
    '''Test urgency detection'''
    content = "URGENT: Wire transfer needed immediately!"
    
    # Mock gemini to return high urgency
    text_analyzer.gemini_client.analyze_text.return_value = {
        "text": '{"linguistic_score": 80, "urgency_score": 90}'
    }
    
    result = await text_analyzer.analyze(
        content=content,
        sender="test@fake.com",
        subject="Urgent"
    )
    
    # Check for rule-based indicators or Gemini result
    # Note: precise score depends on implementation, but should be high
    assert result.linguistic_risk_score > 50
    # Check if any indicator relates to urgency
    assert any(ind.type == "urgency" for ind in result.threat_indicators)

@pytest.mark.asyncio
async def test_detect_credential_request(text_analyzer):
    '''Test credential harvesting detection'''
    content = "Please verify your password by clicking here"
    
    result = await text_analyzer.analyze(
        content=content,
        sender="security@fake.com"
    )
    
    # Rule based matcher should catch "verify your password"
    assert any(ind.type == "credential_request" for ind in result.threat_indicators)
    assert result.linguistic_risk_score > 40

@pytest.mark.asyncio
async def test_legitimate_email_low_score(text_analyzer):
    '''Test legitimate email receives low score'''
    content = "Thanks for the meeting today. Attached is the report."
    
    # Mock gemini to return low risk
    text_analyzer.gemini_client.analyze_text.return_value = {
        "text": '{"linguistic_score": 10, "urgency_score": 0}'
    }
    
    result = await text_analyzer.analyze(
        content=content,
        sender="colleague@company.com",
        subject="Report"
    )
    
    assert result.linguistic_risk_score < 30
    assert result.confidence > 0.0

@pytest.mark.asyncio
async def test_url_extraction(text_analyzer):
    '''Test URL extraction and analysis'''
    content = "Click here: http://192.168.1.1/fake-login.php"
    
    result = await text_analyzer.analyze(
        content=content,
        sender="test@test.com"
    )
    
    assert len(result.suspicious_urls) > 0
    assert result.suspicious_urls[0].is_suspicious
    assert "IP address" in result.suspicious_urls[0].reason

@pytest.mark.asyncio
async def test_ai_generated_detection(text_analyzer):
    '''Test AI-generated text detection'''
    content = """Dear valued customer, 
    We appreciate your continued patronage. In order to maintain the highest 
    standards of security, we kindly request that you verify your credentials 
    at your earliest convenience."""
    
    # Mock Gemini to say it's AI generated
    text_analyzer.gemini_client.analyze_text.return_value = {
        "text": '{"linguistic_score": 60, "ai_generated_prob": 0.9}'
    }
    
    result = await text_analyzer.analyze(content=content, sender="test@test.com")
    # Our implementation might set this from Gemini
    assert result.ai_generated_probability > 0.6
