# Brian Blaylock
# February 7, 2017

"""
Get the potential temperature at 700 mb and the surface from the SLC balloon
"""

import multiprocessing # :)
import numpy as np
from datetime import datetime, timedelta

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_data.data_manager import get_wyoming_sounding


def get_700_sfc_from_sounding(DATE):
    """
    Return the surface and 700 mb potential temperature
    """
    print "working on", DATE
    s = get_wyoming_sounding(DATE)
    idx_700 = np.argwhere(s['press'] == 700)[0][0]
    theta_700 = s['theta'][idx_700]
    theta_sfc = s['theta'][0]
    temp_700 = s['temp'][idx_700]
    temp_sfc = s['temp'][0]

    return [temp_sfc, theta_sfc, temp_700, theta_700]



if __name__ == "__main__":

    base = datetime(2017, 1, 23)
    numdays = 14
    numhours = numdays*24
    date_list = np.array([base + timedelta(hours=x) for x in range(0, numhours+1, 12)])

    # Multiprocessing :)
    num_proc = multiprocessing.cpu_count() # use all processors
    num_proc = 12                           # specify number to use (to be nice)
    p = multiprocessing.Pool(num_proc)
    data = p.map(get_700_sfc_from_sounding, date_list)

    data = np.array(data)
    SLC_sfc_temp = data[:, 0]
    SLC_sfc_theta = data[:, 1]
    SLC_700_temp = data[:, 2]
    SLC_700_theta = data[:, 3]

    write_this = np.transpose(np.vstack([date_list, SLC_sfc_temp, SLC_sfc_theta, SLC_700_temp, SLC_700_theta]))

    np.savetxt('UWFPS_inversion_SLC_balloon.csv', write_this,
               delimiter=',',
               fmt="%s",
               header='datetime, SLC_sfc_temp, SLC_sfc_theta, SLC_700_temp, SLC_700_theta')