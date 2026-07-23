from typing import Dict, Any, List
import statistics
import copy,json

from app.pipeline.session_pipeline.session.session_schema import EMPTY_SESSION_SCHEMA

from app.utils.langfuse_utils import get_langfuse_config
from langchain_core.runnables import RunnableLambda

# =========================================================
# VALIDATION
# =========================================================

def validate_session_data(api_response: Dict[str, Any]) -> List[Dict]:
    """
    Validate raw API response structure.

    Returns:
        segments list

    Raises:
        ValueError if structure is invalid
    """

    if not isinstance(api_response, dict):
        raise ValueError("api_response must be a dictionary")

    data = api_response.get("data", {})
    segments = data.get("segments")

    if segments is None:
        raise ValueError("Missing 'segments' field in API response")

    if not isinstance(segments, list):
        raise ValueError("'segments' must be a list")

    if len(segments) == 0:
        raise ValueError("No segments found in API response")

    return segments

# =========================================================
# MATH HELPERS
# =========================================================

def calculate_mean(numbers: List[float]) -> float:
    return round(sum(numbers) / len(numbers), 2) if numbers else 0


def calculate_max(numbers: List[float]) -> float:
    return round(max(numbers), 2) if numbers else 0


def calculate_min(numbers: List[float]) -> float:
    return round(min(numbers), 2) if numbers else 0


def calculate_median(numbers: List[float]) -> float:
    return round(statistics.median(numbers), 2) if numbers else 0


def calculate_std(numbers: List[float]) -> float:
    return round(statistics.pstdev(numbers), 2) if len(numbers) > 1 else 0


def calculate_variance(numbers: List[float]) -> float:
    return round(statistics.pvariance(numbers), 2) if len(numbers) > 1 else 0

# =========================================================
# EXTRACTION HELPERS
# =========================================================

def extract_speed(segment: Dict) -> float:
    return (segment.get("data", {}).get("speed"))


def extract_release_height(segment: Dict) -> float:
    return (segment.get("data", {}).get("dqi_report", {}).get("meta", {}).get("events", {}).get("release_height_m"))


def extract_bounce_x(segment: Dict) -> float:
    return (segment.get("data", {}).get("bounce", {}).get("x"))


def extract_bounce_y(segment: Dict) -> float:
    return (segment.get("data", {}).get("bounce", {}).get("y"))


def extract_trajectory_points(segment: Dict) -> int:
    trajectory = (segment.get("data", {}).get("trajectory", []))
    return len(trajectory)


def extract_flight_time(segment: Dict) -> float:
    return (segment.get("data", {}).get("physics", {}).get("flight_time_s"))


def extract_distance_3d(segment: Dict) -> float:
    return (segment.get("data", {}).get("physics", {}).get("straight_line_distance_3d_m"))


def extract_speed_mps(segment: Dict) -> float:
    return (segment.get("data", {}).get("physics", {}).get("speed_mps"))


def extract_rmse(segment: Dict) -> float:
    return (segment.get("data", {}).get("dqi_report", {}).get("meta", {}).get("stability", {}).get("rmse"))


def extract_smoothness(segment: Dict) -> float:
    return (segment.get("data", {}).get("dqi_report", {}).get("meta", {}).get("stability", {}).get("m_smoothness"))


def extract_bad_jumps(segment: Dict) -> int:
    return (segment.get("data", {}).get("dqi_report", {}).get("meta", {}).get("stability", {}).get("bad_jumps"))


# =========================================================
# MAIN SESSION METRICS BUILDER
# =========================================================

