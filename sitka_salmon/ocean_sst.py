import os
from sitka_salmon import config
import pandas as pd
from uafgi.util import shputil

LMEs66_shp = os.path.join(config.HARNESS, 'data', 'usgs', 'LMEs66', 'LMEs66.shp')

print(LMEs66_shp)
df = shputil.read_df(LMEs66_shp)
df = df.loc[df.LME_NAME.isin({'Gulf of Alaska', 'East Bering Sea'})]
print(df.columns)
print(df)

