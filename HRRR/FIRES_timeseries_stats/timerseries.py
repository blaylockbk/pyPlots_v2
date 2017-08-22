# Brian Blaylock
# August 3, 2017                 I made blackberry jam with Grandma yesterday

"""
Plot time series of HRRR statistics with MesoWest observations and HRRR forecasts
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from matplotlib.dates import DateFormatter

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
from BB_downloads.HRRR_S3 import point_hrrr_time_series_multi, get_hrrr_variable
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_HRRR.OSG_stats import get_OSG_stats


# Date range
sDATE = datetime(2017, 6, 19)
eDATE = datetime(2017, 6, 27)

# Dictinary of locations
locs = {'BHCU1':{'latitude':37.66296,'longitude':-112.83760}}
MWid = 'BHCU1'

# Get MesoWest data
a = get_mesowest_ts(MWid, sDATE, eDATE, variables='air_temp,wind_speed')

variable = 'TMP:2 m'
var = variable.replace(':','_').replace(' ','_')
# Get HRRR time sereis
h = point_hrrr_time_series_multi(sDATE, eDATE, locs,
                                 variable=variable,
                                 fxx=0, model='hrrr', field='sfc',
                                 area_stats=False,
                                 reduce_CPUs=2,
                                 verbose=True)

# Get HRRR OSG statistics
SS = get_OSG_stats(locs, variable, ['MAX', 'MEAN', 'MIN'],
                   months=[6], hours=range(0,24), extra=True, fxx=0)


# Plot the time series
plt.figure(1, figsize=[12, 6])
plt.title(MWid+': '+var+'\n%s--%s' % (sDATE.strftime('%b %d,%Y'), eDATE.strftime('%b %d,%Y')))
plt.plot(a['DATETIME'], a['air_temp'], lw=3, c='k', label='MesoWest')
plt.plot(h['DATETIME'], h['BHCU1']-273.15, lw=3, c='orange', label='HRRR anlys')

max_stats = [SS['BHCU1']['MAX'][np.where(SS['hour']==d.hour)] for d in h['DATETIME']]
min_stats = [SS['BHCU1']['MIN'][np.where(SS['hour']==d.hour)] for d in h['DATETIME']]
mean_stats = [SS['BHCU1']['MEAN'][np.where(SS['hour']==d.hour)] for d in h['DATETIME']]
plt.scatter(h['DATETIME'], max_stats, c='r', label='HRRR month max')
plt.scatter(h['DATETIME'], min_stats, c='b', label='HRRR month min')
plt.scatter(h['DATETIME'], mean_stats, c='g', label='HRRR month mean')
plt.legend(fontsize=7)
plt.grid()
plt.xlim([sDATE, eDATE])
formatter = DateFormatter('%b %d\n%H:%M')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
if variable == 'TMP:2 m':
    plt.ylabel('Temperature (C)')
elif variable == 'WIND:10 m':
    plt.ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
else:
    print 'no y label units'

plt.savefig('Fire_start_stats.png', bbox_inches='tight')
 

########### WIND SPEED ##############
variable = 'WIND:10 m'
var = variable.replace(':','_').replace(' ','_')
# Get HRRR time sereis
h = point_hrrr_time_series_multi(sDATE, eDATE, locs,
                                 variable=variable,
                                 fxx=0, model='hrrr', field='sfc',
                                 area_stats=False,
                                 reduce_CPUs=2,
                                 verbose=True)

# Get HRRR OSG statistics
SS = get_OSG_stats(locs, variable, ['MAX', 'MEAN', 'MIN', 'P95'],
                   months=[6], hours=range(0,24), extra=True, fxx=0)


# Plot the time series
plt.figure(2, figsize=[12, 6])
plt.title('BHCU1: '+var+'\n%s--%s' % (sDATE.strftime('%b %d,%Y'), eDATE.strftime('%b %d,%Y')))
plt.plot(a['DATETIME'], a['wind_speed'], lw=3, c='k', label='MesoWest')
plt.plot(h['DATETIME'], h['BHCU1'], lw=3, c='orange', label='HRRR anlys')

max_stats = [SS['BHCU1']['MAX'][np.where(SS['hour']==d.hour)] for d in h['DATETIME']]
min_stats = [SS['BHCU1']['MIN'][np.where(SS['hour']==d.hour)] for d in h['DATETIME']]
mean_stats = [SS['BHCU1']['MEAN'][np.where(SS['hour']==d.hour)] for d in h['DATETIME']]
p95_stats = [SS['BHCU1']['P95'][np.where(SS['hour']==d.hour)] for d in h['DATETIME']]
plt.scatter(h['DATETIME'], max_stats, c='r', label='HRRR month max')
plt.scatter(h['DATETIME'], min_stats, c='b', label='HRRR month min')
plt.scatter(h['DATETIME'], mean_stats, c='g', label='HRRR month mean')
plt.scatter(h['DATETIME'], p95_stats, c='tomato', label='HRRR month P95')
plt.legend(fontsize=7)
plt.grid()
plt.xlim([sDATE, eDATE])
plt.ylim(bottom=0)
formatter = DateFormatter('%b %d\n%H:%M')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
if variable == 'TMP:2 m':
    plt.ylabel('Temperature (C)')
elif variable == 'WIND:10 m':
    plt.ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
else:
    print 'no y label units'

plt.savefig('Fire_start_stats%sBB.png'% (var), dpi=100, bbox_inches='tight')
