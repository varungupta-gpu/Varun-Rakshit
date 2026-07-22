import os
import json
from pathlib import Path
from dotenv import load_dotenv

from langfuse import Langfuse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# from langchain_google_vertexai import ChatVertexAI
from app.utils.langfuse_utils import get_langfuse_config


load_dotenv()

# Knowledge Source
KNOWLEDGE_SOURCE_PATH = Path(__file__).parent.parent / "Knowledge_source" / "biomechanics_knowledge_source.md"

with open(KNOWLEDGE_SOURCE_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE_SOURCE = f.read()


langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# Lazy initialization - only create chain when function is called
def _get_chain():
    prompt_from_langfuse = langfuse.get_prompt("session_analysis_prompt")
    SYSTEM_PROMPT = prompt_from_langfuse.prompt

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                """
                Knowledge Source:{knowledge_source}
                Session Data: {session_json}
                """
            )
        ]
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.4
    )

    output_parser = StrOutputParser()
    return prompt | llm | output_parser


def generate_session_analysis(
    session_metrics: dict,
    session_id: str = None,
    user_id: str = None,
    trace_metadata: dict = None,
    tags: list = None
) -> str:
    """
    Takes session metrics JSON and generates
    session-level biomechanics analysis.
    """

    with langfuse.start_as_current_observation(name="session-analysis"):
        chain = _get_chain()
        response = chain.invoke({
            "knowledge_source": KNOWLEDGE_SOURCE,
            "session_json": json.dumps(session_metrics, indent=4, ensure_ascii=False)},
            config={
                **get_langfuse_config(
                    session_id=session_id,
                    user_id=user_id,
                    trace_name="player-analysis",
                    metadata=trace_metadata,
                    tags=tags),
                    "run_name": "session-analysis"})
        return str(response)