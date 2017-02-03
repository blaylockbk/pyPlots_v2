# Brian Blaylock
# 22 Novebmer 2016
# MS Series -- Plots from my Master's Research

"""
Plots vertical profile in three subplots:
    1. Potential Temperature
    2. Mixing Ratio
    3. Wind Vector

With data from:
    KSL
    HRRR analysis
    HRRR 1-hr forecast
    WRF Output
"""


import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator, FormatStrFormatter
style_path = '/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/BB_mplstyle/'
plt.style.use(style_path+'publications.mplstyle')
plt.style.use([style_path+'publications.mplstyle',
               style_path+'width_100.mplstyle',
               style_path+'dpi_high.mplstyle']
             )

from datetime import datetime

import os
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
sys.path.append('B:/pyBKB_v2/')
from BB_data.data_manager import get_wyoming_sounding
from BB_WRF.WRF_timeseries import get_vert_data
from BB_wx_calcs.thermodynamics import TempPress_to_PotTemp, DwptPress_to_MixRatio
import BB_wx_calcs.wind as wind_calcs 

import numpy as np


DATE = datetime(2015, 6, 19, 0)
date_save = DATE.strftime('%Y%m%d-%H%M') 

# Get SLC sounding for Salt Lake City
balloon = get_wyoming_sounding(DATE)

# Get WRF from TS list profile data
station = 'KSLC'
wrf_dir = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.8.1_MYNN/DATA/'
tsfile = station + '.d02.TS'
model_start = datetime(2015, 6, 14, 0)
wrf = get_vert_data(wrf_dir+tsfile,model_start,DATE)

# Get HRRR analysis profile from *modified* BUFR file 
# (modified so all data was on one row for easy reading)
hrrr_file = 'kslc_' + DATE.strftime('%Y%m%d%H') + '.txt'
HRRR = np.genfromtxt(hrrr_file, delimiter=' ', names=True)
HRRR_theta = TempPress_to_PotTemp(HRRR['TMPC'], HRRR['PRES'])
HRRR_u, HRRR_v = wind_calcs.wind_spddir_to_uv(HRRR['SKNT']*0.51444, HRRR['DRCT'])
HRRR_mixr = DwptPress_to_MixRatio(HRRR['DWPC'], HRRR['PRES'])

# Get HRRR 1-hour forecast
f = 'F01'
hrrr_file = 'kslc_'+datetime(2015,6,18,23).strftime('%Y%m%d%H')+'_'+f+'.txt'
HRRR_f01 = np.genfromtxt(hrrr_file, delimiter=' ', names=True)
HRRR_f01_theta = TempPress_to_PotTemp(HRRR_f01['TMPC'], HRRR_f01['PRES'])
HRRR_f01_u, HRRR_f01_v = wind_calcs.wind_spddir_to_uv(HRRR_f01['SKNT']*0.51444, HRRR_f01['DRCT'])
HRRR_f01_mixr = DwptPress_to_MixRatio(HRRR_f01['DWPC'], HRRR_f01['PRES'])

"""
Create 3 subplots for 
    1. Potential Temperature
    2. Mixing Ratio
    3. Vector Wind
"""
fig, [ax1, ax2, ax3] = plt.subplots(1,3)

ylims = [wrf['PH'][0]-200, 6000]  # Top of graph is approx. 500 mb
yticks = [wrf['PH'][0], 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]

# ---- Subplot 1 -------------------------------------------------------------
plot = plt.subplot(1, 3, 1)
plt.grid()

plt.plot(balloon['theta'], balloon['height'],
         color='b', label='SLC', lw=1.6, zorder=5)
plt.plot(HRRR_theta,HRRR['HGHT'],
         color='r',label='HRRR anlys',lw=.8,zorder=4)  
plt.plot(HRRR_f01_theta,HRRR_f01['HGHT'],
         color='darkgreen',label='HRRR f01',lw=.8,zorder=4)  
plt.plot(wrf['TH'],wrf['PH'],
         color='k',label='WRF',lw=1.2,zorder=4)

plt.xlabel('Potential \nTemperature (K)')
plt.xlim([315, 328])
plt.xticks([312, 316, 320, 324])
plt.ylabel('Height (m)')
plt.ylim(ylims)
plt.yticks(yticks)

legend = plt.legend(loc=2, frameon=True, ncol=1) 
frame = legend.get_frame()
frame.set_edgecolor('white')

plot.xaxis.set_minor_locator(MultipleLocator(1))
plot.yaxis.set_minor_locator(MultipleLocator(100))
plot.tick_params(axis='y', which='major', color='k', right=False)
plot.tick_params(axis='y', which='minor', color='k', right=False)