def build_session_metrics(api_response: Dict[str, Any], session_id: str = None, user_id: str = None, metadata: Dict[str, Any] = None, tags: List[str] = None) -> Dict[str, Any]:
    """
    Main deterministic session analytics engine.
    Flow:
        Raw API Response
            ↓
        Validation
            ↓
        calculate Extraction
            ↓
        Mathematical Calculations
            ↓
        Final Metrics JSON
    """

    # =====================================================
    # Traces for langfuse
    # =====================================================

    runner = RunnableLambda(lambda x: x).with_config({**get_langfuse_config(session_id=session_id, user_id=user_id, trace_name="session_metrics", metadata=metadata, tags=tags), "run_name": "session_metrics"})
    
    try :

        # =====================================================
        # VALIDATE :
        # =====================================================

        segments = validate_session_data(api_response)

        # =====================================================
        # EXTRACT ARRAYS :
        # =====================================================

        speeds = []
        release_heights = []
        bounce_x_values = []
        bounce_y_values = []

        trajectory_points = []
        flight_times = []
        distances_3d = []
        speed_mps_values = []

        rmse_values = []
        smoothness_values = []
        bad_jumps_values = []

        # =====================================================
        # BIOMECHANICS
        # =====================================================

        segment_ids = []
        segment_insight_ids = []
        combined_llm_insights = []
        combined_biomechanics_reports = []


        # =====================================================
        # calculate EXTRACTION LOOP
        # =====================================================

        for segment in segments:

            # ---------------- SPEED ----------------

            speed = extract_speed(segment)
            if isinstance(speed, (int, float)):
                speeds.append(speed)

            # ---------------- RELEASE ----------------

            release_height = extract_release_height(segment)
            if isinstance(release_height, (int, float)):
                release_heights.append(release_height)

            # ---------------- BOUNCE ----------------

            bounce_x = extract_bounce_x(segment)
            if isinstance(bounce_x, (int, float)):
                bounce_x_values.append(bounce_x)

            bounce_y = extract_bounce_y(segment)
            if isinstance(bounce_y, (int, float)):
                bounce_y_values.append(bounce_y)

            # ---------------- TRAJECTORY ----------------

            trajectory_count = extract_trajectory_points(segment)
            if isinstance(trajectory_count, int):
                trajectory_points.append(trajectory_count)

            # ---------------- PHYSICS ----------------

            flight_time = extract_flight_time(segment)
            if isinstance(flight_time, (int, float)):
                flight_times.append(flight_time)

            distance_3d = extract_distance_3d(segment)
            if isinstance(distance_3d, (int, float)):
                distances_3d.append(distance_3d)

            speed_mps = extract_speed_mps(segment)
            if isinstance(speed_mps, (int, float)):
                speed_mps_values.append(speed_mps)

            # ---------------- STABILITY ----------------

            rmse = extract_rmse(segment)
            if isinstance(rmse, (int, float)):
                rmse_values.append(rmse)

            smoothness = extract_smoothness(segment)
            if isinstance(smoothness, (int, float)):
                smoothness_values.append(smoothness)

            bad_jumps = extract_bad_jumps(segment)
            if isinstance(bad_jumps, (int)):
                bad_jumps_values.append(bad_jumps)


            # =====================================================
            # BIOMECHANICS
            # =====================================================

            llm_segment_insight = segment.get("llm_segment_insight")

            print("==========================================")
            print("llm_segment_insight", llm_segment_insight)
            print("==========================================")
            if llm_segment_insight and llm_segment_insight.get("id"):
        
                segment_ids.append(segment.get("segment_id"))

                segment_insight_ids.append(llm_segment_insight.get("id"))

                results = llm_segment_insight.get("results", {})

                llm_insights = results.get("llm_insights")

                if llm_insights:
                    combined_llm_insights.append(llm_insights)

                bio_mechanics_report = results.get("bio_mechanics_report")

                if bio_mechanics_report:
                    combined_biomechanics_reports.append({
                        "segment_id": segment.get("segment_id"),
                        "bio_mechanics_report": bio_mechanics_report
                    })

        # =====================================================
        # BUILD FINAL JSON
        # =====================================================

        session_metrics = copy.deepcopy(EMPTY_SESSION_SCHEMA)

        # =====================================================
        # SESSION BIOMECHANICS ANALYSIS
        # =====================================================

        session_metrics["session_biomechanics_analysis"]["segment_ids"] = segment_ids
        session_metrics["session_biomechanics_analysis"]["segment_insight_ids"] = segment_insight_ids
        session_metrics["session_biomechanics_analysis"]["segment_llm_insights"] = combined_llm_insights
        session_metrics["session_biomechanics_analysis"]["segment_biomechanics_reports"] = combined_biomechanics_reports

        # =====================================================
        # SESSION METADATA
        # =====================================================

        # session_metrics["session_metadata"]["session_id"] = api_response.get("id")

        # session_metrics["session_metadata"]["video_id"] = api_response.get("video_id")

        # session_metrics["session_metadata"]["total_segments"] = len(segments)

        # =====================================================
        # SPEED ANALYSIS
        # =====================================================

        session_metrics["speed_analysis"]["average_speed_kmph"] = calculate_mean(speeds)

        session_metrics["speed_analysis"]["maximum_speed_kmph"] = calculate_max(speeds)

        session_metrics["speed_analysis"]["minimum_speed_kmph"] = calculate_min(speeds)

        session_metrics["speed_analysis"]["median_speed_kmph"] = calculate_median(speeds)

        session_metrics["speed_analysis"]["speed_std_deviation"] = calculate_std(speeds)

        session_metrics["speed_analysis"]["speed_variance"] = calculate_variance(speeds)

        session_metrics["speed_analysis"]["fastest_delivery"]["speed_kmph"] = calculate_max(speeds)

        session_metrics["speed_analysis"]["slowest_delivery"]["speed_kmph"] = calculate_min(speeds)

        # =====================================================
        # RELEASE ANALYSIS
        # =====================================================

        session_metrics["release_analysis"]["average_release_height_m"] = calculate_mean(release_heights)

        session_metrics["release_analysis"]["max_release_height_m"] = calculate_max(release_heights)

        session_metrics["release_analysis"]["min_release_height_m"] = calculate_min(release_heights)

        session_metrics["release_analysis"]["release_height_std_deviation"] = calculate_std(release_heights)

        # =====================================================
        # BOUNCE ANALYSIS
        # =====================================================

        session_metrics["bounce_analysis"]["average_bounce_x"] = calculate_mean(bounce_x_values)

        session_metrics["bounce_analysis"]["average_bounce_y"] = calculate_mean(bounce_y_values)

        # =====================================================
        # TRAJECTORY ANALYSIS
        # =====================================================

        session_metrics["trajectory_analysis"]["average_trajectory_points"] = calculate_mean(trajectory_points)

        session_metrics["trajectory_analysis"]["average_flight_time_s"] = calculate_mean(flight_times)

        session_metrics["trajectory_analysis"]["average_distance_3d_m"] = calculate_mean(distances_3d)

        session_metrics["trajectory_analysis"]["average_speed_mps"] = calculate_mean(speed_mps_values)

        # =====================================================
        # STABILITY ANALYSIS
        # =====================================================

        session_metrics["stability_analysis"]["average_rmse"] = calculate_mean(rmse_values)

        session_metrics["stability_analysis"]["average_smoothness"] = calculate_mean(smoothness_values)

        session_metrics["stability_analysis"]["average_bad_jumps"] = calculate_mean(bad_jumps_values)

        runner.invoke({"status": "completed", "total_segments": len(segments)})

        return session_metrics
    
    except Exception as e:
        runner.invoke({"status": "failed", "error": str(e)})
        raise e
    


