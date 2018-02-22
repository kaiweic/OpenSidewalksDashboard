import pymysql
import geopandas as gpd
from shapely.geometry import Point, Polygon
import math
import json
import sys

# connect to localhost MySQL server
db = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data', autocommit=True)
cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS crime")
sql_command = '''
    CREATE TABLE crime (id INT PRIMARY KEY NOT NULL, type CHAR(30) NOT NULL, full_time CHAR(19) NOT NULL, 
                        year INT NOT NULL, month INT NOT NULL, hour INT NOT NULL, location CHAR(60) NOT NULL, 
                        sdw_id CHAR(10) NOT NULL);
'''
cursor.execute(sql_command)

# load sidewalk id dataset
try:
    sidewalk_id_data = gpd.read_file('Sidewalks.shp')
except:
    sys.exit('Cannot locate the shapefiles. Make sure you have 5 of them in the same folder. See info on top.')
# load dataset of interest (in json)
try:
    imported_data = json.load(open('crime.json'))
except:
    sys.exit('Cannot locate the json files that contains info to be matched to ID\'s')

# center of city
center_coord = [-122.329237, 47.610541]

# divide a circle into 16 equal pieces
divided_conversion_coord = []
for i in range(0, 16): # 0 ~ 15
    divided_conversion_coord.append([math.cos(math.radians(22.5 * i)), math.sin(math.radians(22.5 * i))])

radius = 125 # km
divided_region = []
for i in range(0, 15): # 0 1, 1 2, ..., 14 15
    divided_region.append(
        Polygon([center_coord,
                 [center_coord[0] + divided_conversion_coord[i][0] * radius * 180 / (math.pi * 6367 * math.cos(center_coord[1])),
                  center_coord[1] + divided_conversion_coord[i][1] * radius * 180 / (math.pi * 6367)],
                 [center_coord[0] + divided_conversion_coord[i+1][0] * radius * 180 / (math.pi * 6367 * math.cos(center_coord[1])),
                  center_coord[1] + divided_conversion_coord[i+1][1] * radius * 180 / (math.pi * 6367)]]))
# 15 0
divided_region.append(
    Polygon([center_coord,
             [center_coord[0] + divided_conversion_coord[15][0] * radius * 180 / (math.pi * 6367 * math.cos(center_coord[1])),
              center_coord[1] + divided_conversion_coord[15][1] * radius * 180 / (math.pi * 6367)],
             [center_coord[0] + divided_conversion_coord[0][0] * radius * 180 / (math.pi * 6367 * math.cos(center_coord[1])),
              center_coord[1] + divided_conversion_coord[0][1] * radius * 180 / (math.pi * 6367)]]))

# each entry correspond to a list of all data in that section of circle
divided_sidewalk_id_data = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]];
for i in range(0, sidewalk_id_data.UNITID.count()):
    if sidewalk_id_data.geometry[i] is not None:
        for j in range(0, 16):
            if divided_region[j].intersects(sidewalk_id_data.geometry[i]):
                divided_sidewalk_id_data[j].append(i)

# for each entry in import_data
for i in range(0 , len(imported_data['data'])):
    long = float(imported_data['data'][i][22])
    lat = float(imported_data['data'][i][23])
    point = Point(long, lat)

    # which region is this point in?
    for q in range(0, 16):
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
                result.append(sidewalk_id_data.UNITID[divided_sidewalk_id_data[region_index][r]])
        # in the case (which is quite often) that the coordinates given is in the middle of the street, both sidewalk
        # segments on the side would be equally likely to be included. To avoid messing up the sidewalk ID field in
        # database, select the first id by default. (This won't matter too much later on in the dashboard as we are
        # counting the number of incidents within a given region)
        if result:
            break
    if result:
        sql_command = (
                      'INSERT INTO crime (id, type, full_time, year, month, hour, location, sdw_id) ' +
                      'VALUES (' + str(i + 1) + ', \'' + imported_data['data'][i][14] + '\', \'' + imported_data['data'][i][16] +
                      '\', ' + imported_data['data'][i][16][0:4] + ', ' + imported_data['data'][i][16][5:7] + ', '
                      + imported_data['data'][i][16][11:13] + ', \'' + imported_data['data'][i][18] + '\', \'' + result[0] + '\');'
                      )
        print(sql_command)
        cursor.execute(sql_command)
cursor.close()
db.close()
