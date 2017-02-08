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
from BB_ASN.BB_Radiometer import get_rad_sounding, get_rad_sounding_range
from BB_data.data_manager import get_wyoming_sounding
from BB_skewt.skewt import SkewT

DATE = datetime(2017, 1, 23)

while DATE < datetime(2017, 2, 6):
    date = DATE.strftime('%Y-%m-%d_%H%M')
    FIG = './figs/'

    # Load the data from each source



    # add wyoming profile
    w = get_wyoming_sounding(DATE)
    wdata = {'dwpt':w['dwpt'], \
             'hght':w['height'], \
             'pres':w['press'], \
             'temp':w['temp'], \
             'sknt':w['wspd'], \
             'drct':w['wdir']}
    S = SkewT.Sounding(soundingdata=wdata)
    S['StationNumber'] = ''
    S['SoundingDate'] = date
    S.make_skewt_axes(tmin=-35., tmax=20., pmin=500., pmax=910.)
    S.add_profile(color='r', lw=5, label='Balloon')


    # add HRRR profile
    b = get_bufr_sounding(DATE)
    bdata = {'dwpt':b['dwpt'][0], \
             'hght':b['hght'][0], \
             'pres':b['pres'][0], \
             'temp':b['temp'][0], \
             'drct':b['drct'][0], \
             'sknt':b['sknt'][0]}
    T = SkewT.Sounding(soundingdata=bdata)
    S.soundingdata = T.soundingdata
    S.add_profile(color='g', lw=4, bloc=1.2, label='HRRR anlys')

    try:
        """
        # add radiometer profile
        r = get_rad_sounding(DATE)
        rdata = {'dwpt':r['ZENITH_DWPT'], \
                    'hght':r['HEIGHT'], \
                    'pres':r['PRES_LEVELS'], \
                    'temp':r['ZENITH_TEMP']}
        T = SkewT.Sounding(soundingdata=rdata)
        S.soundingdata = T.soundingdata
        S.add_profile(color='b', lw=.9, bloc=1.5, label='Radiometer_z')

        # add radiometer profile
        rdata = {'dwpt':r['ANGLE_A_DWPT'], \
                    'hght':r['HEIGHT'], \
                    'pres':r['PRES_LEVELS'], \
                    'temp':r['ANGLE_A_TEMP']}
        T = SkewT.Sounding(soundingdata=rdata)
        S.soundingdata = T.soundingdata
        S.add_profile(color='lightskyblue', lw=.9, bloc=1.5, label='Radiometer_z')
        """
        R = get_rad_sounding_range(DATE-timedelta(minutes=10), DATE+timedelta(minutes=10))

        z = np.mean(R['ZENITH_TEMP'], axis=0)
        a = np.mean(R['ANGLE_A_TEMP'], axis=0)
        n = np.mean(R['ANGLE_N_TEMP'], axis=0)
        s = np.mean(R['ANGLE_S_TEMP'], axis=0)
        # Average of all profile angles for all obs -10/+10 mins
        ALL = np.mean([z, a, n, s], axis=0)

        zd = np.mean(R['ZENITH_DWPT'], axis=0)
        ad = np.mean(R['ANGLE_A_DWPT'], axis=0)
        nd = np.mean(R['ANGLE_N_DWPT'], axis=0)
        sd = np.mean(R['ANGLE_S_DWPT'], axis=0)
        ALLd = np.mean([zd, ad, nd, sd], axis=0)

        Zdata = {'dwpt': zd,
                 'temp': z,
                 'pres': R['PRES_LEVELS'],
                 'hght': R['HEIGHT']}
        T = SkewT.Sounding(soundingdata=Zdata)
        S.soundingdata = T.soundingdata
        S.add_profile(color='lightslategrey', lw=.9, bloc=1.5, label='Radiometer_Z')

        Adata = {'dwpt': ad,
                 'temp': a,
                 'pres': R['PRES_LEVELS'],
                 'hght': R['HEIGHT']}
        T = SkewT.Sounding(soundingdata=Adata)
        S.soundingdata = T.soundingdata
        S.add_profile(color='lightslategrey', lw=.9, bloc=1.5, label='Radiometer_A')

        Ndata = {'dwpt': nd,
                 'temp': n,
                 'pres': R['PRES_LEVELS'],
                 'hght': R['HEIGHT']}
        T = SkewT.Sounding(soundingdata=Ndata)
        S.soundingdata = T.soundingdata
        S.add_profile(color='lightslategrey', lw=.9, bloc=1.5, label='Radiometer_N')

        Sdata = {'dwpt': sd,
                 'temp': s,
                 'pres': R['PRES_LEVELS'],
                 'hght': R['HEIGHT']}
        T = SkewT.Sounding(soundingdata=Sdata)
        S.soundingdata = T.soundingdata
        S.add_profile(color='lightslategrey', lw=.9, bloc=1.5, label='Radiometer_S')

        Rdata = {'dwpt': ALLd,
                 'temp': ALL,
                 'pres': R['PRES_LEVELS'],
                 'hght': R['HEIGHT']}
        T = SkewT.Sounding(soundingdata=Rdata)
        S.soundingdata = T.soundingdata
        S.add_profile(color='blue', lw=3, bloc=1.5, label='Radiometer_all')
    except:
        print "Radiometer unavailable", DATE

    plt.legend() # doesn't work??

    plt.savefig(FIG+'skewT_'+date, bbox_inches="tight")

    DATE = DATE + timedelta(hours=12)
