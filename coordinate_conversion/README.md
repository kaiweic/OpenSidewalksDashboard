# Description
This code prompts the user for input of gps coordinates and a given radius and returns all the sidewalk segments within
the specified region by their sidewalk ID's (SDW id) from the Seattle Government sidewalk dataset.

# Setup
You need all 5 shapefiles in the same folder.
- Download Shapefile from https://data-seattlecitygis.opendata.arcgis.com/datasets/ee6d0642d2a04e35892d0eab77d971d6_2
  (click Download -> Shapefile)
- Unzip the file and put all 5 shapefiles into the same folder as your CoordToSidewalkID.py file
- Make sure you have python 3.5 and shapely and geopandas

# Running the app
- Switch to the directory of your CoordToSidewalkID.py file
- Run: `python CoordToSidewalkID.py`
    Note: If you have both python 2 and python 3, make sure you are using python 3. You may need to check your
          environment variable. It would usually be `python3`.

