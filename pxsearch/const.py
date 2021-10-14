CLIENT_TYPE = "s3"
PAGINATOR_LOOKUP = "list_objects"
INGESTION_BATCH_SIZE = 2

LS8_L2_BUCKET_NAME = "usgs-landsat"
LS8_L2_PAGINATOR_BASE_PREFIX = "collection02/level-2/standard/oli-tirs/"
LS8_L2_STAC_ITEM_FILE = "_T2_SR_stac.json"
LS8_L2_STAC_ITEM_FILE_JMES_SEARCH = (
    f"Contents[?contains(Key, '{LS8_L2_STAC_ITEM_FILE}') == `true`].Key"
)
LS8_L2_COLLECTION_ID = "landsat-c2l2-sr"
