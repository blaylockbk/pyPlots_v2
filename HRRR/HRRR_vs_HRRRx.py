# Brian Blaylock
# January 30, 2017                  Why is it so cold outside!!!

"""
Plots the differences in temperature between the HRRR and HRRRx fields.
"""

import numpy as np
from datetime import datetime, timedelta
import pygrib
import matplotlib.pyplot as plt

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:/pyBKB_v2')
from BB_basemap.draw_maps import draw_Utah_map

# Yesterday's model directory
yesterday = datetime.now()-timedelta(days=1)
DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/' % (yesterday.year, yesterday.month, yesterday.day)

# Open HRRR and get surface temperature
grbs = pygrib.open(DIR+'hrrr/hrrr.t03z.wrfsfcf00.grib2')
temp = grbs.select(name="2 metre temperature")[0].values - 273.15
lat, lon = grbs.select(name="2 metre temperature")[0].latlons()

# Open HRRRx and get surface temperature
grbsX = pygrib.open(DIR+'hrrrX/hrrrX.t03z.wrfsfcf00.grib2')
tempX = grbsX.select(name="2 metre temperature")[0].values - 273.15
latX, lonX = grbsX.select(name="2 metre temperature")[0].latlons()

# Note: lat/lon and latX/lonX should be the same


# Draw map of Utah and plot temperatures
fig = plt.figure(figsize=[13,5])
# first pannel
ax = fig.add_subplot(131)
m = draw_Utah_map()
m.drawstates()
m.drawcoastlines()
m.pcolormesh(lon, lat, temp, cmap='Spectral_r', vmax=temp.max(), vmin=temp.min())
plt.colorbar(orientation='horizontal', shrink=.9, pad=.03)
plt.title('hrrr')

# second pannel
ax = fig.add_subplot(132)
m = draw_Utah_map()
m.drawstates()
m.drawcoastlines()
m.pcolormesh(lon, lat, tempX, cmap='Spectral_r', vmax=temp.max(), vmin=temp.min())
plt.colorbar(orientation='horizontal', shrink=.9, pad=.03)
plt.title('hrrrX')

# third pannel
ax = fig.add_subplot(133)
m = draw_Utah_map()
m.drawstates()
m.drawcoastlines()
m.pcolormesh(lon, lat, tempX-temp, cmap='bwr', vmax=5, vmin=-5)
plt.colorbar(orientation='horizontal', shrink=.9, pad=.03, extend='both')
plt.title('hrrrX - hrrr')

plt.suptitle('2-m Temperature')
