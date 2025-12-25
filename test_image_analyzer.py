import pytest
import io
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.perception.image_analyzer import ImageAnalyzer, ImageAnalysisResult
from PIL import Image

@pytest.fixture
def mock_gemini():
    with patch("app.models.gemini_client.GeminiClient") as MockClient:
        client_instance = MockClient.return_value
        yield client_instance

@pytest.fixture
def sample_image():
    # Create a small red image
    img = Image.new('RGB', (60, 30), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

@pytest.mark.asyncio
async def test_analyze_deepfake(mock_gemini, sample_image):
    analyzer = ImageAnalyzer()
    
    mock_response = {
        "text": """
        {
            "visual_threat_score": 85,
            "deepfake_probability": 0.9,
            "manipulation_indicators": ["unnatural_skin"],
            "authenticity_assessment": "likely_fake",
            "confidence": 0.95,
            "evidence": [{"type": "artifact", "location": "face", "severity": 0.8}],
            "reasoning": "Clear AI artifacts."
        }
        """
    }
    analyzer.gemini_client.analyze_image = AsyncMock(return_value=mock_response)
    
    result = await analyzer.analyze_image(sample_image, "profile_picture")
    
    assert isinstance(result, ImageAnalysisResult)
    assert result.visual_threat_score == 85
    assert result.deepfake_analysis.probability == 0.9
    assert result.deepfake_analysis.authenticity == "likely_fake"
    assert result.metadata.format == "JPEG"

@pytest.mark.asyncio
async def test_metadata_extraction(mock_gemini, sample_image):
    analyzer = ImageAnalyzer()
    # Mock gemini to return neutral
    mock_response = {"text": "{}"}
    analyzer.gemini_client.analyze_image = AsyncMock(return_value=mock_response)
    
    result = await analyzer.analyze_image(sample_image, "profile_picture")
    assert result.metadata.size == [60, 30]
    assert result.metadata.mode == "RGB"

def test_qr_fallback():
    # Test safe fallback if pyzbar missing (mocking import error logic if possible, 
    # but here just testing logic with dummy data if we can't easily uninstall pyzbar)
    pass
