from langchain_core.prompts import PromptTemplate
from app.utils.langfuse_utils import langfuse


def get_prompt(prompt_name: str, label: str = "production"):

    try:
        prompt_client = langfuse.get_prompt(prompt_name, label=label)
        return PromptTemplate(input_variables=prompt_client.variables, template=prompt_client.prompt)

    except Exception as e:
        raise RuntimeError(f"Prompt fetch failed for '{prompt_name}': {e}")