'''
Copyright 2018 Kai-Wei Chang

This uses the number of occurrences and type of incidents to calculate a safety index for each sidewalk segment
'''

import pymysql

# connects to localhost MySQL server
db = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data_pkey', autocommit=True)
cursor = db.cursor()
cursor2 = db.cursor()

# define the score to decrement / incident type
type_score = {
    'BURGLARY': 3,
    'ASSAULT': 5,
    'CAR PROWL': 1,
    'HOMICIDE': 50,
    'ROBBERY': 1,
    'PICKPOCKET': 2,
    'THREATS': 3,
    'PURSE SNATCH': 2,
    'NARCOTICS': 3
}

# fetches unique sdw_id
sql_command = (
'''
    SELECT DISTINCT pkey
    FROM sidewalk_pkey; 
'''
)
num_entries = cursor.execute(sql_command)
i = 0

# for each sdw_id, count the type
for row in cursor:
    print('safety index', i, 'out of', num_entries)
    i += 1
    score = 100
    sql_command = (
    '''
        SELECT type
        FROM crime_reports 
        WHERE pkey = \'''' + str(row[0]) + '''\'
        ;
    '''
    )
    cursor2.execute(sql_command)

    # for each type at this location, subtracts from
    # type_score to get the safety index
    for row2 in cursor2:
        for k, v in type_score.items():
            if k in row2[0]:
                score -= v
    # makes sure no negative scores appear
    if score < 0:
        score = 0

    # updates the safety index to sidewalks table
    sql_command = (
    '''
        UPDATE sidewalk_pkey
        SET safety_index = ''' + str(score) + '''
        WHERE pkey = ''' + str(row[0]) + ''';
    '''
    )
    cursor2.execute(sql_command)

cursor.close()
cursor2.close()
db.close()
