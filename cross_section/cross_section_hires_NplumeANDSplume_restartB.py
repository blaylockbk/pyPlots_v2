# Brian Blaylock
# 14 December 2015

# WRF Cross Section of potential temperature and tracer plumes
# This uses the high resolution output file, auxhis24 which I have 
# outputting at 10 minute intervals, except.....

## Ok, this is a little different. I forgot to output the fields every
## 10 mins, so I have to use the standard wrfout files to plot
## hours 18, 19, and 20


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
from functions_domains_models import *
import matplotlib as mpl
from matplotlib.ticker import AutoMinorLocator, MultipleLocator, FormatStrFormatter


# Set directories
#WRFDIR = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_spinup/DATA/FULL_RUN_June14-19/'
FIGDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/crosssection/spinup/bothplumes/restartB/'
if not os.path.exists(FIGDIR):
    os.makedirs(FIGDIR)

RESTARTDIR = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_spinup/DATA/RESTART_June18-17:00--18-23:00/'
RESTARTAUX = 'auxhist24_d02_2015-06-18_17:00:00'

# create a range of times at an interval of the timestep in minutes. auxhis24 has a 10 minute output
#model_start = datetime(2015,6,14,0)
#timeout_mins=10 # how frequently the output file writes in minutes
#numhours=127
#DateList = [model_start + timedelta(hours=x) for x in np.arange(0, numhours,timeout_mins/60.)]

# Don't really want to make plots for every time, just starting on the 18th
#startplot_index = int(144*4*(17/24))  # add one day = index 144 ## Oh, I need to use nc.variables['Times']
# Heck, just plot everything for now...

domain = 'd02'

# Open WRF file, High-Resolution output 
#The auxhisXX file has the high resolution output. I use 24 for ten minute output of geopotential, potential temperature, and plumes    
#AUXfile = 'auxhist24_%s_%s-%s-%s_%s:%s:%s' % (domain,str(model_start.year),str(model_start.month).zfill(2),str(model_start.day).zfill(2),str(model_start.hour).zfill(2),str(model_start.minute).zfill(2),str(model_start.second).zfill(2))
# Still use a WRF file to get static data


hours = ['18','19','20','21','22','23']

