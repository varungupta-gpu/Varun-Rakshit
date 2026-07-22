from pydantic import BaseModel
from typing import Optional, Literal

class BallSegmentAnalysisRequest(BaseModel):
    """
    Incoming payload for the Cloud Run Job.
    Defines the contract between the orchestrator (GCP Workflow / API) and this job.
    """

    request_id: str
    user_id: Optional[str] = None
    video_id: str
    llm_insight_id: str
    segment_id: Optional[str] = None
    segment_insight_id: Optional[str] = None
    analysis_type: Optional[Literal["segment", "player"]] = None
    player_id: Optional[str] = None
    api_base_url: str
    bearer_access_token: str
