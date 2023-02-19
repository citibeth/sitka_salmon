import os
import numpy as np
import pandas as pd
import netCDF4
from sitka_salmon import config
from sitka_salmon import d_lme,d_orca025


vars = ('iicethic', 'ileadfra', 'sosstsst')
years = list(range(1959,2015))
#years = list(range(1959,1962))
months = (1,2, 6,7,8,12)

def filename(var, year, month):
    return os.path.join(config.HARNESS, 'data', 'era5', f'{var}_control_monthly_highres_2D_{year:04d}{month:02d}_CONS_v0.1.nc')


def integrate_month(var, year, month, lmes):
    """Loads a single month and integrates over the LMEs"""

    # Convert LME names to LME IDs
    lme_info = d_lme.info().set_index('LME_NAME')
    lme_ids = [lme_info.loc[lme] for lme in lmes]

    # Get the LME masks (indexed by LME ID)

    weightss = {lme: d_orca025.area() * d_lme.mask_in(lme) for lme in lmes}

    # Read the file
    with netCDF4.Dataset(filename(var, year, month)) as nc:
        nc.set_auto_mask(False)
        ncv = nc.variables[var]
        val = ncv[:]
        val[val == ncv._FillValue] = 0

    # Multiply by the weights and sum
    ret = dict(year=year, month=month)
    for lme,weights in weightss.items():
        ret[lme] = np.sum(val * weights) / np.sum(weights)
    return ret

def var(var, lmes=None):
    if lmes is None:
        lmes = list(d_lme.info().LME_NAME)

    rows = list()
    for year in years:
        print('(var,year) = ',var,year)
        for month in months:
            rows.append(integrate_month(var, year, month, lmes))

    return pd.DataFrame(rows)

#=['Gulf of Alaska', 'East Bering Sea']