for hour in hours:
    WRFfile = 'wrfout_d02_2015-06-18_%s:00:00' % hour

    nc = netcdf.netcdf_file(RESTARTDIR+WRFfile,'r')

    """
    plt.rc("figure.subplot", left = 0)
    plt.rc("figure.subplot", right = 1)
    plt.rc("figure.subplot", bottom = 0)
    plt.rc("figure.subplot", top = 1)
    """
    
    #for t in np.arange(startplot_index,int(np.shape(nc.variables['Times'])[0])):
        ### Process Data  
    
        
    #str_time = DateList[t].strftime('%Y%b%d-%H%M')

    time = ''.join(nc.variables['Times'][0])
    
    #print 'check that times are matched'
    #print ''.join(nc.variables['Times'][t])
    #print ''.join(ncRESTART.variables['Times'][t-648])
    
    time_dt = datetime.strptime(time,'%Y-%m-%d_%H:%M:%S')
    time_str= datetime.strftime(time_dt,'%Y-%m-%d %H:%M:%S UTC')
    #time_str_local=datetime.strftime(time_dt-timedelta(hours=6),'%Y-%m-%d %H:%M:%S MDT')
    time_save=datetime.strftime(time_dt,'%Y%b%d-%H%M')
    
    # Set the cross section values (the grid points we want)
    lat = np.arange(190,230)
    lon = np.arange(228,229)    
    
    ### We want to plot the 3D vertical velocity, but I only have these fields at the 
    ### top of the hour. So, if time_dt is at the top of the hour (minute = 0) then 
    ### grab the wrfout file for that time and the vertical wind component W
    
    W = nc.variables['W'][0][:,lat,lon]
    Wl = nc.variables['W'][0][:,lat,lon-1]
    Wr = nc.variables['W'][0][:,lat,lon+1]
    Wavg = ((W+Wl+Wr)/3)

    # Read in data from cross section 
    XLAT = nc.variables['XLAT'][0]
    XLON = nc.variables['XLONG'][0]
    XHGT = nc.variables['HGT'][0]
    
    #                         [time,lat,lon]
    LAT = nc.variables['XLAT'][0,lat,lon]    # Latitude
    LON = nc.variables['XLONG'][0,lat,lon]   # Longitude
    HGT = nc.variables['HGT'][0,lat,lon]    
    
    #                       [time][level-stag,lat,lon]
    PH  = nc.variables['PH'][0][:,lat,lon]   # perturbation geopotential  [m2 s-2]
    PHB = nc.variables['PHB'][0][:,lat,lon]  # base state geopotential    [m2 s-2]
    TPH = (PH+PHB)/9.81               # Total Geopotential Height  [meters]

    # Average the three wide potential temperature
    #                      [time][level,lat,lon]
    # theta center    
    TH  = nc.variables['T'][0][:,lat,lon]    # Perturbation potential tempertaure [K]
    TTH = TH+300                          # Total Potential Temperature (theta) [K]

    # theta left
    THl  = nc.variables['T'][0][:,lat,lon-1]    # Perturbation potential tempertaure [K]
    TTHl = TH+300                          # Total Potential Temperature (theta) [K]
    # theta right    
    THr  = nc.variables['T'][0][:,lat,lon+1]    # Perturbation potential tempertaure [K]
    TTHr = TH+300                          # Total Potential Temperature (theta) [K]
    
    TTHavg = (TTH+TTHl+TTHr)/3.
    TTH = TTHavg

    
    # Plume Data
    N_SLV   = nc.variables['N_SLV_rstB'][0][:,lat,lon]
    N_SLV_l = nc.variables['N_SLV_rstB'][0][:,lat,lon-1]
    N_SLV_r = nc.variables['N_SLV_rstB'][0][:,lat,lon+1] 
    S_SLV   = nc.variables['S_SLV_rstB'][0][:,lat,lon]
    S_SLV_l = nc.variables['S_SLV_rstB'][0][:,lat,lon-1]
    S_SLV_r = nc.variables['S_SLV_rstB'][0][:,lat,lon+1]  
    
    # add up the tracer slices (this one is three km thick)
    N_SLV = N_SLV+N_SLV_l+N_SLV_r    
    S_SLV = S_SLV+S_SLV_l+S_SLV_r        
    
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
    Wavg = Wavg[:b_levels]
        
    #S_SLV_b = S_SLV[:b_levels]
    # Consisten chech: can't have any negative numbers
    #S_SLV_b[S_SLV_b<0]=0
    N_SLV_b[N_SLV_b<0]=0    
    S_SLV_b[S_SLV_b<0]=0
    
    LON2D = LON*np.ones_like(PH_b) #for contour plotting
    LAT2D = LAT*np.ones_like(PH_b) #for contour plotting
    
    
    #ax.set_axis_bgcolor('black')

    colors = [(1,0,0,c) for c in np.linspace(0,1,100)]
    cmapred = mcolors.LinearSegmentedColormap.from_list('mycmap', colors, N=15)
    colors = [(0,0,1,c) for c in np.linspace(0,1,100)]
    cmapblue = mcolors.LinearSegmentedColormap.from_list('mycmap', colors, N=15)





    ### Create Plots
    plt.cla()
    plt.clf()
    plt.close()
    
    
    # Set some standard font sizes    
    tick_font = 8
    label_font = 10 
    
    mpl.rcParams['xtick.labelsize'] = tick_font
    mpl.rcParams['ytick.labelsize'] = tick_font 
    

    # Plot an image of the cross section
    #aspect_ratio = np.array([3,2])*6
    
    width=8.4
    height= 2.5    
    
    fig = plt.subplots(1,2,figsize=(width,height))
    plot = plt.subplot(1,2,1)
    #plt.suptitle(time_dt.strftime('%d %B %Y %H%M UTC'),fontsize=label_font)
    
    
  
    
    #plt.pcolormesh(LAT,PH_b,N_SLV_b,cmap=cmapred)  #overlapping boxes causes lines between boxes, use something else like contour or imshow
    #plt.pcolormesh(LAT,PH_b,S_SLV_b,cmap=cmapblue)
    #plt.contourf(LAT2D,PH_b,N_SLV_b,cmap=cmapred,levels=np.arange(0.0,1.26,.25))
    
    

    
    
    plt.contourf(LAT2D,PH_b,S_SLV_b,
                 cmap=cmapblue,
                 levels=np.arange(0.0,3.26,.25),
                 extend='max')
    cbar = plt.colorbar(orientation='horizontal',
                        pad=0.23,
                        ticks=np.arange(0.,3.26,.5))
    plt.clim(0,3.26)
    cbar.set_label('Tracer Count',fontsize=label_font)    
    
    
    CS = plt.contour(LAT2D,PH_b,TH_b,
                colors='k',
                levels=np.arange(int(np.min(TH_b)),int(np.max(TH_b)),.5),
                linewidths=.6)
    plt.clabel(CS, CS.levels[::2],
               inline=1,
               inline_spacing=.1,
               fontsize=7,fmt = '%1.0f')
    
    ## ----- Vertical Wind Speed-----------------------------------------------    
    ## if we are at the top of the hour, plot the vertical wind component
    if time_dt.minute==0:
        contour_interval = .5
        contour_levels = np.arange(-5,5,contour_interval) # negative contours
        contour_levels = np.delete(contour_levels,10)   # delete the zero level
        
        #print contour_levels        
        
        WW = plt.contour(LAT2D,PH_b,Wavg,
                         colors='darkblue',
                         levels=contour_levels,
                         linewidths=1.2)
    ## ----- Vertical Wind Speed-----------------------------------------------    
    
    
    plt.xlim([LAT[0],LAT[-1]])
    plt.xticks([40.5,40.6,40.7, 40.8])
    plt.ylim([1000,3000])
    plt.xlabel('Latitude ('+u'\N{DEGREE SIGN}'+'N)',fontsize=label_font)
    plt.ylabel('Height (m)',fontsize=label_font)
    
    # Adjust ticks ticks
    plot.xaxis.set_minor_locator(MultipleLocator(1))
    plot.yaxis.set_minor_locator(MultipleLocator(100))
    plot.tick_params(axis='x', which='major', color='w', top=False)
    plot.tick_params(axis='x', which='minor', color='w', top=False)
    plot.tick_params(axis='y', which='major', color='k')
    plot.tick_params(axis='y', which='minor', color='k')
    
    #plt.title(time_str+'\n'+time_str_local, bbox=dict(facecolor='white', alpha=0.65),\
    #			x=0.5,y=1.05,weight = 'demibold',style='oblique', \
    #			stretch='normal', family='sans-serif')


    plt.fill_between(LAT,0,HGT,color="black")
    plt.text(40.47,1075,'A',color='w',fontsize=tick_font)
    plt.text(40.801,1075,'B',color='w',fontsize=tick_font)    

    
    
    
