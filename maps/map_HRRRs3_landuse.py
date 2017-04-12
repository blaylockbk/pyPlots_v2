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
from BB_cmap.landuse_colormap import LU_MODIS21

#==============================================================================

DATE = datetime(2016, 9, 1)
model = 'hrrr'

# 1) Get Landuse from HRRR S3 archive
VAR = 'VGTYP:surface'
if model == 'hrrrX':
    # The VGTYP variable is hidden here:
    VAR = 'var discipline=2 center=59 local_table=1 parmcat=0 parm=198'

H = get_hrrr_variable(DATE, VAR, model=model)

# 2) Get the map object and draw map
m = draw_CONUS_HRRR_map()
m.drawcoastlines(linewidth=.3)
m.drawcountries(linewidth=.3)
m.drawstates(linewidth=.3)

x, y = m(H['lon'], H['lat'])

# 3) Plot the map

# Colormap and labels
cm, labels = LU_MODIS21()

m.pcolormesh(x, y, H['value'], cmap=cm, vmin=1, vmax=len(labels) + 1)
cb = plt.colorbar(orientation='vertical',
                  shrink=.6,
                  pad=.01)
cb.set_ticks(np.arange(0.5, len(labels) + 1))
cb.ax.set_yticklabels(labels)
#cb.ax.set_xticklabels(labels) #If using a horizontal colorbar orientation
cb.ax.invert_yaxis()
cb.ax.tick_params(labelsize=5)

plt.title(model.upper() +' Landuse Categories: ' + DATE.strftime('%b %d, %Y'))

# 4) Save the figure
SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/climo/'
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

plt.savefig(SAVE+model+'_landuse.png', bbox_inches='tight', dpi=500)
