from app.utils.langfuse_utils import get_langfuse_config
import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# from Analysis.prompts.commentator_prompt import commentator_prompt
from app.pipeline.segment_pipeline.prompt_manager import get_prompt
from app.pipeline.segment_pipeline.state import AgentState

load_dotenv()


# ---------- LLM - Lazy initialization ----------
def _get_chain():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0.5,
        response_mime_type="application/json",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    commentator_prompt = get_prompt("commentator_prompt", label="production")
    return commentator_prompt | llm


# ---------- MAIN ----------
def run_commentator_agent(state: AgentState) -> AgentState:
    """
    Runs commentator agent and updates state.
    """

    delivery = state["delivery"]

    trace_context = state["trace_context"]

    try:
        chain = _get_chain()
        response = chain.invoke(

            {
                "speed": delivery["metadata"]["speed_kmph"],
                "line": delivery["features"]["line"],
                "length": delivery["features"]["length"],
                "swing": delivery["features"]["swing_type"]
            },

            config={
                **get_langfuse_config(
                    session_id=trace_context["session_id"],
                    user_id=trace_context["user_id"],
                    trace_name="commentator_agent",
                    metadata={
                        **trace_context["trace_metadata"],
                        "agent": "commentator_agent"
                    },
                    tags=trace_context["tags"]
                ),

                "run_name": "commentator_agent"
            }
        )

        # Parse JSON safely
        parsed_output = safe_json_parse(response.content)

        # Update state
        state["outputs"]["commentator"] = parsed_output

    except Exception as e:
        state["outputs"]["commentator"] = {"error": str(e)}

    return state


# ---------- HELPER ----------
def safe_json_parse(text: str):
    """
    Ensures robust JSON parsing from LLM output.
    """

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        # Try to fix common LLM issues
        text = text.strip()

        # Remove markdown if present
        if text.startswith("```"):
            text = text.split("```")[1]

        return json.loads(text)