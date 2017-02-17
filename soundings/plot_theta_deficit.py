# Brian Blaylock
# February 7, 2017          Rachel and I are doing a puzzle together tonight :)

"""
Plots the potential temperature from the HRRR at the surface and 700 mb and
compares that with the values from the SLC balloon.
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

import matplotlib as mpl
## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [12, 8]
mpl.rcParams['figure.titlesize'] = 13
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['legend.fontsize'] = 10
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'


HRRR = np.genfromtxt('UWFPS_inversion_SLC_HRRR_points.csv',
                     delimiter=',',
                     names=True,
                     dtype=None)

f12 = np.genfromtxt('UWFPS_inversion_SLC_HRRR-f12_points.csv',
                     delimiter=',',
                     names=True,
                     dtype=None)

Balloon = np.genfromtxt('UWFPS_inversion_SLC_balloon.csv',
                     delimiter=',',
                     names=True,
                     dtype=None)


HRRR_datetime = HRRR['datetime']
HRRR_datetime = np.array([datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in HRRR_datetime])
HRRR_sfc_theta = HRRR['SLC_sfc_theta']
HRRR_700_theta = HRRR['SLC_700_theta']

f12_sfc_theta = f12['SLC_sfc_theta']
f12_700_theta = f12['SLC_700_theta']

Balloon_datetime = Balloon['datetime']
Balloon_datetime = np.array([datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in Balloon_datetime])
Balloon_sfc_theta = Balloon['SLC_sfc_theta']
Balloon_700_theta = Balloon['SLC_700_theta']

fig, [ax1, ax2] = plt.subplots(2,1)

# First plot the observations
ax1.plot(HRRR_datetime, HRRR_700_theta, color='r', lw=3, label='700 hPa')
ax1.plot(HRRR_datetime, HRRR_sfc_theta, color='b', lw=3, label='Surface')

ax1.plot(HRRR_datetime, f12_700_theta, color='gold', label='f12')
ax1.plot(HRRR_datetime, f12_sfc_theta, color='gold')

ax1.scatter(Balloon_datetime, Balloon_700_theta, s=50, color='k', label='Balloon', zorder=100)
ax1.scatter(Balloon_datetime, Balloon_sfc_theta, s=50, color='k', zorder=100)

ax1.set_ylabel('Potential Temperature')
ax1.legend(loc=4)
ax1.grid()

# Then plot the difference
ax2.plot(HRRR_datetime, HRRR_700_theta-HRRR_sfc_theta, color='b', lw=3, label='HRRR')
ax2.plot(HRRR_datetime, f12_700_theta-f12_sfc_theta, color='gold', label='f12')
ax2.scatter(Balloon_datetime, Balloon_700_theta-Balloon_sfc_theta, s=50, color='k', label='Balloon', zorder=100)


ax2.set_ylabel('Surface Temperature Deficit')
ax2.set_ylim([0,35])
ax2.legend(loc=1)
ax2.grid()

plt.suptitle('Inversion strength at SLC')

plt.savefig('inversion_strength')
