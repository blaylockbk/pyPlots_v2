# Brian Blaylock
# 7 December 2016

"""
Great Salt Lake Surface Temperatures (MODIS)
From: http://www.4dwx.org/projects/GreatSaltLake_temperature/catalog.html
"""

from scipy.io import netcdf
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
from mpl_toolkits.basemap import Basemap
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:/pyBKB_v2')
from BB_basemap.draw_maps import draw_GSL_map


FILE = 'C:\Users\u0553130\Desktop\modis_final_2016341.nc'

nc = netcdf.netcdf_file(FILE, 'r')

ncV = nc.variables

lon = ncV['lon'].data
lat = ncV['lat'].data

# Lake Mask (1=water, 0=land)
water_mask = ncV['GSL_water'].data

# expanded lake (full possible lake size??)
GSL_expanded = ncV['GSL_expand'].data

# threshold lake (smallest possible lake size??)
GSL_thresh = ncV['GSL_thresh'].data

# Lake temperatures (degrees C)
# mask anything larger than 100 C

mo_LST = ncV['mo_LST'].data
mask_LST = ma.masked_values(mo_LST, mo_LST[0,0])

# Plot
m = draw_GSL_map()
m.drawcoastlines()
m.pcolormesh(lon, lat, mask_LST,
               vmax=30, vmin=-10)
plt.colorbar()
plt.contour(lon, lat, water_mask,
            levels=[0,1])


plt.show(block=False)