# ---- Subplot 2 -------------------------------------------------------------
plot = plt.subplot(1,3,2)
plt.grid(zorder=0)

plt.plot(balloon['mixing ratio']*1000, balloon['height'],
         color='b', lw=1.6, zorder=5)
plt.plot(HRRR_mixr, HRRR['HGHT'],
         color='r', lw=.8, zorder=4)    
plt.plot(HRRR_f01_mixr, HRRR_f01['HGHT'],
         color='darkgreen', lw=.8, zorder=4)
plt.plot(wrf['QV']*1000, wrf['PH'],
            color='k', lw=1.2, zorder=4)

plt.xlabel('Mixing Ratio\n(g kg$^-$$^1$)')
plt.xlim([0,13])
plt.xticks([1,3,5,7,9,11,13])
plt.ylim(ylims)
plt.yticks(yticks)
            
plot.xaxis.set_minor_locator(MultipleLocator(1))    
plot.yaxis.set_minor_locator(MultipleLocator(100))    
plot.tick_params(axis='y', which='major', color='k',right=False)
plot.tick_params(axis='y', which='minor', color='k',right=False)  

plt.setp(plot.get_yticklabels(), visible=False)

# ---- Subplot 3 --------------------------------------------------------------
plot = plt.subplot(1,3,3)
plt.grid()

if DATE == datetime(2015,6,18,12):
    wrf_thin = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    HRRR_thin = [0,3,4,5,6,7,8,9,10,11,12,13,14]
    slc_thin = [0,1,4,5,7,8,9,10,11,13,14]
else:
    wrf_thin = [0,2,3,4,5,6,7,8,9,10,11,12,13,14]
    HRRR_thin = [0,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    slc_thin = [0,1,2,3,4,5,6,7,10,11,12,16,17,18,19,20,21]

# SLC
plt.barbs(np.ones(len(balloon['height'][slc_thin]))*1, balloon['height'][slc_thin],
          balloon['u'][slc_thin], balloon['v'][slc_thin],
          color='b',
          length=5.,
          linewidth=.7,
          zorder=4,
          barb_increments=dict(half=1, full=2, flag=10),
          sizes=dict(spacing=0.15, height=0.3, emptybarb=.1))
# HRRR
plt.barbs(np.ones(len(HRRR['HGHT'][HRRR_thin]))*2, HRRR['HGHT'][HRRR_thin],
          HRRR_u[HRRR_thin], HRRR_v[HRRR_thin],
          color='red',
          length=5.,
          linewidth=.7,
          zorder=4,
          barb_increments=dict(half=1, full=2, flag=10),
          sizes=dict(spacing=0.15, height=0.3, emptybarb=.1))

# HRRR f01
plt.barbs(np.ones(len(HRRR_f01['HGHT'][HRRR_thin]))*3, HRRR_f01['HGHT'][HRRR_thin],
          HRRR_f01_u[HRRR_thin], HRRR_f01_v[HRRR_thin],
          color='darkgreen',
          length=5.,
          linewidth=.7,
          zorder=4,
          barb_increments=dict(half=1, full=2, flag=10),
          sizes=dict(spacing=0.15, height=0.3, emptybarb=.1))

# WRF
plt.barbs(np.ones(len(wrf['PH'][wrf_thin]))*4, wrf['PH'][wrf_thin], 
          wrf['UU'][wrf_thin], wrf['VV'][wrf_thin],
            color='k',
            length=5.,
            linewidth=.7,
            zorder=4,
            barb_increments=dict(half=1, full=2, flag=10),
            sizes=dict(spacing=0.15, height=0.3, emptybarb=.1))              

plt.xlabel('\nWind Vector\n(m s$^-$$^1$)')
plt.xticks([0,1,2,3,4,5])
plt.ylim(ylims)
plt.yticks(yticks)   
#plt.xlim([0,5])

plot.yaxis.set_minor_locator(MultipleLocator(100))
plot.tick_params(axis='y', which='major', color='k',right=False)
plot.tick_params(axis='y', which='minor', color='k',right=False) 

plt.setp(plot.get_yticklabels(), visible=False)
plt.setp(plot.get_xticklabels(), visible=False)

# ---- finish work ------------------------------------------------------------
plt.suptitle(DATE)
fig.subplots_adjust(wspace=0.02) 
fig.subplots_adjust(hspace=0.02) 

SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/vertprofile/for_poster/'
if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)

plt.savefig(SAVEDIR + date_save + '.png') 

plt.show(block=False) 