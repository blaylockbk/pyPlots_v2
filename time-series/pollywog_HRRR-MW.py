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
DATE = datetime(2017, 4, 4, 12)
eDATE = datetime(2017, 4, 6, 12)

# MesoWest variable name (we'll translate the HRRR variable later)
#MW_var = 'air_temp'
#MW_var = 'wind_speed'
#MW_var = 'wind_gust'
MW_var = 'sea_level_pressure'

# MesoWest stations for time series
if MW_var == 'air_temp':
    stations = ['KSTL', 'KSUS', 'KSPI', 'E0975']
if MW_var == 'wind_speed':
    stations = ['KSTL', 'KSUS', 'KSPI', 'E0975']
if MW_var == 'sea_level_pressure':
    stations = ['p43ax', 'q44bx', 'o44ax', 'KSTL', 'KSUS', 'KSPI', 'E0975', 'E0126']

# Pollywog hours: a list of hours you want a pollywog to spawn
pHours = range(24)

# Head hours: a list of hours you want to plot a pollywog head (analysis value)
hHours = range(24)

# =============================================================================
# =============================================================================
# Variable name conversion between MesoWest and HRRR
var_convert = {'air_temp':'TMP:2 m',
               'wind_speed':'WIND:10 m',
               'wind_gust':'GUST:surface',
               'sea_level_pressure':'MSLMA:mean sea level'}

# HRRR variable name
HR_var = var_convert[MW_var]

# Create the hourly date list
base = DATE
hours = (eDATE-DATE).days * 24 + (eDATE-DATE).seconds/3600
date_list = [base + timedelta(hours=x) for x in range(0, hours)]

# Control plotting distinct colors based on number of pollywogs
#num_colors = len(pHours)*(eDATE-DATE).days
#color_idx = np.linspace(.1, .9, num_colors)
#colors = cm.nipy_spectral(color_idx)

# Nahh, just cycle through a long list of these colors.
colors = ['red', 'royalblue', 'green', 'darkorange'] * 10

# Create pollywog plot overlaying HRRR and MesoWest data for each station.
for stn in stations:
    # Color index
    color_count = 0
    
    # Create the plot
    fig, ax = plt.subplots(1)

    # Get MesoWest data
    a = get_mesowest_ts(stn, DATE, eDATE)
    # Plot the MesoWest data
    if MW_var == 'sea_level_pressure':
        if 'sea_level_pressure' not in a.keys():
            plt.plot(a['DATETIME'], a['altimeter']/100, c='k', lw=3)
        else:
            plt.plot(a['DATETIME'], a['sea_level_pressure']/100, c='k', lw=3)

    else:
        plt.plot(a['DATETIME'], a[MW_var], c='k', lw=3, zorder=1)

    for D in date_list:
        if D.hour in pHours:
            # Get HRRR pollywog for each hour requested and convert units
            pDates, pValues = get_hrrr_pollywog(D, HR_var, a['LAT'], a['LON'])
            if MW_var == 'air_temp':
                pValues = pValues-273.15
            if MW_var == 'sea_level_pressure':
                pValues = pValues/100

            # Plot the HRRR data
            plt.scatter(pDates[0], pValues[0], c=colors[color_count], s=80, lw=0, zorder=2)
            plt.plot(pDates, pValues, c=colors[color_count], lw=2, zorder=2)
            color_count += 1
        if D.hour in hHours:
            # Plot the head (analysis) value
            pDates, pValues = get_hrrr_pollywog(D, HR_var, a['LAT'], a['LON'], forecast_limit=0)
            if MW_var == 'air_temp':
                pValues = pValues-273.15
            if MW_var == 'sea_level_pressure':
                pValues = pValues/100
            # Plot the HRRR data point grey
            plt.scatter(pDates[0], pValues[0], c=[.2, .2, .2], s=30, lw=0, zorder=3)

    # Figure Cosmetics
    if MW_var == 'air_temp':
        plt.title('Temperature at %s' % (stn))
        plt.ylabel('Temperature (C)')
    elif MW_var == 'wind_speed':
        plt.title('Wind Speed at %s' % (stn))
        plt.ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
    elif MW_var == 'wind_gust':
        plt.title('Wind Gust at %s' % (stn))
        plt.ylabel(r'Wind Gust (ms$\mathregular{^{-1}}$)')
    elif MW_var == 'sea_level_pressure':
        plt.title('Sea Level Pressure at %s' % (stn))
        plt.ylabel('Pressure (hPa)')
    ax.set_xlim([date_list[0], date_list[-1]])
    plt.grid()
    ax.xaxis.set_major_locator(mdates.HourLocator([0, 12]))
    ax.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 3)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))

    plt.savefig(SAVE+stn+'_pollywog_%s.png' % (MW_var))
    plt.close()
    print "\nPlotted a Pollywog:", SAVE+stn+'_pollywog_%s.png' % (MW_var)
