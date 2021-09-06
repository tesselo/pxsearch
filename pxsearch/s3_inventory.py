import datetime
import glob
import gzip
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import traceback

import boto3
import dateutil
import pytz
import rasterio
import sentry_sdk
import structlog

from pxsearch.const import INVENTORY_BUCKET_NAME, TILEINFO_BODY_KEY, TILE_INFO_FILE, BUCKET_NAME

# Setup timezone for timestamp parsing.
UTC = pytz.timezone('UTC')

# Get logger. ????
logger = structlog.get_logger('django_structlog')

def parse_s3_sentinel_1_inventory():
    """
    Full Sentinel-1 inventory synchronization.

    aws s3 ls s3://sentinel-inventory/sentinel-s1-l1c/sentinel-s1-l1c-inventory/
    """
    logger.info('Starting inventory sync.')
    client = boto3.client('s3')
    today = datetime.datetime.now().date() - datetime.timedelta(days=1)
    # Get latest inventory manifest (created yesterday).   aws s3 cp  s3://sentinel-inventory/sentinel-s1-l1c/sentinel-s1-l1c-inventory/2021-09-01T01-00Z/manifest.json $wd/manifest.json --no-sign-request
    manifest = client.get_object(
        Key='sentinel-s1-l1c/sentinel-s1-l1c-inventory/{}T01-00Z/manifest.json'.format(today),
        Bucket=INVENTORY_BUCKET_NAME,
    )
    # o que rola aqui?
    manifest = json.loads(manifest.get(TILEINFO_BODY_KEY).read().decode())
    # Loop through inventory files and ingest listed Sentinel-1 scenes.
    for dat in manifest['files']:
        logger.info('Working on file {}.'.format(dat['key']))
        with tempfile.NamedTemporaryFile(suffix='.csv.gz') as csvgz:
            prefixes = set()
            #download csv files
            client.download_file(
                Key=dat['key'],
                Bucket=INVENTORY_BUCKET_NAME,
                Filename=csvgz.name,
            )
            # abre e lê cada
            with gzip.open(csvgz.name, 'rb') as fl:
                for line in fl:
                    # Add prefix to unique list.
                    prefixes.add('/'.join(str(line).replace('"', '').split(',')[1].split('/')[:7]) + '/')
            logger.info('Found {} unique prefixes.'.format(len(prefixes)))
            # Setup s1tiles from unique prefix list.
            batch = []
            counter = 0
            for prefix in prefixes:
                new_tile = ingest_s1_tile_from_prefix(prefix, client, commit=False)
            #     if not new_tile:
            #         continue
            #     batch.append(new_tile)
            #     counter += 1
            #     if counter % 2500 == 0:
            #         Sentinel1Tile.objects.bulk_create(batch)
            #         batch = []
            #         logger.info('Created {} S1 Tiles'.format(counter))

            # if len(batch):
            #     Sentinel1Tile.objects.bulk_create(batch)

def ingest_s1_tile_from_prefix(tile_prefix, client=None, commit=True):
    """
    Ingest a Sentinel 1 tile from a prefix. Download metadata for the scene and
    create Sentinel1Tile object containing the data.
    """
    # Ignore this if the tile already exists.
    # if Sentinel1Tile.objects.filter(prefix=tile_prefix).exists():
    #     return
    # Instantiate boto3 client.
    if not client:
        client = boto3.client('s3')

    # Construct TileInfo file key.
    tileinfo_key = tile_prefix + TILE_INFO_FILE

    # Get tile info json data.
    try:
        tileinfo = client.get_object(
            Key=tileinfo_key,
            Bucket=BUCKET_NAME,
            RequestPayer='requester',
        )
    except client.exceptions.NoSuchKey:
        logger.error('Could not ingest S1 prefix "{}", tileinfo key "{}" not found.'.format(tile_prefix, tileinfo_key))
        return

    # Decode json tile info data into a dictionary.
    try:
        tileinfo = json.loads(tileinfo.get(TILEINFO_BODY_KEY).read().decode())
    except json.decoder.JSONDecodeError:
        logger.error('Could not ingest S1 prefix "{}", TileInfo json file is malformed.'.format(tile_prefix))
        return

    print("tileinfo >> ", tileinfo)

# Substitute per geopandas or shapely
    # if 'footprint' in tileinfo:
    #     footprint = OGRGeometry(str(tileinfo['footprint'])).geos
    #     if not isinstance(footprint, MultiPolygon):
    #         # Attempt conversion.
    #         footprint = MultiPolygon(footprint, srid=footprint.srid)
    #     # Set geom to none if tile data geom is not valid.
    #     if not footprint.valid:
    #         footprint = None
    # else:
    #     footprint = None

    # # Register tile, log error if creation failed.
    # stile = Sentinel1Tile(
    #     product_name=tileinfo['id'],
    #     prefix=tile_prefix,
    #     mission_id=tileinfo['missionId'],
    #     product_type=tileinfo['productType'],
    #     mode=tileinfo['mode'],
    #     polarization=tileinfo['polarization'],
    #     start_time=UTC.localize(dateutil.parser.parse(tileinfo['startTime']), is_dst=True),
    #     stop_time=UTC.localize(dateutil.parser.parse(tileinfo['stopTime']), is_dst=True),
    #     absolute_orbit_number=tileinfo['absoluteOrbitNumber'],
    #     mission_datatake_id=tileinfo['missionDataTakeId'],
    #     product_unique_identifier=tileinfo['productUniqueIdentifier'],
    #     sci_hub_id=tileinfo['sciHubId'],
    #     footprint=footprint,
    #     filename_map=tileinfo['filenameMap'],
    # )

    # if commit:
    #     stile.save()

    # return stile


#def parse_s3_sentinel_2_inventory():

#def parse_landsat_inventory():

def process_sentinel_sns_message(event, context):
    """
    Ingest tile data based on notifications from SNS topic
    arn:aws:sns:eu-west-1:214830741341:NewSentinel2Product
    """
    message = json.loads(event['Records'][0]['Sns']['Message'])

    # Get prefix for this tile.
    tile_prefix = message['path']

    # Ensure prefix has trailing slash.
    if not tile_prefix.endswith('/'):
        tile_prefix += '/'

    # Skip this tile if it's already registered.
    if Sentinel1Tile.objects.filter(prefix=tile_prefix).exists():
        return

    ingest_s1_tile_from_prefix(tile_prefix)

    # To understand Boto3 https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#

    # instalar stac api 

    #post this data to the api -> docker ultima versao do docker compose.