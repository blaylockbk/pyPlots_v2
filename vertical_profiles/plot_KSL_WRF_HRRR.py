# Brian Blaylock
# 22 Novebmer 2016
# MS Series -- Plots from my Master's Research

"""
Plots vertical profile of:
    Potential Temperature
    Mixing Ratio
    Wind Vector

With data from:
    KSL
    HRRR analysis
    HRRR 1-hr forecast
    WRF Output
"""


import matplotlib.pyplot as plt
style_path = '/uufs/chpc.utah.edu/common/home/u0553130/BB_mplstyle/'
plt.style.use(style_path+'publications.mplstyle')
plt.style.use([style_path+'publications.mplstyle',
               style_path+'width_100.mplstyle',
               style_path+'dpi_high.mplstyle']
             )
