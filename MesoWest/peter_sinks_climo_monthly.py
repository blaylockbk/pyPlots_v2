# Brian Blaylock
# 8 December 2016                              Day of the Horel Christmas Party

"""
Peter Sinks rim and valley temperatures
"""
import matplotlib.pyplot as plt
style_path = '/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/BB_mplstyle/'
style_path = 'B:/pyBKB_v2/BB_mplstyle/'
plt.style.use([style_path+'publications.mplstyle',
                   style_path+'width_50.mplstyle',
                   style_path+'dpi_medium.mplstyle']
                   )
from matplotlib.dates import DateFormatter
from datetime import datetime
import numpy as np
import sys
sys.path.append('B:/pyBKB_v2')
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')

from BB_MesoWest.MesoWest_climo import get_mesowest_climatology


import matplotlib.pyplot as plt

MONTH = np.array([])
AVG_Temp = np.array([])
MAX_Temp = np.array([])
MIN_Temp = np.array([])

station = 'PSINK'
station = 'PSRIM'

months = np.arange(1, 13)
for m in months:
    start = '%02d010000' % (m)
    end = '%02d280000' % (m)

    a = get_mesowest_climatology(station, start, end)
    a['air_temp'][a['air_temp']<-100] = np.nan
    MONTH = np.append(MONTH, m)

    avg_temp = np.nanmean(a['air_temp'])
    AVG_Temp = np.append(AVG_Temp, avg_temp)
    MAX_Temp = np.append(MAX_Temp, np.nanmax(a['air_temp']))
    MIN_Temp = np.append(MIN_Temp, np.nanmin(a['air_temp']))

plt.plot(MONTH, MAX_Temp, label='Max')
plt.plot(MONTH, AVG_Temp, label='Mean')
plt.plot(MONTH, MIN_Temp, label='Min')
plt.title(station
            + "\n"
            + a['DATETIME'][0].strftime('%b %Y')
            + ' to '
            + a['DATETIME'][-1].strftime('%b %Y'))
plt.xlabel('Month')
plt.ylabel('Temperature (C)')
plt.legend()
plt.xlim([1, 12])
plt.ylim([-50,50])

plt.savefig(station + '_' 
            + a['DATETIME'][0].strftime('%b %Y') + '_'
            + a['DATETIME'][-1].strftime('%b %Y'))
