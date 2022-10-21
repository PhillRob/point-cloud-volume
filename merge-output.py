

#!/usr/bin/python3
import pandas as pd
import glob
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from shapely.geometry import Polygon
import json
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
# import pysal as ps
# from pysal.contrib.viz import mapping as maps
from shapely import wkt
# matplotlib.use('TkAgg')

# get data
dfs = [] # an empty list to store the data frames`
StartDir = '/Users/philipp/BPLA Dropbox/03 Planning/DN-Dumping Detection-1087/05_Output/Digitisation/Version-3/DD-lowest'

json_pattern = os.path.join(StartDir,'*.geojson')
file_list = glob.glob(json_pattern)
len(file_list)

for file in file_list:
    data = gpd.read_file(file, lines=True) # read data frame from json file
    dfs.append(data) # append the data frame to the list

# concatenate and format
piles = pd.concat(dfs)
piles['str_geom'] = piles['geometry'].apply(wkt.dumps)
piles['FIDint'] = piles['fid'].astype('int64')
len(piles)

# filter NA's for the cut
piles = piles[(piles.cut != 'NA')]
len(piles)
piles['cut'] = piles['cut'].astype('float64')
piles['volume'] = piles['volume'].astype('float64')

pilesNoNA = piles[(~piles['cut'].isnull())]

len(pilesNoNA)
pilesNoNA['Type'].value_counts()

#piles.to_file(StartDir+"/piles-west-lowest.shp")

# filter for duplicate geometry
pilesNoNA['str_geom_d'] = pilesNoNA.duplicated(subset=['str_geom'], keep=False)
pilesNoNA['str_geom_d'].value_counts()

# unique polygons
pilesNoNANoDup = pilesNoNA[pilesNoNA.str_geom_d == False]
len(pilesNoNANoDup)

pilesNoNADup = pilesNoNA[pilesNoNA.str_geom_d == True]
len(pilesNoNADup)
len(pilesNoNADup.str_geom.unique().tolist())

pilesNoNADupMax = pilesNoNADup.groupby('str_geom', group_keys=False).agg(max)
len(pilesNoNADupMax)

pilesNoNANoDupMax = pilesNoNADup[pilesNoNADup['cut'].isin(list(pilesNoNADupMax['cut']))]
len(pilesNoNANoDupMax)

final = pilesNoNANoDup.append(pilesNoNANoDupMax)
len(final)

final['finalcut'] = final.duplicated(subset=['cut'], keep='first')
final['finalcut'].value_counts()
final = final[final.finalcut == False]
final['area']=final['geometry'].to_crs({'init': 'epsg:32638'}).map(lambda p: p.area)

# output
final['Type'].value_counts()
final.groupby('Type', group_keys=False).agg(sum)['cut']
final.groupby('Type',group_keys=False).agg(sum)['volume']
# final.groupby('Type',group_keys=False).agg(sum)['fill']

final.groupby('Type',group_keys=False).agg(sum)['area']

# plt.hist(final['cut'], bins = 300)
# plt.show()

# final.to_file(StartDir+"/piles-west-lowest-nodubs.shp")






#LReg on small data sets only
toP = gpd.read_file('/Users/philipp/BPLA Dropbox/03 Planning/DN-Dumping Detection-1087/05_Output/Digitisation/Version-4-Worldview3/Final_New_Sat/Final_New_sat.geojson', lines=True)

toP['Type']=toP['Type'].str.lower()
toP['Type'].value_counts()

final['perimeter']=final['geometry'].to_crs({'init': 'epsg:32638'}).map(lambda p: p.length)


final['area']=final['geometry'].to_crs({'init': 'epsg:32638'}).map(lambda p: p.area)

finalSmall = final[final['perimeter'] < 100]
finalSmall = finalSmall[finalSmall['area'] > ]
# final['area'].describe()

x = np.array(finalSmall['area']).reshape((-1, 1))

# x = np.array(finalSmall['perimeter']).reshape((-1, 1))
y = np.array(finalSmall['cut'])

reg = LinearRegression().fit(x,y)
reg.score(x,y)
reg.coef_
reg.intercept_

plt.plot(reg)
plt.plot(x, y, 'ro')
plt.show(block=True)


toP['area']=toP['geometry'].to_crs({'init': 'epsg:32638'}).map(lambda p: p.area)
toP.groupby('Type',group_keys=False).agg(sum)['area']

# predict
y_pred = reg.predict(np.array(toP['area']).reshape(-1, 1))
toP['y_pred']=y_pred
toP['cut']=toP['y_pred']
toP.groupby('Type',group_keys=False).agg(sum)['y_pred']
toP['ratio']=toP['cut'].divide(toP['area'])
toP['ratio'].describe()


# toP.groupby('Type',group_keys=False).agg(sum)['volume']

# toP['area']=toP['geometry'].to_crs({'init': '32638:3395'}).map(lambda p: p.area )

total = final.append(toP)

total['ratio']=total['cut'].divide(total['area'])
total['ratio'].describe()

total.to_file(StartDir+"/piles-combined-lowest-final.shp")
