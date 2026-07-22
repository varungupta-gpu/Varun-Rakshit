import logging
import logging.config
import sys

from app.core.config import settings


def setup_logging(level=None):
    """
    Setup logging configuration for standalone scripts, matching core/logging_config.py.
    """
    if level is None:
        level = settings.LOG_LEVEL

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'request_id': {
                '()': 'app.core.request_logging.RequestIdFilter',
            },
        },
        'formatters': {
            'detailed': {
                '()': 'app.core.request_logging.RequestIdFormatter',
                'format': (
                    '%(request_id)s%(name)s:%(lineno)d - %(levelname)s - %(message)s'
                ),
            },
            'simple': {
                '()': 'app.core.request_logging.RequestIdFormatter',
                'format': '%(request_id)s%(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'detailed',
                'level': level,
                'stream': sys.stdout,
                'filters': ['request_id'],
            }
        },
        'root': {
            'handlers': ['console'],
            'level': 'WARNING'
        },
        'loggers': {
            '__main__':   {'level': level, 'propagate': True},
            'app':        {'level': level, 'propagate': True},
            'Analysis':   {'level': level, 'propagate': True},
            'middleware': {'level': level, 'propagate': True},
        },
    }

    # if logging.root.handlers:
    #     _ensure_request_id_filter_on_root()
    #     return

    logging.config.dictConfig(logging_config)


def _ensure_request_id_filter_on_root():
    """If logging was configured elsewhere, attach RequestIdFilter once per handler."""
    from app.core.request_logging import RequestIdFilter

    for h in logging.root.handlers:
        if any(isinstance(f, RequestIdFilter) for f in h.filters):
            continue
        h.addFilter(RequestIdFilter())
