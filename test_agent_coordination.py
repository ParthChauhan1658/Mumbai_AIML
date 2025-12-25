import pytest
from unittest.mock import AsyncMock, patch
from app.core.orchestrator import ThreatAnalysisOrchestrator, ContentData, AnalysisOptions

@pytest.mark.asyncio
async def test_agent_coordination_flow():
    """
    Verify that the orchestrator correctly coordinates:
    Perception -> Scoring -> Pattern Match -> Defense
    """
    
    # We mock the internal agents but verify the data flow between them
    
    with patch("app.core.orchestrator.TextAnalyzer") as MockText, \
         patch("app.core.orchestrator.ThreatScorer") as MockScorer, \
         patch("app.core.orchestrator.PatternMatcher") as MockPatterns, \
         patch("app.core.orchestrator.DefenseAgent") as MockDefense:
         
        # Setup Mocks
        text_instance = MockText.return_value
        text_instance.analyze = AsyncMock(return_value=AsyncMock(
            model_dump=lambda: {"score": 50},
            threat_indicators=["indicator1"]
        ))
        
        scorer_instance = MockScorer.return_value
        scorer_instance.calculate_threat_score = AsyncMock(return_value=AsyncMock(
            overall_score=80,
            threat_type="Phishing",
            category="HIGH"
        ))
        
        pattern_instance = MockPatterns.return_value
        pattern_instance.find_matching_patterns = AsyncMock(return_value=["pattern1"])
        
        defense_instance = MockDefense.return_value
        defense_instance.determine_actions = AsyncMock(return_value=[AsyncMock(type="alert")])
        
        # Run Orchestrator
        orch = ThreatAnalysisOrchestrator()
        content = ContentData(text_content="test", sender="test")
        result = await orch.analyze_complete(content, options=AnalysisOptions(auto_respond=True))
        
        # Verify Flow
        text_instance.analyze.assert_called_once()
        # The scorer should receive the output from text analyzer
        scorer_instance.calculate_threat_score.assert_called_once()
        # The pattern matcher receives indicators
        pattern_instance.find_matching_patterns.assert_called_once()
        # The defense agent receives the score
        defense_instance.determine_actions.assert_called_once()
        
        # Final result check
        assert result.threat_assessment.category == "HIGH"
        assert len(result.actions_taken) > 0
