'''
Copyright 2018 Kai-Wei Chang

This program matches sidewalk segments in Linestring to the existing sidewalk segments with SDW-ID.  It saves
the results back into the database in a new table.

Files: Sidewalks.shp, sidewalks_incline.geojson
'''


import pymysql
import geopandas as gpd
from shapely.geometry import Polygon
import math
import sys

# connect to localhost MySQL server
print('connecting to server ...')
db = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data', autocommit=True)
cursor = db.cursor()

cursor.execute("DROP TABLE IF EXISTS incline")
sql_command = '''
    CREATE TABLE incline (sdw_id CHAR(10) NOT NULL, pkey INT NOT NULL, incline INT NOT NULL);
'''
cursor.execute(sql_command)

print('loading data ...')
# load sidewalk id dataset
try:
    sidewalk_id_data = gpd.read_file('Sidewalks.shp')
except:
    sys.exit('Cannot locate the shapefiles. Make sure you have 5 of them in the same folder. See info on top.')
# load dataset of interest (in geojson)
try:
    imported_data = gpd.read_file('sidewalks_incline.geojson')
except:
    sys.exit('Cannot locate the shape files that contains info to be matched to ID\'s')

# center of city
center_coord = [-122.329237, 47.610541]

# divide a circle into 16 equal pieces
print('dividing regions ...')
divided_conversion_coord = []

pieces = 200
for i in range(0, pieces): # 0 ~ 15
    divided_conversion_coord.append([math.cos(math.radians(360 / pieces * i)), math.sin(math.radians(360 / pieces * i))])

radius = 125 # km
divided_region = []
for i in range(0, pieces - 1): # 0 1, 1 2, ..., 14 15
    divided_region.append(
        Polygon([center_coord,
                 [center_coord[0] + divided_conversion_coord[i][0] * radius * 180 / (math.pi * 6367 * math.cos(center_coord[1])),
                  center_coord[1] + divided_conversion_coord[i][1] * radius * 180 / (math.pi * 6367)],
                 [center_coord[0] + divided_conversion_coord[i+1][0] * radius * 180 / (math.pi * 6367 * math.cos(center_coord[1])),
                  center_coord[1] + divided_conversion_coord[i+1][1] * radius * 180 / (math.pi * 6367)]]))
# 15 0
divided_region.append(
    Polygon([center_coord,
             [center_coord[0] + divided_conversion_coord[pieces - 1][0] * radius * 180 / (math.pi * 6367 * math.cos(center_coord[1])),
              center_coord[1] + divided_conversion_coord[pieces - 1][1] * radius * 180 / (math.pi * 6367)],
             [center_coord[0] + divided_conversion_coord[0][0] * radius * 180 / (math.pi * 6367 * math.cos(center_coord[1])),
              center_coord[1] + divided_conversion_coord[0][1] * radius * 180 / (math.pi * 6367)]]))

# each entry correspond to a list of all data in that section of circle
divided_sidewalk_id_data = []
for i in range(0, pieces):
    divided_sidewalk_id_data.append([])

for i in range(0, sidewalk_id_data.UNITID.count()):
    print(i, ' out of ', sidewalk_id_data.UNITID.count())
    if sidewalk_id_data.geometry[i] is not None:
        for j in range(0, pieces):
            if divided_region[j].intersects(sidewalk_id_data.geometry[i]):
                divided_sidewalk_id_data[j].append(i)

# for each entry in import_data
print('processing data ...')
for i in range(0 , imported_data.count().streets_pkey):
    if imported_data.geometry[i] is None:
        continue

    incline_data_linestring = imported_data.geometry[i]#.buffer(0.0001)

    # which region is this point in?
    for q in range(0, pieces):
        if divided_region[q].intersects(incline_data_linestring):
            region_index = q
            break

    # match the incline_linestring with our sidewalk id's
    '''
        NOTE: The original dataset has negative incline data.  This program turns all incline data into positive 
        by abs().
    '''
    for r in range(0, len(divided_sidewalk_id_data[region_index])):
        if incline_data_linestring.intersects(sidewalk_id_data.geometry[divided_sidewalk_id_data[region_index][r]]):
            sql_command = (
                'INSERT INTO incline ' +
                'VALUES (\'' + str(sidewalk_id_data.UNITID[divided_sidewalk_id_data[region_index][r]])
                + '\', ' + str(imported_data.pkey[i]) + ', ' + str(abs(imported_data.incline[i])) + ');'
            )
            print(i, ' out of ', imported_data.count().streets_pkey, ': ' ,sql_command)
            cursor.execute(sql_command)

cursor.close()
db.close()
