import json, logging
from app.pipeline.segment_pipeline.state import create_initial_state
from app.pipeline.segment_pipeline.agents.commentator_agent import run_commentator_agent
# from app.pipeline.segment_pipeline.agents.batting_agent import run_batting_agent
from app.pipeline.segment_pipeline.agents.fielding_agent import run_fielding_agent
from app.pipeline.segment_pipeline.agents.bowling_agent import run_bowling_agent
from app.pipeline.segment_pipeline.agents.biomechanics_agent import generate_biomechanics_analysis
logger = logging.getLogger(__name__)

def build_trace_context(
    request_id: str,
    json_data: dict,
    user_id: str = None
) -> dict:
    """
    Centralized Langfuse tracing context.

    Architecture:
    - session_id = request_id
    - user_id = optional real user
    """

    # ---------- SESSION ----------
    session_id = request_id

    # ---------- METADATA ----------
    metadata = {
        "analysis_type": "cricket_bowling_analysis",
        "total_deliveries": str(len(json_data.get("deliveries", []))),
        "has_biomechanics": str("biomechanics" in json_data),
        "system": "sportzenge_llm_analysis"
    }

    # ---------- TAGS ----------
    tags = [
        "cricket",
        "bowling-analysis",
        "gemini-3.1-flash-lite",
        "langchain"
    ]

    return {
        "session_id": session_id,
        "user_id": user_id,
        "trace_metadata": metadata,
        "tags": tags
    }


def run_analysis(json_data, request_id: str, user_id: str = None ):
    """
    Runs all agents
    """

    delivery = json_data["deliveries"][0]
    # attach biomechanics
    delivery["biomechanics"] = json_data.get("biomechanics", {})

    # ---------- TRACE CONTEXT ----------
    trace_context = build_trace_context(request_id=request_id, json_data=json_data, user_id=user_id)

    logger.info("============ PROCESSING DELIVERY ==========")

    # add delivery metadata
    delivery_metadata = {**trace_context["trace_metadata"]}

    logger.info("========== state creation start ==========")

    # create state
    state = create_initial_state(
        delivery=delivery,
        session_id=trace_context["session_id"],
        user_id=trace_context["user_id"],
        trace_metadata=delivery_metadata,
        tags=trace_context["tags"]
    )

    logger.info("========== calling agent start ==========")

    # run agents
    state = run_commentator_agent(state)
    # state = run_batting_agent(state)
    state = run_fielding_agent(state)
    state = run_bowling_agent(state)

    analysis_result = generate_biomechanics_analysis(json_data["biomechanics"], state["trace_context"])
    state["outputs"]["Biomechanics"]["bowler_biomechanics_analysis"] = analysis_result


    return {
    "session_id": trace_context["session_id"],
    "en": {
        "results": [
            {
                "analysis": state["outputs"]
            }
        ]
    },
    "hn": {}
}


def run_full_analysis(json_data, request_id: str, user_id: str = None):
    """
    Complete pipeline:
    load → run → save
    """
    output = run_analysis(json_data=json_data, request_id=request_id, user_id=user_id)
    logger.info("run_full_analysis returned")
    return output

