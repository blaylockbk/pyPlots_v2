# Brian Blaylock
# July 10, 2017                      I think I'm getting married in October.

"""
For a MesoWest Station, create a hovmoller-style diagram to show how the HRRR
forecasted variables change between each successive forecast.

1) Hovmoller Point
2) Hovmoller Max in area
"""
print "\n--------------------------------------------------------"
print "  Working on the HRRR hovmollers (Pioneer_hov.py)"
print "--------------------------------------------------------\n"

import numpy as np
from datetime import datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')		#required for the CRON job or cgi script. Says "do not open plot in a window"??
import matplotlib.pyplot as plt
import os

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_downloads.HRRR_S3 import point_hrrr_time_series_multi, get_hrrr_hovmoller
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_MesoWest.MesoWest_STNinfo import get_station_info
from matplotlib.dates import DateFormatter, HourLocator, DayLocator

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [16, 8]
mpl.rcParams['figure.titlesize'] = 15
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['lines.linewidth'] = 1.8
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.01
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.framealpha'] = .75
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100
mpl.rcParams['savefig.transparent'] = False

#==============================================================================
# Date range
sDATE = datetime(2016, 7, 28)
eDATE = datetime(2016, 11, 3)

# List of MesoWest stations
MesoWestID = ['TT029', 'HFNC1']             # !!! The problem with using these is that the MesoWest metadata has the incorrect Lat/Lon for this period!!!

# Half box for area statistics
half_box = 9

# Directory to save figures (subdirectory will be created for each stnID)
SAVE_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR_fires/PIONEER_2016/'

# Create specifications (spex) for each variable we want to plot
spex = {'Wind Speed':{'HRRR var':'WIND:10 m',
                      'MW var':'wind_speed',
                      'units': r'ms$\mathregular{^{-1}}$',
                      'cmap':'magma_r',
                      'contour':range(4, 30, 4)},
        'Wind Gust':{'HRRR var':'GUST:surface',
                     'MW var':'wind_gust',
                     'units': r'ms$\mathregular{^{-1}}$',
                     'cmap':'magma_r',
                     'contour':range(4, 30, 4)},
        'Simulated Reflectivity':{'HRRR var':'REFC:entire atmosphere',
                                  'MW var':'reflectivity',
                                  'units': 'dBZ',
                                  'cmap':'gist_ncar',
                                  'contour':range(20, 100, 40)},
        'PBL Height':{'HRRR var':'HPBL:surface',
                      'MW var':'pbl_height',
                      'units': 'm',
                      'cmap':'Blues',
                      'contour':range(1000, 3000, 1000)},
        'Surface CAPE':{'HRRR var':'CAPE:surface',
                        'MW var':'surface_CAPE',
                        'units': r'Jkg$\mathregular{^{-1}}$',
                        'cmap':'OrRd',
                        'contour':range(100, 1000, 100)},
        'Air Temperature':{'HRRR var':'TMP:2 m',
                           'MW var':'air_temp',
                           'units': 'C',
                           'cmap':'Spectral_r',
                           'contour':range(5, 30, 5)},
        'Dew Point Temperature':{'HRRR var':'DPT:2 m',
                                 'MW var':'dew_point_temperature',
                                 'units': 'C',
                                 'cmap':'BrBG',
                                 'contour':range(5, 50, 5)}}

#==============================================================================

# Create a dictionary of the locations
#c = get_station_info(MesoWestID)
#locations = {}
#for idx_MW in range(len(MesoWestID)):
#    locations[c['STNID'][idx_MW]] = {'latitude': c['LAT'][idx_MW],
#                                     'longitude': c['LON'][idx_MW],
#                                     'name': c['NAME'][idx_MW],
#                                     'is MesoWest': True}

locations = {'PIONEER': {'latitude':43.95,
                         'longitude':-115.762,
                         'name':'PIONEER',
                         'is MesoWest': False}}

