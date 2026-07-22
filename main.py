import sys, os, json, logging, shutil, tempfile, pandas as pd
from pathlib import Path
from pydantic import ValidationError
from app.utils.langfuse_utils import langfuse
from app.core.logging_setup import setup_logging
from app.core.request_logging import request_id_context_var
from app.core.config import settings
from app.schemas.requests import BallSegmentAnalysisRequest
from app.services.api_client import VideoApiClient
from app.services.gcs_client import GCSClient
from app.pipeline.segment_pipeline.middleware.pipeline import run_pipeline
from app.pipeline.segment_pipeline.runner import run_full_analysis
from app.pipeline.session_pipeline.session.session_metrics import build_session_metrics
from app.pipeline.session_pipeline.session.session_metrics import combine_player_outputs
from app.pipeline.session_pipeline.session.session_metrics import add_phase_frames_to_injuries
from app.pipeline.session_pipeline.session.session_metrics import add_phase_frames_to_corrections
from app.pipeline.session_pipeline.session.session_agent import generate_session_analysis
from app.pipeline.session_pipeline.session.injury.injury_llm import generate_injury_risks
from app.pipeline.session_pipeline.session.correction.correction_llm import generate_corrections
import warnings


# from app.pipeline.segment_pipeline.middleware.pipeline import run_pipeline_batsman
# from app.pipeline.segment_pipeline.agents.batting_agent import generate_llm_analysis



warnings.filterwarnings("ignore", message="Your application has authenticated using end user credentials*")

setup_logging()

logger = logging.getLogger(__name__)

#-------------------------------- fetching segment level data -------------------------------------------
# function to get batter keypoints 
def setup_environment_for_batsman_csv(request: BallSegmentAnalysisRequest) -> pd.DataFrame:
    """
    Environment Setup for Batsman CSV

    - Fetches segment attributes
    - Extracts batter_pose_file_path (or similar field name)
    - Downloads CSV from GCS
    - Loads into pandas DataFrame

    Args:
        request: BallSegmentAnalysisRequest with api_base_url, bearer_access_token, video_id, segment_id

    Returns:
        batter_pose_df: DataFrame with batsman keypoints
    """
    logger.info("Environment Setup For Batsman CSV")

    api = VideoApiClient(base_url=request.api_base_url, token=request.bearer_access_token)

    try:
        # response = api.get_segment_attributes(video_id=request.video_id, segment_id=request.segment_id)
        response = api.get_segment_insight_data(segment_insight_id=request.segment_insight_id)
        logger.info("Segment attributes fetched successfully")

    except Exception:
        logger.exception("[ENVIRONMENT SETUP FAILURE] Failed to fetch segment attributes")
        raise

    try:
        # Try different possible field names for batsman keypoints
        batter_pose_file_path = response.get("data").get("results").get("artifacts").get("batter_all_keypoints_csv")
        logger.info(f"Batter pose file path extracted successfully: {batter_pose_file_path}")

    except Exception:
        logger.exception("[ENVIRONMENT SETUP FAILURE] Failed while fetching batter pose data csv url")
        raise

    # Download CSV from GCS
    gcs = GCSClient(bucket_name=settings.GCS_BUCKET_NAME)

    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_file:
            temp_csv_path = tmp_file.name

        logger.info(f"Downloading batter pose csv from: {batter_pose_file_path}")

        gcs.download_file(batter_pose_file_path, temp_csv_path)
        batter_pose_df = pd.read_csv(temp_csv_path)
        os.remove(temp_csv_path)
        logger.info("Batter pose csv loaded successfully")
        return batter_pose_df

    except Exception:
        logger.exception("[ENVIRONMENT SETUP FAILURE] Failed to download/read batter pose csv")
        raise


