from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from prophet.diagnostics import performance_metrics, cross_validation
from datetime import datetime
from prophet import Prophet
import pandas as pd
import json

settings = json.dump("/workspaces/docker_data_mngmt/settings.json")

token = settings["token"]
bucket = settings["bucket"]
org = settings["org"]

client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)

stop = "2023-01-16T23:59:59Z"
# datetime.isoformat(datetime.today() - datetime.timedelta(hours=1))
start =  "2023-01-17T23:59:59Z"
# datetime.isoformat(datetime.today() - datetime.timedelta(hours=4))

query =  'from(bucket:"{}")' \
    ' |> range(start:{}, stop:{})'\
    ' |> filter(fn: (r) => r._measurement == "env")' \
    ' |> filter(fn: (r) => r._field == "temperature")' \
    .format(bucket, start, stop)
# ' |> filter(fn: (r) => r._field == "gas_concentration")'

result = client.query_api().query(org=org, query=query)

raw = []
for table in result:
    for record in table.records:
        raw.append((record.get_value(), record.get_time()))

df=pd.DataFrame(raw, columns=['y', 'ds'], index=None)
df['ds'] = df['ds'].values.astype('<M8[s]')

m = Prophet()
m.fit(df)

df_cv = cross_validation(m, initial='60 minutes', period='5 seconds', horizon = '2 minutes')

df_p = performance_metrics(df_cv)
print(df_p.head())
