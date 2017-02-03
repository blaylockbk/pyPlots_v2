# Brian Blaylock
# 23 November 2016

"""
Plot surface temperature from the HRRR model, focusing on the Great Salt Lake. 
Comment on the temperature at the Great Salt Lake Buoy (GSLBY)
"""

import pygrib

import matplotlib.pyplot as plt
style_path = '/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/BB_mplstyle/'
plt.style.use([style_path+'publications.mplstyle',
                   style_path+'width_75.mplstyle',
                   style_path+'dpi_medium.mplstyle']
                   )
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta
import numpy as np
import multiprocessing #:)

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:/pyBKB_v2')
from BB_basemap.draw_maps import draw_GSL_map, draw_UtahLake_map, draw_GSL2_map
from BB_data.grid_manager import pluck_point
from BB_MesoWest.MesoWest_buoy import get_buoy_ts
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts


def get_lake_temp(DATE, HRRR_version='hrrr'):
    """
    Opens a HRRR file (hrrr or hrrrX) and returns the surface temperature 
    as well as surface temperatures for select stations.
    """

    try:
        DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/%s/' % (DATE.year, DATE.month, DATE.day, HRRR_version)
        FILE = '%s.t%02dz.wrfsfcf00.grib2' % (HRRR_version, DATE.hour)

        # Get Surface Temperature from the HRRR
        grbs = pygrib.open(DIR+FILE)
        print DATE
        print 'Grabbed:', grbs(name='Temperature')[-1]
        lat, lon = grbs(name='Temperature')[-1].latlons()
        T_surface = grbs(name='Temperature')[-1].values
        temp_2m = grbs(name='2 metre temperature')[-1].values

        """
        If I trim the data to just the Utah Domain it might plot a lot faster!! :)
        """

        # Plot a circle where the GSL Buoy is Located, grab the HRRR surface
        # temperature, and comment that below.
        buoy_lat = 40.89068
        buoy_lon = -112.34551
        p = pluck_point(buoy_lat, buoy_lon, lat, lon)
        buoy_temp = T_surface.flatten()[p]
        buoy_2m = temp_2m.flatten()[p] 

        # Plot a circle where the UofU tripod is located and grab temperature
        #stn = UFD09
        ufd09_lat = 40.92533 
        ufd09_lon = -112.15936 
        p2 = pluck_point(ufd09_lat, ufd09_lon, lat, lon)
        ufd09_temp = T_surface.flatten()[p2]
        # Since this station is in water, grab one point west of station to
        # get the land temperature on Antelope Island
        ufd09_temp2 = T_surface.flatten()[p2-1]
        
        ufd09_2m = temp_2m.flatten()[p]
        ufd09_2m2 = temp_2m.flatten()[p-1]

        # Plot a circle where BFLAT station is located and grab temperature
        bflat_lat = 40.78422
        bflat_lon = -113.82946
        p3 = pluck_point(bflat_lat, bflat_lon, lat, lon)
        bflat_temp = T_surface.flatten()[p3]
        bflat_2m = temp_2m.flatten()[p]

        # Return the data we want, and convert temperatures to Celsius.
        return_this = {'DATE': DATE,
                       'LAT': lat,
                       'LON': lon,
                       'HRRR Version': HRRR_version,
                       'T_surface': T_surface-273.15,
                       'buoy_temp': buoy_temp-273.15,   # surface temp
                       'buoy_2m': buoy_2m-273.15,       # 2m air temp
                       'buoy_lat': buoy_lat,            # latitude
                       'buoy_lon': buoy_lon,            # longitude
                       'ufd09_temp': ufd09_temp-273.15,
                       'ufd09_temp2': ufd09_temp2-273.15,
                       'ufd09_2m': ufd09_2m-273.15,
                       'ufd09_2m2': ufd09_2m2-273.15,
                       'ufd09_lat': ufd09_lat,
                       'ufd09_lon': ufd09_lon,
                       'bflat_temp': bflat_temp-273.15,
                       'bflat_2m': bflat_2m-273.15,
                       'bflat_lat': bflat_lat,
                       'bflat_lon': bflat_lon,
                      }
    except:
        # Return the data we want, and convert temperatures to Celsius.
        return_this = {'DATE': DATE,
                       'LAT': np.nan,
                       'LON': np.nan,
                       'HRRR Version': HRRR_version,
                       'T_surface': np.nan,
                       'buoy_temp': np.nan,
                       'buoy_2m': np.nan,
                       'buoy_lat': np.nan,
                       'buoy_lon': np.nan,
                       'ufd09_temp': np.nan,
                       'ufd09_temp2': np.nan,
                       'ufd09_2m': np.nan,
                       'ufd09_2m2': np.nan,
                       'ufd09_lat': np.nan,
                       'ufd09_lon': np.nan,
                       'bflat_temp': np.nan,
                       'bflat_2m': np.nan,
                       'bflat_lat': np.nan,
                       'bflat_lon': np.nan,
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
    
    fig, (ax1) = plt.subplots(1,1)

    SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/GSL_HRRR_temp/'

    # Handle the date
    str_DATE = lake['DATE'].strftime('%Y-%m-%d %H:%M UTC')
    save_DATE = lake['DATE'].strftime('%Y-%m-%d_%H%Mz')

    # plot the buoy location
    m.scatter(lake['buoy_lon'], lake['buoy_lat'],
              facecolors='none',
              edgecolor='k',
              s=50,
              zorder=500)
    
    # plot the tripod location
    m.scatter(lake['ufd09_lon'], lake['ufd09_lat'],
              facecolors='none',
              edgecolor='k',
              s=50,
              zorder=500)

    
    # plot the BFLAT location
    m.scatter(lake['bflat_lon'], lake['bflat_lat'],
              facecolors='none',
              edgecolor='k',
              s=50,
              zorder=500)              

    # plot the surface temperatures
    m.pcolormesh(lake['LON'], lake['LAT'], lake['T_surface'],
                 vmin=-10, vmax=30,
                 cmap='afmhot_r'
                )
    cb = plt.colorbar(orientation='horizontal', 
                      ticks=range(-10, 31, 5), 
                      shrink=0.6,
                      pad=0.03,
                      extend='both')
    cb.set_label('Surface Temperature (C)')
    cb_plotted = True

    # draw the GSL boundary
    m.drawcoastlines()  # surprisingly a good guess of the lake's current size

    # Figure formating and such
    plt.title('HRRR Surface Temperature\n'+str_DATE)
    
    # Side bar text
    side_text = "Surface Temperatures\n--------------------\n"
    side_text += 'GSLBY: %0.2f C\nUFD09: %0.2f C\nBFLAT: %0.2f C' \
                 % (lake['buoy_temp'], lake['ufd09_temp'], lake['bflat_temp'])
    fig.text(.8, .85, side_text, 
             fontname='monospace', 
             va='top',
             backgroundcolor='white',
             fontsize=7)

    plt.savefig(SAVEDIR+save_DATE, bbox_inches='tight')
    print 'saved:', SAVEDIR+save_DATE


def main(from_mp):  
    """
    Input:
     from_mp - list from multiprocessing
     First element is the datetime object
     Second element is the map object
    """
    try:
        date = from_mp[0]
        map_obj = from_mp[1]
        hrrr_v = from_mp[2]
        lake = get_lake_temp(date, HRRR_version=hrrr_v)
        try:
            plot_lake_temp(lake, map_obj)
        except:
            print 'could not plot', date
        
        return [lake['buoy_temp'], lake['ufd09_temp'], lake['ufd09_temp2'], lake['bflat_temp'], \
                lake['buoy_2m'], lake['ufd09_2m'], lake['ufd09_2m2'], lake['bflat_2m']]
    except:
        print "error plotting:", from_mp[0]
        return np.nan


if __name__ == "__main__":

    # Draw the map once.
    m = draw_GSL2_map(res='i')

    # HRRR version (hrrr, or hrrrX)
    HRRR_version = 'hrrr'

    # Create a list of dates (DATE1 is start date, DATE2 is end date)
    DATE1 = datetime(2016, 10, 1, 0)
    DATE2 = datetime(2017, 1, 2, 0)
    days = (DATE2 - DATE1).days + (DATE2 - DATE1).seconds/3600./24
    hours = int(days*24)  # must be an integer for making lists below
    save_date = DATE1.strftime('%Y%m%d') + '-' + DATE2.strftime('%Y%m%d') 

    increment_by = 'hour'
    increment_by = 'day'


    if increment_by=='hour':
        # make a list of dates and the map object
        date_map_list = np.array([[DATE2 - timedelta(hours=x), m, HRRR_version] for x in range(0, hours)])
        # make a list of just dates
        date_list = np.array([DATE2 - timedelta(hours=x) for x in range(0, hours)])

    if increment_by=='day':
        # for multiprocessing, make a list of dates, map object, and HRRR version
        date_map_list = np.array([[DATE2 - timedelta(days=x), m, HRRR_version] for x in range(0, int(days))])
        # make a list of just dates
        date_list = np.array([DATE2 - timedelta(days=x) for x in range(0, int(days))])


    # Multiprocessing :)
    num_proc = multiprocessing.cpu_count() - 2 # just to be kind, don't use everything
    if num_proc > len(date_list):
        num_proc = len(date_list)  # Only use number of processors as we will make figures for.
    p = multiprocessing.Pool(num_proc)
    temps = p.map(main, date_map_list)

    # convert temps list to a friendly numpy 2D array. Get the values for each
    # of the stations (same order as returned in function above).
    temps = np.array(temps)
    buoy_temps = temps[:, 0]
    ufd09_temps = temps[:, 1]
    ufd09_temps2 = temps[:, 2]  # Remember, these are the 1 grid point west of
                                # the nearest neighbor which isn't water. 
    bflat_temps = temps[:, 3]
    
    # Air temperatures where also returned
    buoy_2m = temps[:, 4]
    ufd09_2m = temps[:, 5]
    ufd09_2m2 = temps[:, 6]  # Remember, these are the 1 grid point west of
                                # the nearest neighbor which isn't water. 
    bflat_2m = temps[:, 7]


    # Get MesoWest observations. 
    try:
        a = get_buoy_ts(date_list[-1], date_list[0])
    except:
        print "no buoy observations"
    MW_bflat = get_mesowest_ts('BFLAT', date_list[-1], date_list[0])
    MW_ufd09 = get_mesowest_ts('UFD09', date_list[-1], date_list[0], variables='air_temp,surface_temp')



    plt.plot(a['Datetimes'], a['T_water1'])
    plt.plto(date_list, buoy_temps)

    """
    Plot time series:
        - HRRR surface temperature and
        - Buoy observed -0.4 meter water temperature.
        - UFD09 surface temperature
    """


    """

    fig, [[ax1, ax2], [ax3,ax4], [ax5, ax6]] = plt.subplots(3, 2, figsize=(10, 8))

    # **** Surface Temperatures **********************************
    # ---- GSLBY -------------------------------------------------    

    # MW Water temperature -0.4 meters
    try:
        ax1.plot(a['DATETIMES'], a['T_water1'],
                color='k',
                linewidth=1.2, 
                label='Observed -0.4 m Water Temp')
    except:
        #ax1.plot(date_list, np.ones_like(date_list)*np.nan,
        #         color='k',
        #         label='GSLBY n/a')
        pass
    # Surface Temp from HRRR
    ax1.plot(date_list, buoy_temps,
            color='dodgerblue',
            label=HRRR_version.upper() + ' Surface Temp')

    ax1.legend()
    ax1.grid()

    ax1.set_title('GSLBY Surface Temperature')
    ax1.set_ylabel('Temperature (C)')
    ax1.set_ylim([-15, 15])
    ax1.set_xlim([DATE1,DATE2])

    # ---- UFD09 -------------------------------------------------
    # MW Surface Temp at UFD09
    ax3.plot(MW_ufd09['DATETIME'], MW_ufd09['surface_temp'],
                color='k',
                linewidth=1.2,
                label='Observed Surface Temp')
    # Surface Temp from HRRR
    ax3.plot(date_list, ufd09_temps, 
                color='dodgerblue',
                label=HRRR_version.upper() + ' Surface Temp (Water)')
    ax3.plot(date_list, ufd09_temps2, 
                color='orangered',
                label=HRRR_version.upper() + ' Surface Temp (Land)')


    ax3.legend()
    ax3.grid()

    ax3.set_title('UFD09 Surface Temperature')
    ax3.set_ylabel('Temperature (C)')
    ax3.set_ylim([-15, 15])
    ax3.set_xlim([DATE1,DATE2])

    # ---- BFLAT -------------------------------------------------
    # MW Air Temp at BFLAT
    # (none available)
    # Surface Temp from HRRR
    ax5.plot(date_list, bflat_temps, 
                color='orangered',
                label=HRRR_version.upper()+ ' Surface Temp')

    ax5.legend()
    ax5.grid()

    ax5.set_title('BFLAT Surface Temperature')
    ax5.set_ylabel('Temperature (C)')
    ax5.set_ylim([-15, 15])
    ax5.set_xlim([DATE1,DATE2])

    # **** Surface Temperatures **********************************
    # ---- GSLBY -------------------------------------------------    

    # MW Air Temp
    try:
        ax2.plot(a['DATETIMES'], a['air_temp'],
                color='k',
                linewidth=1.2, 
                label='Observed Air Temp')
    except:
        ax2.plot(date_list, np.ones_like(date_list)*np.nan,
                color='k',
                label='GSLBY n/a')

    # Surface Temp from HRRR
    ax2.plot(date_list, buoy_2m,
            color='dodgerblue',
            label=HRRR_version.upper() + ' Air Temp')

    ax2.legend()
    ax2.grid()

    ax2.set_title('GSLBY 2 m Air Temperature')
    ax2.set_ylabel('Temperature (C)')
    ax2.set_ylim([-15, 15])
    ax2.set_xlim([DATE1,DATE2])

    # ---- UFD09 -------------------------------------------------
    # MW Surface Temp at UFD09
    ax4.plot(MW_ufd09['DATETIME'], MW_ufd09['air_temp'],
                color='k',
                linewidth=1.2,
                label='Observed Air Temp')
    # Surface Temp from HRRR
    ax4.plot(date_list, ufd09_2m, 
                color='dodgerblue',
                label=HRRR_version.upper() + ' Air Temp (Water)')
    ax4.plot(date_list, ufd09_2m2, 
                color='orangered',
                label=HRRR_version.upper() + ' Air Temp (Land)')


    ax4.legend()
    ax4.grid()

    ax4.set_title('UFD09 2 m Air Temperature')
    ax4.set_ylabel('Temperature (C)')
    ax4.set_ylim([-15, 15])
    ax4.set_xlim([DATE1,DATE2])

    # ---- BFLAT -------------------------------------------------
    # MW Air Temp at BFLAT
    ax6.plot(MW_bflat['DATETIME'], MW_bflat['air_temp'],
                color='k',
                linewidth=1.2,
                label='Observed Air Temp')
    # Surface Temp from HRRR
    ax6.plot(date_list, bflat_2m, 
                color='orangered',
                label=HRRR_version.upper()+ ' Air Temp')

    ax6.legend()
    ax6.grid()

    ax6.set_title('BFLAT 2 m Air Temperature')
    ax6.set_ylabel('Temperature (C)')
    ax6.set_ylim([-15, 15])
    ax6.set_xlim([DATE1,DATE2])



    # Format Ticks on Date Axis
    if days > 3:
        dateFmt = DateFormatter('%b %d')
    else:
        dateFmt = DateFormatter('%b %d\n%H:%M')
    
    ax1.xaxis.set_major_formatter(dateFmt)
    ax2.xaxis.set_major_formatter(dateFmt)
    ax3.xaxis.set_major_formatter(dateFmt)
    ax4.xaxis.set_major_formatter(dateFmt)
    ax5.xaxis.set_major_formatter(dateFmt)
    ax6.xaxis.set_major_formatter(dateFmt)
    ax1.xaxis.set_major_formatter(dateFmt)

    # Other housekeeping
    fig.tight_layout()
    fig.subplots_adjust(top=0.88)

    SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/GSL_HRRR_temp/new/'
    plt.savefig(SAVEDIR+'%s_%s_MesoWest.png' % (save_date, HRRR_version.upper()))
    plt.savefig(SAVEDIR+'%s_%s_MesoWest.eps' % (save_date, HRRR_version.upper()), format='eps')
    print 'saved', SAVEDIR+'%s_%s_MesoWest.png' % (save_date, HRRR_version.upper())

    plt.show(block=False)

    """
