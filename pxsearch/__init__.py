import logging
import os

from kw.structlog_config import configure_stdlib_logging, configure_structlog

from pxsearch.utils import initialize_sentry_sdk

DEBUG = os.environ.get("DEBUG", False)
configure_structlog(debug=DEBUG, timestamp_format="iso")
configure_stdlib_logging(
    debug=DEBUG, timestamp_format="iso", level=logging.INFO
)

# Stop the SPAM from botocore
logging.getLogger("botocore.credentials").setLevel(logging.ERROR)
initialize_sentry_sdk()
