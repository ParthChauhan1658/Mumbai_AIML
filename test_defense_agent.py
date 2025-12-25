import pytest
from app.agents.defense.action_executor import DefenseAgent, Action
from app.agents.threat_intelligence.threat_scorer import ThreatAssessment

@pytest.fixture
def mock_assessment():
    return ThreatAssessment(
        overall_score=85,
        category="CRITICAL",
        confidence=0.9,
        threat_type="Phishing",
        attack_vector="Email",
        contributing_factors=[],
        matched_patterns=[],
        recommended_actions=[],
        explanation="Test",
        risk_breakdown={}
    )

@pytest.mark.asyncio
async def test_determine_actions_critical(mock_assessment):
    agent = DefenseAgent()
    
    # Test CRITICAL level
    mock_assessment.category = "CRITICAL"
    actions = await agent.determine_actions(mock_assessment, auto_execute=False)
    
    types = [a.type for a in actions]
    assert "quarantine" in types
    assert "block_sender" in types
    assert "deploy_decoy" in types
    
    # Check priority sorting (quarantine is 4, block is 3)
    assert actions[0].type == "quarantine"

@pytest.mark.asyncio
async def test_determine_actions_low(mock_assessment):
    agent = DefenseAgent()
    
    mock_assessment.category = "LOW"
    actions = await agent.determine_actions(mock_assessment, auto_execute=False)
    
    assert len(actions) == 1
    assert actions[0].type == "log"

@pytest.mark.asyncio
async def test_execute_actions(mock_assessment):
    agent = DefenseAgent()
    
    actions = [
        Action(type="quarantine", priority=1),
        Action(type="alert_user", priority=1)
    ]
    
    results = await agent.execute_actions(actions, context={})
    
    assert len(results) == 2
    assert all(r.success for r in results)
    assert results[0].details["status"] == "secured"
