# Brian Blaylock
# April 28, 2017                           Jazz are going to Game 5, tonight!!!

# May 19, 2017: Updated to more efficeint plotting

"""
Project Golf is inspired by Dallin Naulu, the superintendant at Spanish Oaks
Golf Course. He wanted to view weather forecasts for his golf course, so I made
this display for him. These are useful plots at many locations. This particular
script makes a plot for the analysis hours.
"""
import matplotlib as mpl
#mpl.use('Agg')		#required for the CRON job or cgi script. Says "do not open plot in a window"??
import numpy as np
from datetime import datetime, timedelta
import time
import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.dates as mdates

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [15, 6]
mpl.rcParams['figure.titlesize'] = 15
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['lines.linewidth'] = 1.8
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.05
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.framealpha'] = .75
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100
mpl.rcParams['savefig.transparent'] = False

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/lib/python2.7/site-packages/')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_S3 import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_MesoWest.MesoWest_radius import get_mesowest_radius
from BB_MesoWest.MesoWest_STNinfo import get_station_info
from MetPy_BB.plots import ctables
from BB_data.grid_manager import pluck_point_new
from BB_wx_calcs.wind import wind_uv_to_spd, wind_spddir_to_uv
from BB_wx_calcs.units import *

# === Stuff you may want to change ============================================

# List of MesoWest stations
MesoWestID = ['UKBKB', 'WBB']

# Date range
sDATE = datetime(2017, 5, 17)
eDATE = datetime(2017, 5, 19)

# Forecast (set to zero for HRRR analysis)
fxx = 18

# Directory to save figures (subdirectory will be created for each stnID)
SAVE_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/anlys/'

# =============================================================================
# =============================================================================

c = get_station_info(MesoWestID)

# 1) Locations
location = {}
for idx_MW in range(len(MesoWestID)):
    location[c['STNID'][idx_MW]] = {'latitude': c['LAT'][idx_MW],
                                    'longitude': c['LON'][idx_MW],
                                    'name': c['NAME'][idx_MW],
                                    'is MesoWest': True}

# 2) Get the HRRR data from NOMADS and store data nicely
print "UTC DATE:", sDATE

# 2.1) Time Series: Plucked HRRR value at all locations
#      These are dictionaries:
#      {'DATETIME':[array of dates], 'station name': [values for each datetime], ...}

TS_temp = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='TMP:2 m', fxx=fxx)
TS_dwpt = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='DPT:2 m', fxx=fxx)

TS_wind = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='WIND:10 m', fxx=fxx)
TS_gust = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='GUST:surface', fxx=fxx)
TS_u = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='UGRD:10 m', fxx=fxx)
TS_v = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='VGRD:10 m', fxx=fxx)
TS_u80 = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='UGRD:80 m', fxx=fxx)
TS_v80 = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='VGRD:80 m', fxx=fxx)
TS_wind80 = {} # we will derive this in the following loop

#TS_prec = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='APCP:surface') # Not valuable for an analysis
# TS_accum = {} # Not available for analysis
TS_hpbl = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='HPBL:surface', fxx=fxx)
TS_hcon = point_hrrr_time_series_multi(sDATE, eDATE, location, variable='HGT:level of adiabatic condensation from sfc', fxx=fxx)

# Convert the units of each Pollywog
for loc in location.keys():
    # Convert Units for the variables in the Pollywog
    TS_temp[loc] = KtoC(TS_temp[loc])
    TS_dwpt[loc] = KtoC(TS_dwpt[loc])

    # Derive some variables:
    TS_wind80[loc] = wind_uv_to_spd(TS_u80[loc],TS_v80[loc])


# Just need one vector of valid dates
TS_dates = np.array(TS_temp['DATETIME'])

# Make a dictionary of map object for each location.
# (This speeds up plotting by creating each map once.)
maps = {}
for loc in location:
    l = location[loc]
    m = Basemap(resolution='i', projection='cyl',\
                    llcrnrlon=l['longitude']-.25, llcrnrlat=l['latitude']-.25,\
                    urcrnrlon=l['longitude']+.25, urcrnrlat=l['latitude']+.25,)
    maps[loc] = m


