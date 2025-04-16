import os              #import os module to access files and folders
import earthaccess      #import eartaccess module to access satellite data
import geopandas as gpd     #import geopandas to work with spatial data
import rasterio as rio      #import rasterio to work with raster data
import rasterio.merge       #import module to combine rasters
import shapely              #import shapely module to work with geometries


earthaccess.login(strategy='netrc')   #earthaccess login access
date_from=(input())         #set start date for image search
date_to= (input())          #set end date for image search
corner_ref=                     #create 1km aoi from corner reference

datasets = earthaccess.search_datasets(
    keyword='elevation', # search for datasets that match the keyword 'elevation'
    polygon=search_area. # search for datasets that intersect coordinates
    provider=sentinel           #set image search to look for sentinel images
    temporal=(date_from, date_to)    #set date range
)

