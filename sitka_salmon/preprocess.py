import os,functools,re,itertools,more_itertools,collections,pickle
import openpyxl
import pandas as pd
import netCDF4,pyproj
import numpy as np
import geopandas
from uafgi.util import make
from sitka_salmon import config
from sitka_salmon import d_orca025, d_lme, d_era5

"""Rules to compute weights and mask of the ORCA025 Grid"""

# The points in the ORCA025 grid as a GeoPandas dataframe
#orca025_gdf_pik = os.path.join(config.HARNESS, 'output', 'orca025_gdf.pik')



# ---------------------------------------------------------------
def orca025_area_action(tdir):
    import netCDF4

    nav_lat, nav_lon = d_orca025.get()
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
    os.makedirs(os.path.dirname(d_orca025.orca025_area_nc), exist_ok=True)
    with netCDF4.Dataset(d_orca025.orca025_area_nc, 'w') as nc:
        nc.set_auto_mask(False)
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

def orca025_area_rule():
    return make.Rule(orca025_area_action, [d_orca025.orca025_grid_nc], [d_orca025.orca025_area_nc])

# -----------------------------------------------------------------------



# ---------------------------------------------------------------------
def lme_mask_action(tdir):
    import netCDF4

    with netCDF4.Dataset(d_orca025.orca025_grid_nc) as nc:
        nc.set_auto_mask(False)
        nlat = len(nc.dimensions['y'])
        nlon = len(nc.dimensions['x'])

    # Polygons dataframe
    print('Loading LMEs from shapefile...')
    lme_df = geopandas.GeoDataFrame.from_file(d_lme.LMEs66_shp) 
    lme_df = lme_df[['LME_NUMBER', 'geometry']]

    # Points dataframe
    print('Loading gridpoints into dataframe...')
    gdf = d_orca025.gdf()
#    with open('gdf.pik', 'rb') as fin:
#        gdf=pickle.load(fin).set_crs('EPSG:4326')

    print('Joining...')
    mask_df = geopandas.gpd.sjoin(gdf, lme_df, how='inner',op='within')
    mask_df = mask_df[['j', 'i', 'LME_NUMBER']]

    # Convert mask dataframe to mask raster
    mask = np.zeros((nlat,nlon), dtype='i')
    mask[mask_df.j, mask_df.i] = mask_df.LME_NUMBER.astype('i')


    # Store it
    os.makedirs(os.path.dirname(d_lme.lme_mask_nc), exist_ok=True)
    with netCDF4.Dataset(d_lme.lme_mask_nc, 'w') as nc:
        nc.set_auto_mask(False)
        nc.createDimension('y', nlat)
        nc.createDimension('x', nlon)
        ncv = nc.createVariable('mask', 'i', ('y', 'x'))
        ncv.description='Large Marine Ecosystem (LME) Mask'

        ncv[:] = mask

def lme_mask_rule():
    return make.Rule(lme_mask_action, [d_orca025.orca025_grid_nc, d_lme.LMEs66_shp], [d_lme.lme_mask_nc])
# ----------------------------------------------------------------------------
def integrate_era5_rule(var):

    inputs = [d_lme.LMEs66_shp]
    for year in d_era5.years:
        for month in d_era5.months:
            inputs.append(d_era5.filename(var, year, month))

    outputs = [os.path.join(config.HARNESS, 'output', f'{var}.csv')]

    def action(tdir):
        #lmes = ['Gulf of Alaska', 'East Bering Sea', 'Aleutian Islands', 'West Bering Sea', 'Northern Bering - Chukchi Seas', 'Sea of Okhotsk', 'Oyashio Current', 'Kuroshio Current', 'Sea of Japan']

        df = d_era5.compute_var(var)
        ofname = os.path.join(config.HARNESS, 'output', f'{var}.csv')
        df.to_csv(ofname, index=False)

    return make.Rule(action, inputs, outputs)

