# Brian Blaylock
# 7 December 2015

# Function for getting MesoWest time series from the API for one station

import numpy as np
import datetime
import json
import urllib2

token = '2562b729557f45f5958516081f06c9eb' #Request your own token at http://mesowest.org/api/signup/

variables = 'wind_direction,wind_speed,air_temp,relative_humidity'

def MWdate_to_datetime(x):
    """
    Converts a MesoWest date string to a python datetime object
    So far only works for summer months (daylight savings time). Best if you
    make your MesoWest API call in UTC time.
    """
    try:
        return datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')
    		#print 'Times are in UTC'
    except:
        return datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%S-0600')
    		#print 'Times are in Local Time'


def get_mesowest_ts(stationID,start_time,end_time):
    """
    Makes a time series query from the MesoWest API
    
    Input:
        stationID  : string of the station ID
        start_time : datetime object of the start time in UTC
        end_time   : datetime object of the end time in UTC
        
    Output:
        a dictionary of the data
    """

    # convert the start and end time to the string format requried by the API
    start = start_time.strftime("%Y%m%d%H%M")
    end = end_time.strftime("%Y%m%d%H%M")
    
    # The API request URL
    URL = 'http://api.mesowest.net/v2/stations/timeseries?stid='+stationID+'&start='+start+'&end='+end+'&vars='+variables+'&obtimezone=utc&token='+token
    
    ##Open URL and read the content
    f = urllib2.urlopen(URL)
    data = f.read()
    
    ##Convert that json string into some python readable format
    data = json.loads(data)
    stn_name = str(data['STATION'][0]['NAME'])
    stn_id   = str(data['STATION'][0]['STID'])
    # Need to do some special stuff with the dates
    ##Get date and times
    dates = data["STATION"][0]["OBSERVATIONS"]["date_time"]
    ##Convert to datetime and put into a numpy array
    DATES = np.array([]) #initialize the array to store converted datetimes
    
    # Convert MesoWest String time into datetime quickly with vectorized function
    converttime = np.vectorize(MWdate_to_datetime)
    DATES = converttime(dates)

    # Get Met variables. If doesn't exist, then return an array of zeros
    try:    
        temp = np.array(data['STATION'][0]["OBSERVATIONS"]["air_temp_set_1"],dtype=np.float) 
    except:
        temp = [np.nan for x in range(0,len(DATES))]
    try:
        rh = np.array(data['STATION'][0]["OBSERVATIONS"]["relative_humidity_set_1"],dtype=np.float)
    except:
        rh = [np.nan for x in range(0,len(DATES))]
    try:
        wd = np.array(data['STATION'][0]["OBSERVATIONS"]["wind_direction_set_1"],dtype=np.float)
    except:
        wd = [np.nan for x in range(0,len(DATES))]    
    try:
        ws = np.array(data['STATION'][0]["OBSERVATIONS"]["wind_speed_set_1"],dtype=np.float)
    except:
        ws = [np.nan for x in range(0,len(DATES))]
    try:
        wg = np.array(data['STATION'][0]["OBSERVATIONS"]["wind_gust_set_1"],dtype=np.float)
    except:
        wg = [np.nan for x in range(0,len(DATES))]
    
    
    data_dict = {
                'station name':stn_name,
                'station id':stn_id,
                'datetimes':DATES,                
                'temperature':temp,
                'relative humidity':rh,
                'wind direction':wd,
                'wind speed':ws,
                'wing gust':wg
                }
                
    return data_dict
    
    
#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":
    
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
    
    # Get MesoWest data from functin above
    station = 'UKBKB'
    start_time = datetime.datetime(2015,4,1)
    end_time = datetime.datetime(2015,5,2)
    
    a = get_mesowest_ts(station,start_time,end_time)
    
    # Make a quick temperature plot
    temp = a['temperature']
    RH = a['relative humidity']
    dates = a['datetimes']
    
    #convert dates from UTC to mountain time (-6 hours)
    dates = dates - datetime.timedelta(hours=6)
    
    fig = plt.figure(figsize=(8,4))
    plt.title(station)
    plt.xticks(rotation=30)    
    plt.xlabel('Date Time MDT')
    ax1 = fig.add_subplot(111)
    ax1.plot(dates,temp, 'r')
    ax1.set_ylabel('Temperature (c)')
    ax2 = ax1.twinx()
    ax2.plot(dates,RH,'g')
    ax2.set_ylabel('Relative Humidity (%)')    

    

    """
    ##Format Ticks##
    ##----------------------------------
    # Find months
    months = MonthLocator()
    # Find days
    days = DayLocator()
    # Find each 0 and 12 hours
    hours = HourLocator(byhour=[0,6,12,18])
    # Find all hours
    hours_each = HourLocator()
    # Tick label format style
    dateFmt = DateFormatter('%b %d, %Y\n%H:%M')
    # Set the x-axis major tick marks
    ax1.xaxis.set_major_locator(hours)
    # Set the x-axis labels
    ax1.xaxis.set_major_formatter(dateFmt)
    # For additional, unlabeled ticks, set x-axis minor axis
    ax1.xaxis.set_minor_locator(hours_each)
    """
    
    
