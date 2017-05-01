# Brian Blaylock
# April 28, 2017       Jazz are going to Game 5, tonight!!!

"""
Project Golf is inspired by Dallin Naulu, the superintendant at Spanish Oaks
Golf Course. He wanted to view weather forecasts for his golf course, so I made
this display for him. These are useful plots at many locations. This particular
script makes a plot for the analysis hours.
"""
import matplotlib as mpl
#mpl.use('Agg')		#required for the CRON job. Says "do not open plot in a window"??
import multiprocessing #:)
import numpy as np
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.dates as mdates

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [17, 7]
mpl.rcParams['figure.titlesize'] = 13
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.05
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 150

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/lib/python2.7/site-packages/')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_S3 import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_MesoWest.MesoWest_radius import get_mesowest_radius
from MetPy_BB.plots import ctables
from BB_data.grid_manager import pluck_point_new
from BB_wx_calcs.wind import wind_uv_to_spd, wind_spddir_to_uv
from BB_wx_calcs.units import *


# 1) Locations
location = {'MMOM4': {'latitude': 44.676111,
                      'longitude': -84.128333,
                      'name': 'Mio',
                      'is MesoWest': True,    # Is the Key a MesoWest ID?
                      'timezone': 4},         # Time Zone Hours to subtract form UTC
            'KGOV': {'latitude': 44.68028,
                     'longitude': -84.72889,
                     'name': 'Grayling Army Airfield',
                     'is MesoWest': True,
                     'timezone': 4}
           }


# 2) Get the HRRR data from NOMADS and store data nicely
sDATE = datetime(2017, 4, 25)
eDATE = datetime(2017, 4, 26)

print "UTC DATE:", sDATE

# 2.1) Time Series: Plucked HRRR value at all locations
#      These are dictionaries:
#      {'DATETIME':[array of dates], 'station name': [values for each datetime], ...}

TS_temp = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='TMP:2 m')
TS_dwpt = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='DPT:2 m')

TS_wind = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='WIND:10 m')
TS_gust = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='GUST:surface')
TS_u = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='UGRD:10 m')
TS_v = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='VGRD:10 m')
TS_u80 = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='UGRD:80 m')
TS_v80 = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='VGRD:80 m')
TS_wind80 = {} # we will derive this in the following loop

#TS_prec = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='APCP:surface') # Not valuable for an analysis
TS_hpbl = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='HPBL:surface')
TS_hcon = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='HGT:level of adiabatic condensation from sfc')

# Convert the units of each Pollywog
for loc in location.keys():
    # Convert Units for the variables in the Pollywog
    TS_temp[loc] = KtoF(TS_temp[loc])
    TS_dwpt[loc] = KtoF(TS_dwpt[loc])
    TS_wind[loc] = mps_to_MPH(TS_wind[loc])
    TS_gust[loc] = mps_to_MPH(TS_gust[loc])
    TS_u[loc] = mps_to_MPH(TS_u[loc])
    TS_v[loc] = mps_to_MPH(TS_v[loc])
    TS_u80[loc] = mps_to_MPH(TS_u80[loc])
    TS_v80[loc] = mps_to_MPH(TS_v80[loc])
    #TS_prec[loc] = mm_to_inches(TS_prec[loc])

    # Derive some variables:
    TS_wind80[loc] = wind_uv_to_spd(TS_u80[loc],TS_v80[loc])


# Just need one vector of valid dates
TS_dates = np.array(TS_temp['DATETIME'])

# Make a dictionary of map object for each location.
# (This speeds up plotting by creating each map once.)
maps = {}
for loc in location.keys():
    l = location[loc]
    m = Basemap(resolution='i', projection='cyl',\
                    llcrnrlon=l['longitude']-.1, llcrnrlat=l['latitude']-.1,\
                    urcrnrlon=l['longitude']+.1, urcrnrlat=l['latitude']+.1,)
    maps[loc] = m

