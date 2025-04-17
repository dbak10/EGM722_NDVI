import os              #import os module to access files and folders
import geopandas as gpd     #import geopandas to work with spatial data
import rasterio as rio      #import rasterio to work with raster data
import rasterio.merge       #import module to combine rasters
import shapely as shp             #import shapely module to work with geometries
import pandas as pd         #import pandas module
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from geopy import Point
from geopy.distance import distance
import pyproj
from shapely.geometry import Polygon
import matplotlib as plt


api = SentinelAPI(None, None, 'https://apihub.copernicus.eu/apihub/')   #sentinelsat login access
print("enter start date in format yyyymmdd")
start_date=input()        #set start date for image search user imput?
print("enter end date in format yyyymmdd")
end_date=input()          #set end date for image search user input?

corner_grid=input("enter easting, northings for an OS 1km square e.g. 604000 279000").split()     #input of corner grid, split into list
corner_grid_x= int(corner_grid[0]) #easting of corner grid
corner_grid_y= int(corner_grid[1]) #northing of corner grid

crs_OS = pyproj.Proj(init='EPSG:27700') #set variable with projected OS ctm
crs_wgs84 = pyproj.Proj(init='EPSG:4326')  #set variale with lat long ctm
corner_grid_lon_lat = pyproj.transform(crs_OS, crs_wgs84, corner_grid_x, corner_grid_y) #convert corner grid inputs to long lat


#create square polygon off corner grid reference
p1= Point(corner_grid_lon_lat[1], corner_grid_lon_lat[0])      #set corner point in lat lon (reverse of transform!)
p2= distance(kilometers=1).destination((p1), bearing=0)  #set next corner location 1km North
p3 = distance(kilometers=1).destination((p2), bearing=90)   #set next corner location 1km East
p4 = distance(kilometers=1).destination((p3), bearing=180)   #set next corner location 1km South
p0 = p1     #set a p0 to close the polygon with the same coordinates as the start point
points = [(p.longitude, p.latitude) for p in [p1,p2,p3,p4, p0]]  #convert points to lat lon explicit to create polygon
km_square = Polygon(points)                         #create polygon using the 4 corner points

aoi=shp.to_geojson(km_square)

#search by polygon, time, and SciHub query keywords
footprint = geojson_to_wkt(aoi)
products = api.query(footprint,
                     date=(start_date, end_date), #start and end dates from user input variables
                     platformname='Sentinel-2',   #limit to sentinel 2 multispectral sensor
                     cloudcoverpercentage=(0, 15))  #limit cloud cover to 15% of image

# download all results from the search
api.download_all(products)

# convert to Pandas DataFrame
products_df = api.to_dataframe(products)

# GeoJSON FeatureCollection containing footprints and metadata of the scenes
api.to_geojson(products)

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
api.to_geodataframe(products)

# Get basic information about the product: its title, file size, MD5 sum, date, footprint and
# its download url
#api.get_product_odata(<product_id>)


