# Brian Blaylock
# April 13, 2017                 Utah Jazz finally going to the playoffs again!

"""
Plot pollywog graph of HRRR forecasts (from S3 archive) with MesoWest
observations. (need to speed this up with multiprocessing or smarter pluck function)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cm
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
mpl.rcParams['savefig.dpi'] = 300

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_S3 import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts

# === Save directory ==========================================================
BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
SAVE = BASE + 'public_html/PhD/HRRR/GravityWave_2017-04-05/pollywog/'
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = BASE + 'public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

# === Stuff you may want to change ============================================
# Date range
DATE = datetime(2017, 4, 4, 0)
eDATE = datetime(2017, 4, 7, 0)

# MesoWest stations for time series
stations = ['KSTL', 'KSUS', 'KSPI', 'E0975', 'E0126']
stations = ['KSTL']

# Pollywog hours: a list of hours you want a pollywog to spawn
pHours = [0, 6, 12, 18]

# Head hours: a list of hours you want to plot a pollywog head (analysis value)
hHours = range(24)

# MesoWest variable name (we'll translate the HRRR variable later)
MW_var = 'air_temp'

# =============================================================================
# =============================================================================
# Variable name conversion between MesoWest and HRRR
var_convert = {'air_temp':'TMP:2 m',
               'wind_speed':'WIND:10 m'}

# HRRR variable name
HR_var = var_convert[MW_var]

# Create the hourly date list
base = DATE
hours = (eDATE-DATE).days * 24
date_list = [base + timedelta(hours=x) for x in range(0, hours)]

# Control plotting distinct colors based on number of pollywogs
num_colors = len(pHours)*(eDATE-DATE).days
color_idx = np.linspace(0, 1, num_colors)
colors = cm.jet(color_idx)
color_count = 0

# Create pollywog plot overlaying HRRR and MesoWest data for each station.
for stn in stations:
    # Create the plot
    fig, ax = plt.subplots(1)

    # Get MesoWest data
    a = get_mesowest_ts(stn, DATE, eDATE)
    # Plot the MesoWest data
    plt.plot(a['DATETIME'], a[MW_var], c='k', lw=3, zorder=1)

    for D in date_list:
        if D.hour in pHours:
            # Get HRRR pollywog for each hour requested
            pDates, pValues = get_hrrr_pollywog(D, HR_var, a['LAT'], a['LON'])
            if MW_var == 'air_temp':
                pValues = pValues-273.15
            # Plot the HRRR data
            plt.scatter(pDates[0], pValues[0], c=colors[color_count], s=80, lw=0, zorder=2)
            plt.plot(pDates, pValues, c=colors[color_count], lw=2, zorder=2)
            color_count += 1
        if D.hour in hHours:
            # Plot the head (analysis) value
            pDates, pValues = get_hrrr_pollywog(D, HR_var, a['LAT'], a['LON'], forecast_limit=0)
            if MW_var == 'air_temp':
                pValues = pValues-273.15
            # Plot the HRRR data point grey
            plt.scatter(pDates[0], pValues[0], c=[.2,.2,.2], s=30, lw=0, zorder=3)



    # Figure Cosmetics
    if MW_var == 'air_temp':
        plt.title('Temperature at %s' % (stn))
        plt.ylabel('Temperature (C)')
    elif MW_var == 'wind_speed':
        plt.title('Wind Speed at %s (f%02d)' % (stn, fxx))
        plt.ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
    ax.set_xlim([date_list[0], date_list[-1]])
    plt.grid()
    ax.xaxis.set_major_locator(mdates.HourLocator([0, 12]))
    ax.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 3)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))

    plt.savefig(SAVE+stn+'_pollywog_%s.png' % (MW_var))
    plt.close()
    print "\nPlotted a Pollywog:", SAVE+stn+'_pollywog_%s.png' % (MW_var)
