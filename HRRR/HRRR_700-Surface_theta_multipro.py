# Brian Blaylock
# February 7, 2017                                         It's raining outside

"""
Plot the potential temperature excess for Northern Utah in the HRRR analyses
(700 mb theta) - (Surface theta) to show the strength of the inversion.
"""

import multiprocessing # :)
import pygrib
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

import matplotlib as mpl
## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [15, 8]
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
sys.path.append('/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/lib/python2.7/site-packages/')
import pygrib
from BB_basemap.draw_maps import draw_UWFPS_map
from BB_wx_calcs.thermodynamics import TempPress_to_PotTemp

# Oder is xmin, xmax, ymin, ymax
subset = {'Utah':[470, 725, 391, 603],
          'GSL':[630, 697, 453, 511],
          'UtahLake':[611, 635, 486, 505],
          'west':[0, 1799, 0, 950],
          'east':[0, 1799, 850, 1799],
          'CONUS':[0, 1799, 0, 1799],
          'Uintah':[470, 725, 391, 603], #need to fix these indexes. currently is Utah domain
         }

domain = 'Utah'


def plot_excess_temp_map(input):
    m = input[0]
    DATE = input[1]

    date = DATE.strftime('%Y-%m-%d_%H%M')
    print 'working on', date

    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/' % (DATE.year, DATE.month, DATE.day)

    # Open HRRR and get surface temperature and surface pressure
    grbs = pygrib.open(DIR+'hrrr/hrrr.t%02dz.wrfsfcf00.grib2' % (DATE.hour))
    temp = grbs.select(name="2 metre temperature")[0].values[subset[domain][0]:subset[domain][1], subset[domain][2]:subset[domain][3]] - 273.15
    sfcpres = grbs.select(name="Surface pressure")[0].values[subset[domain][0]:subset[domain][1], subset[domain][2]:subset[domain][3]]/100
    lat, lon = grbs.select(name="2 metre temperature")[0].latlons()
    lat = lat[subset[domain][0]:subset[domain][1], subset[domain][2]:subset[domain][3]]
    lon = lon[subset[domain][0]:subset[domain][1], subset[domain][2]:subset[domain][3]]

    # Get the 700 hPa temperatures
    T700 = grbs.select(name="Temperature")[1].values[subset[domain][0]:subset[domain][1], subset[domain][2]:subset[domain][3]] - 273.15


    # Convert temperatures to potental temperature (theta)
    theta_sfc = TempPress_to_PotTemp(temp, sfcpres)
    theta_700 = TempPress_to_PotTemp(T700, 700)

    # Draw map and plot temperatures
    fig = plt.figure(figsize=[13, 5])
    # first pannel
    fig.add_subplot(131)

    m.drawstates()
    m.drawcoastlines()
    m.drawcounties(zorder=100)
    m.pcolormesh(lon, lat, theta_sfc, cmap='Spectral_r', vmax=305, vmin=270)
    cb = plt.colorbar(orientation='horizontal',
                      shrink=.9,
                      pad=.03,
                      ticks=range(270, 306, 5),
                      extend="both")
    cb.set_label('Potential Temperature')
    plt.title('Surface theta')


    # second pannel
    fig.add_subplot(132)

    m.drawstates()
    m.drawcoastlines()
    m.drawcounties(zorder=100)
    m.pcolormesh(lon, lat, theta_700, cmap='Spectral_r', vmax=305, vmin=270)
    cb = plt.colorbar(orientation='horizontal',
                      shrink=.9,
                      pad=.03,
                      ticks=range(270, 306, 5),
                      extend="both")
    cb.set_label('Potential Temperature')
    plt.title('700 hPa theta')

    # third pannel
    ax = fig.add_subplot(133)

    m.drawstates()
    m.drawcoastlines()
    m.drawcounties(zorder=100)
    m.pcolormesh(lon, lat, theta_700-theta_sfc, cmap='Reds', vmax=30, vmin=0)
    cb = plt.colorbar(orientation='horizontal',
                      shrink=.9,
                      pad=.03,
                      ticks=range(0, 31, 5),
                      extend='max')
    cb.set_label('Temperature Excess')
    plt.title('theta 700 - theta sfc')
    plt.suptitle('HRRR anlys: '+ str(DATE))


    # savefig
    plt.savefig('./figs/excess_temp/'+date)



if __name__ == '__main__':
    m = draw_UWFPS_map()

    # Create list of dates with map object in tuple: (map, datetime)
    base = datetime(2017, 1, 23)
    numdays = 14
    numhours = numdays*24
    date_list = np.array([(m, base + timedelta(hours=x)) for x in range(0, numhours)])

    # Multiprocessing :)
    num_proc = multiprocessing.cpu_count() # use all processors
    num_proc = 12                           # specify number to use (to be nice)
    p = multiprocessing.Pool(num_proc)
    result = p.map(plot_excess_temp_map, date_list)
