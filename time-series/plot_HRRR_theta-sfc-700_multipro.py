# Brian Blaylock
# February 21, 2017                I took the 16 personalities test. I'm ISFJ-A 

"""
Create a time series of potential temperature at 700 mb and the surface for a
period. Pluck the point from any location in the HRRR domain.
Also, add plots of the observed sounding.
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:/pyBKB_v2')
from BB_HRRR.get_bufr_sounding import get_bufr_sounding
from BB_wx_calcs.thermodynamics import TempPress_to_PotTemp
from BB_data.grid_manager import pluck_point

from datetime import datetime, timedelta
import os
import numpy as np
import pygrib
import multiprocessing # :)

import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.ticker import MultipleLocator
import matplotlib as mpl
## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [12, 6]
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

# Domain for triming grib data. Oder is xmin, xmax, ymin, ymax
subset = {'Utah':[470, 725, 391, 603],
          'GSL':[630, 697, 453, 511],
          'UtahLake':[611, 635, 486, 505],
          'west':[0, 1799, 0, 950],
          'east':[0, 1799, 850, 1799],
          'CONUS':[0, 1799, 0, 1799],
          'Uintah':[470, 725, 391, 603], #need to fix these indexes. currently is Utah domain
         }

# ======================================================
#                Stuff you can change :)
# ======================================================
# Station
stn = 'KSLC'
stn_lat = 40.77
stn_lon = -111.95

# start and end date
DATE = datetime(2017, 1, 1, 0)
eDATE = datetime(2017, 2, 17, 0)

# Forecast hour
fxx = 0

# Save directory
BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
SAVE = BASE + 'public_html/PhD/UWFPS_2017/time-series/jan-feb/'
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = BASE + 'public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

# Specify the domain, for cutting data
domain = 'GSL'

# =====================================================
#                   Get the data
# =====================================================
# Adjust date by the forecast hour to get the valid date.
DATE = DATE - timedelta(hours=fxx)
eDATE = eDATE - timedelta(hours=fxx)

def get_theta_from_grb(DATE):
    """
    Gets the potential temperature at a point from the HRRR surface field
    files for a single time.
    """

    VALID_DATE = DATE + timedelta(hours=fxx)

    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/' % (DATE.year, DATE.month, DATE.day)

    # Open HRRR and get surface temperature and surface pressure
    grbs = pygrib.open(DIR+'hrrr/hrrr.t%02dz.wrfsfcf%02d.grib2' % (DATE.hour, fxx))
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

    # Pluck value for the station location
    pluck_index = pluck_point(stn_lat, stn_lon, lat, lon)

    # use that pluck index on the flattened array to ge the value
    stn_theta_sfc = theta_sfc.flatten()[pluck_index]
    stn_theta_700 = theta_700.flatten()[pluck_index]

    # Return the values
    print "Got it:", DATE
    
    # close the grib file
    grbs.close() 
    
    return [VALID_DATE, stn_theta_sfc, stn_theta_700]

if __name__ == "__main__":
    # =================================================
    #                 Get the data
    # =================================================
    # Create a range of dates
    base = DATE
    hours = (eDATE - DATE).days*24 + (eDATE-DATE).seconds/60/60
    date_list = np.array([base + timedelta(hours=x) for x in range(0, hours)])

    # Multiprocessing :)
    num_proc = multiprocessing.cpu_count() # use all processors
    num_proc = 12                           # specify number to use (to be nice)
    p = multiprocessing.Pool(num_proc)
    data = p.map(get_theta_from_grb, date_list)
    data = np.array(data)

    date_list = data[:, 0]
    stn_sfc_theta = data[:, 1]
    stn_700_theta = data[:, 2]

    theta_diff = stn_700_theta-stn_sfc_theta


# Begin Plotting
fig, [ax1, ax2] = plt.subplots(2, 1)
# =================================================
#  Plot: 700 hPa and Surface Potential Temperature
# =================================================
ax1.plot(date_list, stn_700_theta,
            color='r',
            lw=3,
            label=r'$\theta$$\mathregular{_{700 hPa}}$')
ax1.plot(date_list, stn_sfc_theta,
            color="b",
            lw=3,
            label=r'$\theta$$\mathregular{_{surface}}$')
ax1.grid()
ax1.set_title(stn + ' HRRR Potential Temperature')
ax1.set_ylabel('Potential Temperature (K)')
ax1.set_xticklabels([])

legend = ax1.legend(frameon=True, framealpha=.5)
legend.get_frame().set_linewidth(0)

# =================================================
#  Plot2: Surface Potential Temperature Deficit
#         (700 hPa - Surface Potential Temperature)
# =================================================
ax2.plot(date_list, theta_diff,
            color='k',
            lw=3)
ax2.grid()
ax2.set_title(stn + ' HRRR Surface Potential Temperature Deficit')
ax2.set_ylabel('Temperature (K)')

# Format the dates on the Axis
date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
ax2.xaxis.set_major_formatter(date_formatter)

plt.savefig(SAVE+stn+"theta_diff")

