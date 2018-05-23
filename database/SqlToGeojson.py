'''
Copyright 2018 Kai-Wei Chang

This program utilizes pandas to create a new geojson file that stores sidewalk information in Seattle.
The information contained for each sidewalk includes:
    - sidewalk id
    - geometry/location
    - safety index (calculated from occurrences and types of 911 reports)
    - all 911 reports associated with its type, year, month, and hour of day
    - incline of sidewalk
'''


import json
import pymysql
import pandas as pd
import decimal

# connect to localhost MySQL server
db = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data', autocommit=True)
cursor = db.cursor()
cursor2 = db.cursor()

# import the opendata from Seattle Data Open Portal
sidewalk_raw_data = pd.read_json('Sidewalks.geojson')

# the main dictionary structure for our geojson
d = {'type': 'FeatureCollection', 'features':[]}

# for each sidewalk segment in the open data portal
for i in range(0, sidewalk_raw_data['features'].size):
    print('adding', i, 'out of', sidewalk_raw_data['features'].size)

    # fetch the safety index for this sidewalk from our own SQL db
    sql_command = (
        '''
            SELECT safety_index
            FROM sidewalks 
            WHERE sdw_id = \'''' + sidewalk_raw_data['features'][i]['properties']['UNITID'] + '''\'
        '''
    )
    cursor.execute(sql_command)
    safety_index = cursor.fetchall()
    if len(safety_index) is not 0:
        safety_index = safety_index[0][0]
    else :
        safety_index = None

    # store all the crime incidents from our own SQL db
    crime_set = []
    sql_command = (
        '''
            SELECT type, year, month, hour
            FROM crime
            WHERE sdw_id = \'''' + sidewalk_raw_data['features'][i]['properties']['UNITID'] + '''\'
        '''
    )
    cursor2.execute(sql_command)
    for k in cursor2:
        crime_set.append({'type': k[0], 'year': k[1], 'month': k[2], 'hour': k[3]})

    # add in the incline data
    sql_command = (
        '''
            SELECT AVG(incline)
            FROM incline
            WHERE sdw_id = \'''' + sidewalk_raw_data['features'][i]['properties']['UNITID'] + '''\'
        '''
    )
    cursor2.execute(sql_command)
    incline = cursor2.fetchall()
    incline = incline[0][0]

    # append all the data to our dictionary
    d['features'].append({'type': 'Feature',
                          'id': sidewalk_raw_data['features'][i]['properties']['UNITID'],
                          'geometry': sidewalk_raw_data['features'][i]['geometry'],
                          "properties": {'911_report_index': safety_index, '911_reports': crime_set,
                                         'incline': str(incline) if incline is not None else incline}})

# output our dictionary as json
dumped = json.dumps(d)

with open("sidewalks_data.geojson", "w") as f:
    f.write(dumped)
