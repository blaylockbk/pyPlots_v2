# Brian Blaylock
# March 15, 2017                                                "Et tu, Brute?"

"""
Plot a map of mean sea level pressure from the HRRR model
"""
from numpy import ma
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
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
mpl.rcParams['savefig.dpi'] = '500'

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')

from BB_basemap.draw_maps import *
from BB_downloads.HRRR_S3 import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from MetPy_BB.plots import ctables

# Get the map object
m = draw_CONUS_HRRR_map()

def plots(inputs):
    fxx = inputs[0]
    DATE = inputs[1]

    plt.figure(1)
    # Get the 2m Temperature
    VAR = 'TMP:2 m'
    H = get_hrrr_variable(DATE, VAR, fxx=fxx)
    x, y = m(H['lon'], H['lat'])
    temp = H['value']-273.15 # in C
    m.drawstates()
    m.drawcoastlines()
    m.drawcountries()
    m.pcolormesh(x, y, temp, cmap='Spectral_r')
    savedate = H['valid'].strftime('valid_%Y-%m-%d_%H%M')
    plt.savefig(SAVE+savedate+'_f%02d_TEMP2m' % (fxx), bbox_inches="tight", dpi=300)


    plt.figure(2)
    # Get the mean sea level pressure
    VAR = 'MSLMA:mean sea level'
    H = get_hrrr_variable(DATE, VAR, fxx=fxx)
    mslp = H['value'] /100 # in hPa
    m.drawstates()
    m.drawcoastlines()
    m.drawcountries()
    plt.pcolormesh(x, y, mslp, cmap='viridis')
    levels = np.arange(960, 1100, 4)
    CS = m.contour(x, y, mslp, colors='k', linewidths=.7, levels=levels)
    plt.clabel(CS, levels[1::2], fontsize=8, inline=1, fmt='%1.0f')
    plt.savefig(SAVE+savedate+'_f%02d_MSLP' % (fxx), bbox_inches="tight", dpi=300)

    plt.figure(3)
    # Get Simulated Composite Reflectivity
    VAR = 'REFC:entire atmosphere'
    H = get_hrrr_variable(DATE, VAR, fxx=fxx)
    ref = H['value'] # in dBZ
    ref = ma.array(ref)
    ref[ref == -10] = ma.masked
    m.drawstates()
    m.drawcoastlines()
    m.drawcountries()
    ctable = 'NWSReflectivity'
    norm, cmap = ctables.registry.get_with_steps(ctable, -0, 5)
    m.pcolormesh(x, y, ref, norm=norm, cmap=cmap)
    plt.savefig(SAVE+savedate+'_f%02d_REFC' % (fxx), bbox_inches="tight", dpi=300)

    plt.figure(4)
    # Get the mean sea level pressure
    VAR = 'DPT:2 m'
    H = get_hrrr_variable(DATE, VAR, fxx=fxx)
    dwpt = H['value'] -273.15
    m.drawstates()
    m.drawcoastlines()
    m.drawcountries()
    plt.pcolormesh(x, y, dwpt, cmap='BrBG', vmin=-20, vmax=20)
    plt.savefig(SAVE+savedate+'_f%02d_DWPT' % (fxx), bbox_inches="tight", dpi=300)

    plt.figure(5)
    # Gust
    VAR = 'GUST:surface'
    H = get_hrrr_variable(DATE, VAR, fxx=fxx)
    gust = H['value']
    m.drawstates()
    m.drawcoastlines()
    m.drawcountries()
    plt.pcolormesh(x, y, gust, cmap='inferno_r')
    plt.savefig(SAVE+savedate+'_f%02d_Gust' % (fxx), bbox_inches="tight", dpi=300)


if __name__ == "__main__":

    timer1 = datetime.now()

    # === Stuff you may want to change ========================================
    # Date range
    DATE = datetime(2017, 4, 5, 14)

    # Forecast Hour
    fxx = 0

    # =========================================================================

    # Save directory
    BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
    SAVE = BASE + 'public_html/PhD/HRRR/Samples/'
    if not os.path.exists(SAVE):
        # make the SAVE directory
        os.makedirs(SAVE)
        # then link the photo viewer
        photo_viewer = BASE + 'public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
        os.link(photo_viewer, SAVE+'photo_viewer.php')

    plots([fxx, DATE])
