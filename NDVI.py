import os              #import os module to access files and folders
import geopandas as gpd     #import geopandas to work with spatial data
import rasterio as rio      #import rasterio to work with raster data
import rasterio.merge       #import module to combine rasters
from rasterio.mask import mask
import shapely as shp             #import shapely module to work with geometries
from geopy import Point
from geopy.distance import distance
import pyproj
from shapely.geometry import Polygon
from cdsetool.query import query_features
from cdsetool.credentials import Credentials, validate_credentials
from cdsetool.download import download_features
import json
import zipfile
import glob
import numpy as np
import matplotlib.pyplot as plt

credentials = Credentials()   # cdsetool login access using .netrc file (must only contain the cdsetool login data)
print(validate_credentials(username=None, password=None)) # validates credentials against .netrc


print("enter search start date in format yyyymmdd")
start_date=input()        # set start date for image search user input?
print("enter search end date in format yyyymmdd")
end_date=input()          # set end date for image search user input?
start_date = start_date[:4] + "-" + start_date[4:6] + "-" + start_date[6:] + "T00:00:00Z" # reformat for sentinel search
end_date = end_date[:4] + "-" + end_date[4:6] + "-" + end_date[6:] + "T23:59:59Z"



corner_grid=input("enter easting, northings for an OS 1km square e.g. 604000 279000").split()  # input of corner grid, split into list
corner_grid_x= int(corner_grid[0])  # easting of corner grid
corner_grid_y= int(corner_grid[1])  # northing of corner grid

crs_OS = pyproj.Proj(init='EPSG:27700')  # set variable with projected OS ctm
crs_wgs84 = pyproj.Proj(init='EPSG:4326')  # set variable with lat long ctm
corner_grid_lon_lat = pyproj.transform(crs_OS, crs_wgs84, corner_grid_x, corner_grid_y)  # convert corner grid inputs to long lat
crs_NDVI="EPSG:32630"

#create square polygon off corner grid reference
p1= Point(corner_grid_lon_lat[1], corner_grid_lon_lat[0])  # set corner point in lat lon (reverse of transform)
p2= distance(kilometers=1).destination((p1), bearing=0)  # set next corner location 1km North
p3 = distance(kilometers=1).destination((p2), bearing=90)   # set next corner location 1km East
p4 = distance(kilometers=1).destination((p3), bearing=180)   # set next corner location 1km South
p0 = p1     # set a p0 to close the polygon with the same coordinates as the start point
points = [(p.longitude, p.latitude) for p in [p1,p2,p3,p4, p0]]  # convert points to lat lon explicit to create polygon
aoi_square = Polygon(points)                         # create polygon using the 4 corner points

aoi_gdf = gpd.GeoDataFrame([{'geometry': aoi_square}], crs="EPSG:4326")
aoi_wkt = shp.to_wkt(aoi_square)   # convert km_square to a wkt which is needed for the cdsetool area search

#search copernicus data collection by polygon, time, sensor, level 2 data
datasets = query_features("SENTINEL-2",{
    "startDate":start_date,
    "completionDate":end_date,
    "geometry":aoi_wkt,
    "processingLevel":"S2MSI2A"})

full_square_cover = []  # setup empty list for following loop
for d in datasets:  # loop through datasets to filter for aoi total coverage
    datasets_str=json.dumps(d['geometry'])  # convert geojson dictionary to str
    footprint = shp.from_geojson(datasets_str)  # convert to shapely object
    cloudcover = d['properties']['cloudCover']  # find cloud cover from the properties in metadata
    if footprint.contains(aoi_square) and cloudcover<=20:  # for loop to check area of interest against datasets for full spatial coverage and less than 10% cloudcover
        full_square_cover.append(d)     # appends any datasets the full_square_cover list

print(full_square_cover[0:2])  # prints first 3 results
print(len(full_square_cover))  # prints number of filtered datasets that cover aoi

