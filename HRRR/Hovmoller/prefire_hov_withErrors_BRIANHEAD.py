# Brian Blaylock
# July 11, 2017                    Umm, I think I'm getting married in October

"""
Hovemoller for two weeks prior to a fire, with bias and RMS errors calculated
for each forecast hour against the analysis hour.
"""
import matplotlib as mpl
mpl.use('Agg')#required for the CRON job. Says "do not open plot in a window"??
import numpy as np
from datetime import datetime, timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator
import os

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_downloads.HRRR_S3 import point_hrrr_time_series_multi, get_hrrr_hovmoller
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_MesoWest.MesoWest_STNinfo import get_station_info
from BB_data.active_fires import get_fires


## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [15, 12]        #[15, 6]
mpl.rcParams['figure.titlesize'] = 15
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['lines.linewidth'] = 1.8
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.18     #0.01
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.framealpha'] = .75
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100
mpl.rcParams['savefig.transparent'] = False

print "\n--------------------------------------------------------"
print "  Working on the HRRR hovmollers fires (%s)" % sys.argv[0]
print "--------------------------------------------------------\n"

#==============================================================================


# Directory to save figures (subdirectory will be created for each stnID)
SAVE_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR_fires/'

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

# For Hovmoller statistics, define the half box.
# The demisions of the box will be (halfbox*2)*3km**2. 
# ex. if halfbox=3, then the variable statistics will be calculeted for a 18km**2 box
# centered at the station latitude/longitude.
half_box = 9

#==============================================================================
# 1) Read in large fires file:
fires_file = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt' # Operational file: local version copied from the gl1 crontab

fires = np.genfromtxt(fires_file, names=True, dtype=None,delimiter='\t')
#column names:
    # 0  INAME - Incident Name
    # 1  INUM
    # 2  CAUSE
    # 3  REP_DATE - reported date
    # 4  START_DATE
    # 5  IMT_TYPE
    # 6  STATE
    # 7  AREA
    # 8  P_CNT - Percent Contained
    # 9  EXP_CTN - Expected Containment
    # 10 LAT
    # 11 LONG
    # 12 COUNTY
print "there are", len(fires), "large fires"

# 1) Locations (dictionary)
locations = {}
for F in range(0, len(fires)):
    FIRE = fires[F]
    # 1) Get Latitude and Longitude for the indexed large fire [fire]
    # No HRRR data for Alaska or Hawaii, so don't do it.
    # Also, don't bother running fires less than 1000 acres
    if FIRE[7] < 1000 or FIRE[6] == 'Alaska' or FIRE[6] == 'Hawaii':
        continue
    locations[FIRE[0]] = {'latitude': FIRE[10],
                          'longitude': FIRE[11],
                          'name': FIRE[0],
                          'start':FIRE[4],
                          'state': FIRE[6],
                          'area': FIRE[7],
                          'start date': FIRE[4],
                          'is MesoWest': False
                         }