def setup_environment(request: BallSegmentAnalysisRequest) -> tuple:
    
    """
    Environment Setup
    - Fetches segment_insights
    - Extracts cv results
    - Extracts dqi scores
    - Extracts final_combined.json - read filepath from `artifacts.final_csv` and download from GCS
    - Extracts bowler_keypoints.csv - read filepath from `artifacts.pose_data_csv` and download from GCS

    Returns:
        (local_video_path, camera_data, pitch_data, stumps_data, world_data, video_metadata)
    """
    
    api = VideoApiClient(base_url=request.api_base_url, token=request.bearer_access_token)

    # Adding try except for API fetch completion.

    try:
        insight_resp = api.get_segment_insight_data(segment_insight_id=request.segment_insight_id)
        logger.info("Segment insight data fetched successfully")
        logger.info("segment_insight: \n", insight_resp)

    except Exception:
        logger.exception("[ENVIRONMENT SETUP FAILURE] Failed to fetch segment insight data from API")
        raise

    # Addind try except for response parsing completion 

    try:
        insight_data = insight_resp.get("data", {})
        status = insight_data.get("status", None)
        insight_type = insight_data.get("insight_type", None)

        if status != "completed":
            raise ValueError(f"Segment insight status is not completed: {status}")

        if insight_type != "ball_segment":
            raise ValueError(f"Segment insight type is not ball_segment: {insight_type}")

        results = insight_data.get("results", {})
        release_frame = results.get("release", {}).get("frame")


        print("===============================================================")
        print("release frame :")
        print(release_frame)
        print("===============================================================")

        dqi_report = results.get("dqi_report", {})
        artifacts = results.get("artifacts", {})

        del results["dqi_report"]
        del results["artifacts"]

        cv_data = results

    except Exception:
        logger.exception("[ENVIRONMENT SETUP FAILURE] Failed while parsing segment insight response")
        raise

    # Download final_combined.json from GCS :
 
    final_combined_json_path = artifacts.get("final_csv", None)
    bowler_keypoints_csv_path = artifacts.get("pose_data_csv", None)
    
    gcs = GCSClient(bucket_name=settings.GCS_BUCKET_NAME)

    local_final_combined_json_path = None

    # Adding try except for GCS final combined download completion

    if final_combined_json_path:
        try:
            local_final_combined_json_path = os.path.join(settings.DATA_DIR, f"{request.segment_id}/{request.segment_insight_id}_final_combined.json")
            gcs.download_file(final_combined_json_path, local_final_combined_json_path)

            logger.info("final_combined.json downloaded successfully")

        except Exception:
            logger.exception("[ENVIRONMENT SETUP FAILURE] Failed to download final_combined.json from GCS")
            raise
    
    local_bowler_keypoints_csv_path_for_bowling_arm = None
    
    # Adding try except for GCS bowler CSV download completion
    
    if bowler_keypoints_csv_path:
        try:
            local_bowler_keypoints_csv_path_for_bowling_arm = os.path.join(settings.DATA_DIR, f"{request.segment_id}/{request.segment_insight_id}_bowler_keypoints.csv")
            gcs.download_file(bowler_keypoints_csv_path, local_bowler_keypoints_csv_path_for_bowling_arm)
            logger.info("bowler_keypoints.csv used to fetch bowling arm downloaded successfully")

        except Exception:
            logger.exception("[ENVIRONMENT SETUP FAILURE] Failed to download bowler_keypoints.csv from GCS")
            raise

    return cv_data, dqi_report, local_final_combined_json_path, release_frame, local_bowler_keypoints_csv_path_for_bowling_arm

def setup_environment_for_csv(request: BallSegmentAnalysisRequest) -> pd.DataFrame:
    """
    Environment Setup for Bowler CSV

    - Fetches segment attributes
    - Extracts bowler_pose_file_path
    - Downloads CSV from GCS
    - Loads into pandas DataFrame

    Returns:
        bowler_pose_df
    """

    logger.info("Environment Setup For CSV")

    api = VideoApiClient(base_url=request.api_base_url, token=request.bearer_access_token)

    try:
        response = api.get_segment_attributes(video_id=request.video_id, segment_id=request.segment_id)
        logger.info("Segment attributes fetched successfully")

    except Exception:
        logger.exception("[ENVIRONMENT SETUP FAILURE] Failed to fetch segment attributes")
        raise


    try:
        bowler_pose_file_path = response.get("bowler_pose_file_path")
        if not bowler_pose_file_path:
            raise ValueError("bowler_pose_file_path not found in API response")
        
        logger.info("Bowler pose file path extracted successfully")

    except Exception:
        logger.exception("[ENVIRONMENT SETUP FAILURE] Failed while parsing attributes response")
        raise

    # Download CSV :
    gcs = GCSClient(bucket_name=settings.GCS_BUCKET_NAME)

    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_file:
            temp_csv_path = tmp_file.name

        logger.info(f"Downloading bowler pose csv")

        gcs.download_file(bowler_pose_file_path, temp_csv_path)
        bowler_pose_df = pd.read_csv(temp_csv_path)
        os.remove(temp_csv_path)
        logger.info("Bowler pose csv loaded successfully")
        return bowler_pose_df

    except Exception:
        logger.exception("[ENVIRONMENT SETUP FAILURE] Failed to download/read bowler pose csv")
        raise

