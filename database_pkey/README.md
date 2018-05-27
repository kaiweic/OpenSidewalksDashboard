## Code for creating our geojson file

### All code and data can be found at this [link](). The geojson we produced is called [sidewalks_data.geojson]().

AddQualityIndex.py: Adds the sidewalk quality index to SQL database based on the sidewalk observations.

AddSafetyIndex.py: Adds the safety index to SQL database based on the 911 reports.

BuildDB.py: Code that executes all files in this folder.

InsertBusstopsDataIntoDB.py: Inserts bus stop info into SQL database.

InsertCrimeDataToDB.py: Inserts 911 reports to SQL database.

InsertObservationDataToDB.py: Inserts sidewalk observation data into SQL database.

InsertPkeyToDB.py: Inserts the pkey and geometry (in shape) of each sidewalk segment into SQL database.

InsertTreeDataIntoDB.py: Inserts tree info into SQL database.

SqlToGeojson.py: Extracts data from SQL database and store them into GeoJson format. Each entry is a sidewalk segment with all the properties associated with it.
