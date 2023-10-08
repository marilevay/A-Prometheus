# Data manipulation
import numpy as np
import pandas as pd

# Data visualization
import matplotlib.pyplot as plt
import seaborn as sns

from io import StringIO

!pip install sodapy

!pip install requests
import requests

api_key = '[API_KEY]'

url = 'https://firms.modaps.eosdis.nasa.gov/api/country/csv/8e32c5e1a58133ddf186114abfe0f3d2/VIIRS_NOAA20_NRT/USA/1/TODAY'

'''
params = {
    'api_key': api_key,
    'source': 'VIIRS_NOAA20_NRT',  # Example latitude (replace with your own)
    'country_code': 'USA',  # Example longitude (replace with your own)
    'day_range': '7',  # Example start date in YYYYMMDD format
    'date': '2023-10-07'    # Example end date in YYYYMMDD format
}
'''

response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Print the first few lines of the CSV data
      # Adjust the number to display more or fewer characters

    try:
        # Parse the CSV data into a Pandas DataFrame
        firms_df = pd.read_csv(StringIO(response.text))

        # Print the DataFrame
        print(firms_df.head())
    except pd.errors.ParserError as e:
        print(f"ParserError: {e}")
else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code}")
    print(response.text)

firms_df

print(firms_df.columns.tolist())

#https://api.meteomatics.com/2023-10-07T22:30:00.000-07:00--2023-10-08T22:30:00.000-07:00:PT5M/t_min_-300cm_1h:C,wind_speed_FL10:bft,relative_humidity_2m:p,forest_fire_warning:idx,soil_moisture_deficit:mm,soil_moisture_index_-300cm:idx/37.7790262,-122.419906/csv?model=mix

#!/usr/bin/env python

import pandas as pd
from sodapy import Socrata

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.sfgov.org", None)

# Example authenticated client (needed for non-public datasets):
# client = Socrata(data.sfgov.org,
#                  MyAppToken,
#                  username="user@example.com",
#                  password="AFakePassword")

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
results = client.get("6tt8-ugnj", limit=2000)

# Convert to pandas DataFrame
streetlights_df = pd.DataFrame.from_records(results)
streetlights_df[['latitude', 'longitude']] = streetlights_df['point'].apply(lambda x: pd.Series([x['latitude'], x['longitude']]))

!pip install meteomatics

import datetime as dt
import meteomatics.api as api

username = 'minervauniversity_levay_marina'
password = 'MpG4n0b36A'
# url = 'https://api.meteomatics.com/2023-10-07T00:00:00.000Z--2023-10-18T00:00:00.000Z:P1D/t_2m:C,msl_pressure:hPa,precip_24h:mm,wind_speed_10m:ms,weather_symbol_24h:idx/37.7790262,-122.419906/csv?model=mix'

# Every change among different streetlights will be very small. The conditions for meteomatics shouldn't be individual for each streetlight. Leave the location as in San Francisco. The maximum number of street lights that can be considered is 500
coordinates = [(37.7790262, -122.419906)]
parameters = ['t_2m:C', 'msl_pressure:hPa', 'precip_24h:mm', 'wind_speed_10m:ms', 'weather_symbol_24h:idx']
model = 'mix'
startdate = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
enddate = startdate + dt.timedelta(days=1)
interval = dt.timedelta(hours=25)

meteomatics_df = api.query_time_series(coordinates, startdate, enddate, interval, parameters, username, password, model=model)
wind_speed = meteomatics_df['wind_speed_10m:ms']
precipitation = meteomatics_df['precip_24h:mm']

wind_speed

precipitation

meteomatics_df

meteomatics_df['precip_24h:mm'].max()

import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import haversine_distances
from math import radians

# Preprocess Data
# Convert latitude and longitude columns to float, handle NaN values
streetlights_df['latitude'] = pd.to_numeric(streetlights_df['latitude'], errors='coerce')
streetlights_df['longitude'] = pd.to_numeric(streetlights_df['longitude'], errors='coerce')

# Drop rows with NaN values
streetlights_df = streetlights_df.dropna(subset=['latitude', 'longitude'])

# Convert latitude and longitude to radians element-wise
streetlights_df['latitude_rad'] = streetlights_df['latitude'].apply(radians)
streetlights_df['longitude_rad'] = streetlights_df['longitude'].apply(radians)

'''

# Define and Fit DBSCAN Model
epsilon = 10  # Maximum distance to consider points as neighbors (in kilometers)
min_samples = 10  # Minimum number of samples required to form a dense region
db = DBSCAN(eps=epsilon, min_samples=min_samples, metric='haversine').fit(streetlights_df[['latitude_rad', 'longitude_rad']])

# Add Cluster Labels to DataFrame
streetlights_df['cluster'] = db.labels_

# Print or Use Clusters
clusters = streetlights_df['cluster'].unique()
for cluster in clusters:
    cluster_streetlights_df = streetlights_df[streetlights_df['cluster'] == cluster]
    print(f"Cluster {cluster}:", cluster_streetlights_df[['latitude', 'longitude']])

'''

streetlights_df

streetlights_df.info()

from math import radians, sin, cos, sqrt, atan2, inf, e, log

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points on the Earth's surface.

    Parameters:
    - lat1, lon1: Latitude and longitude of point 1 in degrees
    - lat2, lon2: Latitude and longitude of point 2 in degrees

    Returns:
    - Distance in kilometers
    """
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return round(distance)

# Example usage:
lat1, lon1 = 34.0522, -118.2437  # Coordinates of point 1 (Los Angeles)
lat2, lon2 = 40.7128, -74.0060   # Coordinates of point 2 (New York)

haversine_distance(lat1, lon1, lat2, lon2)

### NEW COLUMNS TO THE DATABASE

Complementing the streetligths database with FIRMS and Meteomatics data

# Convert latitude and longitude columns to float, handle NaN values
firms_df['latitude'] = pd.to_numeric(firms_df['latitude'], errors='coerce')
firms_df['longitude'] = pd.to_numeric(firms_df['longitude'], errors='coerce')

# Drop rows with NaN values
firms_df = firms_df.dropna(subset=['latitude', 'longitude'])

# Convert latitude and longitude to radians element-wise
firms_df['latitude_rad'] = firms_df['latitude'].apply(radians)
firms_df['longitude_rad'] = firms_df['longitude'].apply(radians)

firms_df

firms_df['fire_id'] = range(len(firms_df))

firms_df

smallest_distances = []
fire_ids = []
smallest_distance = math.inf

## SIMPLEST VERSION BY EXHAUSTION
for lat_sl, long_sl in zip(streetlights_df['latitude_rad'], streetlights_df['longitude_rad']):
  for lat_fire, long_fire, id in zip(firms_df['latitude_rad'], firms_df['longitude_rad'], firms_df['fire_id']):
    curr_distance = haversine_distance(lat_sl, long_sl, lat_fire, long_fire)
    if curr_distance > 0 and curr_distance < smallest_distance:
      smallest_distance = curr_distance
      # print(lat_sl, long_sl, smallest_distance)
  smallest_distances.append(smallest_distance)
  fire_ids.append(id)
  smallest_distance = math.inf

interm

# Formula for Danger Level

danger_level = (2**(1/distance_fire_street_lights) * 1 + wind_speed)/math.log(math.e + precipitation)