# ----------------saving segment analysis data---------------------------------------------------

def save_data(request: BallSegmentAnalysisRequest, analysis_data: dict, biomech_report: dict,  pipeline_context: dict) -> bool:
    """
    Save data to DB using API

    Returns:
        Success status
    """
    api = VideoApiClient(base_url=request.api_base_url, token=request.bearer_access_token)
    try:
        api.save_analysis_data(llm_insight_id=request.llm_insight_id, segment_insight_id=request.segment_insight_id, llm_analysis=analysis_data, biomech_report=biomech_report,  pipeline_context=pipeline_context)
        logger.info("Segment analysis saved to DB successfully")
    
    except Exception:
        logger.exception("Failed to save analysis data")
        raise
    return True

# ----------------saving session analysis data---------------------------------------------------

def save_session_data( request: BallSegmentAnalysisRequest, final_player_report: dict, session_metrics) -> bool:
    """
    Save session analysis to DB using API
    """

    api = VideoApiClient( base_url=request.api_base_url, token=request.bearer_access_token)
    try:
        api.save_player_llm_analysis(player_id=request.player_id, final_player_report=final_player_report, session_metrics=session_metrics)
        logger.info("Session analysis saved to DB successfully")

    except Exception:
        logger.exception("Failed to save session analysis")
        raise

    return True

# ------------------------fetching session analysis data-------------------------------------------

def fetch_session_data( request: BallSegmentAnalysisRequest) -> dict:
    """
    Fetch session batch data from API.
    """

    api = VideoApiClient(base_url=request.api_base_url, token=request.bearer_access_token)

    # ==========================================
    # FETCH SESSION BATCH DATA
    # ==========================================

    try:
        response = api.get_player_overview(player_id=request.player_id)
        logger.info("Session batch insights fetched successfully")

    except Exception:
        logger.exception("[SESSION FETCH FAILURE] Failed to fetch session batch insights from API")
        raise

    # ==========================================
    # VALIDATE RESPONSE
    # ==========================================

    try:
        if not response:
            raise ValueError("Empty API response")
        
        if not isinstance(response, dict):
            raise ValueError("Player overview response must be dict")

        logger.info("Session batch API response validated successfully")

    except Exception:
        logger.exception("[SESSION FETCH FAILURE] Invalid session batch API response")
        raise

    return response


def handle_pipeline_failure(request: BallSegmentAnalysisRequest):

    """
    Update pipeline_failed=True
    when segment pipeline crashes.
    """

    try:

        api = VideoApiClient(base_url=request.api_base_url, token=request.bearer_access_token)

        api.mark_pipeline_failed(llm_insight_id=request.llm_insight_id, segment_insight_id=request.segment_insight_id)

        logger.info(f"Pipeline failure updated for segment_insight_id = {request.segment_insight_id}")

    except Exception :
        logger.exception("Failed to update pipeline failure status")


def main():

    # Handle both cases:
    # 1. API : single argument (sys.argv[1] is the JSON string)
    # 2. gcloud CLI: --args splits JSON on commas → multiple sys.argv entries
    if len(sys.argv) == 2:
        raw = sys.argv[1]
    elif len(sys.argv) > 2:
        raw = ",".join(sys.argv[1:])
        logger.info(f"Joined {len(sys.argv) - 1} comma-split args back into JSON")
    else:
        logger.error("Usage: python main.py '<json_payload>'")
        sys.exit(1)

    # Parse and validate
    try:
        req = BallSegmentAnalysisRequest(**json.loads(raw))
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Invalid payload: {e}")
        sys.exit(1)

    # Set request_id in context for logger and subsequent API calls
    _rid_token = request_id_context_var.set(req.request_id)

    try:

        try:
            # TODO: Add environment setup
            # =========================================================
            # SEGMENT ANALYSIS
            # =========================================================

            if req.analysis_type is None or not req.analysis_type or req.analysis_type == "segment":

                logger.info("===== RUNNING SEGMENT ANALYSIS =====")
                logger.info("Setting up environment...")

                pipeline_context = {
                    "failed": False,
                    "stage": None,
                    "error": None,
                }

            # Adding try except for checking the completion of the Environment setup.

                try:
                    cv_data, dqi_report, local_final_combined_json_path, release_frame, local_bowler_keypoints_csv_path_for_bowling_arm= setup_environment(req)
                    bowler_keypoint_df = setup_environment_for_csv(req)
                    logger.info("Environment setup completed successfully")

