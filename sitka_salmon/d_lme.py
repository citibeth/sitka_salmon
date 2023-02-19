import functools,os
import netCDF4
import geopandas
from sitka_salmon import config

# Inputs
LMEs66_shp = os.path.join(config.HARNESS, 'data', 'usgs', 'LMEs66', 'LMEs66.shp')

# Outputs
# Mask (on the ORCA025 grid) of the Large Marine Ecosystems
lme_mask_nc = os.path.join(config.HARNESS, 'output', 'lme_mask.nc')

# -------------------------------------------------------------
@functools.lru_cache()
def info():
    lme_df = geopandas.GeoDataFrame.from_file(LMEs66_shp)
    return lme_df

@functools.lru_cache()
def full_mask():
    with netCDF4.Dataset(lme_mask_nc, 'r') as nc:
        nc.set_auto_mask(False)
        return nc.variables['mask'][:]

def mask_in(lme):
    """Creates an integration mask for a single LME
    lme:
        Name of the LME to make a mask for
    """
    lme_id = int(info().set_index('LME_NAME').loc[lme].LME_NUMBER)
    return (full_mask() == lme_id)
