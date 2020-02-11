# THIS STUFF IS SO OLD, DON'T LOOK AT IT.
### I keep it here so you and I can scavage for parts
![](https://github.com/blaylockbk/Ute_WRF/blob/master/rusty.jpg)

# pyPlots_v2
## Python scrips for creating various plots. 

A goal of my PhD research is improved *documentation*, and *organization*. I'm 
learning this takes some extra time and thought. But, I'm counting that this
"extra planning" will in fact same time.

Here is my logic in nameing convention for directories and file names. The idea
is that these directories tell you what kind of plot those scripts make, and
the file name 

## Directories
- **HRRR** Misc. related to HRRR plots (need to reorganize, it doesn't fit above description)
- **MesoWest** Plots related to MesoWest (need to reorganzie, for same reason as above)
- **NASA_MUR_SST** This is old. Should be moved
- **NEXRAD_II** Radar plots
- **soundings** related to atmospheric soundings
- **time-height** time-height plots, from model data, bufr soundings, real soundings, etc.
- **vertical_profiles** this isn't really different than soundings, be maybe it's necessary??
- **WRF-Tracers** put this old code from my MS work here for someone else to see. Can be cleaned.
- **time-series** time series plots

## File names
- **plot_...** creates a plot
- **get_...** gets data needed to make a plot (sometimes this is necessary)

- **..._MW_...** data from the mesowest API
- **..._bufr_...** data from bufr soundings (typically HRRR)
- **..._STNid_...** some sort of station identifier

## Saving figures
Save figures in directories with similar names as the directory and file name
that created the plot. The "root" should be the project I'm working on.

example: 
.../Project/subProject/plotDirecotry/plotFilename+extra.png
.../PhD/Jan2017_inversion/time-height/bufr_sounding_kslc.png
