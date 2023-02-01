from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from matplotlib import pyplot as plt
from prophet import Prophet
import numpy as np
import datetime
import pandas as pd
import json
import math
from sklearn.metrics import mean_squared_error
import csv

settings = json.load(open("settings.json"))

token = settings["token"]
bucket = settings["bucket"]
org = settings["org"]
start =  "2023-01-16T23:59:59Z"
stop = "2023-01-17T23:59:59Z"

def get_data(query):
    client = InfluxDBClient(url="http://192.168.1.16:8086", token=token, org=org)
    query_api = client.query_api()
    result = query_api.query(org=org, query=query)
    return result

def create_dataframe(result, what="temperature"):
    raw = []

    for record in result[0].records:
        raw.append((record.get_value(), record.get_time()))

    df1=pd.DataFrame(raw, columns=[what, 'ds'], index=None)
    df1['ds'] = df1['ds'].values.astype('<M8[s]')

    raw = []

    for record in result[1].records:
        raw.append((record.get_value(), record.get_time()))

    df2=pd.DataFrame(raw, columns=['yhat', 'ds'], index=None)
    df2['ds'] = df2['ds'].values.astype('<M8[s]')



    df = df1.merge(df2, how='inner', on='ds') #intersection of keys
    return df

def predict(df, changepoint=0.1, periods=20, frequency="5 S"):
    m = Prophet(changepoint_prior_scale=changepoint)
    m.fit(df)

    future = m.make_future_dataframe(periods = periods, freq=frequency, include_history = False)
    forecast = m.predict(future)

    return forecast

def test_predict(changepoint=0.1, what="temperature"):
    # start = "2023-01-15T23:59:59Z"
    # stop =  "2023-01-16T23:59:59Z"
    timefmtstring = "%Y-%m-%dT%H:%M:%SZ"

    start = datetime.datetime.strptime("2023-01-15T23:59:59Z", timefmtstring)
    stop =  datetime.datetime.strptime("2023-01-16T23:59:59Z", timefmtstring)

    raw = []
    
    predictions = pd.DataFrame([], columns=['y', 'ds'], index=None)

    for i in range(0, 60*60*24, 100):
        _start = start + datetime.timedelta(seconds=i)
        _stop  = stop  + datetime.timedelta(seconds=i+100)

        data_query = 'from(bucket: "{}")' \
        '|> range(start: {}, stop: {})' \
        '|> filter(fn: (r) => r["_measurement"] == "env")' \
        '|> filter(fn: (r) => r["_field"] == "{}")' \
        '|> aggregateWindow(every: 5s, fn: mean, createEmpty: false)' \
        '|> yield(name: "mean")' \
        .format(bucket, _start.strftime(timefmtstring), _stop.strftime(timefmtstring), what)

        result = get_data(data_query)
        raw = []
        for table in result:
            for record in table.records:
                raw.append((record.get_value(), record.get_time()))

        df=pd.DataFrame(raw, columns=['y', 'ds'], index=None)
        df['ds'] = df['ds'].values.astype('<M8[s]')
        
        _predictions = predict(df, changepoint = changepoint, periods=20)
        _predictions = _predictions[['ds', 'yhat']].copy()
        predictions = pd.concat([predictions, _predictions])


    return predictions

def show_df(df, yhats_new_pred):
    plt.plot(df[what], 'g')
    plt.plot(df['yhat'], 'r')
    plt.plot(yhats_new_pred[0], 'b')
    plt.plot(yhats_new_pred[1], 'c')
    plt.plot(yhats_new_pred[2], 'y')
    plt.show()

if __name__ == "__main__":

    what = 'gas_concentration' # temperature, humidity
    forecast = f'forecast_{what}'

    query = 'from(bucket: "{}")' \
        '|> range(start: {}, stop: {})' \
        '|> filter(fn: (r) => r["_measurement"] == "{}" or r["_measurement"] == "env")' \
        '|> filter(fn: (r) => r["_field"] == "yhat" or r["_field"] == "{}")' \
        '|> aggregateWindow(every: 5s, fn: mean, createEmpty: false)' \
        '|> yield(name: "mean")' \
        .format(bucket, start, stop, forecast, what)

    result = get_data(query)
    df = create_dataframe(result, what)
    df.set_index(df['ds'], inplace=True)

    mse01 = mean_squared_error(df[what], df['yhat'])
    print('RMSE changepoint 0.1: %.3f' % mse01)

    csvfile = open(f'rms_{what}.csv', 'w')
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["0.1", mse01])
    
    # run new predictions
    yhats_new_pred = []

    for i in [0.001, 0.5, 10]:
        changepoint = i
        df_new_preds = test_predict(changepoint, what=what)
        
        df_new_preds.set_index(df_new_preds['ds'], inplace=True)
        
        _min = min(len(df[what]), len(df_new_preds['yhat']) )
        mseother = mean_squared_error(df[what][:_min], df_new_preds['yhat'][:_min])
        print('RMSE', changepoint,  ': %.3f' % mse01)
        
        csvwriter.writerow([i, mseother])

        yhats_new_pred.append(df_new_preds['yhat'])

    csvfile.close()

    show_df(df, yhats_new_pred)