# #---------------------------Adding API check for the failure of complete setup_environment function ---------------------------

                except Exception as e:
                    logger.exception("[SEGMENT PIPELINE FAILURE] Environment setup failed")

                    pipeline_context["failed"] = True
                    pipeline_context["stage"] = "environment_setup"
                    pipeline_context["error"] = str(e)

                    cv_data = None
                    dqi_report = None
                    local_final_combined_json_path = None
                    release_frame = None
                    local_bowler_keypoints_csv_path_for_bowling_arm = None
                    bowler_keypoint_df = None

                logger.info("===== RUNNING PIPELINE =====")

                # Adding try except for checking pipeline completion detection

                if not pipeline_context["failed"] :

                    try:
                        json_data, biomech_report = run_pipeline(
                            cv_data,
                            dqi_report,
                            local_final_combined_json_path,
                            bowler_keypoint_df,
                            release_frame,
                            local_bowler_keypoints_csv_path_for_bowling_arm
                        )

                        logger.info("Middleware pipeline completed successfully")

                    except Exception as e:
                        logger.exception("[SEGMENT PIPELINE FAILURE] Middleware pipeline failed")
                        pipeline_context["failed"] = True
                        pipeline_context["stage"] = "middleware_pipeline"
                        pipeline_context["error"] = str(e)

                        json_data = None
                        biomech_report = None

                else:
                    # Previous stage already failed, so don't run middleware, just pass the empty middleware result  
                    json_data = None
                    biomech_report = None

                logger.info("===== RUNNING ANALYSIS =====")

                # Adding try except for LLM analysis completion detection 

                if not pipeline_context["failed"]:

                    try:
                        analysis_output = run_full_analysis(
                            json_data=json_data,
                            request_id=req.request_id,
                            user_id=getattr(req, "user_id", None)
                        )

                        logger.info("LLM analysis completed successfully")

                    except Exception as e:
                        logger.exception("[SEGMENT PIPELINE FAILURE] LLM analysis failed")

                        pipeline_context["failed"] = True
                        pipeline_context["stage"] = "llm_analysis"
                        pipeline_context["error"] = str(e)

                        analysis_output = None

                else:
                    # Previous stage already failed, so don't run LLM analysis
                    analysis_output = None

