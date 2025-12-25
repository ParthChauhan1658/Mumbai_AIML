import pytest
from app.agents.threat_intelligence.pattern_matcher import PatternMatcher, ThreatPattern

@pytest.mark.asyncio
async def test_find_matching_patterns_exact():
    matcher = PatternMatcher()
    
    # Simulate indicators for CEO fraud
    indicators = ["urgent", "wire_transfer", "confidential", "executive_impersonation"]
    
    matches = await matcher.find_matching_patterns(indicators)
    
    # Should match ceo_fraud_001
    assert len(matches) > 0
    assert matches[0].pattern_id == "ceo_fraud_001"
    assert matches[0].similarity_score > 0.8

@pytest.mark.asyncio
async def test_find_matching_patterns_fuzzy():
    matcher = PatternMatcher()
    
    # Simulate indicators that partially match
    # "payroll" matches bec_payroll_update
    # "urgent" is generic
    # "random_thing" is noise
    indicators = ["payroll", "urgent", "random_thing", "update_account"]
    
    matches = await matcher.find_matching_patterns(indicators, confidence_threshold=0.5)
    
    # Should find matches
    match_ids = [m.pattern_id for m in matches]
    assert "bec_payroll_update" in match_ids

@pytest.mark.asyncio
async def test_add_pattern():
    matcher = PatternMatcher()
    
    new_pat = ThreatPattern(
        pattern_id="test_pat_001",
        pattern_type="test",
        indicators=["test_ind"],
        attack_category="test",
        severity="low",
        description="test"
    )
    
    pid = await matcher.add_pattern(new_pat)
    assert pid == "test_pat_001"
    
    matches = await matcher.find_matching_patterns(["test_ind"])
    assert matches[0].pattern_id == "test_pat_001"
