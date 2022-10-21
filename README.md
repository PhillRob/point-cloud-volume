# Volume estimate

Here I explore ways to estimate volume for stockpiles based on UAV point clouds and polygones. 


## Drone Deploy API
Tools for interacting with the drone deploy API using python. See https://help.dronedeploy.com/hc/en-us/sections/1500000794002-API for more info on the drone deploy API.

## Volume measurements
The `volume-query.py` script takes for arguments and returns cut, fill and volume measurements per polygon.

`python volume-query.py -i <geojson_file> -p <plan_id> -b <baseplane_type> -a <api_key>'` runs accross the entire data set and `volume-query.py -i <geojson_file> -p <plan_id> -b <baseplane_type> -a <api_key> -s <poly_start> -e <poly_end>` allows for subsetting large `geojson` files by feature numbers. The subsetting is experimental.
