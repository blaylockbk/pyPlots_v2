# Brian Blaylock
# Feburary 9, 2017              Rachel and I finished a 500 pc puzzle yesterday

"""
Plot a time height from HRRR Bufr Data
    - Potential Temperature
    - Temperature
    - Dew point temperature
    - Relative Humidity
"""

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.ticker import MultipleLocator
import numpy as np
import os

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

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:/pyBKB_v2')
from BB_HRRR.get_bufr_sounding import get_bufr_sounding
from BB_wx_calcs.thermodynamics import TempPress_to_PotTemp
from BB_wx_calcs.humidity import Tempdwpt_to_RH


stn = 'kogd'
stn = 'kpvu'
#stn = 'kslc'

SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/UWFPS_2017/time-height/'
if not os.path.exists(SAVE):
    os.makedirs(SAVE)

# Loop for each hour...
DATE = datetime(2017, 1, 23, 0)
date_list = np.array([])

while DATE < datetime(2017, 2, 5, 1):
    date_list = np.append(date_list, DATE)
    # Get the bufr sounding for the hour
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/hrrr/' \
        % (DATE.year, DATE.month, DATE.day)
    FILE = '%s_%04d%02d%02d%02d.buf' \
        % (stn, DATE.year, DATE.month, DATE.day, DATE.hour)
    b = get_bufr_sounding(DATE, site=stn)

    # Note: the zeros index of the bufr array, b, is tha analysis hour.
    try:
        # Try to stack the array, if it doens't work then the variable hasn't
        # been created yet.
        heights = np.column_stack([heights, b['hght'][0]])
        press = np.column_stack([press, b['pres'][0]])
        temps = np.column_stack([temps, b['temp'][0]])
        dwpts = np.column_stack([dwpts, b['dwpt'][0]])
    except:
        # It looks like the variable hasn't been created yet, so create it.
        heights = np.array(b['hght'][0])
        press = np.array(b['pres'][0])
        temps = np.array(b['temp'][0])
        dwpts = np.array(b['dwpt'][0])

    DATE += timedelta(hours=1)

# Derive a few more variables
thetas = TempPress_to_PotTemp(temps, press)
RHs = Tempdwpt_to_RH(temps, dwpts)

# make a grid of the dates for the size of the array
dates = np.ones_like(heights) * range(np.shape(heights)[1])

# Make the plot, but to trim out the upper level stuff we need to know the
# index level we should grab.
max_pres = 600
idx = np.max(np.argwhere(press>max_pres)[0:, 0])



#==============================================================================
# figure for potential temperature
fig, ax = plt.subplots(1, 1)
# Because the contour funciton doesn't like dates, need to convert dates
# to some other happy x axis number. Then the x axis dates can be formatted.
x = matplotlib.dates.date2num(date_list)
x2D = x*np.ones_like(heights)

cmesh = plt.pcolormesh(x2D[0:idx, :], heights[0:idx, :], thetas[0:idx, :],
                       cmap='Spectral_r',
                       vmax=305, 
                       vmin=270)
levels = np.arange(200, 400, 5)
conto = plt.contour(x2D[0:idx, :], heights[0:idx, :], thetas[0:idx, :],
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

# Simulate the ground by filling a black area    
plt.ylim([heights.min()-100, heights[idx-1:, :].min()])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

plt.title(stn.upper() + ' HRRR bufr soundings: Potential Temperature')

plt.savefig(SAVE+stn+'_hrrr_theta')


#==============================================================================
# Now make a plot for RH
fig, ax = plt.subplots(1, 1)
# Because the contour funciton doesn't like dates, need to convert dates
# to some other happy x axis number. Then the x axis dates can be formatted.
x = matplotlib.dates.date2num(date_list)
x2D = x*np.ones_like(heights)

cmesh = plt.pcolormesh(x2D[0:idx, :], heights[0:idx, :], RHs[0:idx, :],
                       cmap='BrBG',
                       vmax=100,
                       vmin=0)
levels = np.arange(0, 101, 20)
conto = plt.contour(x2D[0:idx, :], heights[0:idx, :], RHs[0:idx, :],
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
plt.ylim([heights.min()-100, heights[idx-1:, :].min()])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

plt.title(stn.upper() + ' HRRR bufr soundings: Relative Humidity')

plt.savefig(SAVE+stn+'_hrrr_RH')

#==============================================================================
# Now make a plot for DWPT
fig, ax = plt.subplots(1, 1)
# Because the contour funciton doesn't like dates, need to convert dates
# to some other happy x axis number. Then the x axis dates can be formatted.
x = matplotlib.dates.date2num(date_list)
x2D = x*np.ones_like(heights)

cmesh = plt.pcolormesh(x2D[0:idx, :], heights[0:idx, :], dwpts[0:idx, :],
                       cmap='RdYlGn',
                       vmax=0,
                       vmin=-30)
levels = np.arange(-30, 6, 5)
conto = plt.contour(x2D[0:idx, :], heights[0:idx, :], dwpts[0:idx, :],
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
plt.ylim([heights.min()-100, heights[idx-1:, :].min()])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

plt.title(stn.upper() + ' HRRR bufr soundings: Dew Point Temperature')

plt.savefig(SAVE+stn+'_hrrr_dwpt')

#==============================================================================
# Now make a plot for true temperature
fig, ax = plt.subplots(1, 1)
# Because the contour funciton doesn't like dates, need to convert dates
# to some other happy x axis number. Then the x axis dates can be formatted.
x = matplotlib.dates.date2num(date_list)
x2D = x*np.ones_like(heights)

cmesh = plt.pcolormesh(x2D[0:idx, :], heights[0:idx, :], temps[0:idx, :],
                       cmap='Spectral_r',
                       vmax=10,
                       vmin=-30)
levels = np.arange(-30, 11, 5)
conto = plt.contour(x2D[0:idx, :], heights[0:idx, :], temps[0:idx, :],
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
plt.ylim([heights.min()-100, heights[idx-1:, :].min()])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

plt.title(stn.upper() + ' HRRR bufr soundings: Temperature')

plt.savefig(SAVE+stn+'_hrrr_temp')

#==============================================================================
# Now make a plot height of pressure levels
fig, ax = plt.subplots(1, 1)
# Because the contour funciton doesn't like dates, need to convert dates
# to some other happy x axis number. Then the x axis dates can be formatted.
x = matplotlib.dates.date2num(date_list)
x2D = x*np.ones_like(heights)

cmesh = plt.pcolormesh(x2D[0:idx, :], heights[0:idx, :], press[0:idx, :],
                       cmap='Blues',
                       vmax=900,
                       vmin=600)
levels = np.arange(600, 901, 50)
CS = plt.contour(x2D[0:idx, :], heights[0:idx, :], press[0:idx, :],
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
plt.ylim([heights.min()-100, heights[idx-1:, :].min()])
plt.fill_between([date_list[0], date_list[-1]], np.min(heights), color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

plt.title(stn.upper() + ' HRRR bufr soundings: Pressure')

plt.savefig(SAVE+stn+'_hrrr_press')