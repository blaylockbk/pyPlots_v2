# Brian Blaylock
# June 13, 2017                      Golden State beats the Cavs. James is sad.

"""
For a MesoWest Station, create a hovmoller-style diagram to show how the HRRR
forecasted variables change between each successive forecast.

1) Hovmoller Point
2) Hovmoller Max in area
"""
import numpy as np
from datetime import datetime, timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_downloads.HRRR_S3 import point_hrrr_time_series_multi
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from matplotlib.dates import DateFormatter, HourLocator

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [14, 8]
mpl.rcParams['figure.titlesize'] = 15
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['lines.linewidth'] = 1.8
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.01
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.framealpha'] = .75
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100
mpl.rcParams['savefig.transparent'] = False

#==============================================================================
# Set Date Range
sDATE = datetime(2017, 6, 8)
eDATE = datetime(2017, 6, 13)

# Set Station Location
stn = 'GNI'

# Set the Variable
HRRR_var = 'WIND:10 m'
MW_var = 'wind_speed'
title_var = "Wind Speed"
#==============================================================================

# Get data from the MesoWest Station
a = get_mesowest_ts(stn, sDATE, eDATE, variables=MW_var)

# Make a time series of HRRR forecasts for each forecast hour.
loc = {stn:{'latitude':a['LAT'],'longitude':a['LON']}}
data = {}
for f in range(19):
    sOffset = sDATE - timedelta(hours=f)
    eOffset = eDATE - timedelta(hours=f)
    data[f] = point_hrrr_time_series_multi(sOffset, eOffset, loc,
                                           variable=HRRR_var,
                                           fxx=f)

# combine the data arrays into a hovmoller array
hovmoller = np.array([data[i][stn] for i in range(19)])
hovDATES = np.append(data[0]['DATETIME'], data[0]['DATETIME'][-1]+timedelta(hours=1))
hovFxx = range(20)
hmin = np.nanmin([np.nanmin(a[MW_var]), np.nanmin(hovmoller)])
hmax = np.nanmax([np.nanmax(a[MW_var]), np.nanmax(hovmoller)])

# Plot the Hovmoller diagram
fig = plt.figure(1)
ax1 = plt.subplot2grid((8, 1), (0, 0), rowspan=7)
ax2 = plt.subplot(8, 1, 8)

plt.suptitle('%s %s\n%s - %s' % (stn, title_var, sDATE.strftime('%Y-%m-%d %H:%M'), eDATE.strftime('%Y-%m-%d %H:%M')))

hv = ax1.pcolormesh(hovDATES, hovFxx, hovmoller, cmap='magma_r', vmax=hmax, vmin=hmin)
ax1.set_xlim(hovDATES[0], hovDATES[-1])
ax1.set_ylim(0, 19)
ax1.set_yticks(range(0,19,3))
ax1.axes.xaxis.set_ticklabels([])
ax1.set_ylabel('HRRR Forecast Hour')

mw = ax2.pcolormesh(a['DATETIME'], range(3), [a['wind_speed'],a['wind_speed']], cmap='magma_r', vmax=hmax, vmin=hmin)
ax2.axes.yaxis.set_ticklabels([])
ax2.set_yticks([])
ax2.set_ylabel('Observed')


fig.subplots_adjust(hspace=0, right=0.8)
cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
cb = fig.colorbar(hv, cax=cbar_ax)
cb.ax.set_ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')

ax2.xaxis.set_major_locator(HourLocator(byhour=[0, 6, 12, 18]))
dateFmt = DateFormatter('%b %d\n%H:%M')
ax2.xaxis.set_major_formatter(dateFmt)

plt.savefig('HRRR_hovmoller_%s.png' % stn)
