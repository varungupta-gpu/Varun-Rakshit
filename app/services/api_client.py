import logging, json, os, requests
import httpx
from typing import Dict, Any

from app.core.request_logging import request_id_context_var

logger = logging.getLogger(__name__)

class VideoApiClient:

#-------------------------------------------- Class constructor -----------------------------------------------------------------------------------------------

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token

#-------------------------------------------- make request -----------------------------------------------------------------------------------------------

    def _make_client(self) -> httpx.Client:
        """Returns an httpx.Client with default headers and X-Request-ID injection."""
        def _inject_request_id(request: httpx.Request) -> None:
            request_id = request_id_context_var.get()
            if request_id:
                request.headers["X-Request-ID"] = request_id

        default_headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",             # compress the json easy in sending
        }
        return httpx.Client(
            headers=default_headers,
            event_hooks={"request": [_inject_request_id]}
        )

#-------------------------------------------- segment level -----------------------------------------------------------------------------------------------
    
    def get_segment_insight_data(self, segment_insight_id: str) -> dict:
        """
        Fetch segment insight data from the API.
        """

        url = f"{self.base_url}/api/v1/insights/segment-insights/{segment_insight_id}"
        
        try:
            with self._make_client() as client:
                response = client.get(url, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"[API] HTTP Error {e.response.status_code} for {e.request.url}: {e.response.text}")
            raise e
        except httpx.RequestError as e:
            logger.error(f"[API] Request Error while requesting {e.request.url}: {e}")
            raise e

    def get_segment_attributes(self, video_id: str, segment_id: str) -> Dict[str, Any]:
        """
        Fetch segment attributes from the API.
        """

        url = (f"{self.base_url}/api/v1/videos/segments/{video_id}/{segment_id}/attributes")

        try:
            with self._make_client() as client:
                response = client.get(url, timeout=30.0)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"[API] HTTP Error {e.response.status_code} for {e.request.url}: {e.response.text}")
            raise

        except httpx.RequestError as e:
            logger.error(f"[API] Request Error while requesting {e.request.url}: {e}")
            raise

    def save_analysis_data(self, llm_insight_id: str, segment_insight_id: str, llm_analysis: dict, biomech_report: dict,  pipeline_context: dict):
        """
        Update the segment insight with llm analysis output.
        """
        if not llm_insight_id or not segment_insight_id :
            logger.warning("Missing required parameters for segment insight update")
            return False
        

        url = f"{self.base_url}/api/v1/insights/{llm_insight_id}/update"

        status = ("completed" if not pipeline_context["failed"] else "failed")

        payload = {
            "update_type": "llm_insights_update",
            "cv_segment_insight_id": segment_insight_id,
            "status": status,
            "data": llm_analysis,
            "bio_mechanics_report": biomech_report,
        }


        logger.debug(f"Updating segment insight.")
        
        try:
            with self._make_client() as client:
                response = client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                logger.info(f"Segment insight update successful")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"[API] HTTP Error {e.response.status_code} for {e.request.url}: {e.response.text}")
            raise e
        except httpx.RequestError as e:
            logger.error(f"[API] Request Error while requesting {e.request.url}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Failed to update segment insight {segment_insight_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise e
#--------------------------------------------for marking pipeline failed ------------------------------------------------------------------------------------

    def mark_pipeline_failed(self, llm_insight_id: str, segment_insight_id: str) -> Dict[str, Any]:
        """
        Mark segment pipeline as failed.
        """

        if not llm_insight_id or not segment_insight_id:
            logger.warning("Missing parameters for pipeline failure update")
            return False

        url = (f"{self.base_url}/api/v1/insights/{llm_insight_id}/segments/{segment_insight_id}")

        payload = {"pipeline_failed": True}

        logger.info(f"Marking pipeline failed for segment {segment_insight_id}")

        try:
            with self._make_client() as client:
                response = client.patch(url, json=payload, timeout=30.0)
                response.raise_for_status()
                logger.info(f"Pipeline failure marked successfully: {segment_insight_id}")
                return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"[API] HTTP Error {e.response.status_code} for {e.request.url}: {e.response.text}")
            raise e

        except httpx.RequestError as e:
            logger.error(f"[API] Request Error while requesting {e.request.url}: {e}")
            raise e

#--------------------------------------------player level -------------------------------------------------------------------------------------------

    def get_player_overview(self, player_id: str) -> dict:
        """
        Fetch batch insight session data.
        """

        if not player_id:
            logger.warning("Missing player_ids for API")
            return None

        url = f"{self.base_url}/api/v1/players/{player_id}/overview"
        logger.debug(f"Fetching batch insights")

        try:
            with self._make_client() as client:
                headers = {"api-key": "1b284812-7067-4e33-911e-848873099971"}
                response = client.get(url, headers=headers, timeout=60.0,)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"[API] HTTP Error {e.response.status_code} "
                f"for {e.request.url}: {e.response.text}"
            )
            raise e

        except httpx.RequestError as e:
            logger.error(
                f"[API] Request Error while requesting "
                f"{e.request.url}: {e}"
            )
            raise e
             
    def save_player_llm_analysis(self, player_id: str, final_player_report: dict, session_metrics) -> Dict[str, Any]:
        """
        Save player level LLM analysis.
        """

        url = (f"{self.base_url}/api/v1/players/{player_id}/llm-analysis")
        headers = {"api-key": "1b284812-7067-4e33-911e-848873099971"}
        biomechanics = session_metrics["session_biomechanics_analysis"]["segment_biomechanics_reports"]
        segment_ids = session_metrics["session_biomechanics_analysis"]["segment_ids"]
        segment_insight_ids = session_metrics["session_biomechanics_analysis"]["segment_insight_ids"]


        if isinstance(biomechanics, list):
            biomechanics = (
                biomechanics[0]["bio_mechanics_report"]
                if biomechanics else {}
            )

        payload = {
            "data": final_player_report,
            "bio_mechanics_report": biomechanics,
            "segment_ids": segment_ids,
            "segment_insight_ids": segment_insight_ids
        }


        logger.debug(f"Updating player LLM analysis at DB")

        try:

            with self._make_client() as client:
                response = client.put(url, json=payload, timeout=30.0, headers=headers)
                response.raise_for_status()
                logger.info(f"Player LLM analysis update successful")
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"[API] HTTP Error {e.response.status_code} for {e.request.url}: {e.response.text}")
            raise e

        except httpx.RequestError as e:
            logger.error(f"[API] Request Error while requesting {e.request.url}: {e}")

            raise e


