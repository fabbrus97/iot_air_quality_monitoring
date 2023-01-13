from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from prophet import Prophet
import pandas as pd
import json
import time

settings = json.load(open("/workspace/settings.json"))

token = settings["token"]
bucket = settings["bucket"]
org = settings["org"]

#"what" can be gas_concentration, temperature, humidity
def predict(what, periods, frequency, start, stop):
    client = InfluxDBClient(url="http://docker_src-influx-1:8086", token=token, org=org)
    query_api = client.query_api()

    # stop = datetime.datetime.isoformat(datetime.datetime.today() - datetime.timedelta(hours=3)) 
    # start = datetime.datetime.isoformat(datetime.datetime.today() - datetime.timedelta(hours=5)) 
    
    print("Asking for {} data between {} and {}...".format(what, start, stop))

    query =  'from(bucket:"{}")' \
        ' |> range(start:{}, stop:{})'\
        ' |> filter(fn: (r) => r._measurement == "env")' \
        ' |> filter(fn: (r) => r._field == "{}")' \
        .format(bucket, start, stop, what)

    print(query)

    result = query_api.query(org=org, query=query)

    print("query done; results:")
    print(result)

    raw = []
    for table in result:
        for record in table.records:
            raw.append((record.get_value(), record.get_time()))

    df=pd.DataFrame(raw, columns=['y', 'ds'], index=None)
    df['ds'] = df['ds'].values.astype('<M8[s]')

    # https://facebook.github.io/prophet/docs/non-daily_data.html
    # https://github.com/facebook/prophet/issues/1320
    m = Prophet(changepoint_prior_scale=0.1)
    m.fit(df)

    future = m.make_future_dataframe(periods = periods, freq=str(frequency) + " S", include_history = False)
    forecast = m.predict(future)

    print("My predictions are:")
    print(forecast.head())

    forecast['measurement'] = "forecast_{}".format(what)
    cp = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'measurement']].copy()
    lines = [str(cp["measurement"][d])
        + ",type=forecast"
        + " "
        + "yhat=" + str(cp["yhat"][d]) + ","
        + "yhat_lower=" + str(cp["yhat_lower"][d]) + ","
        + "yhat_upper=" + str(cp["yhat_upper"][d])
        + " " + str(int(time.mktime(cp['ds'][d].timetuple()))) + "000000000" for d in range(len(cp))]

    _write_client = client.write_api(write_options=WriteOptions(batch_size=1000, 
                                                                flush_interval=10_000,
                                                                jitter_interval=2_000,
                                                                retry_interval=5_000))

    _write_client.write(bucket, org, lines)

    _write_client.__del__()
    client.__del__()

    print("Predictions written on db")
