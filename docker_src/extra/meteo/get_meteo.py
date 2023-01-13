from influxdb_client import InfluxDBClient, Point, WritePrecision
import datetime
import asyncio
import json
from meteostat import Point as metPoint, Hourly
import time

settings = json.load(open("/workspace/settings.json"))

token = settings["token"]
bucket = settings["bucket"]
org = settings["org"]

def save_data(data):
    client = InfluxDBClient(url="http://docker_src-influx-1:8086", 
             token=token,
             bucket=bucket, organization=org)
    with client.write_api() as write:
            write.write(record=data, bucket=bucket, org=org)
    client.close()
        
def meteostat():
        now = datetime.datetime.now()
        # Set time period
        start = now - datetime.timedelta(hours=1)
        end = now

        # Create Point from lat/lon/alt
        lat, lon = 44.494887, 11.342616
        location = metPoint(lat, lon, 54)

        # Get hourly data from yesterday
        data = Hourly(location, start, end)
        data = data.fetch()

        d = []
        for idx in data.index:
        # print(idx, data.loc[idx, "temp"])
                d.append(Point("extra")
                        .tag("location", "%s,%s".format(lat,lon))
                        .field("temperature", data.loc[idx, "temp"])
                        .time(idx, WritePrecision.S)
                )
        save_data(d)

def run():
    while True:
        try:
            meteostat()
            time.sleep(60*60) # 1 hour
        except Exception as e:
            print(e)
            time.sleep(60*15) # 15 min

if __name__ == "__main__":
    run()

