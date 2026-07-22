"""
Request-scoped logging: bind Cloud Run / job request_id to every log line via contextvars.
"""
import contextvars
import logging
from typing import Optional

# Set per job in process_ball_segment (try/finally with reset).
request_id_context_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Injects record.request_id from request_id_context_var for formatters."""

    def filter(self, record: logging.LogRecord) -> bool:
        req_id = request_id_context_var.get()
        record.request_id = f"[{req_id}] " if req_id else ""
        return True


class RequestIdFormatter(logging.Formatter):
    """Ensures %(request_id)s is always defined if a handler lacks RequestIdFilter."""

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "request_id"):
            record.request_id = ""
        return super().format(record)
