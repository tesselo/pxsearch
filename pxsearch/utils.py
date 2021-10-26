import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection_url(postgres_dbname=None) -> str:
    """
    Get connection URL from environment variables
    (see environment variables set in docker-compose)
    """
    postgres_user = os.environ.get("POSTGRES_USER", "postgres")
    postgres_pass = os.environ.get("POSTGRES_PASS", "")
    postgres_host = os.environ.get("POSTGRES_HOST", "localhost")
    postgres_port = os.environ.get("POSTGRES_PORT", "5432")
    if not postgres_dbname:
        postgres_dbname = os.environ.get("POSTGRES_DBNAME", "pxsearch")

    connection_string = (
        f"postgresql://{postgres_user}:{postgres_pass}@"
        f"{postgres_host}:{postgres_port}/{postgres_dbname}"
    )

    logger.info(f"PGSQL connection {connection_string}")
    return connection_string
