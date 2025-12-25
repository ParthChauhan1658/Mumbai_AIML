import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.orchestrator import ThreatAnalysisOrchestrator, ContentData, AnalysisOptions

# Mocks for dependencies
@pytest.fixture
def mock_text_analyzer():
    mock = AsyncMock()
    mock.analyze.return_value = MagicMock(
        model_dump=lambda: {"linguistic_risk_score": 80},
        threat_indicators=["urgent", "password_request"],
        sender_analysis=MagicMock(is_valid_domain=False)
    )
    return mock

@pytest.fixture
def mock_image_analyzer():
    mock = AsyncMock()
    mock.analyze_image.return_value = MagicMock(
        model_dump=lambda: {"visual_threat_score": 0}
    )
    return mock

@pytest.fixture
def mock_video_analyzer():
    mock = AsyncMock()
    mock.analyze_video.return_value = MagicMock(
        model_dump=lambda: {"deepfake_score": 0}
    )
    return mock

@pytest.fixture
def mock_scorer():
    mock = AsyncMock()
    mock.calculate_threat_score.return_value = MagicMock(
        overall_score=85,
        category="HIGH",
        threat_type="Phishing",
        recommended_actions=["Alert"],
        model_dump=lambda: {}
    )
    return mock

@pytest.fixture
def mock_matcher():
    mock = AsyncMock()
    mock.find_matching_patterns.return_value = []
    return mock

@pytest.fixture
def mock_defense():
    mock = AsyncMock()
    mock.determine_actions.return_value = [MagicMock(type="alert_user")]
    return mock

@pytest.mark.asyncio
async def test_analyze_complete_flow(
    mock_text_analyzer, mock_image_analyzer, mock_video_analyzer,
    mock_scorer, mock_matcher, mock_defense
):
    # Setup Orchestrator with mocks
    orch = ThreatAnalysisOrchestrator()
    orch.text_analyzer = mock_text_analyzer
    orch.image_analyzer = mock_image_analyzer
    orch.video_analyzer = mock_video_analyzer
    orch.threat_scorer = mock_scorer
    orch.pattern_matcher = mock_matcher
    orch.defense_agent = mock_defense
    
    # Input
    content = ContentData(
        text_content="Urgent wire transfer",
        sender="boss@fake.com"
    )
    options = AnalysisOptions(auto_respond=True)
    
    # Execute
    result = await orch.analyze_complete(content, options)
    
    # Verify Perception
    mock_text_analyzer.analyze.assert_called_once()
    mock_image_analyzer.analyze_image.assert_not_called() # No image provided
    
    # Verify Scorer
    mock_scorer.calculate_threat_score.assert_called_once()
    
    # Verify Patterns
    mock_matcher.find_matching_patterns.assert_called_once()
    
    # Verify Defense
    mock_defense.determine_actions.assert_called_once()
    
    # Verify Result
    assert result.threat_assessment.category == "HIGH"
    assert "alert_user" in result.actions_taken
    assert result.analysis_duration_ms > 0
