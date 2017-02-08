# Brian Blaylock
# February 3, 2017                  Rachel is coming over for dinner tonight :)

"""
Get and plot sounding data from HRRR analyses, DEQ Radiometer, and SLC balloon.
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')
from BB_HRRR.get_bufr_sounding import get_bufr_sounding
from BB_ASN.BB_Radiometer import get_rad_sounding
from BB_data.data_manager import get_wyoming_sounding

DATE = datetime(2017, 1, 20)

while DATE < datetime.now():
    date = DATE.strftime('%Y-%m-%d_%H%M')
    FIG = './figs/'

    # Load the data from each source
    


    # plot the data
    plt.figure(figsize=[6,7])

    try:
        w = get_wyoming_sounding(DATE)
        plt.plot(w['temp'], w['press'], \
                 color='k',
                 lw=4,
                 label='SLC')
    except:
        print "no wyoming", DATE

    try:
        b = get_bufr_sounding(DATE)
        plt.plot(b['temp'][0], b['pres'][0], \
                 color='green',
                 lw=2,
                 label='HRRR Anyls')
    except:
        print "no bufr", DATE

    try:
        r = get_rad_sounding(DATE)
        plt.plot(r['ZENITH_TEMP'], r['PRES_LEVELS'], \
                 color='blue',
                 lw=2,
                 label='Radiometer_Zenith')
        plt.plot(r['ANGLE_A_TEMP'], r['PRES_LEVELS'], \
                 color='magenta',
                 lw=1,
                 label='Radiometer_A')
        plt.plot(r['ANGLE_N_TEMP'], r['PRES_LEVELS'], \
                 color='gold',
                 lw=1,
                 label='Radiometer_N')
        plt.plot(r['ANGLE_S_TEMP'], r['PRES_LEVELS'], \
                 color='cyan',
                 lw=1,
                 label='Radiometer_S')
    except:
        print "no radiometer", DATE

    plt.title(DATE)
    plt.legend()
    plt.gca().invert_yaxis()
    plt.yscale('log')
    plt.yticks([1000, 900, 800, 700, 600, 500, 400, 300, 200], \
                ['1000', '900', '800', '700', '600', '500', '400', '300', '200'])
    plt.grid()
    plt.ylim([900, 500])
    plt.xlim([-30, 10])

    plt.savefig(FIG+date, bbox_inches="tight")

    DATE = DATE + timedelta(hours=12)
