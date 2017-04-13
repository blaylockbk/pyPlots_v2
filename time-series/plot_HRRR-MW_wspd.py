# Brian Blaylock
# April 12, 2017                                              Back from Boston

"""
Plot comparision of MesoWest observed sea level pressure and 
HRRR sea level pressure (from HRRR S3 archive).
"""


import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import matplotlib as mpl
## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [8, 4]
mpl.rcParams['figure.titlesize'] = 13
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['legend.fontsize'] = 10
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')

from BB_basemap.draw_maps import *
from BB_downloads.HRRR_S3 import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_cmap.my_cmap import cmap_gust

# Save directory
BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
SAVE = BASE + 'public_html/PhD/HRRR/GravityWave_2017-04-05/timeseries_wspd/'
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = BASE + 'public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

# === Stuff you may want to change ========================================
# Date range
DATE = datetime(2017, 4, 4, 0)
eDATE = datetime(2017, 4, 7, 0)

# MesoWest Station for Time series
stations = ['KSTL', 'KSUS', 'KSPI', 'E0975', 'E0126']

# Forecast Hour
forecasts = [0, 6, 12, 16, 18]

# =========================================================================

base = DATE
hours = (eDATE-DATE).days * 24
date_list = [base + timedelta(hours=x) for x in range(0, hours)]

for stn in stations:
    for fxx in forecasts:

        # Create pressure time series plot for HRRR and MesoWest:
        # Get MesoWest data
        a = get_mesowest_ts(stn, DATE, eDATE)

        Hvar = 'WIND:10 m above '
        validDate, value = point_hrrr_time_series(DATE, eDATE, variable=Hvar,
                                                  lat=a['LAT'], lon=a['LON'],
                                                  fxx=fxx, model='hrrr', field='sfc',
                                                  reduce_CPUs=0)
        # Create the plot
        fig, ax = plt.subplots(1)

        # Plot the HRRR data
        plt.plot(validDate, value, c='k', lw=2, label="HRRR") # convert Pa to hPa

        # Plot the MesoWest data
        plt.plot(a['DATETIME'], a['wind_speed'], c='r', lw=2, label=stn)

        plt.title('Wind Speed at %s (f%02d)' % (stn, fxx))
        plt.ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
        ax.set_xlim([date_list[0], date_list[-1]])
        plt.legend(loc=2)
        plt.grid()
        ax.xaxis.set_major_locator(mdates.HourLocator([0, 12]))
        ax.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 3)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))

        plt.savefig(SAVE+stn+'_timeseries_f%02d.png' % (fxx))
        plt.close()
