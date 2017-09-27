# Brian Blaylock
# September 26, 2017            # It is Millie's Birthday party today

"""
Overlay HRRR data over GOES-16 images
"""

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta
from netCDF4 import Dataset
import urllib
import os
import multiprocessing # :)

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
sys.path.append('H:\\pyBKB_v2')

from BB_GOES16.get_GOES16 import files_on_pando, get_GOES16_truecolor
from BB_basemap.draw_maps import draw_CONUS_HRRR_map, draw_Utah_map
from BB_downloads.HRRR_S3 import get_hrrr_variable


DATE = datetime(2017, 9, 24)
flist = files_on_pando(DATE)

# Draw Map Objects
m = draw_CONUS_HRRR_map()

def plot_Gfile(f):
    # File scan Start time
    scanStart = datetime.strptime(f.split('_')[3], 's%Y%j%H%M%S%f')

    # Build the URL and temporary file name, then download
    URL = "https://pando-rgw01.chpc.utah.edu/GOES16/ABI-L2-MCMIPC/%s/%s" % (DATE.strftime('%Y%m%d'), f)
    NAME = "./temp_GOES16_%s.nc" % (scanStart.strftime('%Y%m%d_%H%M')) 
    urllib.urlretrieve(URL, NAME)

    # Get GOES TrueColor
    G = get_GOES16_truecolor(NAME)

    # Get HRRR Variable
    hDATE = datetime(scanStart.year, scanStart.month, scanStart.day, scanStart.hour)
    H = get_hrrr_variable(hDATE, variable='TMP:700 mb')

    # Plot GOES-16 True Color
    plt.figure(1, figsize=(8,10))
    plt.clf(); plt.cla()
    newmap = m.pcolormesh(G['lon'], G['lat'], G['TrueColor'][:,:,1],
                            color=G['rgb_tuple'],
                            linewidth=0,
                            latlon=True)
    newmap.set_array(None) # must have this line if using pcolormesh and linewidth=0

    # Plot HRRR 700 mb temperatures on map
    CS = m.contour(H['lon'], H['lat'], H['value']-273.15, 
                    latlon=True,
                    levels=range(-30,30,2),
                    cmap='Spectral_r', vmin=-10, vmax=10)
    plt.clabel(CS, inline=1, fmt='%2.f')
    
    m.drawcoastlines()
    m.drawstates()
    
    plt.title('GOES-16 TrueColor/IR and HRRR 700 mb Temperature\nGOES Date:%s\nHRRR Date:%s' \
           % (G['DATE'].strftime('%Y %b %d, %H:%M'), H['valid'].strftime('%Y %b %d, %H:%M')))
    figname = 'GOES16TrueColor_HRRR700mbTemp_%s.png' % (G['DATE'].strftime('%Y%m%d-%H%M'))
    plt.savefig(figname, bbox_inches='tight', dpi=150)
    print "Created:", figname

    # Remove the temp file
    os.remove(NAME)
    print 'removed:',NAME


p = multiprocessing.Pool(15)
p.map(plot_Gfile, flist)
p.close()

