'''
Copyright 2018 Kai-Wei Chang

This program utilizes pandas to create a new geojson file that stores sidewalk information in Seattle.
The information contained for each sidewalk includes:
    - sidewalk id (pkey)
    - geometry/location
    - safety index (calculated from occurrences and types of 911 reports)
    - all 911 reports associated with its type, year, month, and hour of day
    - incline of sidewalk
    - tree data associated with each sidewalk segment
    - condition index (calculated from issues of sidewalks)
    - condition reports associated with each sidewalk segment
    - bus stop information for each sidewalk segment

The geojson now looks like the following (with ALL_CAPS being the actual data):
{
    'type': 'FeatureCollection',
    'features:': [
        {
            'pkey': PKEY,
            'geometry': GEOMETRY_IN_LINESTRING,
            'properties': {
                'safety_index': SAFETY_INDEX,
                '911_reports': [{911_REPORT_0}, {911_REPORT_1}, ...],
                'incline': INCLINE,
                'trees': [{TREE_INFO_0}, {TREE_INFO_1}, ...],
                'condition_index': CONDITION_INDEX,
                'condition_reports': [{SDW_ISSUE_0}, {SDW_ISSUE_1}, ...],
                'bus_stops': [{BUS_STOP_0}, {BUS_STOP_1}, ...]
            }
            'type': 'Feature',
        },
        {
            ANOTHER_SIDEWALK_SEGMENT
        }
    ]
}
'''

import json
import pymysql
import pandas as pd
import sys


# connect to localhost MySQL server
db = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data_pkey', autocommit=True)
cursor = db.cursor()

# load all sidewalk segments
try:
    sidewalk_pkey_data = pd.read_json('sidewalks_incline.geojson')
except:
    sys.exit('Error while loading sidewalks_incline.geojson.')

# the main dictionary structure for our geojson
d = {'type': 'FeatureCollection', 'features':[]}

i = 0

# for each sidewalk segment in the open data portal
for i in range(0, len(sidewalk_pkey_data['features'])):
    print('adding geojson', i, 'out of', len(sidewalk_pkey_data['features']))

    # store all the crime incidents from our own SQL db
    crime_set = []
    sql_command = (
        '''
            SELECT type, year, month, hour
            FROM crime_reports
            WHERE pkey = ''' + str(sidewalk_pkey_data['features'][i]['properties']['pkey']) + '''
        '''
    )
    cursor.execute(sql_command)
    for k in cursor:
        crime_set.append({'type': k[0], 'year': k[1], 'month': k[2], 'hour': k[3]})

    # store all the trees from our own SQL db
    tree_set = []
    sql_command = (
        '''
            SELECT tree_id, genus
            FROM trees
            WHERE pkey = ''' + str(sidewalk_pkey_data['features'][i]['properties']['pkey']) + '''
        '''
    )
    cursor.execute(sql_command)
    for k in cursor:
        tree_set.append({'tree_id': k[0], 'genus': k[1]})

    # store all the sidewalk issues from our own SQL db
    condition_set = []
    sql_command = (
        '''
            SELECT type, height_diff
            FROM sidewalk_conditions
            WHERE pkey = ''' + str(sidewalk_pkey_data['features'][i]['properties']['pkey']) + '''
        '''
    )
    cursor.execute(sql_command)
    for k in cursor:
        condition_set.append({'type': k[0], 'height_diff': k[1]})

    # store all the bus stops from our own SQL db
    bus_stops_set = []
    sql_command = (
        '''
            SELECT stop_id, stop_name, accessibility_level, ada_landing_pad, awning, curb, curb_height
            FROM bus_stops
            WHERE pkey = ''' + str(sidewalk_pkey_data['features'][i]['properties']['pkey']) + '''
        '''
    )
    cursor.execute(sql_command)
    for k in cursor:
        bus_stops_set.append({'stop_id': k[0], 'stop_name': k[1], 'accessibility_level': k[2], 'ada_landing_pad': k[3],
                          'awning': k[4], 'curb': k[5], 'curb_height': k[6]})

    cursor.execute('SELECT * FROM sidewalk_pkey WHERE pkey = ' + str(sidewalk_pkey_data['features'][i]['properties']['pkey']))
    k = cursor.fetchone()

    # append all the data to our dictionary
    d['features'].append({'type': 'Feature',
                          'pkey': k[0],
                          'geometry': sidewalk_pkey_data['features'][i]['geometry'],
                          "properties": {'safety_index': k[8], '911_reports': crime_set,
                                         'incline': k[4], 'trees': tree_set, 'condition_index': k[9],
                                         'condition_reports': condition_set, 'bus_stops': bus_stops_set}})

# output our dictionary as json
dumped = json.dumps(d)

with open("sidewalks_data.geojson", "w") as f:
    f.write(dumped)
