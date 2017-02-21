# Brian Blaylock
# 14 December 2015

# WRF Cross Section of potential temperature and tracer plumes
# This uses the high resolution output file, auxhis24 which I have 
# outputting at 10 minute intervals


from functions import wind_calcs, MesoWest_timeseries, WRF_timeseries, read_tslist, WRF_timeseries
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
import os
#from netCDF4 import Dataset  # we dont have this library. use scipy instead
from scipy.io import netcdf
from mpl_toolkits.basemap import Basemap
import matplotlib.colors as mcolors


# Set directories
WRFDIR = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_spinup_41levs/WRFV3/WRFV3/test/em_real/'
FIGDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/crosssection/spinup/41levs/lake/'
if not os.path.exists(FIGDIR):
    os.makedirs(FIGDIR)


# create a range of times at an interval of the timestep in minutes. auxhis24 has a 10 minute output
model_start = datetime(2015,6,14,0)
timeout_mins=10 # how frequently the output file writes in minutes
numhours=127
DateList = [model_start + timedelta(hours=x) for x in np.arange(0, numhours,timeout_mins/60.)]

# Don't really want to make plots for every time, just starting on the 18th
startplot_index = 0  # June 18th = index 144 ## Oh, I need to use nc.variables['Times']

domain = 'd02'

# Open WRF file, High-Resolution output 
#The auxhisXX file has the high resolution output. I use 24 for ten minute output of geopotential, potential temperature, and plumes    
AUXfile = 'auxhist24_%s_%s-%s-%s_%s:%s:%s' % (domain,str(model_start.year),str(model_start.month).zfill(2),str(model_start.day).zfill(2),str(model_start.hour).zfill(2),str(model_start.minute).zfill(2),str(model_start.second).zfill(2))
# Still use a WRF file to get static data
WRFfile = 'wrfout_%s_%s-%s-%s_%s:%s:%s' % (domain,str(model_start.year),str(model_start.month).zfill(2),str(model_start.day).zfill(2),str(model_start.hour).zfill(2),str(model_start.minute).zfill(2),str(model_start.second).zfill(2))    

nc = netcdf.netcdf_file(WRFDIR+AUXfile,'r')
ncW = netcdf.netcdf_file(WRFDIR+WRFfile,'r')