##Subplot 2####################################################################################################### Subplot 2    
    plot = plt.subplot(1,2,2)
    
    ### Tracer Plume    
    plt.contourf(LAT2D,PH_b,N_SLV_b,
                 cmap=cmapred,
                 levels=np.arange(0.0,3.26,.25),
                 extend='max')
    cbar = plt.colorbar(orientation='horizontal',
                        pad=0.23,
                        ticks=np.arange(0.,3.26,.5))
    plt.clim(0,3.26)
    cbar.set_label('Tracer Count',fontsize=label_font)    
    
    
    CS = plt.contour(LAT2D,PH_b,TH_b,
                colors='k',
                levels=np.arange(int(np.min(TH_b)),int(np.max(TH_b)),.5),
                linewidths=.6)
    plt.clabel(CS, CS.levels[::2],
               inline=1,
               inline_spacing=.1,
               fontsize=7,fmt = '%1.0f')
    
    ## ----- Vertical Wind Speed-----------------------------------------------    
    ## if we are at the top of the hour, plot the vertical wind component
    if time_dt.minute==0:
        contour_interval = .5
        contour_levels = np.arange(-5,5,contour_interval) # negative contours
        contour_levels = np.delete(contour_levels,10)   # delete the zero level
        
        #print contour_levels        
        
        WW = plt.contour(LAT2D,PH_b,Wavg,
                         colors='darkblue',
                         levels=contour_levels,
                         linewidths=1.2)
    ## ----- Vertical Wind Speed-----------------------------------------------    
    
    
    plt.xlim([LAT[0],LAT[-1]])
    plt.xticks([40.5,40.6,40.7, 40.8])
    plt.ylim([1000,3000])
    plt.yticks([])
    plt.xlabel('Latitude ('+u'\N{DEGREE SIGN}'+'N)',fontsize=label_font)
    #plt.ylabel('Geopotential Height (m)',fontsize=label_font)
    
    # Adjust ticks ticks
    plot.xaxis.set_minor_locator(MultipleLocator(1))
    plot.yaxis.set_minor_locator(MultipleLocator(100))
    plot.tick_params(axis='x', which='major', color='w', top=False)
    plot.tick_params(axis='x', which='minor', color='w', top=False)
    plot.tick_params(axis='y', which='major', color='k')
    plot.tick_params(axis='y', which='minor', color='k')
    
    #plt.title(time_str+'\n'+time_str_local, bbox=dict(facecolor='white', alpha=0.65),\
    #			x=0.5,y=1.05,weight = 'demibold',style='oblique', \
    #			stretch='normal', family='sans-serif')


    plt.fill_between(LAT,0,HGT,color="black")
    plt.text(40.47,1075,'A',color='w',fontsize=tick_font)
    plt.text(40.801,1075,'B',color='w',fontsize=tick_font) 
