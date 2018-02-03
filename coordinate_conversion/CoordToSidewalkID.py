#!/usr/bin/env python
'''
By Kai-Wei Chang 2018

RUN WITH PYTHON 3.5

This code prompts the user for input of gps coordinates and a given radius and returns all the sidewalk segments within
the specified region by their sidewalk ID's (SDW id) from the Seattle Government sidewalk dataset.

You need all 5 shapefiles in the same folder.
Download from https://data-seattlecitygis.opendata.arcgis.com/datasets/ee6d0642d2a04e35892d0eab77d971d6_2
Click Download -> Shapefile
'''

import math
import re
import sys
from shapely.geometry import Polygon
import geopandas as gpd

if __name__ == '__main__':
    print('Please wait for the program to load in sidewalk data')
    print()
    try:
        all_data = gpd.read_file('Sidewalks.shp')
    except:
        sys.exit('Cannot locate the shapefiles. Make sure you have 5 of them in the same folder. See info on top.')

    while True:
        print('Please enter coordinates in the following format: long lat radius(in km) sidewalk_decription(yes/no)')
        print('                                             i.e. -122.333896 47.607177 0.1 yes')
        user_input = input()
        if not re.match(r'-?[0-9]*.[0-9]* -?[0-9]*.[0-9]* ([0-9]*.)?[0-9]* (yes|no)', user_input):
            print('please check your input format')
            print()
        else:
            user_input_list = user_input.split(" ")
            point_coord = [float(user_input_list[0]), float(user_input_list[1])]
            radius = float(user_input_list[2])
            if user_input_list[3] == 'yes':
                sidewalk_info = True
            else:
                sidewalk_info = False

            sqrt2 = math.sqrt(2)
            conversion_coord = [[1, 0], [1 / sqrt2, -1 / sqrt2], [0, -1], [-1 / sqrt2, -1 / sqrt2], [-1, 0],
                                [-1 / sqrt2, 1 / sqrt2], [0, 1], [1 / sqrt2, 1 / sqrt2]]

            polygon_list = []

            for i in range(0, len(conversion_coord)):
                long = point_coord[0] + conversion_coord[i][0] * radius * 180 / (math.pi * 6367 * math.cos(point_coord[1]))
                lat = point_coord[1] + conversion_coord[i][1] * radius * 180 / (math.pi * 6367)
                polygon_list.append([long, lat])

            point = Polygon(polygon_list)

            for i in range(0, all_data.UNITID.count()):
                if all_data.geometry[i] is not None:
                    if point.intersects(all_data.geometry[i]):
                        print(all_data.UNITID[i] + " " + (all_data.UNITDESC[i] if sidewalk_info else ''))
            print()
            print('finished!!')
            print()