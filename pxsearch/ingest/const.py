import datetime

INGEST_CHUNK_SIZE = 500
MAX_DECODE_ERROR_ATTEMPTS = 3
STAC_SEARCH_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
ONE_DAY = datetime.timedelta(days=1)
SENTINEL_2_SNS_ARN = "arn:aws:sns:us-west-2:608149789419:cirrus-v0-publish"
USGS_SNS_ARN = "arn:aws:sns:us-west-2:673253540267:public-c2-notify"
