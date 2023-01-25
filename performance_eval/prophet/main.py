from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime
import pandas as pd
import json
import math
from sklearn.metrics import mean_squared_error

settings = json.load(open("settings.json"))

token = settings["token"]
bucket = settings["bucket"]
org = settings["org"]

client = InfluxDBClient(url="http://192.168.1.16:8086", token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)

stop = "2023-01-17T23:59:59Z"
# datetime.isoformat(datetime.today() - datetime.timedelta(hours=1))
start =  "2023-01-16T23:59:59Z"
# datetime.isoformat(datetime.today() - datetime.timedelta(hours=4))

temp_query = 'from(bucket: "{}")' \
    '|> range(start: {}, stop: {})' \
    '|> filter(fn: (r) => r["_measurement"] == "forecast_temperature" or r["_measurement"] == "env")' \
    '|> filter(fn: (r) => r["_field"] == "yhat" or r["_field"] == "temperature")' \
    '|> aggregateWindow(every: 5s, fn: mean, createEmpty: false)' \
    '|> yield(name: "mean")' \
    .format(bucket, start, stop)

hum_query = 'from(bucket: "{}")' \
    '|> range(start: {}, stop: {})' \
    '|> filter(fn: (r) => r["_measurement"] == "forecast_humidity" or r["_measurement"] == "env")' \
    '|> filter(fn: (r) => r["_field"] == "yhat" or r["_field"] == "humidity")' \
    '|> aggregateWindow(every: 5s, fn: mean, createEmpty: false)' \
    '|> yield(name: "mean")' \
    .format(bucket, start, stop)

gas_query = 'from(bucket: "{}")' \
    '|> range(start: {}, stop: {})' \
    '|> filter(fn: (r) => r["_measurement"] == "forecast_gas_concentration" or r["_measurement"] == "env")' \
    '|> filter(fn: (r) => r["_field"] == "yhat" or r["_field"] == "gas_concentration")' \
    '|> aggregateWindow(every: 5s, fn: mean, createEmpty: false)' \
    '|> yield(name: "mean")' \
    .format(bucket, start, stop)


result = client.query_api().query(org=org, query=temp_query)

raw = []

for record in result[0].records:
    raw.append((record.get_value(), record.get_time()))

df1=pd.DataFrame(raw, columns=['temperature', 'ds'], index=None)
df1['ds'] = df1['ds'].values.astype('<M8[s]')

raw = []

for record in result[1].records:
    raw.append((record.get_value(), record.get_time()))

df2=pd.DataFrame(raw, columns=['yhat', 'ds'], index=None)
df2['ds'] = df2['ds'].values.astype('<M8[s]')

df = df1.merge(df2, how='inner', on='ds') #intersection of keys

mse = mean_squared_error(df['temperature'], df['yhat'])
print('Test RMSE: %.3f' % mse)
df.set_index(df['ds'], inplace=True)

plt.plot(df['temperature'])
plt.plot(df['yhat'])
plt.show()