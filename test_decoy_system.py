import pytest
from unittest.mock import AsyncMock, patch
from app.agents.defense.decoy_system import DecoySystem, DecoyDeployment

@pytest.fixture
def mock_gemini():
    with patch("app.models.gemini_client.GeminiClient") as MockClient:
        client_instance = MockClient.return_value
        yield client_instance

@pytest.mark.asyncio
async def test_deploy_decoy(mock_gemini):
    system = DecoySystem()
    
    mock_response = {
        "text": "Hi, I am looking into this request. Can you verify your account number?"
    }
    system.gemini_client.analyze_text = AsyncMock(return_value=mock_response)
    
    deployment = await system.deploy_decoy(
        threat_id="t1",
        sender="badguy@evil.com",
        original_message="Wire me money now.",
        decoy_type="information_request"
    )
    
    assert isinstance(deployment, DecoyDeployment)
    assert deployment.sender == "badguy@evil.com"
    assert deployment.active is True
    assert system.gemini_client.analyze_text.called

@pytest.mark.asyncio
async def test_track_interaction(mock_gemini):
    system = DecoySystem()
    
    # Manually seed a deployment/intel since we don't have DB persistence
    # To test tracking, we first need to deploy to init the dicts
    system.gemini_client.analyze_text = AsyncMock(return_value={"text": "ok"})
    deployment = await system.deploy_decoy("t1", "s1", "msg")
    
    await system.track_decoy_interaction(
        deployment.decoy_id,
        "clicked_link",
        {"ip": "10.0.0.1", "user_agent": "Mozilla/5.0"}
    )
    
    intel = await system.analyze_decoy_intelligence(deployment.decoy_id)
    assert "clicked_link" in intel.attacker_actions
    assert "10.0.0.1" in intel.ip_addresses
