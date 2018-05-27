'''
Copyright 2018 Kai-Wei Chang

This code inserts the data in sidewalks_incline.geojson to SQL database.  It uses the new primary key "pkey".

File(s) required:
    1. sidewalks_incline.geojson (contains the pkey and incline)
'''

import pymysql
import geopandas as gpd
import sys

# connect to localhost MySQL server
db = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data_pkey', autocommit=True)
cursor = db.cursor()

cursor.execute("DROP TABLE IF EXISTS sidewalk_pkey")
sql_command = '''
    CREATE TABLE sidewalk_pkey (
        pkey INT PRIMARY KEY NOT NULL, 
        streets_pkey INT, 
        name VARCHAR(50),
        side VARCHAR(2),
        incline INT,
        surface VARCHAR(15),
        width float,
        geometry TEXT,
        safety_index INT,
        quality_index INT
    );
'''
cursor.execute(sql_command)

# load sidewalk id dataset
try:
    sidewalk_pkey_data = gpd.read_file('sidewalks_incline.geojson')
except:
    sys.exit('Error while loading sidewalks_incline.geojson.')

for i in range(0, len(sidewalk_pkey_data.pkey)):
    print('pkey', i, 'out of', len(sidewalk_pkey_data.pkey))
    sql_command = '''
        INSERT INTO sidewalk_pkey VALUES (
            ''' + str(sidewalk_pkey_data.pkey[i]) + ''', 
            ''' + str(sidewalk_pkey_data.streets_pkey[i]) + ''', 
            \'''' + str(sidewalk_pkey_data.street_name[i]) + '''\', \'''' + str(sidewalk_pkey_data.side[i]) + '''\', 
            ''' + str(sidewalk_pkey_data.incline[i]) + ''', \'''' + str(sidewalk_pkey_data.surface[i]) + '''\', 
            ''' + str(sidewalk_pkey_data.width[i]) + ''', \'''' + str(sidewalk_pkey_data.geometry[i]) + '''\', null, null 
        );
    '''
    cursor.execute(sql_command)

cursor.execute('CREATE INDEX p_index ON sidewalk_pkey(pkey) USING HASH')
cursor.close()
db.close()