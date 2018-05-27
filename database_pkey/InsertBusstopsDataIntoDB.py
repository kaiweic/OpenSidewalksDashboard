'''
Copyright 2018 Kai-Wei Chang

This code matches each tuple in bus_stops database table to the pkey and inserts the data into SQL database.

File(s) required:
    1. sidewalks_incline.geojson (contains the pkey)
    2. bus stops sql table
'''

import pymysql
import geopandas as gpd
from shapely.geometry import Point, Polygon
import math
import sys

# connect to localhost MySQL server
db = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data_pkey', autocommit=True)
cursor = db.cursor()

cursor.execute("DROP TABLE IF EXISTS bus_stops")
sql_command = '''
    CREATE TABLE bus_stops (
        table_id INT PRIMARY KEY NOT NULL, 
        stop_id INT,
        stop_name VARCHAR(50),
        accessibility_level VARCHAR(10),
        ada_landing_pad VARCHAR(3),
        awning VARCHAR(3),
        curb VARCHAR(3),
        curb_height INT,
        pkey INT NOT NULL
    );
'''
cursor.execute(sql_command)

# load sidewalk id dataset
try:
    sidewalk_id_data = gpd.read_file('sidewalks_incline.geojson')
except:
    sys.exit('Error while loading sidewalks_incline.geojson')

# load dataset of interest
db_data = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data', autocommit=True)
cursor2 = db_data.cursor()
num_entries = cursor2.execute(
    ''' SELECT * FROM busstops '''
)

# center of city
center_coord = [-122.329237, 47.610541]

pieces = 200

# divide a circle into equal pieces
divided_conversion_coord = []
for i in range(0, pieces):
    divided_conversion_coord.append([math.cos(math.radians(360 / pieces * i)), math.sin(math.radians(360 / pieces * i))])

radius = 125 # km
divided_region = []
for i in range(0, pieces - 1):
    divided_region.append(
        Polygon([center_coord,
                 [center_coord[0] + divided_conversion_coord[i][0] * radius * 180 / (math.pi * 6367 * math.cos(center_coord[1])),
                  center_coord[1] + divided_conversion_coord[i][1] * radius * 180 / (math.pi * 6367)],
                 [center_coord[0] + divided_conversion_coord[i+1][0] * radius * 180 / (math.pi * 6367 * math.cos(center_coord[1])),
                  center_coord[1] + divided_conversion_coord[i+1][1] * radius * 180 / (math.pi * 6367)]]))

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

for i in range(0, len(sidewalk_id_data)):
    print('building', i, 'out of', len(sidewalk_id_data))
    if sidewalk_id_data.geometry[i] is not None:
        for j in range(0, pieces):
            if divided_region[j].intersects(sidewalk_id_data.geometry[i]):
                divided_sidewalk_id_data[j].append(i)

# for each entry in import_data
i = 0
for item in cursor2:
    print('bus stops processing', i, 'out of', num_entries)
    i += 1

    long = float(item[6])
    lat = float(item[5])
    point = Point(long, lat)

    # which region is this point in?
    for q in range(0, pieces):
        if divided_region[q].intersects(point):
            region_index = q
            break

    # code to match sidewalk id
    sqrt2 = math.sqrt(2)
    conversion_coord = [[1, 0], [1 / sqrt2, -1 / sqrt2], [0, -1], [-1 / sqrt2, -1 / sqrt2], [-1, 0],
                        [-1 / sqrt2, 1 / sqrt2], [0, 1], [1 / sqrt2, 1 / sqrt2]]

    radius_unit = 0.005  # if i = 1, radius = 5 m or 0.005 km

    # for all the radius
    for k in range(1, 21):  # 5 meters to 100 meters
        # creates a list to store the coordinates of polygon of this point with the radius given
        polygon_list = []
        # for all the directions
        for j in range(0, len(conversion_coord)):
            point_long = long + conversion_coord[j][0] * radius_unit * k * 180 / (math.pi * 6367 * math.cos(lat))
            point_lat = lat + conversion_coord[j][1] * radius_unit * k * 180 / (math.pi * 6367)
            polygon_list.append([point_long, point_lat])
        # creates the polygon
        point = Polygon(polygon_list)
        result = []

        for r in range(0, len(divided_sidewalk_id_data[region_index])):
            if point.intersects(sidewalk_id_data.geometry[divided_sidewalk_id_data[region_index][r]]):
                result.append(sidewalk_id_data.pkey[divided_sidewalk_id_data[region_index][r]])
        # in the case (which is quite often) that the coordinates given is in the middle of the street, both sidewalk
        # segments on the side would be equally likely to be included. To avoid messing up the sidewalk ID field in
        # database, select the first id by default. (This won't matter too much later on in the dashboard as we are
        # counting the number of incidents within a given region)
        if result:
            break
    if result:
        sql_command = (
                      'INSERT INTO bus_stops VALUES(' +
                      str(i + 1) + ', ' + str(item[0]) + ', \'' + str(item[1]) + '\', \'' + str(item[9]) + '\', \'' +
                      str(item[10]) + '\', \'' +str(item[12]) + '\', \'' +str(item[13]) + '\', ' + str(item[14]) + ', '
                      + str(result[0]) +
                      ');'
                      )
        print(sql_command)
        cursor.execute(sql_command)

cursor.execute('CREATE INDEX p_index ON bus_stops(pkey) USING HASH')
cursor.close()
db.close()
