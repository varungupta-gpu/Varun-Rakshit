import time
import json
import re
import os

from app.utils.langfuse_utils import get_langfuse_config

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

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
    bowling_prompt = get_prompt("bowling_prompt", label="production")
    return bowling_prompt | llm


# ---------- JSON PARSER ----------
def safe_json_parse(text: str):

    if not text or text.strip() == "":
        raise ValueError("Empty response")

    text = text.strip()

    text = re.sub(r"```(?:json)?", "", text)
    text = text.replace("```", "")

    start = text.find("{")

    if start == -1:
        raise ValueError("No JSON found")

    stack = 0
    end = None

    for i in range(start, len(text)):

        if text[i] == "{":
            stack += 1

        elif text[i] == "}":
            stack -= 1

            if stack == 0:
                end = i + 1
                break

    if end is None:
        raise ValueError("Incomplete JSON")

    return json.loads(text[start:end])


# ---------- VALIDATION ----------
def validate_output(data: dict):

    if "bowler_view" not in data or "batter_view" not in data:
        raise ValueError("Missing main keys")

    if "current_plan" not in data["bowler_view"]:
        raise ValueError("Missing current_plan")

    if "next_variations" not in data["bowler_view"]:
        raise ValueError("Missing next_variations")

    if not isinstance(data["bowler_view"]["next_variations"], list):
        raise ValueError("next_variations must be list")

    if "expected_adjustment" not in data["batter_view"]:
        raise ValueError("Missing expected_adjustment")

    if "counter_strategy" not in data["batter_view"]:
        raise ValueError("Missing counter_strategy")

    return True


# ---------- RETRY ----------
def call_with_retry(
    inputs,
    session_id=None,
    user_id=None,
    metadata=None,
    tags=None,
    retries=1,
    delay=1
):

    for i in range(retries):

        try:
            chain = _get_chain()
            response = chain.invoke(
                inputs,

                config={
                    **get_langfuse_config(
                        session_id=session_id,
                        user_id=user_id,
                        trace_name="bowling_agent",
                        metadata=metadata,
                        tags=tags
                    ),

                    "run_name": "bowling_agent"
                }
            )

            parsed = safe_json_parse(response.content)

            validate_output(parsed)

            return parsed

        except Exception as e:

            if i == retries - 1:
                raise e

            time.sleep(delay)


# ---------- MAIN ----------
def run_bowling_agent(state: AgentState) -> AgentState:

    delivery = state["delivery"]

    trace_context = state["trace_context"]

    try:

        parsed_output = call_with_retry(

            inputs={
                "speed": delivery["metadata"]["speed_kmph"],
                "line": delivery["features"]["line"],
                "length": delivery["features"]["length"],
                "swing": delivery["features"]["swing_type"]
            },

            session_id=trace_context["session_id"],

            user_id=trace_context["user_id"],

            metadata={
                **trace_context["trace_metadata"],
                "agent": "bowling_agent"
            },

            tags=trace_context["tags"]
        )

        state["outputs"]["bowling"] = parsed_output

    except Exception as e:

        state["outputs"]["bowling"] = {
            "error": str(e),
            "fallback": {
                "bowler_view": {},
                "batter_view": {}
            }
        }

    return state