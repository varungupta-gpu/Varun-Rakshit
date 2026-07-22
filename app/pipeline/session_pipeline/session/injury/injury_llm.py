import os
import json

from pathlib import Path
from dotenv import load_dotenv

from langfuse import Langfuse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langfuse.langchain import CallbackHandler
langfuse_handler = CallbackHandler()



load_dotenv()

CURRENT_DIR = Path(__file__).parent
KNOWLEDGE_SOURCE_PATH = CURRENT_DIR / "processed_doc.md"

with open(KNOWLEDGE_SOURCE_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE_SOURCE = f.read()

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)

# Lazy initialization - only create chain when function is called
def _get_chain():
    prompt_from_langfuse = langfuse.get_prompt("injury_risk")
    SYSTEM_PROMPT = prompt_from_langfuse.prompt

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),

            (
                "human",
                """
                # Biomechanics Knowledge Source
                {knowledge_source}

                # Bowler Biomechanics Report
                {biomechanics_report}
                """
            )
        ]
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2
    )

    output_parser = StrOutputParser()
    return prompt | llm | output_parser


def generate_injury_risks(biomechanics_report: dict) -> str:
    """
    Analyse bowler biomechanics and return
    top injury risks in JSON format.
    """
        
    with langfuse.start_as_current_observation(name="injury-analysis-chain"):
        chain = _get_chain()
        response = chain.invoke(
            {
                "knowledge_source": KNOWLEDGE_SOURCE,
                "biomechanics_report": json.dumps(
                    biomechanics_report,
                    indent=4
                )
            },
            config={
                "callbacks": [langfuse_handler],
                "run_name": "injury_analysis"
            }
        )

        return str(response)