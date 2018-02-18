import pymysql
import geopandas as gpd
from shapely.geometry import Polygon
import math
import json
import sys

# connect to localhost MySQL server
db = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data', autocommit=True)
cursor = db.cursor()
#cursor.execute("DROP TABLE IF EXISTS crime")
sql_command = '''
    CREATE TABLE crime (id INT PRIMARY KEY NOT NULL, type CHAR(30) NOT NULL, year INT NOT NULL, date CHAR(11) NOT NULL,
                        time CHAR(8) NOT NULL, hour INT NOT NULL, location CHAR(60) NOT NULL, sdw_id CHAR(10) NOT NULL);
'''
#cursor.execute(sql_command)

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

# for each entry in import_data
for i in range(0, len(imported_data['data'])):
    # print('id:', (i + 1))
    '''
    print('type:', imported_data['data'][i][14])
    print('year:', int(imported_data['data'][i][15][:4]))
    print('date:', imported_data['data'][i][15][:10])
    print('time:', imported_data['data'][i][15][11:])
    print('hour:', int(imported_data['data'][i][15][11:13]))
    print('location:', imported_data['data'][i][16])
    '''
    long = float(imported_data['data'][i][20])
    lat = float(imported_data['data'][i][21])

    # code to match sidewalk id
    sqrt2 = math.sqrt(2)
    conversion_coord = [[1, 0], [1 / sqrt2, -1 / sqrt2], [0, -1], [-1 / sqrt2, -1 / sqrt2], [-1, 0],
                        [-1 / sqrt2, 1 / sqrt2], [0, 1], [1 / sqrt2, 1 / sqrt2]]

    radius_unit = 0.005  # if i = 1, radius = 5 m or 0.005 km

    # for all the radius
    for k in range(1, 51):  # 5 meters to 250 meters
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

        for m in range(0, sidewalk_id_data.UNITID.count()):
            if sidewalk_id_data.geometry[m] is not None:
                if point.intersects(sidewalk_id_data.geometry[m]):
                    result.append(sidewalk_id_data.UNITID[m])
        # in the case (which is quite often) that the coordinates given is in the middle of the street, both sidewalk
        # segments on the side would be equally likely to be included. To avoid messing up the sidewalk ID field in
        # database, select the first id by default. (This won't matter too much later on in the dashboard as we are
        # counting the number of incidents within a given region)
        if result:
            break
    if result:
        sql_command = (
                      'INSERT INTO crime (id, type, year, date, time, hour, location, sdw_id) ' +
                      'VALUES (' + str(i + 1) + ', \'' + imported_data['data'][i][14] + '\', ' + imported_data['data'][i][15][:4] +
                      ', \'' + imported_data['data'][i][15][:10] + '\', \'' + imported_data['data'][i][15][11:] + '\', ' +
                      str(int(imported_data['data'][i][15][11:13])) + ', \'' + imported_data['data'][i][16] + '\', \'' + result[0] + '\');'
                      )
        print(sql_command)
        cursor.execute(sql_command)
cursor.close()
db.close()
