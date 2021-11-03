CLIENT_TYPE = "s3"
PAGINATOR_LOOKUP = "list_objects"
INGESTION_BATCH_SIZE = 50
DATETIME_RFC339 = "%Y-%m-%dT%H:%M:%S.%fZ"

# LS8 L2 constants.
LS_BUCKET_NAME = "usgs-landsat"
LS_L2_PAGINATOR_BASE_PREFIX = "collection02/level-2/standard/"
WRS_PATH_MAX = 251
WRS_ROW_MAX = 248
LS_L2_COLLECTION_ID = "landsat-c2l2"
LS_L2_STAC_ITEM_FILE_JMES_SEARCH = (
    "Contents[?contains(Key, '_stac.json') == `true`].Key"
)
LS_COLLECTIONS = [
    "landsat-c2l1",
    "landsat-c2l2-sr",
    "landsat-c2l2-st",
    "landsat-c2l2alb-bt",
    "landsat-c2l2alb-sr",
    "landsat-c2l2alb-st",
    "landsat-c2l2alb-ta",
]