for t in np.arange(0,int(np.shape(nc.variables['Times'])[0])):

    plt.cla()
    plt.clf()
    plt.close()
    
    str_time = DateList[t].strftime('%Y%b%d-%H%M')

    time = ''.join(nc.variables['Times'][t])
    time_dt = datetime.strptime(time,'%Y-%m-%d_%H:%M:%S')
    time_str= datetime.strftime(time_dt,'%Y-%m-%d %H:%M:%S UTC')
    time_str_local=datetime.strftime(time_dt-timedelta(hours=6),'%Y-%m-%d %H:%M:%S MDT')
    time_save=datetime.strftime(time_dt,'%Y%b%d-%H%M')


    
    # Set the cross section values
    lat = np.arange(190,240)
    lon = np.arange(225,226)
    
    # Read in data from cross section 
    XLAT = ncW.variables['XLAT'][0]
    XLON = ncW.variables['XLONG'][0]
    XHGT = ncW.variables['HGT'][0]
    
    #                         [time,lat,lon]
    LAT = ncW.variables['XLAT'][0,lat,lon]    # Latitude
    LON = ncW.variables['XLONG'][0,lat,lon]   # Longitude
    HGT = ncW.variables['HGT'][0,lat,lon]    
    
    #                       [time][level-stag,lat,lon]
    PH  = nc.variables['PH'][t][:,lat,lon]   # perturbation geopotential  [m2 s-2]
    PHB = nc.variables['PHB'][t][:,lat,lon]  # base state geopotential    [m2 s-2]
    TPH = (PH+PHB)/9.81               # Total Geopotential Height  [meters]
    #                      [time][level,lat,lon]
    TH  = nc.variables['T'][t][:,lat,lon]    # Perturbation potential tempertaure [K]
    TTH = TH+300                          # Total Potential Temperature (theta) [K]
    
    # Plume Data
    N_SLV = nc.variables['LAKE'][t][:,lat,lon]
    S_SLV = nc.variables['BUOY'][t][:,lat,lon]
    
    
    # PH and TH are plotted on different levels:
    #               PH = level-staggered
    #               TH = level
    # Right now I don't deal with this, just say are close enough and plot the 
    # bottom x levels
    b_levels = 12
    PH_b = TPH[:b_levels]
    TH_b = TTH[:b_levels]
    N_SLV_b = N_SLV[:b_levels]
    S_SLV_b = S_SLV[:b_levels]
    # Consisten chech: can't have any negative numbers
    S_SLV_b[S_SLV_b<0]=0
    N_SLV_b[N_SLV_b<0]=0    
    
    
    LON2D = LON*np.ones_like(PH_b) #for contour plotting
    LAT2D = LAT*np.ones_like(PH_b) #for contour plotting
    
    # Plot an image of the cross section
    fig = plt.figure(1,figsize=(16,9))
    ax = plt.subplot(1,1,1)
    #ax.set_axis_bgcolor('black')

    colors = [(0,1,0,c) for c in np.linspace(0,1,100)]
    cmapred = mcolors.LinearSegmentedColormap.from_list('mycmap', colors, N=5)
    colors = [(1,.6,0,c) for c in np.linspace(0,1,100)]
    cmapblue = mcolors.LinearSegmentedColormap.from_list('mycmap', colors, N=5)
    
  
    
    #plt.pcolormesh(LAT,PH_b,N_SLV_b,cmap=cmapred)  #overlapping boxes causes lines between boxes, use something else like contour or imshow
    #plt.pcolormesh(LAT,PH_b,S_SLV_b,cmap=cmapblue)
    plt.contourf(LAT2D,PH_b,N_SLV_b,cmap=cmapred,levels=np.arange(0.0,1.26,.25))
    cbar = plt.colorbar(pad=0.01,ticks=np.arange(0.,1.1,.25))    
    plt.contourf(LAT2D,PH_b,S_SLV_b,cmap=cmapblue,levels=np.arange(0.0,1.26,.25))
        
    
    plt.clim(0,1.1)
    cbar.set_label('Tracer Units')    
    
    
    CS = plt.contour(LAT2D,PH_b,TH_b,
                colors='k',
                levels=np.arange(int(np.min(TH_b)),int(np.max(TH_b)),1),
                widths=.25)
    plt.clabel(CS, inline=1, fontsize=9,fmt='%1.0f')
    
    
    plt.xlim([LAT[0],LAT[-1]])
    plt.ylim([1000,3500])
    plt.xlabel('Latitude')
    plt.ylabel('Geopotential Height (m)')
    plt.title(time_str+'\n'+time_str_local, bbox=dict(facecolor='white', alpha=0.65),\
    			x=0.5,y=.90,weight = 'demibold',style='oblique', \
    			stretch='normal', family='sans-serif')

    plt.fill_between(LAT,0,HGT,color="black")
    
    
    plt.savefig(FIGDIR+time_save+'.png', bbox_inches='tight')
    print 'Saved', str_time

# Plot figure showing where cross section is located in domain
plt.figure(2)

bot_left_lat  = np.min(XLAT)
bot_left_lon  = np.min(XLON)
top_right_lat = np.max(XLAT)
top_right_lon = np.max(XLON)

## Map in cylindrical projection (data points may apear skewed because WRF runs in LCC projection)
m = Basemap(resolution='i',area_thresh=10000.,projection='cyl',\
    llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
    urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)

m.drawstates()
water = ncW.variables['LAKEMASK'][0]
m.contour(XLON,XLAT,water,levels=[0])
m.drawgreatcircle(LON[0], LAT[0],LON[-1], LAT[-1], color='r', linewidth='4')
m.contourf(XLON,XLAT,XHGT,cmap='binary')
plt.savefig(FIGDIR+'Xsection.png', bbox_inches='tight',dpi=300)



