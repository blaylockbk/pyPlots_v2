# Brian Blaylock
# Use this to look at all the different map bacgrounds available 
# from the arcgis map server
# Look at Salt Lake Valley map backgrounds here: 
#      http://kbkb-wx-python.blogspot.com/2016/04/python-basemap-background-image-from.html

import matplotlib.pyplot as plt
import numpy as np
from functions_domains_models import *

from mpl_toolkits.basemap import Basemap


# Define the map boundaries lat/lon
domain = get_domain('salt_lake_valley')
top_right_lat = domain['top_right_lat']+.1
top_right_lon = domain['top_right_lon']-.1
bot_left_lat = domain['bot_left_lat']
bot_left_lon = domain['bot_left_lon']

## Map in cylindrical projection (data points may apear skewed)
m = Basemap(resolution='i',projection='cyl',\
    llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
    urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
 

map_list = [
'ESRI_Imagery_World_2D',    # 0
'ESRI_StreetMap_World_2D',  # 1
'NatGeo_World_Map',         # 2
'NGS_Topo_US_2D',           # 3
#'Ocean_Basemap',            # 4
'USA_Topo_Maps',            # 5
'World_Imagery',            # 6
'World_Physical_Map',       # 7    blurry
'World_Shaded_Relief',      # 8
'World_Street_Map',         # 9
'World_Terrain_Base',       # 10
'World_Topo_Map'            # 11
]

for maps in map_list: 
    plt.figure(figsize=[10,20])    
    ## Instead of using WRF terrain fields you can get a high resolution image from ESRI
    m.arcgisimage(service=maps, xpixels = 3500, dpi=500, verbose= True)
    m.drawstates()
    plt.title(maps)
    
    plt.savefig('00'+maps,bbox_inches="tight")

