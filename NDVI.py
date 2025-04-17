import os              #import os module to access files and folders
# import earthaccess      #import eartaccess module to access satellite data
import geopandas as gpd     #import geopandas to work with spatial data
import rasterio as rio      #import rasterio to work with raster data
import rasterio.merge       #import module to combine rasters
import shapely              #import shapely module to work with geometries
import pandas as pd         #import pandas module
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt




api = SentinelAPI(None, None, 'https://apihub.copernicus.eu/apihub/')   #sentinelsat login access
start_date=(input())         #set start date for image search user imput?
end_date= (input())          #set end date for image search user input?
corner_ref=                     #create 1km aoi from corner grid reference


# search by polygon, time, and SciHub query keywords
footprint = geojson_to_wkt(read_geojson('/path/to/map.geojson'))
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
api.get_product_odata(<product_id>)


