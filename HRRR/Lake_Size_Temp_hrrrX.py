# Brian Blaylock
# 23 November 2016

"""
Plot surface temperature from the HRRR model, focusing on the Great Salt Lake. 
Comment on the temperature at the Great Salt Lake Buoy (GSLBY)
"""

import pygrib

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta
import numpy as np
import os

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:/pyBKB_v2')
from BB_basemap.draw_maps import draw_GSL_map, draw_UtahLake_map
from BB_data.grid_manager import pluck_point
from BB_MesoWest.MesoWest_buoy import get_mesowest_ts

# I want to append to this global variable
buoy_data = np.array([])


def get_lake_temp(DATE):

    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/hrrrX/' % (DATE.year, DATE.month, DATE.day)
    FILE = 'hrrrX.t%02dz.wrfsfcf00.grib2' % (DATE.hour)

    # Get Surface Temperature from the HRRR
    grbs = pygrib.open(DIR+FILE)
    print DATE
    print 'Grabbed:', grbs(name='Temperature')[-1]
    lat, lon = grbs(name='Temperature')[-1].latlons()
    T_surface = grbs(name='Temperature')[-1].values

    # Plot a circle where the GSL Buoy is Located, grab the HRRR surface
    # temperature, and comment that below.
    buoy_lat = 40.89068
    buoy_lon = -112.34551
    p = pluck_point(buoy_lat, buoy_lon, lat, lon)
    buoy_temp = T_surface.flatten()[p]


    """
    If I trim the data to just the Utah Domain it might plot a lot faster!! :)
    """

    # Return the data we want, and convert temperatures to Celsius.
    return_this = {'DATE': DATE,
                   'LAT': lat,
                   'LON': lon,
                   'T_surface': T_surface-273.15,
                   'buoy_temp': buoy_temp-273.15,
                   'buoy_lat': buoy_lat,
                   'buoy_lon': buoy_lon
                  }

    return return_this


def plot_lake_temp(lake, m):
    """
    Plots the Great Salt Lake and surounding area surface
    temperature from the HRRR analyses.

    Input:
        lake - a dictinary from the get_lake_temp() function
        m - a map object that has been drawn.abs
        cb_plotted - a flag that says if the cb_has been plotted
                     if False, then it will draw the colorbar
                     if True, then it wont draw the colorbar

    Output:
        a figure that is saved to the SAVEDIR
    """

    # clean off the plot (this prevents drawing multiple color bars)
    plt.cla()
    plt.clf()

    SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/GSL_HRRR_temp/Aug-Nov/hrrrX/'
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)

    # Handle the date
    str_DATE = lake['DATE'].strftime('%Y-%m-%d %H:%M UTC')
    save_DATE = lake['DATE'].strftime('%Y-%m-%d_%H%Mz')

    # plot the buoy location
    m.scatter(lake['buoy_lon'], lake['buoy_lat'],
              facecolors='none',
              edgecolor='k',
              s=100,
              zorder=500)

    # plot the surface temperatures
    m.pcolormesh(lake['LON'], lake['LAT'], lake['T_surface'],
                 vmin=270-273.15, vmax=300-273.15,
                )

    # draw the GSL boundary
    m.drawcoastlines()  # a good guess of the lake's current size

    # Figure formating and such
    plt.title('HRRR-X Surface Temperature\n'+str_DATE)
    plt.xlabel('%0.2f C at GSLBY' % (lake['buoy_temp']))

    cb = plt.colorbar()
    cb.set_label('Surface Temperature (C)')
    cb_plotted = True

    plt.savefig(SAVEDIR+save_DATE, bbox_inches='tight')


def main(from_mp):
    """
    Input:
     from_mp - list from multiprocessing
     First element is the datetime object
     Second element is the map object
    """
    try:
        lake = get_lake_temp(from_mp[0])
        plot_lake_temp(lake, from_mp[1])

        return lake['buoy_temp']
    except:
        print "error plotting:", from_mp[0]
        return np.nan


if __name__ == "__main__":

    import multiprocessing #:)

    # Draw the map once.
    m = draw_GSL_map(res='f')

    # Create a list of dates
    DATE = datetime(2016, 11, 27, 18)
    DATE2 = datetime(2016, 8, 2, 18)
    days = (DATE - DATE2).days
    #numdays = 60
    #hours = int(numdays*24)  # must be an integer for making list

    DATE = datetime(2016, 11, 29, 18)
    # make a list of dates and the map object
    #date_map_list = np.array([[DATE - timedelta(days=x), m] for x in range(0, days)])
    date_map_list = [datetime(2016, 11, 29, 18), m]

    # make a list of just dates
    #date_list = np.array([DATE - timedelta(days=x) for x in range(0, days)])
    date_list = [datetime(2016, 11, 29, 18)]

    # Multiprocessing :)
    #num_proc = multiprocessing.cpu_count() - 2 # just to be kind, don't use everything
    #p = multiprocessing.Pool(num_proc)
    #buoy_temps = p.map(main, date_map_list)
    main(date_map_list)


    # Get MesoWest buoy observations
    a = get_mesowest_ts(date_list[-1], date_list[0])


"""
Plot time series:
    - HRRR surface temperature and
    - Observed -0.4 meter water temperature.
"""
# Plot the Time Series of Buoy Temps
fig, ax1 = plt.subplots(1, 1, figsize=(10, 6))
ax1.plot(date_list, buoy_temps, label='HRRR Surface Temp')
ax1.plot(a['DATES'], a['T_water1'], color='r', label='GSLBY -0.4 meters')

ax1.legend()
ax1.grid()

plt.title('Great Salt Lake Surface Temperature at GSLBY')
plt.ylabel('Temperature (C)')

##Format Ticks on Date Axis##
##----------------------------------
# Find months
months = MonthLocator()
# Find days
days = DayLocator(bymonthday=[1,5,10,15,20,25])
# Find each 0 and 12 hours
hours = HourLocator(byhour=[0, 3, 6, 9, 12, 15, 18, 21])
# Find all hours
hours_each = HourLocator()
# Tick label format style
dateFmt = DateFormatter('%b %d\n%H:%M')
blank_dateFmt = DateFormatter('')
# Set the x-axis major tick marks
#ax1.xaxis.set_major_locator(days)
# Set the x-axis labels
ax1.xaxis.set_major_formatter(dateFmt)
# For additional, unlabeled ticks, set x-axis minor axis
#ax1.xaxis.set_minor_locator(hours)

SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/GSL_HRRR_temp/'
plt.savefig(SAVEDIR+'GSLBY_HRRR_MesoWest.png')

plt.savefig(SAVEDIR+'GSLBY_HRRR_MesoWest.eps', format='eps')