# #------------------------------------saving segment analysis data to DB-------------------------------------------------

                logger.info("Saving analysis to DB...")

                try:
                    # status = "failed" if pipeline_context["failed"] else "completed"
                    save_data(req, analysis_output, biomech_report,  pipeline_context=pipeline_context)

                    logger.info("Analysis saved successfully.")

                except Exception as e:
                    logger.exception("[SEGMENT PIPELINE FAILURE] Failed to save analysis data to DB")

                    if not pipeline_context["failed"]:
                        pipeline_context["failed"] = True
                        pipeline_context["stage"] = "save_data"
                        pipeline_context["error"] = str(e)

                    raise

                # Deleting that Data folder 
                # (we created that, coz we have to use it, then we delete that folder after it's use 😈)

                try:
                    if os.path.exists(settings.DATA_DIR):
                        shutil.rmtree(settings.DATA_DIR)
                        logger.info(f"DATA_DIR deleted successfully")

                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temporary files: {cleanup_error}")


                #batting agent
            
                try:
                    print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                    print("starting batter analysis...")
                    print("+++++++++++++++++++++++++++++++++++++++++++++++++")

                    pipeline_context_batter = {
                        "failed": False,
                        "stage": None,
                        "error": None,
                    }


                    logger.info("Starting Batsman Analysis Pipeline...")
                    
                    # Step 1: Get batsman keypoints
                    # batsman_keypoints_df = setup_environment_for_batsman_csv(req)
                    try:
                        batsman_keypoints_df = setup_environment_for_batsman_csv(req)
                    except Exception as e:
                        print(f"❌ Error while setting up batsman environment: {e}")
                        pipeline_context_batter["failed"] = True
                        pipeline_context_batter["stage"] = "environment_setup"
                        pipeline_context_batter["error"] = str(e)
                        batsman_keypoints_df = None


                    logger.info(f"Batsman keypoints loaded: {len(batsman_keypoints_df)} frames")
                    
                    # Step 2: Run batsman pipeline (phase prediction, biomechanics, stats)
                    # batting_report, batting_metadata = run_pipeline_batsman(batsman_keypoints_df)
                    if not pipeline_context_batter["failed"]:
                        try:
                            from app.pipeline.segment_pipeline.middleware.pipeline import run_pipeline_batsman
                            batting_report, batting_metadata = run_pipeline_batsman(batsman_keypoints_df)
                            logger.info("Batsman pipeline completed successfully")
                        except Exception as e:
                            logger.exception("❌ Error while running batsman pipeline")
                            pipeline_context_batter["failed"] = True
                            pipeline_context_batter["stage"] = "pipeline_execution"
                            pipeline_context_batter["error"] = str(e)
                            batting_report = None
                            batting_metadata = None

                    logger.info("Batsman pipeline completed successfully")
                    
                    # Step 3: Generate LLM analysis
                    batting_llm_output_dir = Path("output") / "batting_analysis" / f"{req.segment_id}_{req.segment_insight_id}"
                    batting_llm_output_dir.mkdir(parents=True, exist_ok=True)
                    
                    style_json = None
                    if not pipeline_context_batter["failed"]:

                        try:
                            from app.pipeline.segment_pipeline.agents.batting_agent import generate_llm_analysis
                            style_json = generate_llm_analysis(biomech_features_dict=batting_report["biomechanics_features"],statistics_dict=batting_report["biomechanics_statistics"], output_dir=batting_llm_output_dir)
                        except Exception as e:
                            logger.exception("❌ Error while generating batting LLM analysis")
                            pipeline_context_batter["failed"] = True
                            pipeline_context_batter["stage"] = "llm_analysis"
                            pipeline_context_batter["error"] = str(e)


                    if style_json:
                        batting_llm_json_path = batting_llm_output_dir / "style_analysis.json"
                        with open(batting_llm_json_path, 'r', encoding='utf-8') as f:
                            batting_llm_response = json.load(f)
                        
                        logger.info("Batsman LLM analysis generated successfully")
                        logger.info(f"Batsman LLM Response: {json.dumps(batting_llm_response, indent=2)}")
                    else:
                        logger.error("Batsman LLM analysis failed")
                        batting_llm_response = None
                        
                except Exception:
                    handle_pipeline_failure(req)
                    logger.exception("[BATTING PIPELINE FAILURE] Batsman analysis failed")
                    raise  

    #----------------------------Saving segment analysis in DB---------------------------------------------------------
                logger.info("Saving segment analysis to DB...")
                try:
                    # save_session_data(req, final_player_report, session_metrics)
                    save_data(req, batting_llm_response, batting_report,  pipeline_context=pipeline_context_batter)
                    # save_data(req, final_player_report, session_metrics)
                    logger.info("Segment Analysis Saved Successfully")

                except Exception:
                    handle_pipeline_failure(req)
                    logger.exception("[SEGMENT PIPELINE FAILURE] Failed to save segment analysis to DB")
                    raise

    #--------------------------------------------------------------------------------------------------------------------
                logger.info("===== SEGMENT ANALYSIS COMPLETE =====")

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#===================================================== PLAYER ANALYSIS =================================================================================================


            elif req.analysis_type == "player":

                logger.info("===== RUNNING Player ANALYSIS =====")

                # Adding try except for checking Player API fetch completion

                try:
                    session_api_response = fetch_session_data(req)
                    logger.info("Session batch API fetched successfully")

