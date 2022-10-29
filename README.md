# Volume calculation from point clouds

Here I explore ways to estimate volume for stockpiles based on UAV point clouds and polygons. 


## Drone Deploy API
Drone deploy provides tools for interacting with the drone deploy API using python. See https://help.dronedeploy.com/hc/en-us/sections/1500000794002-API for more info on the drone deploy API.

### Volume measurements
The `volume-query.py` uses the drone deploy API. This script takes for arguments and returns cut, fill and volume measurements per polygon.

`python volume-query.py -i <geojson_file> -p <plan_id> -b <baseplane_type> -a <api_key>'` runs across the entire data set and `volume-query.py -i <geojson_file> -p <plan_id> -b <baseplane_type> -a <api_key> -s <poly_start> -e <poly_end>` allows to subset large `geojson` files by feature numbers. This is experimental.

## Direct point clouds



## Pile height
Short script `pile-height.inpynb` to extract the difference in height (z) of points within a polygons. Originally set up to estimate stockpile height.