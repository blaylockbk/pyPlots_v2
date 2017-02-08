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
from BB_data.grid_manager import pluck_point

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
    DATE = input

    date = DATE.strftime('%Y-%m-%d_%H%M')
    print 'working on', date

    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/' % (DATE.year, DATE.month, DATE.day)

    # Open HRRR and get surface temperature and surface pressure
    try:
        grbs = pygrib.open(DIR+'hrrrX/hrrrX.t%02dz.wrfsfcf00.grib2' % (DATE.hour))
        print "opened", DATE

        temp = grbs.select(name="2 metre temperature")[0].values[subset[domain][0]:subset[domain][1], subset[domain][2]:subset[domain][3]] - 273.15
        sfcpres = grbs.select(name="Surface pressure")[0].values[subset[domain][0]:subset[domain][1], subset[domain][2]:subset[domain][3]]/100
        lat, lon = grbs.select(name="2 metre temperature")[0].latlons()
        lat = lat[subset[domain][0]:subset[domain][1], subset[domain][2]:subset[domain][3]]
        lon = lon[subset[domain][0]:subset[domain][1], subset[domain][2]:subset[domain][3]]

        # Get the 700 hPa temperatures (!! NOT AVAILABLE IN HRRR-X FILE)
        #T700 = grbs.select(name="Temperature")[1].values[subset[domain][0]:subset[domain][1], subset[domain][2]:subset[domain][3]] - 273.15


        # Convert temperatures to potental temperature (theta)
        theta_sfc = TempPress_to_PotTemp(temp, sfcpres)
        #theta_700 = TempPress_to_PotTemp(T700, 700)

        # pluck the value for SLC
        SLC_lat = 40.77
        SLC_lon = -111.95
        pluck_index = pluck_point(SLC_lat, SLC_lon, lat, lon)

        # use that pluck index on the flattened array to ge the value
        SLC_sfc_temp = temp.flatten()[pluck_index]
        SLC_sfc_theta = theta_sfc.flatten()[pluck_index]
        #SLC_700_temp = T700.flatten()[pluck_index]
        #SLC_700_theta = theta_700.flatten()[pluck_index]

        return [SLC_sfc_temp, SLC_sfc_theta]
    
    except:
        print "could not open", DATE
        return [np.nan, np.nan]

if __name__ == '__main__':
    # Create list of dates with map object in tuple: (map, datetime)
    base = datetime(2017, 1, 23)
    numdays = 14
    numhours = numdays*24
    date_list = np.array([base + timedelta(hours=x) for x in range(0, numhours)])

    # Multiprocessing :)
    num_proc = multiprocessing.cpu_count() # use all processors
    num_proc = 12                           # specify number to use (to be nice)
    p = multiprocessing.Pool(num_proc)
    data = p.map(plot_excess_temp_map, date_list)
    data = np.array(data)
    SLC_sfc_temp = data[:, 0]
    SLC_sfc_theta = data[:, 1]

    write_this = np.transpose(np.vstack([date_list, SLC_sfc_temp, SLC_sfc_theta]))

    np.savetxt('UWFPS_inversion_SLC_HRRR-X_points.csv', write_this,
               delimiter=',',
               fmt="%s",
               header='datetime, SLC_sfc_temp, SLC_sfc_theta')