# #-------------------------Adding API check for the failure of complete fetch_session_data function-----------------------------

                except Exception:
                    # handle_pipeline_failure(req)
                    logger.exception("[SESSION PIPELINE FAILURE] Failed to fetch session batch API data")
                    raise

                # BUILD SESSION METRICS :

                # Adding try except for checking the session metrices completion

                try:
                    session_metrics = build_session_metrics(
                        session_api_response,
                        session_id=req.request_id,
                        user_id=getattr(req, "user_id", None),
                        metadata={"analysis_type": "session_metrics", "video_id": req.video_id, "llm_insight_id": req.llm_insight_id},
                        tags=["session-analysis", "metrics"]
                    )

                    logger.info("Session Metrics Generated")

# #---------------------Adding API check for the failure of complete build_session_metrics function------------------------------------

                except Exception:
                    handle_pipeline_failure(req)
                    logger.exception("[SESSION PIPELINE FAILURE] Failed while building session metrics")
                    raise

                # ==========================================
                # SESSION LLM ANALYSIS
                # ==========================================

            # Adding try except for checking the session llm analysis completion

                try:
                    session_analysis = generate_session_analysis(
                        session_metrics=session_metrics,
                        session_id=req.request_id,
                        user_id=getattr(req, "user_id", None),
                        trace_metadata={"analysis_type": "player_agent", "video_id": req.video_id, "llm_insight_id": req.llm_insight_id},
                        tags=["player-analysis", "llm-analysis"]
                    )
                    # =====================================================
                    # CLEAN LLM OUTPUT
                    # =====================================================

                    session_analysis = session_analysis.strip()

                    if session_analysis.startswith("```json"):
                        session_analysis = session_analysis.replace("```json", "", 1)

                    if session_analysis.startswith("```"):
                        session_analysis = session_analysis.replace("```", "", 1)

                    if session_analysis.endswith("```"):
                        session_analysis = session_analysis[:-3]

                    session_analysis = session_analysis.strip()
                    session_analysis_json = json.loads(session_analysis)

                    logger.info("Session LLM Analysis Generated")

                    # =====================================================
                    # Combined biomechanics for Injury and Correction
                    # =====================================================

                    combined_biomechanics_json = session_metrics["session_biomechanics_analysis"]["segment_biomechanics_reports"]

# #--------------------------------------------------------------------------------------------------------------------------------------------------------

                    # Generating Injury : 
                    logger.info("Generating Injury : ")

                    injuries = generate_injury_risks(combined_biomechanics_json)

                    injuries = injuries.strip()
                    if injuries.startswith("```json"):
                        injuries = injuries.replace("```json", "", 1)

                    elif injuries.startswith("```"):
                        injuries = injuries.replace("```", "", 1)

                    if injuries.endswith("```"):
                        injuries = injuries[:-3]

                    injuries = injuries.strip()
                    injuries_json = json.loads(injuries)

                    # Adding frames :
                    injury = add_phase_frames_to_injuries(injuries_json, combined_biomechanics_json)

# #--------------------------------------------------------------------------------------------------------------------------------------------------------

                    # Generating Correction : 
                    logger.info("Generating Correction : ")

                    corrections = generate_corrections(combined_biomechanics_json)
                    corrections = corrections.strip()

                    if corrections.startswith("```json"):
                        corrections = corrections.replace("```json", "",1)

                    if corrections.endswith("```"):
                        corrections = corrections[:-3]

                    corrections = corrections.strip()
                    corrections_json = json.loads(corrections)

                    # Adding frames :
                    correction = add_phase_frames_to_corrections(corrections_json, combined_biomechanics_json)

# #--------------------------------------------------------------------------------------------------------------------------------------------------------
                    
                    # Combining player_report, injury, correction :
                    logger.info("Combining player_report, injury, correction : ")
                    final_player_report = combine_player_outputs(session_analysis_json, correction, injury)


# #---------------------Adding API check for the failure of complete run_session_agent function---------------------

                except Exception:
                    handle_pipeline_failure(req)
                    logger.exception("[SESSION PIPELINE FAILURE] Session LLM analysis failed")
                    raise
        
        except Exception as e:
            logger.exception(f"Job failed with error: {e}")
            langfuse.flush()

        logger.info("Job execution finished.")
        langfuse.flush()

    finally:
        request_id_context_var.reset(_rid_token)


if __name__ == "__main__":
    main()
