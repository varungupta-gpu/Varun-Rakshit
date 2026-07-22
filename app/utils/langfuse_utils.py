import os
from typing import Optional

from app.core.config import settings
# ---------- LANGFUSE ----------
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

# ---------- ENV ----------
os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_BASE_URL"] = settings.LANGFUSE_BASE_URL


langfuse = Langfuse()

# Shared callback handler
langfuse_handler = CallbackHandler()


# ---------- CONFIG HELPER ----------
def get_langfuse_config(
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    trace_name: Optional[str] = None,
    tags: Optional[list] = None,
    metadata: Optional[dict] = None,
):

    final_metadata = (
        {k: str(v) for k, v in metadata.items()}
        if metadata else {}
    )

    if session_id:
        final_metadata["langfuse_session_id"] = str(session_id)

    if user_id:
        final_metadata["langfuse_user_id"] = str(user_id)

    if tags:
        final_metadata["langfuse_tags"] = tags

    # ADD THIS
    if trace_name:
        final_metadata["langfuse_trace_name"] = trace_name

    return {
        "callbacks": [langfuse_handler],

        "run_name": trace_name,

        "metadata": final_metadata,
    }