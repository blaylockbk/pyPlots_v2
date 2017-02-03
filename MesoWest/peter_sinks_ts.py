# Brian Blaylock
# 8 December 2016                              Day of the Horel Christmas Party

"""
Peter Sinks rim and valley temperatures
"""

import matplotlib.pyplot as plt
style_path = '/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/BB_mplstyle/'
#style_path = 'B:/pyBKB_v2/BB_mplstyle/'
plt.style.use([style_path+'publications.mplstyle',
                   style_path+'width_100.mplstyle',
                   style_path+'dpi_medium.mplstyle']
                   )
from matplotlib.dates import DateFormatter, HourLocator
from datetime import datetime

import sys
sys.path.append('B:/pyBKB_v2')
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')

from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts


DATE_START = datetime(2017, 1, 4)
DATE_END = datetime.now()
save_date = DATE_START.strftime('%Y%m%d')+'-'+DATE_END.strftime('%Y%m%d')

valley = get_mesowest_ts('PSINK', DATE_START, DATE_END)
rim = get_mesowest_ts('PSRIM', DATE_START, DATE_END)


"""
Plot
"""
fig, ax1 = plt.subplots(1, 1)

ax1.plot(rim['DATETIME'], rim['air_temp'],
         color='r',
         label='rim')
ax1.plot(valley['DATETIME'], valley['air_temp'],
         color='b',
         label='valley')


plt.grid()

ax1.legend()
ax1.set_title('Peter Sinks')
ax1.set_ylabel('Temperature (C)')

ax1.xaxis.set_major_locator(HourLocator(byhour=[0,12]))
dateFmt = DateFormatter('%b %d\n%H:%M')

ax1.xaxis.set_major_formatter(dateFmt)

plt.savefig('peter_sinks_'+save_date)
