# Brian Blaylock
# March 29, 2017                       My bus buddy Brent is retires next month

"""
Plot Topography of the HRRR model
"""
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
#mpl.rcParams['figure.figsize'] = [15, 8]
mpl.rcParams['figure.titlesize'] = 13
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['legend.fontsize'] = 15
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')

from BB_basemap.draw_maps import draw_CONUS_HRRR_map
from BB_downloads.HRRR_S3 import get_hrrr_variable
from BB_cmap.terrain_colormap import terrain_cmap_256

DATE = datetime(2017, 1, 1)

# 1) Get Topography and Land-Sea mask from HRRR S3 archive
VAR = 'HGT:surface'
LAND = 'LAND:surface'

H = get_hrrr_variable(DATE, VAR)
L = get_hrrr_variable(DATE, LAND, value_only=True)

# 2) Set water value in Topography
water = -99
topo = H['value']
topo[L['value'] == 0] = water

# 2) Get the map object and draw map
m = draw_CONUS_HRRR_map()
m.drawcoastlines(linewidth=.5, color=(0,0,0,.75))
m.drawcountries(linewidth=.5, color=(0,0,0,.75))
m.drawstates(linewidth=.3, color=(0,0,0,.75))

x, y = m(H['lon'], H['lat'])

# 3) Plot the map
m.pcolormesh(x, y, topo, cmap=terrain_cmap_256())
cb = plt.colorbar(orientation='horizontal',
                  shrink=.9,
                  pad=.03)
cb.set_label('Topography (m)')

plt.title('HRRR Terrain Height')

# 4) Save the figure
SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/climo/'
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

plt.savefig(SAVE+'hrrr_topography.png', bbox_inches='tight', dpi=500)
