# Brian Blaylock
# 16 December 2016

"""
Plot Sea Surface Temperature from NASA MUR (Multi-scale, Ultra-high resolution)
"""

from scipy.io import netcdf
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

FILE = '20161215090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc'

nc = netcdf.netcdf_file(FILE, 'r')

lat = nc.variables['lat'].data
lon = nc.variables['lon'].data
sst = nc.variables['analysed_sst'].data

#m = Basemap()
#m.drawcoastlines()

#plt.pcolormesh(lon, lat, sst)