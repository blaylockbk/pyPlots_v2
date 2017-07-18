# Brian Blaylock
# July 6, 2017                        Had some free pizza for lunch today :)

import matplotlib as mpl
#mpl.use('Agg') #required for the CRON job. Says "do not open plot in a window"??
import numpy as np
from datetime import date, datetime, timedelta
import time
import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.dates as mdates
from matplotlib.patches import Polygon
from matplotlib import colors as c
from matplotlib.collections import PatchCollection

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [15, 6]
mpl.rcParams['figure.titlesize'] = 15
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['lines.linewidth'] = 1.8
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.05
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.framealpha'] = .75
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 750
mpl.rcParams['savefig.transparent'] = False

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/lib/python2.7/site-packages/')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_S3 import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_MesoWest.MesoWest_radius import get_mesowest_radius
from MetPy_BB.plots import ctables
from BB_data.grid_manager import pluck_point_new
from BB_wx_calcs.wind import wind_uv_to_spd, wind_spddir_to_uv
from BB_wx_calcs.units import *
from BB_basemap.draw_maps import draw_CONUS_cyl_map

# =============================================================================
daylight = time.daylight # If daylight is on (1) then subtract from timezone.
location = {'UKBKB': {'latitude':40.09867,
                      'longitude':-111.62767,
                      'name':'Spanish Fork Bench',
                      'timezone': 7-daylight,
                      'is MesoWest': True},
            'KSLC':{'latitude':40.77069,
                    'longitude':-111.96503,
                    'name':'Salt Lake International Airport',
                    'timezone': 7-daylight,
                    'is MesoWest': True}}

colors = ['red', 'lightsage', 'lightpink', 'lawngreen', 'tomato', \
            'skyblue', 'thistle', 'teal', 'steelblue', 'springgreen', \
            'powderblue', 'red', 'blue', 'yellow', 'orange', \
            'brown', 'cornsilk', 'darkgrey', 'seagreen']

def splot_same_time(DATE, loc, fxx=range(18,-1, -1)):
    """
    Make paint splots for a single verification time

    Input: 
        DATE - the verification time. Will consider all forecast hours for that
               time.
        loc  - a dictionary of data about the location.
        fxx  - forecast hours (work backwards from 18 to 0 so analysis hour is plotted on top)
    """

    #for L in loc:
    #    l = loc[L]
    #
    #    # Create a figure
    #    plt.clf()
    #    plt.cla()
    #    m = Basemap(resolution='i', projection='cyl',\
    #                llcrnrlon=l['longitude']-.75, llcrnrlat=l['latitude']-.75,\
    #                urcrnrlon=l['longitude']+.75, urcrnrlat=l['latitude']+.75,)
    m = draw_CONUS_cyl_map()
    m.arcgisimage(service='World_Shaded_Relief', xpixels=2700, verbose=False)
    m.drawstates()
    m.drawcountries()

    for f in fxx:
        # Get HRRR data
        get_DATE = DATE - timedelta(hours=f)
        H = get_hrrr_variable(get_DATE, 'REFC:entire atmosphere', fxx=f)
        # Set mask criteria
        dBZ = H['value']
        dBZ = np.ma.array(dBZ)
        dBZ[dBZ < 20] = np.ma.masked
        # Plot the masked array on the map
        plt.pcolormesh(H['lon'], H['lat'], dBZ, cmap=c.ListedColormap([colors[f]]), alpha=.5)
        plt.title('All forecasts valid at %s\nHRRR Reflectivity > 20 dBZ' % (DATE.strftime('%Y-%b-%d %H:%M')))

    plt.savefig('REF_paint_validat_%s' % DATE.strftime("%Y%m%d-%H%M"))



def splot_same_run(DATE, fxx=range(0,19)):
    """
    Make paint splots for each hour of a certain model run hour.

    Input: 
        DATE - the model run time. Will consider all forecast hours outputed by
               the model at that run time.
    """
    m = draw_CONUS_cyl_map()
    m.arcgisimage(service='World_Shaded_Relief', xpixels=2700, verbose=False)
    m.drawstates()
    m.drawcountries()

    for f in fxx:
        # Get HRRR data
        H = get_hrrr_variable(DATE, 'REFC:entire atmosphere', fxx=f)
        # Set mask criteria
        dBZ = H['value']
        dBZ = np.ma.array(dBZ)
        dBZ[dBZ < 20] = np.ma.masked
        # Plot the masked array on the map
        plt.pcolormesh(H['lon'], H['lat'], dBZ, cmap=c.ListedColormap([colors[f]]), alpha=.5)
        plt.title('Run begining at %s\nHRRR Reflectivity > 20 dBZ' % (DATE.strftime('%Y-%b-%d %H:%M')))

    plt.savefig('REF_paint_runbegining_%s' % DATE.strftime("%Y%m%d-%H%M"))

if __name__ == "__main__":
    DATE = datetime(2017, 7, 6, 18)
    splot_same_time(DATE, loc=location)
    splot_same_run(DATE)