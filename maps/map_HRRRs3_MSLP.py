# Brian Blaylock
# March 15, 2017                                                "Et tu, Brute?"

"""
Plot a map of mean sea level pressure from the HRRR model
"""

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

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')

from BB_basemap.draw_maps import draw_CONUS_HRRR_map
from BB_downloads.HRRR_S3 import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts

# Save directory
BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
SAVE = BASE + 'public_html/PhD/HRRR/plan-view/MSLP/'
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = BASE + 'public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

# Get the map object
m = draw_CONUS_HRRR_map()

def plot_MSLP(DATE):
    # Get the mean sea level pressure data
    VAR = 'MSLMA:mean sea level' # Mean sea level MAPS System Reduction
    H = get_hrrr_variable(DATE, VAR)

    fig = plt.figure()
    fig.add_subplot(111)

    x, y = m(H['lon'], H['lat'])
    mslp = H['value'] /100 # in hPa
    m.drawstates()
    m.drawcoastlines()
    m.drawcountries()

    m.pcolormesh(x, y, mslp, cmap='viridis', vmin=976, vmax=1040)
    cb = plt.colorbar(orientation='horizontal',
                      shrink=.9,
                      pad=.03,
                      ticks=range(976, 1041, 4)[0::2], # Label every other contour
                      extend="both")
    cb.set_label('Mean Sea Level Pressure (hPa)')

    levels = np.arange(960, 1100, 4)
    CS = m.contour(x, y, mslp, colors='k', levels=levels)
    plt.clabel(CS, levels[1::2], fontsize=10, inline=1, fmt='%1.0f')

    plt.title('HRRR Anlys %s Valid: %s' % (VAR, H['valid']))

    savedate = H['valid'].strftime('%Y-%m-%d_%H%M')
    plt.savefig(SAVE+savedate, bbox_inches="tight", dpi=300)
    print 'saved', savedate


if __name__ == "__main__":

    timer1 = datetime.now()

    # === Stuff you may want to change ========================================
    # Date range
    DATE = datetime(2017, 3, 13, 0)
    eDATE = datetime(2017, 3, 16, 0)

    # MesoWest Station for Time series
    stn = 'M65AX'

    # =========================================================================

    base = DATE
    hours = (eDATE-DATE).days * 24
    date_list = [base + timedelta(hours=x) for x in range(0, hours)]

    num_proc = multiprocessing.cpu_count() # use all processors
    p = multiprocessing.Pool(num_proc)

    # Create map for each hour
    p.map(plot_MSLP, date_list)

    total_time = datetime.now() - timer1
    print ""
    print 'total time:', total_time, 'with', num_proc, 'processors.'

    # Create pressure time series plot for HRRR and MesoWest:
    # Get MesoWest data
    a = get_mesowest_ts(stn, DATE, eDATE)

    date, data = point_hrrr_time_series(DATE, eDATE, variable='MSLMA:mean sea level',
                                        lat=a['LAT'], lon=a['LON'],
                                        fxx=0, model='hrrr', field='sfc',
                                        reduce_CPUs=0)

fig, ax = plt.subplots(1)
plt.plot(date, data/100, c='k', lw=2, label="HRRR") # convert Pa to hPa
plt.plot(a['DATETIME'], a['pressure']/100, c='r', lw=2, label=stn)
plt.title('MSLMA:mean sea level at %s' % stn)
plt.ylabel('Pressure (hPa)')
ax.set_yticks(range(976, 1041, 4)[0::2])
plt.legend()
plt.grid()
ax.xaxis.set_major_locator(mdates.HourLocator([0, 12]))
ax.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 3)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))
plt.savefig(SAVE+stn+'_timeseries.png')
plt.show(block=False)