def add_phase_frames_to_injuries(injuries_json, combined_biomechanics_json):

    # segment lookup
    segment_lookup = {
        seg["segment_id"]: seg["bio_mechanics_report"]["metadata"]
        for seg in combined_biomechanics_json
    }


    PHASE_MAPPING = {
        "gather_phase": "Gather Phase",
        "gather": "Gather Phase",

        "backfoot_phase": "Backfoot Phase",
        "backfoot": "Backfoot Phase",

        "delivery_stride_phase": "Delivery Stride",
        "delivery_stride": "Delivery Stride",

        "frontfoot_phase": "Frontfoot Phase",
        "frontfoot": "Frontfoot Phase",

        "follow_through_phase": "Follow Through",
        "follow_through": "Follow Through"
    }

    for injury in injuries_json["top_injuries"]:

        seg_num = injury["most_supported_segment"]
        llm_phase = injury["phase"]

        metadata = segment_lookup.get(seg_num, {})

        actual_phase = PHASE_MAPPING.get(llm_phase)

        start_frame = None
        end_frame = None

        for phase_info in metadata.get("phases", []):

            if phase_info["phase"] == actual_phase:
                start_frame = phase_info["start_frame"]
                end_frame = phase_info["end_frame"]
                break

        injury["starting_frame"] = start_frame
        injury["ending_frame"] = end_frame

    return injuries_json


