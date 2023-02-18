import os,functools,re,itertools,more_itertools,collections,pickle
import openpyxl
import pandas as pd
import netCDF4,pyproj
import numpy as np
import geopandas
from uafgi.util import make
from sitka_salmon import config

"""Rules to compute weights and mask of the ORCA025 Grid"""

# ---------- Inputs
LMEs66_shp = os.path.join(config.HARNESS, 'data', 'usgs', 'LMEs66', 'LMEs66.shp')
orca025_grid_nc = os.path.join(config.HARNESS, 'data', 'era5', 'orca025_grid.nc')

# -------- Outputs
# Area of each orca025 grid cell
orca025_area_nc = os.path.join(config.HARNESS, 'output', 'orca025_area.nc')

# The points in the ORCA025 grid as a GeoPandas dataframe
#orca025_gdf_pik = os.path.join(config.HARNESS, 'output', 'orca025_gdf.pik')

# Mask (on the ORCA025 grid) of the Large Marine Ecosystems
lme_mask_nc = os.path.join(config.HARNESS, 'output', 'lme_mask.nc')

def orca025_area_rule():
    def action():
        with netCDF4.Dataset(orca025_grid_nc) as nc:
            nav_lon = nc.variables['nav_lon'][:]
            nav_lat = nc.variables['nav_lat'][:]

        nlat,nlon = nav_lat.shape
        print('shape ', nav_lat.shape)

        wgs84=pyproj.Geod(ellps='WGS84')

        # ---- Compute area of each gridcell
        area = np.zeros((nlat, nlon))
        for jj in range(1,nlat-1):
            print('jj ', jj)
            for ii in range(1,nlon-1):
    #        for ii in range(1,2):
    #            print(jj,ii)

                lon_l = nav_lon[jj, ii-1]
                lon0 = nav_lon[jj,ii]
                lon_r = nav_lon[jj, ii+1]
                lat_u = nav_lat[jj-1, ii]
                lat0 = nav_lat[jj,ii]
                lat_d = nav_lat[jj+1, ii]

                dx = wgs84.inv(lon_r, lat0, lon_l, lat0)[2]
                dy = wgs84.inv(lon0, lat_d, lon0, lat_u)[2]
                area[jj,ii] = dx * dy

        print(dx)
        print(dy)


        # Store it
        os.makedirs(os.path.dirname(orca025_area_nc), exist_ok=True)
        with netCDF4.Dataset(orca025_area_nc, 'w') as nc:
            nc.createDimension('y', nlat)
            nc.createDimension('x', nlon)
            ncv = nc.createVariable('area', 'd', ('y', 'x'))
            ncv.descritpion='Area of each gridcell'
            ncv.units = 'm^2'

            ncv[:] = area


    #    dx = np.concatenate([
    #        np.zeros((nlat,1)),
    #        0.5 * (nav_lon[:,2:] - nav_lon[:,:-2]),
    #        np.zeros((nlat,1))],
    #        axis=1)

    #    print(dx.shape, nav_lon.shape)

    return make.Rule(action, [orca025_grid_nc], [orca025_area_nc])

# https://geopandas.org/en/stable/gallery/create_geopandas_from_pandas.html#:~:text=This%20example%20shows%20how%20to%20create%20a%20GeoDataFrame,matplotlib.pyplot%20as%20plt%20From%20longitudes%20and%20latitudes%20%23
def load_orca025_to_gdf():
    """Converts the orca025 grid to a GeoPandas dataframe of points"""

    with netCDF4.Dataset(orca025_grid_nc) as nc:
        nav_lon = nc.variables['nav_lon'][:]
        nav_lat = nc.variables['nav_lat'][:]
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


#    with open('gdf.pik', 'wb') as out:
#        pickle.dump(gdf, out)
#
#    print(gdf)
    return gdf


def lme_mask_rule():

    def action():

        with netCDF4.Dataset(orca025_grid_nc) as nc:
            nlat = len(nc.dimensions['y'])
            nlon = len(nc.dimensions['x'])

        # Polygons dataframe
        print('Loading LMEs from shapefile...')
        polys = geopandas.GeoDataFrame.from_file(LMEs66_shp) 
        polys = polys[['LME_NUMBER', 'geometry']]

        # Points dataframe
        print('Loading gridpoints into dataframe...')
        gdf = load_orca025_to_gdf()
    #    with open('gdf.pik', 'rb') as fin:
    #        gdf=pickle.load(fin).set_crs('EPSG:4326')

        print('Joining...')
        mask_df = geopandas.gpd.sjoin(gdf, polys, how='inner',op='within')
        mask_df = mask_df[['j', 'i', 'LME_NUMBER']]

        # Convert mask dataframe to mask raster
        mask = np.zeros((nlat,nlon), dtype='i')
        mask[mask_df.j, mask_df.i] = mask_df.LME_NUMBER.astype('i')


        # Store it
        os.makedirs(os.path.dirname(lme_mask_nc), exist_ok=True)
        with netCDF4.Dataset(lme_mask_nc, 'w') as nc:
            nc.createDimension('y', nlat)
            nc.createDimension('x', nlon)
            ncv = nc.createVariable('area', 'i', ('y', 'x'))
            ncv.descritpion='Large Marine Ecosystem (LME) Mask'

            ncv[:] = mask

    return make.Rule(action, [orca025_grid_nc, LMEs66_shp], [lme_mask_nc])


def main():
    makefile = make.Makefile()
    makefile.add(orca025_area_rule())
    makefile.add(lme_mask_rule())
    makefile.generate(os.path.join(config.HARNESS, 'output'), run=True)

main()