######################################################################################################### Subplot 2    
    
    fig[0].subplots_adjust(wspace=0.02) 
    fig[0].subplots_adjust(hspace=0.02)    
    
    #plt.show()
    #break    
    
    plt.savefig(FIGDIR+time_save+'.png', bbox_inches='tight',dpi=500)
    print 'Saved', time_str, 'max plume', np.max(N_SLV_b)




# Plot figure showing where cross section is located in domain
plt.figure(2)

bot_left_lat  = np.min(XLAT)
bot_left_lon  = np.min(XLON)
top_right_lat = np.max(XLAT)
top_right_lon = np.max(XLON)

domain = get_domain('salt_lake_valley')
top_right_lat = domain['top_right_lat']+.1
top_right_lon = domain['top_right_lon']-.1
bot_left_lat = domain['bot_left_lat']
bot_left_lon = domain['bot_left_lon']

## Map in cylindrical projection (data points may apear skewed because WRF runs in LCC projection)
m = Basemap(resolution='i',area_thresh=10000.,projection='cyl',\
    llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
    urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)

m.drawstates()
spat= 'auxhist23_d02_2015-06-17_00:00:00'
directory = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_urbanforest/DATA/more_trees/'
nc_spatial = netcdf.netcdf_file(directory+spat,'r')
landmask = nc_spatial.variables['LANDMASK'][0,:,:]
m.contour(XLON,XLAT,landmask, [0,1], linewidths=1.5, colors="b")
m.drawgreatcircle(LON[0], LAT[0],LON[-1], LAT[-1], color='k', linewidth='4')
m.contourf(XLON,XLAT,XHGT,levels=np.arange(1000,4000,500),cmap=plt.get_cmap('binary'))

# add location of tracers
tracerS  = ncW.variables['S_SLV'][0][0]
tracerN  = ncW.variables['N_SLV'][0][0]
latP     = ncW.variables['XLAT'][0]
lonP     = ncW.variables['XLONG'][0]
x,y = m(lonP,latP)
plt.pcolormesh(x,y,tracerS,cmap=cmapblue)
plt.pcolormesh(x,y,tracerN,cmap=cmapred)

plt.savefig(FIGDIR+'Xsection.png', bbox_inches='tight',dpi=500)



