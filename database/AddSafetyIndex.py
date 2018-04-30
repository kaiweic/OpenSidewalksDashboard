import pymysql

# connects to localhost MySQL server
db = pymysql.connect(host='localhost', user='kevin', passwd='kevin', db='sidewalk_data', autocommit=True)
cursor = db.cursor()

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
    SELECT DISTINCT sdw_id
    FROM sidewalks; 
'''
)
cursor.execute(sql_command)

# for each sdw_id, counts the type
for row in cursor:
    score = 100
    sql_command = (
    '''
        SELECT type
        FROM crime
        WHERE sdw_id = \'''' + row[0] + '''\'
        ;
    '''
    )
    cursor2 = db.cursor()
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
        UPDATE sidewalks
        SET safety_index = ''' + str(score) + '''
        WHERE sdw_id = \'''' + row[0] + '''\'
    '''
    )
    print(row[0], score)
    cursor2.execute(sql_command)
    cursor2.close()

cursor.close()
db.close()
