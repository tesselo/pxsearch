import logging
import os

import sentry_sdk
import structlog
from kw.structlog_config import configure_stdlib_logging, configure_structlog


def get_connection_url() -> str:
    """
    Get connection URL from environment variables
    (see environment variables set in docker-compose)
    """
    postgres_user = os.environ.get("POSTGRES_USER", "postgres")
    postgres_pass = os.environ.get("POSTGRES_PASS", "")
    postgres_host = os.environ.get("POSTGRES_HOST", "localhost")
    postgres_port = os.environ.get("POSTGRES_PORT", "5432")
    postgres_dbname = os.environ.get("POSTGRES_DBNAME", "pxsearch")

    return (
        f"postgresql://{postgres_user}:{postgres_pass}@"
        f"{postgres_host}:{postgres_port}/{postgres_dbname}"
    )


def configure_logging() -> None:
    debug = os.environ.get("DEBUG", False)
    configure_structlog(debug=debug, timestamp_format="iso")
    configure_stdlib_logging(
        debug=debug, timestamp_format="iso", level=logging.INFO
    )

    # Stop the SPAM from botocore
    logging.getLogger("botocore.credentials").setLevel(logging.ERROR)


def initialize_sentry_sdk() -> None:
    if "SENTRY_DSN" in os.environ:
        sentry_sdk.init(
            os.environ.get("SENTRY_DSN"),
            traces_sample_rate=1.0,
        )


def configure_instrumentation():
    configure_logging()
    initialize_sentry_sdk()
    return structlog.get_logger(__name__)
