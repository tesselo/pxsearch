import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import box

sentinel = gpd.read_csv('/home/keren/projects/API_Images/sentinel/new/index_s2_l2a_2.csv')
sentinel.head(2)
sentinel.crs

sentinel['bbox'] = sentinel.apply(lambda row: box(row.WEST_LON, row.SOUTH_LAT, row.EAST_LON, row.NORTH_LAT), axis=1)
sentinel.head()
sentinel.dtypes

# Verify no data in column total_size to avoid problems with data types in PostgreSQL
print(sentinel['TOTAL_SIZE'].isnull().sum())
print(sentinel.shape)

# Pandas interprets TOTAL_SIZE as float, so we have to convert to int
sentinel['TOTAL_SIZE'] = sentinel['TOTAL_SIZE'].fillna(0).astype(np.int64)

sentinel.to_csv('/home/keren/projects/API_Images/landsat/new/index_landsat_2.csv', index=False)