from app.utils.langfuse_utils import get_langfuse_config
import re
import os
import time
import json
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
    fielding_prompt = get_prompt("fielding_prompt", label="production")
    return fielding_prompt | llm


# ---------- JSON PARSER ----------
def safe_json_parse(text: str):

    if not text or text.strip() == "":
        raise ValueError("Empty response")

    text = text.strip()

    # remove markdown
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

    for phase in ["powerplay", "middle_overs", "death_overs"]:

        if phase not in data:
            raise ValueError(f"Missing {phase}")

        for key in ["attacking_field", "defensive_field"]:

            if key not in data[phase]:
                raise ValueError(f"Missing {key} in {phase}")

            if not isinstance(data[phase][key], list):
                raise ValueError(f"{key} must be list")

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
                        trace_name="fielding_agent",
                        metadata=metadata,
                        tags=tags
                    ),

                    "run_name": "fielding_agent"
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
def run_fielding_agent(state: AgentState) -> AgentState:

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
                "agent": "fielding_agent"
            },

            tags=trace_context["tags"]
        )

        state["outputs"]["fielding"] = parsed_output

    except Exception as e:

        state["outputs"]["fielding"] = {
            "error": str(e),
            "fallback": {
                "powerplay": {
                    "attacking_field": [],
                    "defensive_field": []
                },

                "middle_overs": {
                    "attacking_field": [],
                    "defensive_field": []
                },

                "death_overs": {
                    "attacking_field": [],
                    "defensive_field": []
                }
            }
        }

    return state