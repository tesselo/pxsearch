import datetime
import gzip
import logging
import os
import shutil
import tempfile
from operator import itemgetter

import ipdb
import numpy as np
import pandas as pd
import psycopg2
import requests
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

begin_time = datetime.datetime.now()
print(begin_time)

# DB variables.
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")

# Setup db engine and connect.
if DB_NAME is not None:
    DB_TEMPLATE = "postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
    db_url = DB_TEMPLATE.format(
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=5432,
        database=DB_NAME,
    )
    engine = create_engine(db_url, client_encoding="utf8")
else:
    engine = create_engine(
        "postgresql+psycopg2://postgres:postgres@localhost:5432/pixels"
    )

# URLS
LANDSAT_URL = "https://storage.googleapis.com/gcp-public-data-landsat/index.csv.gz"
S2_L1C_URL = "https://storage.googleapis.com/gcp-public-data-sentinel-2/index.csv.gz"
S2_L2A_URL = "https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/index.csv.gz"

# Csv names to save
LANDSAT_CSV = "landsat.csv"
S2_L1C_CSV = "s2_l1c.csv"
S2_L2A_CSV = "s2_l2a.csv"

# Create temp folder to use as directory.
with tempfile.TemporaryDirectory() as path:
    # Download and extract csv here, and make update.
    print(path)

    def download_unzip_data(url, filename, path):
        # Download gz file
        zipfile = url.split("/")[-1]
        zipfile_path = os.path.join(path, zipfile)
        with open(zipfile_path, "wb") as f:
            csv_data = requests.get(url)
            f.write(csv_data.content)
        # Unzip and save as csv
        csv_file_path = os.path.join(path, filename)
        with gzip.open(zipfile_path, "rb") as f_in:
            with open(csv_file_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        # Remove gz file
        if os.path.isfile(zipfile_path):
            os.remove(zipfile_path)
        else:
            print("Error: {} file not found".format(zipfile_path))
        # Return csv_path to pass to pandas
        return csv_file_path

    # Download
    landsat_file_path = download_unzip_data(LANDSAT_URL, LANDSAT_CSV, path)
    print("Dowloaded and unzip: ", landsat_file_path)
    s2_l1c_file_path = download_unzip_data(S2_L1C_URL, S2_L1C_CSV, path)
    print("Dowloaded and unzip: ", s2_l1c_file_path)
    s2_l2a_file_path = download_unzip_data(S2_L2A_URL, S2_L2A_CSV, path)
    print("Dowloaded and unzip: ", s2_l2a_file_path)

    # Read files
    landsat = pd.read_csv(landsat_file_path)
    s2_l1c = pd.read_csv(s2_l1c_file_path)
    s2_l2a = pd.read_csv(s2_l2a_file_path)

    # Ensure datetype of sensing_time is datetime
    landsat["SENSING_TIME"] = pd.to_datetime(landsat["SENSING_TIME"])
    s2_l1c["SENSING_TIME"] = pd.to_datetime(s2_l1c["SENSING_TIME"])
    s2_l2a["SENSING_TIME"] = pd.to_datetime(s2_l2a["SENSING_TIME"])

    def get_last_date(table):
        query = "SELECT sensing_time FROM {table} ORDER BY sensing_time DESC LIMIT 1".format(
            table=table
        )
        result = engine.execute(query)
        result = [dict(row) for row in result]
        date = list(map(itemgetter("sensing_time"), result))
        date = str(date[0])
        return date

    # Get date in DB
    date = get_last_date("imagery")
    print("The maximum date in DB : " + date)

    # Check last dates in csvs - substitute prints -> logging
    print(" Max date L2A: ", s2_l2a.SENSING_TIME.max())
    print(" Max date L1C: ", s2_l1c.SENSING_TIME.max())
    print(" Max date LANDSAT: ", landsat.SENSING_TIME.max())

    # Delete old data based on Last sensingtime of imagery table
    s2_l2a = s2_l2a[s2_l2a["SENSING_TIME"] > date]
    s2_l1c = s2_l1c[s2_l1c["SENSING_TIME"] > date]
    landsat = landsat[landsat["SENSING_TIME"] > date]
    # Check shape of filtered df
    print("Sentinel 2 - L2A shape is : ", s2_l2a.shape)
    print("Sentinel 2- L1C shape is : ", s2_l1c.shape)
    print("LANDSAT shape is : ", landsat.shape)

    # Change dtyppe -> loat to int.
    s2_l1c["TOTAL_SIZE"] = s2_l1c["TOTAL_SIZE"].astype(np.int64)
    # Save.
    landsat.to_csv(landsat_file_path, index=False)
    s2_l1c.to_csv(s2_l1c_file_path, index=False)
    s2_l2a.to_csv(s2_l2a_file_path, index=False)

    # Open to verify dtypes
    landsat = pd.read_csv(landsat_file_path)
    s2_l1c = pd.read_csv(s2_l1c_file_path)
    s2_l2a = pd.read_csv(s2_l2a_file_path)

    # Get total number of records
    def get_total_records(table):
        count = "SELECT COUNT(DISTINCT product_id) FROM {table};".format(table=table)

        result = engine.execute(count)
        result = [dict(row) for row in result]
        total = list(map(itemgetter("count"), result))
        total = str(total[0])
        print("The total number of records in the table is: ", total)

    #get_total_records("imagery")
    # The total number of records in the table is:  36287945
    print("The sum of data is: ", s2_l2a.shape[0] + s2_l1c.shape[0] + landsat.shape[0])
    # The sum of data is:  2101105

    # Update db
    def update_db(s2_l2a_data, s2_l1c_data, landsat_data):

        sentinel = [s2_l2a_data, s2_l1c_data]
        landsat = landsat_data

        # From the engine isolate a psycopg2 connection:
        connection = engine.connect().connection
        # Get a cursor on that connection:
        cursor = connection.cursor()

        # Copy sentinel 2
        for data in sentinel:
            with open(data, "r") as f:
                command = "COPY imagery(GRANULE_ID, PRODUCT_ID, DATATAKE_IDENTIFIER, MGRS_TILE, SENSING_TIME, TOTAL_SIZE, CLOUD_COVER, GEOMETRIC_QUALITY_FLAG, GENERATION_TIME, NORTH_LAT, SOUTH_LAT, WEST_LON, EAST_LON, BASE_URL) FROM STDIN WITH (FORMAT CSV,HEADER true, DELIMITER ',');"
                cursor.copy_expert(command, f)
                connection.commit()

        # Copy landsat
        with open(landsat, "r") as f:
            command = "COPY imagery(SCENE_ID, PRODUCT_ID, SPACECRAFT_ID, SENSOR_ID, DATE_ACQUIRED, COLLECTION_NUMBER, COLLECTION_CATEGORY, SENSING_TIME, DATA_TYPE, WRS_PATH, WRS_ROW, CLOUD_COVER, NORTH_LAT, SOUTH_LAT, WEST_LON, EAST_LON, TOTAL_SIZE, BASE_URL) FROM STDIN WITH (FORMAT CSV,HEADER true, DELIMITER ',');"
            cursor.copy_expert(command, f)
            connection.commit()

        # Update db columns
        update_columns = """
        UPDATE imagery SET spacecraft_id = 'SENTINEL_2' WHERE spacecraft_id IS NULL;
        UPDATE imagery SET bbox = ST_MakeEnvelope(west_lon, south_lat, east_lon, north_lat, 4326) WHERE bbox IS NULL;
        """
        engine.execute(update_columns)
        cursor.close()

    update_db(s2_l2a_file_path, s2_l1c_file_path, landsat_file_path)

    # Get new date in DB.
    date = get_last_date("imagery")
    print("The new date is: ", date)

    #get_total_records("imagery")
    #print("The sum of data is: ", s2_l2a.shape[0] + s2_l1c.shape[0] + landsat.shape[0])

print(datetime.datetime.now()-begin_time)
