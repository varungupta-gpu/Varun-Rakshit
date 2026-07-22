import os
import json
from langfuse import Langfuse
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import (ChatGoogleGenerativeAI)
from langchain_core.output_parsers import (StrOutputParser)
from app.utils.langfuse_utils import get_langfuse_config
from app.pipeline.segment_pipeline.prompt_manager import get_prompt

load_dotenv()
KNOWLEDGE_SOURCE_PATH = (Path(__file__).parent.parent/ "knowledge_source"/ "biomechanics_knowledge_source.md")
with open(KNOWLEDGE_SOURCE_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE_SOURCE = f.read()

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# Lazy initialization - only create chain when function is called
def _get_chain():
    prompt = get_prompt("Biomechanics prompt", label="production")
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0.4)
    output_parser = StrOutputParser()
    return (prompt|llm|output_parser)

def generate_biomechanics_analysis( final_output: dict, trace_context: dict ) -> dict:
    """
    Sends biomechanics data to Gemini
    and returns professional analysis.
    """

    with langfuse.start_as_current_observation(name="biomechanics-analysis"):
        chain = _get_chain()
        response = chain.invoke(
            {
                "knowledge_source": KNOWLEDGE_SOURCE,
                "final_output_according_tertile": json.dumps(
                    final_output,
                    indent=4
                )
            },

            config={
                **get_langfuse_config(
                    session_id=trace_context["session_id"],
                    user_id=trace_context["user_id"],
                    trace_name="biomechanics_agent",
                    metadata={
                        **trace_context["trace_metadata"],
                        "agent": "biomechanics_agent"
                    },
                    tags=trace_context["tags"]
                ),

                "run_name": "biomechanics_agent"
            }
        )
        
        
        analysis_result = str(response).strip()
        
        if analysis_result.startswith("```json"):
            analysis_result = analysis_result.replace("```json", "", 1)
        if analysis_result.endswith("```"):
            analysis_result = analysis_result[:-3]

        analysis_result = analysis_result.strip()

        return json.loads(analysis_result)