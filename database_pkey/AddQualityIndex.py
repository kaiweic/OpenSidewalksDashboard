'''
Copyright 2018 Kai-Wei Chang

This uses the number of issues to calculate a sidewalk quality index for each sidewalk segment
'''


import pymysql

issue_impact = 5

# connects to localhost MySQL server
db = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data_pkey', autocommit=True)
cursor = db.cursor()
cursor2 = db.cursor()

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
    print('quality index', i, 'out of', num_entries)
    i += 1
    score = 100
    sql_command = (
    '''
        SELECT *
        FROM sidewalk_conditions
        WHERE pkey = \'''' + str(row[0]) + '''\'
        ;
    '''
    )
    cursor2.execute(sql_command)

    # for each type at this location, subtracts a score for each issue
    for row2 in cursor2:
        score -= issue_impact

    # makes sure no negative scores appear
    if score < 0:
        score = 0

    # updates the safety index to sidewalks table
    sql_command = (
    '''
        UPDATE sidewalk_pkey
        SET quality_index = ''' + str(score) + '''
        WHERE pkey = ''' + str(row[0]) + ''';
    '''
    )
    cursor2.execute(sql_command)

cursor.close()
cursor2.close()
db.close()
