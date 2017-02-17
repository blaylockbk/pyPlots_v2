# Brian Blaylock
# February 16, 2017                                       Bowling Night

"""
Plot time-height series of layer energy (CAPE/CIN) and LCL heights from HRRR
bufr data.
    - CAPE of each layer for parcels lifed at each level
    - Sum energy for parcel at each level to rise to some target height
    - how close is the levels LCL temp and pressure to the level's environment
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2') # CHPC
sys.path.append('B:/pyBKB_v2')                                       # PC
from BB_wx_calcs.Parcels_LCL_CAPE import LCL_and_Parcels_from_bufr

from datetime import datetime, timedelta
import os
import numpy as np
import numpy.ma as ma

import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.ticker import MultipleLocator
import matplotlib as mpl
## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [12, 4]
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

# ======================================================
#                Stuff you can change :)
# ======================================================
# Save directory
BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
SAVE = BASE + 'public_html/PhD/UWFPS_2017/time-height/CAPE/jan-feb/'
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = BASE + 'public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

# bufr station ID
stn = 'kslc'

# start and end date
#DATE = datetime(2017, 1, 23, 0)
#DATEe = datetime(2017, 2, 5, 1)
DATE = datetime(2017, 1, 1, 0)
DATEe = datetime(2017, 2, 17, 0)

# meters to raise a parcel (find level nearest this increase)
target_rise = 700

# HRRR bufr forcast hour
fxx = 0

# top layer you want (you don't really need to get all 50 layers, now do you)
top_layer = 15

# ======================================================
#       Get data and store for each HRRR hour
# ======================================================
date_list = np.array([])
dates_skipped = np.array([])

# initialize a dictionary to store calculations from each layer
layer = {} # to clarify, I call bufr points levels, and mean CAPE points layers

while DATE < DATEe:
    # Loop for each hour...
    try:
        # Get the CAPE and hght from the bufr data for the hour
        data = LCL_and_Parcels_from_bufr(DATE, fxx=fxx)
        date_list = np.append(date_list, DATE)

    except:
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        print "!  Skipping", DATE, "     !"
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        dates_skipped = np.append(dates_skipped, DATE)
        DATE += timedelta(hours=1)
        continue

    try:
        # Try to stack the array, if it doesn't work then the variable hasn't
        # been created yet.
        for i in range(0, top_layer):
            layer[i]['CAPE'] = np.column_stack([layer[i]['CAPE'], data['mean CAPE'][i]['CAPE']])
            layer[i]['hght'] = np.column_stack([layer[i]['hght'], data['mean CAPE'][i]['hght']])
            layer[i]['pres'] = np.column_stack([layer[i]['pres'], data['mean CAPE'][i]['pres']])

        theta = np.column_stack([theta, data['bufr']['theta']])
        lcl = np.column_stack([lcl, data['LCL']['temp']])
        plcl = np.column_stack([plcl, data['LCL']['pres']])
        temp = np.column_stack([temp, data['bufr']['temp']])
        hght = np.column_stack([hght, data['bufr']['hght']])
        pres = np.column_stack([pres, data['bufr']['pres']])

    except:
        # If you get here, then it looks like the variable hasn't been created
        # yet, so create it.
        for i in range(0, top_layer):
            CAPE = data['mean CAPE'][i]['CAPE'] # zero is the surface parcel
            hght = data['mean CAPE'][i]['hght']
            pres = data['mean CAPE'][i]['pres']
            layer[i] = {'CAPE':CAPE, 'hght':hght, 'pres':pres}

        theta = data['bufr']['theta']
        lcl = data['LCL']['temp']
        plcl = data['LCL']['pres']
        temp = data['bufr']['temp']
        hght = data['bufr']['hght']
        pres = data['bufr']['pres']

    print 'Got it:', DATE
    DATE += timedelta(hours=1)

# mask out any nan values that prevent plotting with pcolormesh
for i in layer.keys():
    lCAPE = layer[i]['CAPE'] # layerCAPE
    layer[i]['CAPE'] = ma.masked_where(np.isnan(lCAPE), lCAPE)

# Because the contour funciton doesn't like dates, we must convert dates
# to some other happy x axis number. Then the x axis dates can be formatted.
# Note: make 2D dates array for each array size (CAPE arrays have one less than
# the bufr data becuase CAPE data is for the "layers" while bufr sounding data
# is for the "level".
x = matplotlib.dates.date2num(date_list)
x2D_layer = x*np.ones_like(layer[0]['CAPE'])
x2D = x*np.ones_like(hght)


# === Begin Plots ===

#==============================================================================
#          Plot: CAPE of each layer for parcel liftd from the level.
#==============================================================================
for i in layer.keys():
    fig, ax = plt.subplots(1, 1)

    # CAPE shading
    cmesh = plt.pcolormesh(x2D_layer, layer[i]['hght'], layer[i]['CAPE'],
                           cmap='PuOr_r',
                           vmax=150,
                           vmin=-150)

    # Potential temperature contour
    levels = np.arange(200, 400, 5)
    conto = plt.contour(x2D, hght, theta,
                        colors='k',
                        levels=levels)

    # Format the dates on the Axis
    date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
    ax.xaxis.set_major_formatter(date_formatter)

    # Label y axis starting with the surface tick
    sfc_height = hght.min()
    yticks = range(1000, 5000, 500)
    yticks.extend([sfc_height])
    plt.yticks(yticks)
    plt.ylabel('Height (m)')

    # colorbar
    cb = plt.colorbar(cmesh,
                      orientation='vertical',
                      shrink=.7,
                      pad=.02,
                      ticks=range(-200, 201, 50),
                      extend="both")
    cb.set_label(r'Layer CAPE (J kg$\mathregular{^{-1}}$)')

    # Visually simulate the ground by filling a black area at the bottom
    plt.ylim([sfc_height-100, 4000])
    plt.fill_between([date_list[0], date_list[-1]], sfc_height, color="black")

    # Make ticks on ground white, otherwise they wont show on black "ground"
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(100))
    ax.tick_params(axis='x', which='major', color='w', top=False)
    ax.tick_params(axis='x', which='minor', color='w', top=False)
    ax.tick_params(axis='y', which='major', color='k')
    ax.tick_params(axis='y', which='minor', color='k')

    # identify the parcel's initial height and pressure
    parcel_idx = i
    parcel_hgt = layer[i]['hght'][:, 0][parcel_idx]
    parcel_prs = layer[i]['pres'][:, 0][parcel_idx]
    plt.title(stn.upper() + ' HRRR bufr soundings: Layer CAPE and Potential Temperature\n Parcel Level: %2d, Pres: %.1f hPa, Hght: %.1f m' \
              % (i, parcel_prs, parcel_hgt))

    plt.savefig(SAVE+stn+'_hrrr_CAPE_lvl_%02d' % i)
    plt.close()

    #==========================================================================
    #   Plot: Energy required to lift this parcel level up target_rise meters
    #==========================================================================
    plt.figure()
    # The number of levels to sum is dependent on the height.
    # Determine approximatly how many layers up gives the target_rise increase.
    hgt_diff = layer[i]['hght'][:, 0][i:] - layer[i]['hght'][:, 0][i]
    closest_rise = np.argmin(np.abs(hgt_diff-target_rise))
    hgt_increase = hgt_diff[closest_rise]

    sum_CAPE_layers = np.sum(layer[i]['CAPE'].data[i:i+closest_rise+1], axis=0)
    sum_hgt_layers = layer[i]['hght'][i]

    # Save the sum_CAPE_layers array
    try:
        # Try to stack the array, if it doens't work then the variable hasn't
        # been created yet.
        sum_CAPE = np.vstack([sum_CAPE_layers, sum_CAPE])
        sum_hgt = np.vstack([sum_hgt_layers, sum_hgt])
    except:
        # It looks like the variable hasn't been created yet, so create it.
        sum_CAPE = sum_CAPE_layers
        sum_hgt = sum_hgt_layers

    # Sum Energy
    plt.plot(date_list, sum_CAPE_layers,
             color="k",
             lw='3')

    # Zero energy line to spearate positive and negative area visually
    plt.axhline(y=0, ls='--', lw=2, color='grey')

    # Share the area between
    plt.fill_between(date_list, np.zeros(len(sum_CAPE_layers)), sum_CAPE_layers,
                     where=sum_CAPE_layers >= np.zeros(len(sum_CAPE_layers)),
                     facecolor='orange',
                     alpha=.5,
                     interpolate=True)
    plt.fill_between(date_list, np.zeros(len(sum_CAPE_layers)), sum_CAPE_layers,
                     where=sum_CAPE_layers <= np.zeros(len(sum_CAPE_layers)),
                     facecolor='mediumpurple',
                     alpha=.5,
                     interpolate=True)

    # Labels and save
    plt.ylabel(r'Energy (J kg$\mathregular{^{-1}}$)')
    plt.title('Energy of level %2d parcel when lifted %.1f  m (target rise: %d)' \
              % (i, hgt_increase, target_rise))
    plt.ylim([-400, 200])

    plt.savefig(SAVE+stn+'_hrrr_lvl_%02d_engergy_rise_%dm' % (i, target_rise))
    plt.close()
    print 'plotted: parcel level', i

#==============================================================================
#            Plot: Total energy of parcels lifted to target level
#==============================================================================
fig, ax = plt.subplots(1, 1)

# Shaded energy
cmesh = plt.pcolormesh(date_list, sum_hgt, sum_CAPE,
                       cmap='PuOr_r',
                       vmax=200,
                       vmin=-200)

# Potential temperature contours
levels = np.arange(200, 400, 5)
conto = plt.contour(x2D, hght, theta,
                    colors='k',
                    levels=levels)

# Format the dates on the Axis
date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
ax.xaxis.set_major_formatter(date_formatter)

# Label y axis starting with the surface tick
sfc_height = hght.min()
yticks = range(1000, 5000, 500)
yticks.extend([sfc_height])
plt.yticks(yticks)
plt.ylabel('Height (m)')

# colorbar
cb = plt.colorbar(cmesh,
                  orientation='vertical',
                  shrink=.7,
                  pad=.02,
                  ticks=range(-200, 201, 50),
                  extend="both")
cb.set_label('Total Energy (J kg$\mathregular{^{-1}}$)')

# Visually simulate the ground by filling a black area at the bottom
plt.ylim([sfc_height-100, 4000])
plt.fill_between([date_list[0], date_list[-1]], sfc_height, color="black")

# Make ticks on ground white, otherwise they wont show up on black
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

# Title and save
plt.title(stn.upper() + ' HRRR bufr soundings: parcel energy when lifted %d m' % (target_rise))

plt.savefig(SAVE+stn+'_hrrr_energyLift_%dm' % target_rise)
plt.close()

#==============================================================================
#     Plot: how near the environment temp is to the LCL temp for each level
#==============================================================================
# I like to think this plots how close a parcel at each level is to saturation
# Blue is for "blue sky" and white means it's "almost" cloudy
fig, ax = plt.subplots(1, 1)

# How close is the LCL temperature to the envrionmental temperature
Tdiff = lcl-temp

# Shaded Tdiff
cmesh = plt.pcolormesh(x2D, hght, Tdiff,
                       cmap='Blues_r',
                       vmax=0,
                       vmin=-10)

# Potential temperature contours
levels = np.arange(200, 400, 5)
conto = plt.contour(x2D, hght, theta,
                    colors='k',
                    levels=levels)

# Format the dates on the Axis
date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
ax.xaxis.set_major_formatter(date_formatter)

# Label y axis starting with the surface tick
sfc_height = hght.min()
yticks = range(1000, 5000, 500)
yticks.extend([sfc_height])
plt.yticks(yticks)
plt.ylabel('Height (m)')

# colorbar
cb = plt.colorbar(cmesh,
                  orientation='vertical',
                  shrink=.7,
                  pad=.02,
                  ticks=range(-10, 1, 2),
                  extend="min")
cb.set_label('TempLCL - TempLevel (C)')

# Visually simulate the ground by filling a black area at the bottom
plt.ylim([sfc_height-100, 4000])
plt.fill_between([date_list[0], date_list[-1]], sfc_height, color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')


# Title and save
plt.title(stn.upper() + ' HRRR bufr soundings: TempLCL - TempLevel and Potential Temperature')

plt.savefig(SAVE+stn+'_hrrr_LCL-T-diff_theta')


#==============================================================================
#  Plot: how near the environment pressure is to the LCL temp for each level
#==============================================================================
# I like to think this plots how close a parcel at each level is to saturation.
# As before, Blue is for "blue sky" and white means it's "almost" cloudy
fig, ax = plt.subplots(1, 1)

# How close is the LCL pressure to the envrionmental pressure
Pdiff = plcl-pres

# Shadded Pdiff
cmesh = plt.pcolormesh(x2D, hght, Pdiff,
                       cmap='Blues_r',
                       vmax=0,
                       vmin=-100)

# Potential temperature contours
levels = np.arange(200, 400, 5)
conto = plt.contour(x2D, hght, theta,
                    colors='k',
                    levels=levels)

# Format the dates on the Axis
date_formatter = matplotlib.dates.DateFormatter('%b-%d\n%Y')
ax.xaxis.set_major_formatter(date_formatter)

# Label y axis starting with the surface tick
sfc_height = hght.min()
yticks = range(1000, 5000, 500)
yticks.extend([sfc_height])
plt.yticks(yticks)
plt.ylabel('Height (m)')

# colorbar
cb = plt.colorbar(cmesh,
                  orientation='vertical',
                  shrink=.7,
                  pad=.02,
                  ticks=range(-90, 1, 30),
                  extend="min")
cb.set_label('PresLCL - PresLevel (hPa)')

# Visually simulate the ground by filling a black area at bottom
plt.ylim([sfc_height-100, 4000])
plt.fill_between([date_list[0], date_list[-1]], sfc_height, color="black")

# Make ticks on ground white, otherwise they wont show up
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(100))
ax.tick_params(axis='x', which='major', color='w', top=False)
ax.tick_params(axis='x', which='minor', color='w', top=False)
ax.tick_params(axis='y', which='major', color='k')
ax.tick_params(axis='y', which='minor', color='k')

# Title and save
plt.title(stn.upper() + ' HRRR bufr soundings: PresLCL - PresLevel and Potential Temperature')

plt.savefig(SAVE+stn+'_hrrr_LCL-P-diff_theta')