square_selected = full_square_cover[0]  # selects first file from the list
selected_title=square_selected['properties']['title']  # find title of the selected file from metadata
sentinel_files_downloads='sentinel_files/' + selected_title   # creates a variable with name for the proposed directory
os.makedirs(sentinel_files_downloads, exist_ok=True)   # makes a directory and checks if it already exists

# download files to directory
downloads = download_features([square_selected], sentinel_files_downloads, {"concurrency":1})
for id in downloads:
    print(f"feature {id} downloaded")


zipped_file=zipped_file = os.path.join(sentinel_files_downloads, selected_title + ".zip")   # store location of downloaded zip
unzipped_files = os.path.join("sentinel_unzipped", selected_title[0:20]) # create directory for unzipped files
os.makedirs(unzipped_files, exist_ok=True)

with zipfile.ZipFile(zipped_file, 'r') as zip_ref:   # extract zipped data
    zip_ref.extractall(unzipped_files)

B08_path="sentinel_unzipped/**/*B08_10m.jp2"  # find path for band 8 and store to NIR variable
B08_NIR=glob.glob(B08_path, recursive=True)

B04_path="sentinel_unzipped/**/*B04_10m.jp2"  # find path for band 4 and store to Red variable
B04_RED=glob.glob(B04_path, recursive=True)

# taken from (https://developers.planet.com/docs/planetschool/calculate-an-ndvi-in-python/)
np.seterr(divide='ignore', invalid='ignore')  # allow division by zero

aoi_projected=aoi_gdf.to_crs(crs_NDVI)  # reproject the area of interest to match the sentinel raster projection

def band_processing(band_select, aoi_polygon):
    """
    opens the relevant band and masks to the area of interest, converts output to float type
    :param band_select: the chosen band (in this case NIR or RED)
    :param aoi_polygon: the area of interest, a 1km square
    :return: the band from the sentinel image masked to the area of interest with the affine transformation info
    """

    with rio.open(band_select) as band:
        masked_band, out_transform = mask(band, [aoi_polygon], crop=True)
        masked_band = masked_band[0].astype(float)
    return masked_band, out_transform

aoi_projected_geom = aoi_projected.geometry.iloc[0]  # access the single geometry in the gdf

NIR, out_transform = band_processing(B08_NIR[0], aoi_projected_geom)
RED, _ = band_processing(B04_RED[0], aoi_projected_geom)
ndvi = np.where((NIR + RED) == 0, 0, (NIR - RED) / (NIR + RED))  # calculate ndvi, avoiding division of zeros

# adapted this question: https://www.reddit.com/r/learnpython/comments/136yorw/using_fstrings_with_a_list/
ndvi_output = f"ndvi_output_{'_'.join(corner_grid)}.tif"  # set the filename
width, height=ndvi.shape  # set the height and width of the image to variables

with rasterio.open(ndvi_output, 'w', driver='GTiff', height=height, width=width, count=1, dtype='float64', crs=crs_NDVI,  transform=out_transform) as dst:
    dst.write(ndvi,1)  # write the ndvi data to geotiff


# Open the NDVI raster file
with rasterio.open(ndvi_output) as dataset:
    ndvi_data = dataset.read(1)  # Read the first band (NDVI values)
    xmin, ymin, xmax, ymax = dataset.bounds  # Get the raster bounds


fig, ax = plt.subplots(figsize=(10, 10), dpi=300)  # Plot the NDVI data
cax = ax.imshow(ndvi_data, cmap='RdYlGn', origin='upper', extent=[xmin, ymin, xmax, ymax])  # set the colour map and extent
cbar = fig.colorbar(cax, ax=ax, shrink=0.6, aspect=10)  # Add a colorbar
cbar.set_label('NDVI')  # Add a label
ax.set_title('NDVI Map for 1Km Square')  # Add a title



output_image_path = f"ndvi_{'_'.join(corner_grid)}.png"  # save the output to a png image
plt.savefig(output_image_path, format='png', dpi=300, bbox_inches='tight')
plt.close()  # close the plot
print(f"Map saved as {output_image_path}")  # confirmatory statement of image output name'