# Create a figure for each location. Add permenant elements to each.
print 'making permenant figure elements...'
figs = {}
locs = location.keys() # a list of all the locations
locs_idx = range(len(locs)) # a number index for each location
for n in locs_idx:
    locName = locs[n]
    l = location[locName]
    figs[locName] = {0:plt.figure(n)}
    plt.suptitle('HRRR Forecast: %s' % (l['name']), y=1)
    # Map - background, roads, radar, wind barbs
    figs[locName][1] = figs[locName][0].add_subplot(121)
    maps[locName].drawcounties()
    maps[locName].drawstates()
    maps[locName].arcgisimage(service='World_Shaded_Relief',
                              xpixels=500,
                              verbose=False)
    # Overlay Utah Roads
    BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
    maps[locName].readshapefile(BASE+'shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads',
                                'roads',
                                linewidth=.5,
                                color='dimgrey')
    x, y = m(l['longitude'], l['latitude']) # Location
    maps[locName].scatter(x, y, s=100, color='white', edgecolor='k', zorder=100)
    #
    # Plot: Temperature, dewpoint
    figs[locName][2] = figs[locName][0].add_subplot(322)
    figs[locName][2].plot(TS_temp['DATETIME'], TS_temp[locName], c='r', label='Temperature')
    figs[locName][2].plot(TS_dwpt['DATETIME'], TS_dwpt[locName], c='g', label='Dew Point')
    leg2 = figs[locName][2].legend()
    leg2.get_frame().set_linewidth(0)
    figs[locName][2].grid()
    figs[locName][2].set_ylabel('Degrees (C )')
    figs[locName][2].set_xlim([TS_temp['DATETIME'][0], TS_temp['DATETIME'][-1]])
    figs[locName][2].set_ylim([np.nanmin(TS_dwpt[locName])-3, np.nanmax(TS_temp[locName])+3])
    figs[locName][2].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 6)))
    figs[locName][2].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    figs[locName][2].xaxis.set_major_formatter(mdates.DateFormatter(''))
    #
    # Plot: Wind speed, gust, barbs
    figs[locName][3] = figs[locName][0].add_subplot(324)
    figs[locName][3].plot(TS_wind['DATETIME'], TS_wind80[locName], c='saddlebrown', label='Instantaneous 80 m wind')
    figs[locName][3].plot(TS_gust['DATETIME'], TS_gust[locName], c='chocolate', label='Instantaneous Wind Gust')
    figs[locName][3].plot(TS_wind['DATETIME'], TS_wind[locName], c='darkorange', label='Previous Hour Max Wind')
    # plt.barbs can not take a datetime object, so find the date indexes:
    idx = mpl.dates.date2num(TS_u['DATETIME'])
    spd = wind_uv_to_spd(TS_u[locName], TS_v[locName])
    # For some reason we have to plot each barb within a loop
    for ibarb in range(len(idx)):
        figs[locName][3].barbs(idx[ibarb], spd[ibarb], TS_u[locName][ibarb], TS_v[locName][ibarb],
                               length=6,
                               barb_increments=dict(half=2.5, full=5, flag=25))
    leg3 = figs[locName][3].legend()
    leg3.get_frame().set_linewidth(0)
    figs[locName][3].grid()
    figs[locName][3].set_ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
    figs[locName][3].set_ylim([0, np.nanmax(TS_gust[locName])+3])
    figs[locName][3].set_yticks([0, np.nanmax(TS_gust[locName])+3], 2.5)
    figs[locName][3].set_xlim([TS_gust['DATETIME'][0], TS_gust['DATETIME'][-1]])
    figs[locName][3].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 6)))
    figs[locName][3].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    figs[locName][3].xaxis.set_major_formatter(mdates.DateFormatter(''))
    #
    # Plot: Boundary Layer Height and Level of Adiabatic condensation 
    figs[locName][4] = figs[locName][0].add_subplot(326)
    figs[locName][4].plot(TS_hcon['DATETIME'], TS_hcon[locName], color='skyblue', lw='1.5', label='Level of adiabatic condensation from surface')
    figs[locName][4].plot(TS_hpbl['DATETIME'], TS_hpbl[locName], color='indigo', lw='1.5', label='Boundary Layer Height')
    figs[locName][4].set_xlim([TS_hcon['DATETIME'][0], TS_hcon['DATETIME'][-1]])
    maxHeight = np.nanmax([np.nanmax(TS_hcon[locName]), np.nanmax(TS_hpbl[locName])])
    figs[locName][4].set_ylim([0, maxHeight+25])
    figs[locName][4].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 6)))
    figs[locName][4].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    figs[locName][4].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))
    leg4 = figs[locName][4].legend()
    leg4.get_frame().set_linewidth(0)
    figs[locName][4].grid()
    figs[locName][4].set_ylabel('Height (m)')
    #
    # Finally, add MesoWest data if it is available
    if l['is MesoWest'] is True:
        a = get_mesowest_ts(locName, sDATE, eDATE,
                            variables='air_temp,wind_speed,dew_point_temperature')
        if a != 'ERROR':
            figs[locName][2].plot(a['DATETIME'], a['air_temp'], c='k', ls='--')
            figs[locName][2].plot(a['DATETIME'], a['dew_point_temperature'], c='k', ls='--')
            figs[locName][3].plot(a['DATETIME'], a['wind_speed'], c='k', ls='--')


