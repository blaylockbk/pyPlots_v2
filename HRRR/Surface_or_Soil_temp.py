# Brian Blaylock
# 23 November 2016

"""
Q: Should I use the Surface temperature or the soil temperature??
A: Turns out, they are the same for points over water. Largest differences 
   occur over mountainous areas.
"""

import pygrib
from datetime import datetime
import matplotlib.pyplot as plt

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:/pyBKB_v2')
from BB_basemap.draw_maps import draw_utah_map
from BB_data.grid_manager import pluck_point



DATE = datetime(2016, 11, 22, 18)
DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/hrrr/' % (DATE.year, DATE.month, DATE.day)
FILE = 'hrrr.t%02dz.wrfprsf00.grib2' % (DATE.hour)

# Get Surface Temperature from the HRRR
grbs = pygrib.open(DIR+FILE)
print DATE
print 'Grabbed:', grbs(name='Temperature')[-1]
lat, lon = grbs(name='Temperature')[-1].latlons()
T_surface = grbs(name='Temperature')[-1].values
soil_temp = grbs(name='Soil Temperature')[0].values


m = draw_utah_map()

m.drawstates()
m.pcolormesh(lon, lat, T_surface-soil_temp, vmax=.5, vmin=-.5, cmap='bwr')
plt.colorbar()
plt.title('Difference between Surface Temp and Top Layer Soil Temp\n%s' % (DATE))
plt.savefig('Difference_between_surface_temp_and_soil_temp')
plt.show()