def add_phase_frames_to_corrections(
        corrections_json: dict,
        combined_biomechanics_json: dict
) -> dict:
    """
    Add starting_frame and ending_frame to each correction
    using most_supported_segment and phase.
    """
    
    segment_metadata_map = {}

    for segment in combined_biomechanics_json:

        segment_id = segment.get("segment_id")

        metadata = (
            segment.get("bio_mechanics_report", {})
            .get("metadata", {})
        )

        segment_metadata_map[segment_id] = metadata

    # LLM phase -> metadata phase mapping
    PHASE_MAPPING = {
        "gather_phase": "Gather Phase",
        "gather": "Gather Phase",

        "backfoot_phase": "Backfoot Phase",
        "backfoot": "Backfoot Phase",

        "delivery_stride_phase": "Delivery Stride",
        "delivery_stride": "Delivery Stride",

        "frontfoot_phase": "Frontfoot Phase",
        "frontfoot": "Frontfoot Phase",

        "follow_through_phase": "Follow Through",
        "follow_through": "Follow Through"
    }

    # Add frames to each correction
    for correction in corrections_json.get("top_corrections", []):

        segment_id = correction.get("most_supported_segment")
        llm_phase = correction.get("phase")

        metadata = segment_metadata_map.get(segment_id, {})

        actual_phase = PHASE_MAPPING.get(llm_phase)

        start_frame = None
        end_frame = None

        for phase_info in metadata.get("phases", []):

            if phase_info.get("phase") == actual_phase:
                start_frame = phase_info.get("start_frame")
                end_frame = phase_info.get("end_frame")
                break

        correction["starting_frame"] = start_frame
        correction["ending_frame"] = end_frame

    return corrections_json


def combine_player_outputs(
    analysis_json: dict,
    corrections_json: dict,
    injuries_json: dict
) -> dict:
    """
    Combine analysis, corrections and injuries
    into a single final player report.
    """

    combined_json = {}

    # Add analysis keys
    combined_json.update(analysis_json)

    # Add corrections
    combined_json["top_corrections"] = (
        corrections_json.get("top_corrections", [])
    )

    # Add injuries
    combined_json["top_injuries"] = (
        injuries_json.get("top_injuries", [])
    )

    return combined_json


def build_session_metrics_batsman(api_response: Dict[str, Any], session_id: str = None, user_id: str = None, metadata: Dict[str, Any] = None, tags: List[str] = None) -> Dict[str, Any]:
    """
    Build session metrics for batsman analysis.
    Extracts batsman-specific biomechanics data from API response.
    """
    
    runner = RunnableLambda(lambda x: x).with_config({**get_langfuse_config(session_id=session_id, user_id=user_id, trace_name="session_metrics_batsman", metadata=metadata, tags=tags), "run_name": "session_metrics_batsman"})
    
    try:
        segments = validate_session_data(api_response)
        
        segment_ids = []
        segment_insight_ids = []
        combined_llm_insights = []
        combined_biomechanics_reports = []
        
        for segment in segments:
            llm_segment_insight = segment.get("llm_segment_insight")
            
            print("==========================================")
            print("llm_segment_insight (batsman)", llm_segment_insight)
            print("==========================================")
            
            if llm_segment_insight and llm_segment_insight.get("id"):
                segment_ids.append(segment.get("segment_id"))
                segment_insight_ids.append(llm_segment_insight.get("id"))
                
                results = llm_segment_insight.get("results", {})
                
                llm_insights = results.get("llm_insights")
                if llm_insights:
                    combined_llm_insights.append(llm_insights)
                
                bio_mechanics_report = results.get("bio_mechanics_report")
                if bio_mechanics_report:
                    combined_biomechanics_reports.append({
                        "segment_id": segment.get("segment_id"),
                        "bio_mechanics_report": bio_mechanics_report
                    })
        
        session_metrics = copy.deepcopy(EMPTY_SESSION_SCHEMA)
        
        session_metrics["session_biomechanics_analysis"]["segment_ids"] = segment_ids
        session_metrics["session_biomechanics_analysis"]["segment_insight_ids"] = segment_insight_ids
        session_metrics["session_biomechanics_analysis"]["segment_llm_insights"] = combined_llm_insights
        session_metrics["session_biomechanics_analysis"]["segment_biomechanics_reports"] = combined_biomechanics_reports
        
        runner.invoke({"status": "completed", "total_segments": len(segments)})
        
        return session_metrics
    
    except Exception as e:
        runner.invoke({"status": "failed", "error": str(e)})
        raise e