for s in spex:
    S = spex[s]
    #
    #
    #
    first_mw_attempt = S['MW var']
    for stn in locations.keys():
        print "\nWorking on %s %s" % (stn, s)
        #
        # Collect the hovmollers. !! Extreamly inefficient becuase the start
        # date of each fire is different. Oh, well.
        ## Date range
        if locations[stn]['start'] == 'Not Reported':
            continue
        # Only do the Brian Head Fire
        if stn != 'BRIANHEAD':
            continue

        eDATE = datetime.strptime(locations[stn]['start'],'%d-%b-%y')    # Start Date of fire
        sDATE = eDATE-timedelta(days=14)
        # Retreive a "Hovmoller" array, all forecasts for a period of time, for
        # each station in the locaiton dicionary.
        hovmoller = get_hrrr_hovmoller(sDATE, eDATE, locations,
                                    variable=S['HRRR var'],
                                    area_stats=half_box)
        #
        #
        SAVE = SAVE_dir + '%s/2week_prefire/' % stn.replace(' ','_')
        if not os.path.exists(SAVE):
            # make the SAVE directory if it doesn't already exist
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
            os.link(photo_viewer, SAVE+'photo_viewer.php')
        #
        # Apply offset to data if necessary
        if s == 'Air Temperature' or s == 'Dew Point Temperature':
            hovmoller[stn]['max'] = hovmoller[stn]['max']-273.15
            hovmoller[stn]['box center'] = hovmoller[stn]['box center']-273.15
        #
        hovCenter = hovmoller[stn]['box center']
        hovCenter = np.ma.array(hovCenter)
        hovCenter[np.isnan(hovCenter)] = np.ma.masked
        #
        hovBoxMax = hovmoller[stn]['max']
        hovBoxMax = np.ma.array(hovBoxMax)
        hovBoxMax[np.isnan(hovBoxMax)] = np.ma.masked
        #
        #
        if s == 'Simulated Reflectivity':
            hmin = 0
            hmax = 80
        else:
            hmin = np.nanmin(hovCenter)
            hmax = np.nanmax(hovCenter)
        #
        # Plot the Hovmoller diagram
        fig = plt.figure(1)
        plt.clf()
        plt.cla()
        fig = plt.figure(1)
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212)
        #
        plt.suptitle('%s %s\n%s - %s' % \
                    (stn, s, sDATE.strftime('%Y-%m-%d %H:%M'),\
                        eDATE.strftime('%Y-%m-%d %H:%M')))
        #
        # =====================================================================
        #      HRRR Hovmoller RAW DATA
        # =====================================================================
        hv = ax1.pcolormesh(hovmoller['valid_1d+'], hovmoller['fxx_1d+'], hovCenter,
                            cmap=S['cmap'],
                            vmax=hmax,
                            vmin=hmin)
        cbar_ax = fig.add_axes([.92, 0.55, 0.02, 0.33]) # Left Bottom Width height
        cb1 = fig.colorbar(hv, cax=cbar_ax)
        cb1.ax.set_ylabel('%s (%s)' % (s, S['units']))
        ax1.set_xlim(hovmoller['valid_1d+'][0], hovmoller['valid_1d+'][-1])
        ax1.set_ylim(0, 19)
        ax1.set_yticks(range(0, 19, 3))
        ax1.axes.xaxis.set_ticklabels([])
        ax1.set_ylabel('HRRR Forecast Hour')
        ax1.set_title('Raw Point Data')
        ax1.grid()
        #
        #
        ax1.xaxis.set_major_locator(HourLocator(byhour=range(0,24,3)))
        dateFmt = DateFormatter('%b %d\n%H:%M')
        ax1.xaxis.set_major_formatter(dateFmt)
        #
        # =====================================================================
        #      HRRR Hovmoller BIAS ERROR
        # =====================================================================
        # Duplicate the analysis row, the first row
        anlys2D = np.tile(hovmoller[stn]['box center'][0], [19,1])
        #
        bias = hovCenter - anlys2D
        MaxMinRange =  np.max([np.abs(np.max(bias)), np.abs(np.min(bias))])
        #
        hvBias = ax2.pcolormesh(hovmoller['valid_1d+'], hovmoller['fxx_1d+'], bias,
                                cmap='bwr',
                                vmax=MaxMinRange,
                                vmin=-MaxMinRange)
        cbar_ax = fig.add_axes([.92, 0.12, 0.02, 0.33]) # Left Bottom Width height
        cb2 = fig.colorbar(hvBias, cax=cbar_ax)
        cb2.ax.set_ylabel('%s Bias (%s)' % (s, S['units']))
        ax2.set_xlim(hovmoller['valid_1d+'][0], hovmoller['valid_1d+'][-1])
        ax2.set_ylim(0, 19)
        ax2.set_yticks(range(0, 19, 3))
        ax2.axes.xaxis.set_ticklabels([])
        ax2.set_ylabel('HRRR Forecast Hour')
        ax2.set_title('Bias Error (Forecast Data - Analysis)')
        ax2.grid()
        #
        #
        ax2.xaxis.set_major_locator(HourLocator(byhour=range(0,24,3)))
        dateFmt = DateFormatter('%b %d\n%H:%M')
        ax2.xaxis.set_major_formatter(dateFmt)
        #
        #
        #
        plt.savefig(SAVE+S['MW var']+'.png')