# Now add the element that changes, save the figure, and remove elements from plot.
# Only download the HRRR grid once per forecast hour.
for hh in range(len(TS_dates)):
    # Loop through each location to make plots for this time
    # 2.2) Radar Reflectivity and winds for entire CONUS
    H = get_hrrr_variable(TS_dates[hh], 'REFC:entire atmosphere', fxx=fxx, model='hrrr')
    H_U = get_hrrr_variable(TS_dates[hh], 'UGRD:10 m', fxx=fxx, model='hrrr', value_only=True)
    H_V = get_hrrr_variable(TS_dates[hh], 'VGRD:10 m', fxx=fxx, model='hrrr', value_only=True)
    #
    # Mask out empty reflectivity values
    dBZ = H['value']
    dBZ = np.ma.array(dBZ)
    dBZ[dBZ == -10] = np.ma.masked
    #
    for n in locs_idx:
        locName = locs[n]
        l = location[locName]
        print "\n--> Working on:", locName, TS_dates[hh]
        #
        SAVE = SAVE = SAVE_dir + '%s/' % locName
        if not os.path.exists(SAVE):
            # make the SAVE directory if id doesn't already exist
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
            os.link(photo_viewer, SAVE+'photo_viewer_fire.php')
        # Title over map
        figs[locName][1].set_title('UTC: %s' % (TS_dates[hh]))
        figs[locName][2].set_title('       Run (UTC): %s f%02d\nValid (UTC): %s' % (H['anlys'].strftime('%Y %b %d, %H:%M'), fxx, H['valid'].strftime('%Y %b %d, %H:%M')))
        #
        # Project on map
        X, Y = maps[locName](H['lon'], H['lat'])            # HRRR grid
        # Trim the data
        cut_v, cut_h = pluck_point_new(l['latitude'],
                                       l['longitude'],
                                       H['lat'],
                                       H['lon'])
        bfr = 15
        trim_X = X[cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
        trim_Y = Y[cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
        trim_dBZ = dBZ[cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
        trim_H_U = H_U['value'][cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
        trim_H_V = H_V['value'][cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
        #
        # Overlay Simulated Radar Reflectivity
        ctable = 'NWSReflectivity'
        norm, cmap = ctables.registry.get_with_steps(ctable, -0, 5)
        radar = figs[locName][1].pcolormesh(trim_X, trim_Y, trim_dBZ, norm=norm, cmap=cmap, alpha=.5)
        if hh == 0:
            # Solution for adding colorbar from stackoverflow
            # http://stackoverflow.com/questions/32462881/add-colorbar-to-existing-axis
            from mpl_toolkits.axes_grid1 import make_axes_locatable
            divider = make_axes_locatable(figs[locName][1])
            cax = divider.append_axes('bottom', size='5%', pad=0.05)
            cb = figs[locName][0].colorbar(radar, cax=cax, orientation='horizontal')
            cb.set_label('Simulated Radar Reflectivity (dBZ)\n\nBarbs: Half=2.5 m/s, Full=5 m/s, Flag=25 m/s')
        #
        # Add nearby MesoWest
        MW_date = TS_temp['DATETIME'][hh]
        b = get_mesowest_radius(MW_date, 15,
                                extra='&radius=%s,%s,60' % (l['latitude'], l['longitude']),
                                variables='wind_speed,wind_direction')
        if len(b['NAME']) > 0:
            MW_u, MW_v = wind_spddir_to_uv(b['wind_speed'], b['wind_direction'])
            MWx, MWy = maps[locName](b['LON'], b['LAT'])
            MW_barbs = figs[locName][1].barbs(MWx, MWy, MW_u, MW_v,
                                              color='r',
                                              barb_increments=dict(half=2.5, full=5, flag=25))
        #
        # Wind Barbs
        # Overlay wind barbs (need to trim this array before we plot it)
        # First need to trim the array
        barbs = figs[locName][1].barbs(trim_X, trim_Y, trim_H_U, trim_H_V, zorder=200, length=6)
        #
        # 3.2) Temperature/Dew Point
        tempF = TS_temp[locName]
        dwptF = TS_dwpt[locName]
        pntTemp = figs[locName][2].scatter(TS_temp['DATETIME'][hh], tempF[hh], c='r', s=60)
        pntDwpt = figs[locName][2].scatter(TS_dwpt['DATETIME'][hh], dwptF[hh], c='g', s=60)
        #
        # 3.3) Wind speed and Barbs
        pntGust = figs[locName][3].scatter(TS_gust['DATETIME'][hh], TS_gust[locName][hh], c='chocolate', s=60)
        pntWind = figs[locName][3].scatter(TS_wind['DATETIME'][hh], TS_wind[locName][hh], c='darkorange', s=60)
        pntW80 = figs[locName][3].scatter(TS_wind['DATETIME'][hh], TS_wind80[locName][hh], c='saddlebrown', s=60)
        #
        # 3.4) Accumulated Precipitation
        pntHcon = figs[locName][4].scatter(TS_hcon['DATETIME'][hh], TS_hcon[locName][hh], edgecolor="k", color='skyblue', s=60)
        pntHpbl = figs[locName][4].scatter(TS_hpbl['DATETIME'][hh], TS_hpbl[locName][hh], edgecolor="k", color='indigo', s=60)
        #
        # 4) Save figure
        figs[locName][0].savefig(SAVE+'%s_f%02d.png' % (TS_dates[hh].strftime('%Y-%m-%d_%H%M'),fxx))
        #
        pntTemp.remove()
        pntDwpt.remove()
        pntGust.remove()
        pntWind.remove()
        pntW80.remove()
        pntHcon.remove()
        pntHpbl.remove()
        barbs.remove()
        radar.remove()
        try:
            MW_barbs.remove()
        except:
            # No barbs were plotted
            pass
    print "Finished:", TS_dates[hh]
