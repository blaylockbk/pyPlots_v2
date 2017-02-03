# Brian Blaylock
# 6 January 2017                              It was -20 F in Logan last night

"""
Time Series for multiple mesowest stations
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
from collections import OrderedDict

import sys
sys.path.append('B:/pyBKB_v2')
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')

from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts


DATE_START = datetime(2017, 1, 4)
DATE_END = datetime.now()
save_date = DATE_START.strftime('%Y%m%d')+'-'+DATE_END.strftime('%Y%m%d')

stations = ['PSINK', 'KLGU', 'UFD09', 'WBB']

data = OrderedDict()

for s in stations:
    data[s] = get_mesowest_ts(s, DATE_START, DATE_END)


"""
Plot
"""
fig, ax1 = plt.subplots(1, 1)

for s in data.keys():
    ax1.plot(data[s]['DATETIME'], data[s]['air_temp'],
            label=s)


plt.grid()

ax1.legend()
ax1.set_title('MesoWest Air Temperature')
ax1.set_ylabel('Temperature (C)')

ax1.xaxis.set_major_locator(HourLocator(byhour=[0,12]))
dateFmt = DateFormatter('%b %d\n%H:%M')

ax1.xaxis.set_major_formatter(dateFmt)

plt.savefig('stations_'+save_date)