# Get data and create plots: Loop through each variable and station
for s in spex:
    print "\n   ---- Working on plots for %s ----\n" % s
    S = spex[s]
    #
    # Retreive a "Hovmoller" array, all forecasts for a period of time, for
    # each station in the locaiton dicionary.
    hovmoller = get_hrrr_hovmoller(sDATE, eDATE, locations,
                                   variable=S['HRRR var'],
                                   reduce_CPUs=0,
                                   area_stats=half_box)
    #
    first_mw_attempt = S['MW var']
    for stn in locations.keys():
        print "\nWorking on %s %s" % (stn, s)
        SAVE = SAVE_dir + '%s/' % stn
        if not os.path.exists(SAVE):
            # make the SAVE directory if it doesn't already exist
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
            os.link(photo_viewer, SAVE+'photo_viewer.php')
        #
        # Get data from the MesoWest Station
        #
        a = get_mesowest_ts(stn, sDATE, eDATE, variables=S['MW var'])
        # Aak, so many different precipitatin variables. Try each one until we
        # find one that works...
        if a == 'ERROR':
            # the variable probably isn't available (i.e. CAPE), so fill with nans
            dates_1d = hovmoller['valid_1d+'][:-1]
            a = {'DATETIME':dates_1d,
                 S['MW var']:[np.nan for i in range(len(dates_1d))]}
        #
        # Apply offset to data if necessary
        if s == 'Air Temperature' or s == 'Dew Point Temperature':
            hovmoller[stn]['max'] = hovmoller[stn]['max']-273.15
            hovmoller[stn]['min'] = hovmoller[stn]['min']-273.15
            hovmoller[stn]['box center'] = hovmoller[stn]['box center']-273.15
        #
        #
        if s == 'Simulated Reflectivity':
            hmin = 0
            hmax = 80
        else:
            hmin = np.nanmin([np.nanmin(a[S['MW var']]), np.nanmin(hovmoller[stn]['box center'])])
            hmax = np.nanmax([np.nanmax(a[S['MW var']]), np.nanmax(hovmoller[stn]['box center'])])
        #
        # Mask the nan values
        #
        #
        # Plot the Hovmoller diagram
        plt.clf()
        plt.cla()
        fig = plt.figure(1)
        ax1 = plt.subplot2grid((8, 1), (0, 0), rowspan=7)
        ax2 = plt.subplot(8, 1, 8)
        #
        plt.suptitle('%s %s\n%s - %s' % \
                    (stn, s, sDATE.strftime('%Y-%m-%d %H:%M'),\
                        eDATE.strftime('%Y-%m-%d %H:%M')))
        #
        # HRRR Hovmoller (tall subplot on top)
        hv = ax1.pcolormesh(hovmoller['valid_1d+'], hovmoller['fxx_1d+'], hovmoller[stn]['box center'],
                            cmap=S['cmap'],
                            vmax=hmax,
                            vmin=hmin)
        ax1.set_xlim(hovmoller['valid_1d+'][0], hovmoller['valid_1d+'][-1])
        ax1.set_ylim(0, 19)
        ax1.set_yticks(range(0, 19, 3))
        ax1.axes.xaxis.set_ticklabels([])
        ax1.set_ylabel('HRRR Forecast Hour')
        #
        # HRRR hovmoller difference of center from box maximum (contour)
        if s in ['Simulated Reflectivity', 'Surface CAPE', 'Wind Speed', 'Wind Gust']:
            CS = ax1.contour(hovmoller['valid_2d'], hovmoller['fxx_2d'], hovmoller[stn]['max']-hovmoller[stn]['box center'],
                            colors='k',
                            levels=S['contour'])
            plt.clabel(CS, inline=1, fontsize=10, fmt='%1.f')
        #
        # Observed mesh (thin subplot on bottom)
        mw = ax2.pcolormesh(a['DATETIME'], range(3), [a[S['MW var']], a[S['MW var']]],
                            cmap=S['cmap'],
                            vmax=hmax,
                            vmin=hmin)
        ax2.axes.yaxis.set_ticklabels([])
        ax2.set_yticks([])
        ax2.set_ylabel('Observed')
        ax2.set_xlim(hovmoller['valid_1d+'][0], hovmoller['valid_1d+'][-1])
        #
        ax1.grid()
        ax2.grid()
        #
        fig.subplots_adjust(hspace=0, right=0.8)
        cbar_ax = fig.add_axes([0.82, 0.15, 0.02, 0.7])
        cb = fig.colorbar(hv, cax=cbar_ax)
        cb.ax.set_ylabel('%s (%s)' % (s, S['units']))
        #
        #ax1.xaxis.set_major_locator(HourLocator(byhour=[0]))
        #ax2.xaxis.set_major_locator(HourLocator(byhour=[0]))
        ax1.xaxis.set_major_locator(DayLocator(bymonthday=[1, 5, 10, 15, 20, 25, 30]))
        ax2.xaxis.set_major_locator(DayLocator(bymonthday=[1, 5, 10, 15, 20, 25, 30]))
        dateFmt = DateFormatter('%b %d')
        ax2.xaxis.set_major_formatter(dateFmt)
        #
        ax1.set_xlabel(r'Contour shows difference between maximum value in %s km$\mathregular{^{2}}$ box centered at %s %s and the value at the center point.' \
                    % (half_box*6, locations[stn]['latitude'], locations[stn]['longitude']), fontsize=8)
        #
        plt.savefig(SAVE+'%s_%s.png' % (stn, S['MW var']))
