import os
from uafgi.util import make
from sitka_salmon import config,preprocess
from sitka_salmon import d_era5

def main():
    makefile = make.Makefile()
    makefile.add(preprocess.orca025_area_rule())
    makefile.add(preprocess.lme_mask_rule())
    for var in d_era5.vars:
        makefile.add(preprocess.integrate_era5_rule(var))
    makefile.generate(os.path.join(config.HARNESS, 'output', 'preprocess_mk'),
        run=True, ncpu=8)

main()

#x=d_era5.integrate_month('sosstsst', 2013, 6)
#print(x)

#x = d_era5.var('sosstsst', )
#print(x)

