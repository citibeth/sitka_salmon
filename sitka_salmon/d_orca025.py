import os,functools,collections
import numpy as np
import pandas as pd
import geopandas
import netCDF4
from sitka_salmon import config

# ---------- Inputs
orca025_grid_nc = os.path.join(config.HARNESS, 'data', 'era5', 'orca025_grid.nc')

# -------- Outputs
# Area of each orca025 grid cell
orca025_area_nc = os.path.join(config.HARNESS, 'output', 'orca025_area.nc')

# -----------------------------------------------------------------
GetResult = collections.namedtuple('GetResult', ('nav_lat', 'nav_lon'))
def get():
    with netCDF4.Dataset(orca025_grid_nc) as nc:
        nc.set_auto_mask(False)
        nav_lat = nc.variables['nav_lat'][:]
        nav_lon = nc.variables['nav_lon'][:]
    return GetResult(nav_lat, nav_lon)

# -----------------------------------------------------------------
# https://geopandas.org/en/stable/gallery/create_geopandas_from_pandas.html#:~:text=This%20example%20shows%20how%20to%20create%20a%20GeoDataFrame,matplotlib.pyplot%20as%20plt%20From%20longitudes%20and%20latitudes%20%23
def gdf():
    """Helper function, Converts the orca025 grid to a GeoPandas dataframe of points"""

    with netCDF4.Dataset(orca025_grid_nc) as nc:
        nc.set_auto_mask(False)
        nav_lat = nc.variables['nav_lat'][:]
        nav_lon = nc.variables['nav_lon'][:]
    nlat,nlon = nav_lat.shape

    # Array giving the ilon and ilat index in each position
    x = np.indices((nlat,nlon))
    ilats = x[0,:]
    ilons = x[1,:]


    df = pd.DataFrame(dict(zip(
        ['j', 'i', 'lat', 'lon'],
        [ilats.reshape(-1), ilons.reshape(-1), nav_lat.reshape(-1), nav_lon.reshape(-1)])))
    gdf = geopandas.GeoDataFrame(
        df, geometry=geopandas.points_from_xy(df.lon, df.lat))

    gdf = gdf.set_crs('EPSG:4326')
    return gdf



@functools.lru_cache()
def area():
    print(orca025_area_nc)
    with netCDF4.Dataset(orca025_area_nc) as nc:
        nc.set_auto_mask(False)
        return nc.variables['area'][:]

        
