import pytest
import numpy as np
import cv2
import json
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.perception.video_analyzer import VideoAnalyzer, VideoAnalysisResult

@pytest.fixture
def mock_gemini():
    with patch("app.models.gemini_client.GeminiClient") as MockClient:
        client_instance = MockClient.return_value
        yield client_instance

@pytest.fixture
def sample_video():
    # Create a dummy video file using OpenCV
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video_path = tfile.name
    tfile.close()

    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (64, 64))

    for _ in range(10):
        # Create a black frame
        frame = np.zeros((64, 64, 3), np.uint8)
        # Draw a moving rectangle
        cv2.rectangle(frame, (10, 10), (30, 30), (255, 255, 255), -1)
        out.write(frame)

    out.release()
    yield video_path
    
    # Cleanup
    if os.path.exists(video_path):
        os.remove(video_path)

@pytest.mark.asyncio
async def test_analyze_video(mock_gemini, sample_video):
    analyzer = VideoAnalyzer()
    
    mock_response = {
        "text": """
        {
            "deepfake_score": 15,
            "manipulation_type": "none",
            "frame_analyses": [],
            "temporal_inconsistencies": [],
            "overall_confidence": 0.9,
            "evidence_timeline": []
        }
        """
    }
    analyzer.gemini_client.analyze_multimodal = AsyncMock(return_value=mock_response)
    
    result = await analyzer.analyze_video(sample_video, frame_interval=1)
    
    assert isinstance(result, VideoAnalysisResult)
    assert result.deepfake_score == 15
    assert result.manipulation_type == "none"
    # Logic in VideoAnalyzer limits frames, creating at least 1?
    # The dummy video is short (10 frames at 20fps = 0.5s), extracting at 1s interval might result in 1 frame (frame 0)
    # The extraction loop gets frame 0, next step is frame_step (20). Loop breaks. So 1 frame.
    
    # Verify extraction logic was called implicitly
    assert analyzer.gemini_client.analyze_multimodal.called
