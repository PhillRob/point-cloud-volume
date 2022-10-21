#!/usr/bin/python3
import sys
import requests
from time import sleep
import random
import getopt
import json
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from pathlib import Path

# todo: collection of params is inverted

def main(argv):

    urlprefix = "https://public-api.dronedeploy.com/v2/tiles/"
    urlendpoint = "/volume/POLYGON(("
    urlparams = "))?baseplane_type="
    urlapikey = "&api_key="

    geojsonFilename = 'empty'
    plan_id = 'empty'
    baseplane_type = 'empty'
    api_key = 'empty'
    poly_start = 1
    poly_end = 100

    # check if start and end are given
    try:
        opts, args = getopt.getopt(argv, "hi:p:b:a:s:e:", ["geojson=", "plan=", "baseplane=", "api=", "start=", "end="])

    except getopt.GetoptError:
        print('Please use the follwing command to query the DD measurements API for a subset of features. volume-query.py -i <geojson_file> -p <plan_id> -b <baseplane_type> -a <api_key> -s <poly_start> -e <poly_end>')

        try:
            opts, args = getopt.getopt(argv, "hi:p:b:a:", ["geojson=", "plan=", "baseplane=", "api="])
            print('Please use the follwing command to query the DD measurements API for a all features. volume-query.py -i <geojson_file> -p <plan_id> -b <baseplane_type> -a <api_key>')

        except getopt.GetoptError:
            print('volume-query.py -i <geojson_file> -p <plan_id> -b <baseplane_type> -a <api_key>')
            sys.exit(2)

        for opt, arg in opts:
            if opt == '-h':
                print('Please use the follwing command to query the DD measurements API for a all features. volume-query.py -i <geojson_file> -p <plan_id> -b <baseplane_type> -a <api_key>')
                sys.exit()
            elif opt in ("-i", "--geojson"):

                path = Path(arg)
                if path.is_file():
                    print(f'The file {arg} exists')
                    geojsonFilename = arg
                else:
                    print(f'The file {arg} does not exist')
                    sys.exit(2)
            elif opt in ("-p", "--plan"):
                plan_id = arg
            elif opt in ("-b", "--baseplane"):
                baseplane_type = arg
            elif opt in ("-a", "--api"):
                api_key = arg

        print('Input file is:', geojsonFilename)
        print('Plan ID is:', plan_id)
        print('Baseplane is:', baseplane_type)
        print('API key is:', api_key)
        print('Start at:', poly_start)
        print('End at:', poly_end)

    for opt, arg in opts:
        if opt == '-h':
            print('Please use the follwing command to query the DD measurements API for a subset of features. volume-query.py -i <geojson_file> -p <plan_id> -b <baseplane_type> -a <api_key> -s <poly_start> -e <poly_end>')
            sys.exit()
        elif opt in ("-i", "--geojson"):

            path = Path(arg)
            if path.is_file():
                print(f'The file {arg} exists')
                geojsonFilename = arg
            else:
                print(f'The file {arg} does not exist')
                sys.exit(2)
        elif opt in ("-p", "--plan"):
            plan_id = arg
        elif opt in ("-b", "--baseplane"):
            baseplane_type = arg
        elif opt in ("-a", "--api"):
            api_key = arg
        elif opt in ("-s", "--start"):
            poly_start = arg
        elif opt in ("-e", "--end"):
            poly_end = arg
    print('Input file is:', geojsonFilename)
    print('Plan ID is:', plan_id)
    print('Baseplane is:', baseplane_type)
    print('API key is:', api_key)

    f = open(geojsonFilename)
    data = json.load(f)
    poly_end = len(data['features'])
    print('Start at:', poly_start)
    print('End at:', len(data['features']))

    # functions
    def getUrlFriendlyCoords(coordinates):
        result = ""

        for c in coordinates:
            for c2 in c:
                for c3 in c2:
                    result = (result + str(c3[0]) + "%20" + str(c3[1])) + ","
        result = result[:-1]
        return result

    def callAPI(url):
        #print("Calling API: " + url)
        resp = requests.get(url)
        # Wait a small period to stop any issues with rate limits on the API
        randWait = random.uniform(0.01,0.5)
        print('I am waiting '+str(randWait), 'sec between the queries to avoid stressing the API. ')
        sleep(randWait)

        if resp.status_code == 200:
            jsonResponse = resp.json()
            print(jsonResponse)
            return [jsonResponse["cut"], jsonResponse["fill"], jsonResponse["volume"]]
        elif resp.status_code == 400:
            jsonResponse = resp.json()
            print(jsonResponse)
            return ["NA", "NA", "NA"]
        else:
            jsonResponse = resp.content
            print(jsonResponse)
            return ["NA", "NA", "NA"]

    f = open(geojsonFilename)
    data = json.load(f)

    # get bounds of drone image
    planurl = "https://public-api.dronedeploy.com/v2/plans/" + plan_id+"?api_key="+api_key
    planresp = requests.get(planurl)
    planjsonResponse = planresp.json()
    plandf = pd.DataFrame(planjsonResponse['geometry'])
    planlist = plandf.values.tolist()
    invplanlist = []

    for c in planlist:
        coords = (c[1], c[0])
        invplanlist.append(coords)

    poly1 = Polygon(invplanlist)
    features = data["features"]


    count=0
    for i in data:
        if (i == "features"):
            for j in data[i]:
               count=count+1
               if count >= int(poly_start) and count <= int(poly_end):
                #print(j)
                datacoords = j['geometry']['coordinates'][0]
                flat_list = []
                for sublist in datacoords:
                    for item in sublist:
                        flat_list.append(item)

                dataPoly = Polygon(flat_list)

                intersect = poly1.intersection(dataPoly)
                print(intersect)
                if not intersect.is_empty:
                    print('intersecting polygons')
                    apiurl = urlprefix + plan_id + urlendpoint + getUrlFriendlyCoords(j["geometry"]["coordinates"]) + urlparams + baseplane_type + urlapikey + api_key
                    result = callAPI(apiurl)

                    j["properties"]["cut"] = result[0]
                    j["properties"]["fill"] = result[1]
                    j["properties"]["volume"] = result[2]
                else:
                    #print('NON-intersecting polygons')
                    j["properties"]["cut"] = 'NA'
                    j["properties"]["fill"] = 'NA'
                    j["properties"]["volume"] = 'NA'
            else:
                print('No')

    outputFilename = geojsonFilename.replace(".geojson", "_" + plan_id + "_" + baseplane_type + "_"+str(poly_start) + "_" + str(poly_end)+".geojson")
    print(outputFilename)
    with open(outputFilename, 'w') as fp:
        json.dump(data, fp, indent=4)

    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])

