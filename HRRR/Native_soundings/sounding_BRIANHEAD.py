# Brian Blaylock
# June 30, 2017           Rachel and I are going to the Owlz game on Monday :)

"""
Plots a sounding from the HRRR native grids
HRRR data is on the CHPC Pando archive: http://hrrr.chpc.utah.edu
"""

import urllib
from datetime import date, datetime, timedelta
import pygrib
import numpy as np
import matplotlib.pyplot as plt

def reporthook(a, b, c):
    """
    Report download progress in megabytes
    """
    print "% 3.1f%% of %.2f MB\r" % (min(100, float(a * b) / c * 100), c/1000000.),

# Download the full native grid file. Not too bad when the subregion is 25MB
def get_HRRR_native(DATE, name, fxx=0, OUTDIR='./'):
    """
    Downloads a grib2 file to the current directory and 
    Input:
        DATE - datetime object of the model run datetime (UTC)
        name - name of the subregion. Usually the name of a fire like BRIANHEAD
        fxx  - the forecast hour. Default the analysis hour, 0
    Output:
        Downloads the file into the current directory
        Returns the file name.
    """
    URL = "https://pando-rgw01.chpc.utah.edu/HRRR/oper/nat/%s/hrrr.t%sz.wrfnatf%02d.grib2.%s" % \
          (DATE.strftime('%Y%m%d'), DATE.strftime('%H'), fxx, name)
    fileName = OUTDIR + '%s_f%02d_%s' % (DATE.strftime('%Y-%m-%d_%H%M'), fxx, name)
    print "Downloading:", URL
    urllib.urlretrieve(URL, fileName, reporthook=reporthook)
    print "Got it!",  fileName

    return fileName

def TempRH_to_dwpt(Temp, RH):
    """
    Convert a temperature and relative humidity to a dew point temperature.
    Equation from:
    http://andrew.rsmas.miami.edu/bmcnoldy/humidity_conversions.pdf

    Input:
        Temp - Air temperature in Celsius
        RH - relative humidity in %
    Output:
        dwpt - Dew point temperature in Celsius
    """
    # Check if the Temp coming in is in celsius and if RH is between 0-100%
    passed = False
    test_temp = Temp < 65
    #
    if np.sum(test_temp) == np.size(Temp):
        passed = True
        test_rh = np.logical_and(RH <= 100, RH >= 0)
        if np.sum(test_rh) == np.size(RH):
            passed = True
        else:
            print "faied relative humidity check"
    else:
        print "faild temperature check"
    #
    if passed is True:
        a = 17.625
        b = 243.04
        dwpt = b * (np.log(RH/100.) + (a*Temp/(b+Temp))) / (a-np.log(RH/100.)-((a*Temp)/(b+Temp)))
        return dwpt
    #
    else:
        print "TempRH_to_dwpt input requires a valid temperature and humidity."
        return "Input needs a valid temperature (C) and humidity (%)."

def pluck_point_new(stn_lat, stn_lon, grid_lat, grid_lon, return_c=False):
    """
    From the grid, get the data for the point nearest the MesoWest station
    Figure out the nearest lat/lon in the HRRR domain for the station location
    Input:
        stn_lat, stn_lon - The latitude and longitude of the station
        grid_lat, grid_lon - The 2D arrays for both latitude and longitude
    Output:
        The index of the flattened array
    """

    abslat = np.abs(grid_lat-stn_lat)
    abslon = np.abs(grid_lon-stn_lon)

    # Element-wise maxima. (Plot this with pcolormesh to see what I've done.)
    c = np.maximum(abslon, abslat)

    # The index of the minimum maxima (which is the nearest lat/lon)
    latlon_idx = np.where(np.min(c)==c)

    if return_c == False:
        return latlon_idx
    else:
        return [latlon_idx, c]

if __name__ == "__main__":

    sDATE = datetime(2017, 6, 25, 0)
    eDATE = datetime(2017, 6, 30, 0)
    hours = (eDATE - sDATE).days*24 + (eDATE - sDATE).seconds/60/60
    DATELIST = [sDATE+timedelta(hours=h) for h in range(0, hours)]
    name = 'BRIANHEAD'
    fxx = 0
    got_idx = False

    for DATE in DATELIST:    
        # Download the grib file and get the file name
        grbFile = get_HRRR_native(DATE, name, fxx=fxx)
        
        # Yeah! Now do stuff with the file
        grbs = pygrib.open(grbFile)

        # Index a position
        if got_idx is False:
            lat, lon = grbs[1].latlons()
            idx = pluck_point_new(37.82274, -112.4346, lat, lon)
            x = idx[0]
            y = idx[1]
            got_idx = True

        # Temperature all layers
        temps = np.array([])
        T = grbs.select(name="Temperature")
        for i in range(0, 50):
            temp = T[i].values[x, y]
            temps = np.append(temps, temp-273.15)
            
        
        # Specific Humidity all layers
        shmds = np.array([])
        S = grbs.select(name="Specific humidity")
        for i in range(0, 50):
            shmd = S[i].values[x, y]
            shmds = np.append(shmds, shmd) # kg/kg
        
        # Pressure all layers
        press = np.array([])
        P = grbs.select(name="Pressure")
        for i in range(0, 50):
            pres = P[i].values[x, y]
            press = np.append(press, pres/100) # hPa
        
        # Hights all layers
        hghts = np.array([])
        H = grbs.select(name="Geopotential Height")
        for i in range(0, 50):
            hght = H[i].values[x, y]
            hghts = np.append(hghts, hght) # m
        
        # U wind all layers
        us = np.array([])
        U = grbs.select(name="U component of wind")
        for i in range(0, 50):
            u = U[i].values[x, y]
            us = np.append(us, u) # m/s

        # V wind all layers
        vs = np.array([])
        V = grbs.select(name="V component of wind")
        for i in range(0, 50):
            v = V[i].values[x, y]
            vs = np.append(vs, v) # m/s

        
        # Specific Humidity to Relative Humidity
        RH = 0.263*press*100*shmds*(np.exp((17.67*(temps+273.15-273.15))/(temps+273.15-29.65)))**-1
        DWPT = TempRH_to_dwpt(temps, RH)

        plt.clf()
        plt.plot(temps, press, color='r')
        plt.plot(DWPT, press, color='g')
        plt.gca().invert_yaxis()
        plt.xlim(-20, 50)
        plt.ylim(850, 400)
        plt.title("%s %s" % (name, DATE.strftime("%Y-%b-%d %H:%M")))
        plt.savefig('/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR_fires/BRIANHEAD/natsoundings/'+DATE.strftime("%Y-%m-%d_%H%M")+"_f%02d" % (fxx))