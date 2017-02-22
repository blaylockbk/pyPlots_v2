# Brian Blaylock
# Feburary 9, 2017              Rachel and I finished a 500 pc puzzle yesterday

"""
Plot a time height from HRRR Bufr Data
    - Potential Temperature
    - Temperature
    - Dew point temperature
    - Relative Humidity
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:/pyBKB_v2')
from BB_HRRR.get_bufr_sounding import get_bufr_sounding
from BB_wx_calcs.thermodynamics import TempPress_to_PotTemp
from BB_wx_calcs.humidity import Tempdwpt_to_RH

from datetime import datetime, timedelta
import os
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.ticker import MultipleLocator
import matplotlib as mpl
## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [12, 4]
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
mpl.rcParams['contour.negative_linestyle'] = 'solid'

# ======================================================
#                Stuff you can change :)
# ======================================================
# Station
#stn = 'kogd'
#stn = 'kpvu'
stn = 'kslc'

# start and end date
DATE = datetime(2017, 1, 1, 0)
eDATE = datetime(2017, 2, 17, 0)

# Forecast hour
fxx = 0

# Save directory
BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
SAVE = BASE + 'public_html/PhD/UWFPS_2017/time-height/jan-feb/f%02d/' % (fxx)
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = BASE + 'public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

# ======================================================
#                        Get data
# ======================================================
# Adjust date by the forecase hour to get the valid date
DATE = DATE - timedelta(hours=fxx)
eDATE = eDATE - timedelta(hours=fxx)

date_list = np.array([])
dates_skipped = np.array([])

# Loop for each hour...
while DATE < eDATE:
    try:
        # Get the bufr sounding for the hour
        b = get_bufr_sounding(DATE, site=stn)
        VALID_DATE = DATE + timedelta(hours=fxx)
        date_list = np.append(date_list, VALID_DATE)
    except:
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        print "!  Skipping", DATE, "     !"
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        dates_skipped = np.append(dates_skipped, DATE)
        DATE += timedelta(hours=1)
        continue

    # Note: the zeros index of the bufr array, b, is the analysis hour.
    try:
        # Try to stack the array, if it doens't work then the variable hasn't
        # been created yet.
        heights = np.column_stack([heights, b['hght'][fxx]])
        press = np.column_stack([press, b['pres'][fxx]])
        temps = np.column_stack([temps, b['temp'][fxx]])
        dwpts = np.column_stack([dwpts, b['dwpt'][fxx]])
    except:
        # It looks like the variable hasn't been created yet, so create it.
        heights = np.array(b['hght'][fxx])
        press = np.array(b['pres'][fxx])
        temps = np.array(b['temp'][fxx])
        dwpts = np.array(b['dwpt'][fxx])

    print 'Got it: f%02d' % (fxx), DATE
    DATE += timedelta(hours=1)

# Derive a few more variables
thetas = TempPress_to_PotTemp(temps, press)
RHs = Tempdwpt_to_RH(temps, dwpts)

# Calculate difference between potental temperture of columns and surface theta
sfcThetas = thetas[0]
diffThetas = thetas-sfcThetas

# Because the contour funciton doesn't like dates, need to convert dates
# to some other happy x axis number. Then the x axis dates can be formatted.
x = matplotlib.dates.date2num(date_list)
x2D = x*np.ones_like(heights)


# === Begin Plots ===

#==============================================================================
#                     Plot: Potential Temperature
#==============================================================================
fig, ax = plt.subplots(1, 1)

# Shade with theta
cmesh = plt.pcolormesh(x2D, heights, thetas,
                       cmap='Spectral_r',
                       vmax=305,
                       vmin=270)

# Contour theta
levels = np.arange(200, 400, 5)
conto = plt.contour(x2D, heights, thetas,
                    colors='k',
                    levels=levels)

# Format the dates on the Axis
date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
ax.xaxis.set_major_formatter(date_formatter)

# Label y axis starting with the surface tick
sfc_height = heights.min()
yticks = range(1000,5000, 500)
yticks.extend([sfc_height])
plt.yticks(yticks)
plt.ylabel('Height (m)')

# colorbar
cb = plt.colorbar(cmesh,
                  orientation='vertical',
                  shrink=.7,
                  pad=.02,
                  ticks=range(270, 306, 5),
                  extend="both")
cb.set_label('Potential Temperature (K)')

# Visually simulate the ground by filling a black area at the bottom
plt.ylim([sfc_height-100, 4000])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

# Title and save
plt.title(stn.upper() + ' f%02d HRRR bufr soundings: Potential Temperature' % (fxx))

plt.savefig(SAVE+stn+'_hrrr_theta')
print 'Plotted theta'

#==============================================================================
#                      Plot: Relative Humidity
#==============================================================================
fig, ax = plt.subplots(1, 1)

# Shade by Relative Humidity
cmesh = plt.pcolormesh(x2D, heights, RHs,
                       cmap='BrBG',
                       vmax=100,
                       vmin=0)

# Contour RH
levels = np.arange(0, 101, 20)
conto = plt.contour(x2D, heights, RHs,
                    colors='k',
                    levels=levels)

# Format the dates on the Axis
date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
ax.xaxis.set_major_formatter(date_formatter)

# Label y axis starting with the surface tick
sfc_height = heights.min()
yticks = range(1000, 5000, 500)
yticks.extend([sfc_height])
plt.yticks(yticks)
plt.ylabel('Height (m)')

# colorbar
cb = plt.colorbar(cmesh,
                  orientation='vertical',
                  shrink=.7,
                  pad=.02,
                  ticks=range(0, 101, 20))
cb.set_label('Relative Humidity (%)')

# Simulate the ground by filling a black area
plt.ylim([sfc_height-100, 4000])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

# Title and save
plt.title(stn.upper() + '  f%02d HRRR bufr soundings: Relative Humidity' % (fxx))

plt.savefig(SAVE+stn+'_hrrr_RH')
print 'Plotted RH'

#==============================================================================
#                         Plot: Dew points
#==============================================================================
fig, ax = plt.subplots(1, 1)

# Shade dew points
cmesh = plt.pcolormesh(x2D, heights, dwpts,
                       cmap='RdYlGn',
                       vmax=0,
                       vmin=-30)

# Contour dew points
levels = np.arange(-30, 6, 5)
conto = plt.contour(x2D, heights, dwpts,
                    colors='k',
                    levels=levels)

# Format the dates on the Axis
date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
ax.xaxis.set_major_formatter(date_formatter)

# Label y axis starting with the surface tick
sfc_height = heights.min()
yticks = range(1000, 5000, 500)
yticks.extend([sfc_height])
plt.yticks(yticks)
plt.ylabel('Height (m)')

# colorbar
cb = plt.colorbar(cmesh,
                  orientation='vertical',
                  shrink=.7,
                  pad=.02,
                  ticks=range(-30, 6, 5),
                  extend='both')
cb.set_label('Dew Point Temperature (C)')

# Simulate the ground by filling a black area
plt.ylim([sfc_height-100, 4000])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

# Title and save
plt.title(stn.upper() + '  f%02d HRRR bufr soundings: Dew Point Temperature' % (fxx))

plt.savefig(SAVE+stn+'_hrrr_dwpt')
print 'Plotted Dew Point'

#==============================================================================
#                          Plot: Temperature
#==============================================================================
fig, ax = plt.subplots(1, 1)

# Shade temperature
cmesh = plt.pcolormesh(x2D, heights, temps,
                       cmap='Spectral_r',
                       vmax=10,
                       vmin=-30)

# Contour temperature
levels = np.arange(-30, 11, 5)
conto = plt.contour(x2D, heights, temps,
                    colors='k',
                    levels=levels)

# Format the dates on the Axis
date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
ax.xaxis.set_major_formatter(date_formatter)

# Label y axis starting with the surface tick
sfc_height = heights.min()
yticks = range(1000, 5000, 500)
yticks.extend([sfc_height])
plt.yticks(yticks)
plt.ylabel('Height (m)')

# colorbar
cb = plt.colorbar(cmesh,
                  orientation='vertical',
                  shrink=.7,
                  pad=.02,
                  ticks=range(-30, 11, 5),
                  extend='both')
cb.set_label('Temperature (C)')

# Simulate the ground by filling a black area
plt.ylim([sfc_height-100, 4000])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

# Title and save
plt.title(stn.upper() + '  f%02d HRRR bufr soundings: Temperature' % (fxx))

plt.savefig(SAVE+stn+'_hrrr_temp')
print 'Plotted Temperature'

#==============================================================================
#                            Plot: Pressure
#==============================================================================
fig, ax = plt.subplots(1, 1)

# Shade pressure
cmesh = plt.pcolormesh(x2D, heights, press,
                       cmap='Blues',
                       vmax=900,
                       vmin=600)

# Contour pressure 
levels = np.arange(600, 901, 50)
CS = plt.contour(x2D, heights, press,
                    colors='k',
                    levels=levels)
plt.clabel(CS, inline=1, fontsize=10)

# Format the dates on the Axis
date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
ax.xaxis.set_major_formatter(date_formatter)

# Label y axis starting with the surface tick
sfc_height = heights.min()
yticks = range(1000, 5000, 500)
yticks.extend([sfc_height])
plt.yticks(yticks)
plt.ylabel('Height (m)')

# colorbar
cb = plt.colorbar(cmesh,
                  orientation='vertical',
                  shrink=.7,
                  pad=.02,
                  ticks=levels,
                  extend='both')
cb.set_label('Pressure (hPa)')

# Simulate the ground by filling a black area
plt.ylim([sfc_height-100, 4000])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

# Title and save
plt.title(stn.upper() + '  f%02d HRRR bufr soundings: Pressure' % (fxx))

plt.savefig(SAVE+stn+'_hrrr_press')
print 'Plotted Pressure'

#==============================================================================
#        Plot: Potential Temperature Difference (from surface theta)
#==============================================================================
fig, ax = plt.subplots(1, 1)

# Shade with theta
cmesh = plt.pcolormesh(x2D, heights, diffThetas,
                       cmap='Reds',
                       vmax=30,
                       vmin=0)

# Contour theta
levels = np.arange(200, 400, 5)
conto = plt.contour(x2D, heights, thetas,
                    colors='k',
                    levels=levels)

# Format the dates on the Axis
date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
ax.xaxis.set_major_formatter(date_formatter)

# Label y axis starting with the surface tick
sfc_height = heights.min()
yticks = range(1000,5000, 500)
yticks.extend([sfc_height])
plt.yticks(yticks)
plt.ylabel('Height (m)')

# colorbar
cb = plt.colorbar(cmesh,
                  orientation='vertical',
                  shrink=.7,
                  pad=.02,
                  ticks=range(0, 30, 5),
                  extend="both")
cb.set_label('Potential Temperature (K)')

# Visually simulate the ground by filling a black area at the bottom
plt.ylim([sfc_height-100, 4000])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

# Title and save
plt.title(stn.upper() + '  f%02d HRRR bufr soundings: Potential Temperature Difference from Surface' % (fxx))

plt.savefig(SAVE+stn+'_hrrr_theta-diff')
print 'Plotted theta-diff'