for hh in range(len(TS_dates)):
    # 2.2) Radar Reflectivity and winds for entire CONUS
    fxx = 0
    H = get_hrrr_variable(TS_dates[hh], 'REFC:entire atmosphere', fxx=fxx, model='hrrr')
    H_U = get_hrrr_variable(TS_dates[hh], 'UGRD:10 m', fxx=fxx, model='hrrr', value_only=True)
    H_V = get_hrrr_variable(TS_dates[hh], 'VGRD:10 m', fxx=fxx, model='hrrr', value_only=True)

    # Convert Units (meters per second -> miles per hour)
    H_U['value'] = mps_to_MPH(H_U['value'])
    H_V['value'] = mps_to_MPH(H_V['value'])

    # Mask out empty reflectivity values
    dBZ = H['value']
    dBZ = np.ma.array(dBZ)
    dBZ[dBZ == -10] = np.ma.masked

    # Loop through each location to make plots
    for loc in location.keys():
        print "working on:", loc

        SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/MichiganBurn_2017-04-25/%s/' % loc
        if not os.path.exists(SAVE):
            # make the SAVE directory
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
            os.link(photo_viewer, SAVE+'photo_viewer.php')

        # 3) Create a Map and plot for each location
        plt.clf()
        plt.cla()

        # Get the dictionary for the location, includes lat/lon, and name
        l = location[loc]
        tz = l['timezone']

        # 3) Make plot for each location
        plt.suptitle('HRRR Forecast: %s' % (l['name']))

        # 3.1) Map
        ax1 = plt.subplot(1, 2, 1)

        # ESRI Background image
        maps[loc].arcgisimage(service='World_Shaded_Relief', xpixels=1000, verbose=False)

        # Project the lat/lon on th map
        x, y = m(l['longitude'], l['latitude'])
        X, Y = m(H['lon'], H['lat'])

        # Plot point for location
        maps[loc].scatter(x, y, s=100, color='white', edgecolor='k', zorder=100)

        # Overlay Simulated Radar Reflectivity
        ctable = 'NWSReflectivity'
        norm, cmap = ctables.registry.get_with_steps(ctable, -0, 5)
        maps[loc].pcolormesh(X, Y, dBZ, norm=norm, cmap=cmap, alpha=.5)
        cb = plt.colorbar(orientation='horizontal', pad=0.01, shrink=0.75)
        cb.set_label('Simulated Radar Reflectivity (dBZ)\n\nBarbs: Half=5 mph, Full=10 mph, Flag=50 mph')

        # Overlay wind barbs (need to trim this array before we plot it)
        # First need to trim the array
        cut_vertical, cut_horizontal = pluck_point_new(l['latitude'],
                                                       l['longitude'],
                                                       H['lat'],
                                                       H['lon'])
        maps[loc].barbs(X[cut_vertical-5:cut_vertical+5, cut_horizontal-5:cut_horizontal+5],
                        Y[cut_vertical-5:cut_vertical+5, cut_horizontal-5:cut_horizontal+5],
                        H_U['value'][cut_vertical-5:cut_vertical+5, cut_horizontal-5:cut_horizontal+5],
                        H_V['value'][cut_vertical-5:cut_vertical+5, cut_horizontal-5:cut_horizontal+5],
                        zorder=200)

        # Overlay Utah Roads
        BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
        maps[loc].readshapefile(BASE+'shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads',
                                'roads',
                                linewidth=.5)
        ax1.set_title('          UTC: %s\nLocal Time: %s' % (TS_dates[hh]+timedelta(hours=fxx), TS_dates[hh]+timedelta(hours=fxx)-timedelta(hours=tz)))

        # 3.2) Temperature/Dew Point
        ax2 = plt.subplot(3, 2, 2)
        tempF = TS_temp[loc]
        dwptF = TS_dwpt[loc]
        ax2.plot(TS_temp['DATETIME'], tempF, c='r', lw='1.5', label='Temperature')
        ax2.scatter(TS_temp['DATETIME'][hh], tempF[hh], c='r', s=60)
        ax2.plot(TS_dwpt['DATETIME'], dwptF, c='g', lw='1.5', label='Dew Point')
        ax2.scatter(TS_dwpt['DATETIME'][hh], dwptF[hh], c='g', s=60)
        if l['is MesoWest'] is True:
            a = get_mesowest_ts(loc, sDATE, eDATE, variables='air_temp,wind_speed')
            b = get_mesowest_radius(TS_dates[hh], 15, extra='&radius=%s,30' % (loc), variables='wind_speed,wind_direction')
            MW_u, MW_v = wind_spddir_to_uv(b['wind_speed'],b['wind_direction'])
            MW_u = mps_to_MPH(MW_u)
            MW_v = mps_to_MPH(MW_v)
            ax2.plot(a['DATETIME'], CtoF(a['air_temp']), c='k', ls='--')
            MWx, MWy = maps[loc](b['LON'], b['LAT'])
            ax1.barbs(MWx, MWy, MW_u, MW_v, color='r')

        ax2.legend()
        ax2.grid()
        ax2.set_ylabel('Degrees (F)')
        ax2.set_xlim([TS_temp['DATETIME'][0], TS_temp['DATETIME'][-1]])
        ax2.set_ylim([dwptF.min()-1, tempF.max()+1])
        ax2.xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
        ax2.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter(''))
        ax2.set_title('valid: %s Run: %s\nModel Run (UTC): %s f%02d' % (H['valid'], H['anlys'], TS_dates[hh].strftime('%Y %b %d, %H:%M'), fxx))

        # 3.3) Wind Speed and Barbs
        ax3 = plt.subplot(3, 2, 4)
        ax3.plot(TS_wind['DATETIME'], TS_wind80[loc], c='saddlebrown', lw='1.5', label='Instantaneous 80 m wind')
        ax3.scatter(TS_wind['DATETIME'][hh], TS_wind80[loc][hh], c='saddlebrown', s=60)
        ax3.plot(TS_gust['DATETIME'], TS_gust[loc], c='chocolate', lw='1.5', label='Instantaneous 10 m Wind Gust')
        ax3.scatter(TS_gust['DATETIME'][hh], TS_gust[loc][hh], c='chocolate', s=60)
        ax3.plot(TS_wind['DATETIME'], TS_wind[loc], c='darkorange', lw='1.5', label='Previous hour max 10 m wind')
        ax3.scatter(TS_wind['DATETIME'][hh], TS_wind[loc][hh], c='darkorange', s=60)
        if l['is MesoWest'] is True:
            # alreaded loaded up mesowest data into a
            ax3.plot(a['DATETIME'], mps_to_MPH(a['wind_speed']), c='k', ls='--')

        # plt.barbs can not take a datetime object, so find the date indexes:
        # (For some reason, matplotlib doesn't like plotting these barbs, so
        # loop through each hour, and matplotlib is happy plotting the barbs)
        idx = mpl.dates.date2num(TS_u['DATETIME'])
        speeds = wind_uv_to_spd(TS_u[loc], TS_v[loc])
        us = TS_u[loc]
        vs = TS_v[loc]
        for ii in range(len(idx)):
            ax3.barbs(idx[ii], speeds[ii], us[ii], vs[ii])

        ax3.legend()
        ax3.grid()
        #ax3.set_ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
        ax3.set_ylabel('Wind Speed (mph)')
        ax3.set_ylim([0, TS_gust[loc].max()+3])
        ax3.set_yticks([0, TS_gust[loc].max()+3], 2.5)
        ax3.set_xlim([TS_gust['DATETIME'][0], TS_gust['DATETIME'][-1]])
        ax3.xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
        ax3.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter(''))

        """
        # 3.4) Accumulated Precipitation
        local = np.array(TS_dates - timedelta(hours=tz))
        accumP = np.add.accumulate(TS_prec[loc])
        ax4 = plt.subplot(3, 2, 6)
        ax4.bar(local, TS_prec[loc], width=.04, color='dodgerblue', label='1 hour Precipitation')
        ax4.plot(local, accumP, color='limegreen', lw='1.5', label='Accumulated Precipitation')
        ax4.scatter(local[hh], accumP[hh], color='limegreen', s=60)
        ax4.set_xlim([local[0], local[-1]])
        ax4.set_ylim([0, accumP.max()+.1])
        ax4.xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
        ax4.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))

        ax4.legend()
        ax4.grid()
        ax4.set_ylabel('Precipitation (in)')
        """
        # 3.4) Height of boundary layer
        local = np.array(TS_dates - timedelta(hours=tz))
        ax4 = plt.subplot(3, 2, 6)
        ax4.plot(local, TS_hcon[loc], color='skyblue', lw='1.5', label='Level of adiabatic condensation from surface')
        ax4.scatter(local[hh], TS_hcon[loc][hh], color='skyblue', s=60)
        ax4.plot(local, TS_hpbl[loc], color='indigo', lw='1.5', label='Boundary Layer Height')
        ax4.scatter(local[hh], TS_hpbl[loc][hh], color='indigo', s=60)
        ax4.set_xlim([local[0], local[-1]])
        ax4.set_ylim([0, TS_hcon[loc].max()+200])
        ax4.xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
        ax4.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))

        ax4.legend()
        ax4.grid()
        ax4.set_ylabel('Height (m)')
        ax4.set_xlabel('Local Time')

        # 4) Save figure
        save_name = SAVE+'%s_f%02d.png' % (TS_dates[hh].strftime('%Y-%m-%d_%H%M'),fxx)
        plt.savefig(save_name)
        print "saved:", save_name
