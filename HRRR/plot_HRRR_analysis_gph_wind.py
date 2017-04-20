# Brian Blaylock
# 25 March 2016

# Plot HRRR grib2 data

# 500 mb analysis: geopotential height (m), wind speed, wind barbs (m/s)

# Must use CHPC version of python before running, 
# make sure you change python module
#   example: % module load python/2.7.3
#            % which python
#            >> /uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/bin/python

# Documentation on pygrib here: http://pygrib.googlecode.com/svn/trunk/docs/pygrib.open-class.html


import pygrib
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime
from functions import wind_calcs, custom_domains


# Open a file

date = '20150618'
hour = '23'
subdomain = 'no'
# Model level pressure in milibars
mb = 500

DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/'+date+'/models/hrrr/'
FILE = 'hrrr.t'+hour+'z.wrfprsf00.grib2'

grbs = pygrib.open(DIR+FILE)






# Grab geopotential height at 500 mb (just had to figure out that it's in the 18th index)
grb = grbs.select(name='Geopotential Height',level=mb)[0] # for general info
Z = grb.values
Zunits = grb.units
Zname = grb.name

Ugrb = grbs.select(name='U component of wind',level=mb)[0]
U = Ugrb.values
Uunits = Ugrb.units
Uname = Ugrb.name

Vgrb = grbs.select(name='V component of wind',level=mb)[0]
V = Vgrb.values
Vunits = Vgrb.units
Vname = Vgrb.name

lat,lon = grb.latlons()



speed = wind_calcs.wind_uv_to_spd(U,V)
    
    
    # Plot a map of this stuff, using the Grib File map parameters
    ## These HRRR files have a lambert projection
print grb.gridType
lat_0 = grb.LaDInDegrees
lon_0 = grb.LoVInDegrees-360 
lat_1 = grb.Latin1InDegrees
lat_2 = grb.Latin2InDegrees

# Domain Boundaries
bot_left_lon = lon[0][0]
bot_left_lat = lat[0][0]
top_right_lon = lon[-1][-1]
top_right_lat = lat[-1][-1]

if subdomain != 'no':
    domain = custom_domains.get_domain(subdomain)
    top_right_lat = domain['top_right_lat']
    top_left_lat = domain['top_right_lat']
    top_right_lon = domain['top_right_lon']
    top_left_lon = domain['bot_left_lon']
    bot_right_lat = domain['bot_left_lat']
    bot_right_lon = domain['top_right_lon']
    bot_left_lat = domain['bot_left_lat']
    bot_left_lon = domain['bot_left_lon']


print 'Creating Map'
m = Basemap(resolution='i',area_thresh=100.,projection='lcc',\
    lat_0=lat_0,lon_0=lon_0,\
    lat_1=lat_1, lat_2=lat_2,\
    llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
    urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)

plt.figure(figsize=[16*1.5,10*1.5])
m.drawcoastlines()
m.drawcountries()
m.drawstates()

x,y = m(lon,lat)    

# Now plot wind and geopotential height
m.pcolormesh(x,y,speed,cmap="gist_stern_r")
cb = plt.colorbar(shrink=.7)
cb.set_label("Wind Speed (m/s)")

interval = 50
m.barbs(x[::50,::50],y[::50,::50],U[::50,::50],V[::50,::50])  

# Just becuase we can, add 500 mb Geopotential Height Contours on top.
CS = m.contour(x,y,Z,colors='black',levels=np.arange(0,6000,60),linewidths=3)
plt.clabel(CS, inline=1, fontsize=12,fmt='%1.0f')      


validDate = grb.validDate

plt.title('HRRR Analysis Valid '+validDate.strftime('%Y-%b-%d %H:%M:%S')+'\n'+
          str(grb.level)+' mb '+Zname+'and Wind')

plt.savefig('HRRR_anl_'+str(mb)+'.png',dpi=300,bbox_inches='tight')
plt.show()
