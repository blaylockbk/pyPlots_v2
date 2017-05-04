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
#m = draw_CONUS_HRRR_map()
m = draw_midwest_map()

def plot_temp2m(inputs):
    """
    Plots surface gusts with the MSLP countours
    """
    fxx = inputs[0]
    DATE = inputs[1]

    # Get the composite reflectivity
    VAR = 'TMP:2 m'
    H = get_hrrr_variable(DATE, VAR, fxx=fxx)

    # Get the mean sea level pressure
    VAR2 = 'MSLMA:mean sea level'
    H2 = get_hrrr_variable(DATE, VAR2, fxx=fxx)
    mslp = H2['value'] /100 # in hPa

    fig = plt.figure()
    fig.add_subplot(111)

    x, y = m(H['lon'], H['lat'])
    temp = H['value']-273.15 # in C

    m.drawstates()
    m.drawcoastlines()
    m.drawcountries()

    m.pcolormesh(x, y, ref, norm=norm, cmap='Spectral_r')
    cb = plt.colorbar(orientation='horizontal',
                      shrink=.7,
                      pad=.03)

    cb.set_label(r'2 m Temperature (C)')

    # MSLP Countours
    levels = np.arange(960, 1100, 4)
    CS = m.contour(x, y, mslp, colors='k', levels=levels)
    plt.clabel(CS, levels[1::2], fontsize=10, inline=1, fmt='%1.0f')

    if fxx == 0:
        plt.title('HRRR Anlys %s Valid: %s' % (VAR, H['valid']))
    else:
        plt.title('HRRR f%02d %s Valid: %s' % (fxx, VAR, H['valid']))

    savedate = H['valid'].strftime('valid_%Y-%m-%d_%H%M')
    plt.savefig(SAVE+savedate+'_f%02d' % (fxx), bbox_inches="tight", dpi=300)
    print 'saved', SAVE+savedate+'_f%02d' % (fxx)


if __name__ == "__main__":

    timer1 = datetime.now()

    # === Stuff you may want to change ========================================
    # Date range
    DATE = datetime(2017, 4, 4, 18)
    eDATE = datetime(2017, 4, 6, 0)

    # Forecast Hour
    fxx = 16

    # =========================================================================

    # Save directory
    BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
    SAVE = BASE + 'public_html/PhD/HRRR/Sample/' % (fxx)
    if not os.path.exists(SAVE):
        # make the SAVE directory
        os.makedirs(SAVE)
        # then link the photo viewer
        photo_viewer = BASE + 'public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
        os.link(photo_viewer, SAVE+'photo_viewer.php')

    base = DATE - timedelta(hours=fxx) # adjust for forecast hour
    hours = (eDATE-DATE).days * 24
    date_list = [[fxx, base + timedelta(hours=x)] for x in range(0, hours)]

    num_proc = multiprocessing.cpu_count() # use all processors
    p = multiprocessing.Pool(num_proc)

    # Create plot for each hour
    p.map(plot_temp2m, date_list)
    p.close()

    total_time = datetime.now() - timer1
    print ""
    print 'total time:', total_time, 'with', num_proc, 'processors.'

