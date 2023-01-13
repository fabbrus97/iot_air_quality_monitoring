from http.server import CGIHTTPRequestHandler, HTTPServer
from aiohttp import web
from influxdb_client import InfluxDBClient, Point
import aiocoap.resource as resource
import datetime
import aiocoap
import asyncio
import json
import math

settings = json.load(open("/workspace/settings.json"))

token = settings["token"]
bucket = settings["bucket"]
org = settings["org"]

START_COMPUTE_R0 = None
R0 = -1

def save_data(data):
    client = InfluxDBClient(url="http://docker_src-influx-1:8086", 
             token=token,
             bucket=bucket, organization=org)
    with client.write_api() as write:
            write.write(record=data, bucket=bucket, org=org)
    client.close()

def compute_R0(analogRead):
        vin  = 3.3
        vout = (3.3*analogRead)/4096
        rs = ((vin - vout)/vout)
        
        global R0
        global START_COMPUTE_R0
        diff = (datetime.datetime.now() - START_COMPUTE_R0).seconds
        wait_time = 15*60 # wait 15 minutes
        if diff > wait_time: 
                R0 = rs/9.8
                print("R0 set to", R0)
        else:
                print(wait_time - diff, "seconds left")

def compute_ppm(analogRead):
        if analogRead == 0:
                analogRead = 1
        
        # https://thestempedia.com/tutorials/interfacing-mq-2-gas-sensor-with-evive/
        vin  = 3.3
        vout = (3.3*analogRead)/4096
        rs = ((vin - vout)/vout)
        
        global R0
        if R0 == 0:
                print("Computing R0, delaying ppm calculations...")
                compute_R0(analogRead)
                return

        # log(y) = m*log(x) + b
        # m and b for:
        # LPG	
        # Methane	
        # CO	
        # Alcohol	
        # Smoke	
        # Propane	

        gas = [(-0.47305447, 1.412572126, "H2"),
                (-0.454838059, 1.25063406, "LPG" ),
                (-0.372003751, 1.349158571, "Methane" ),
                (-0.33975668, 1.512022272, "CO"),
                (-0.373311285, 1.310286169, "Alcohol" ),
                (-0.44340257, 1.617856412, "Smoke" ),
                (-0.461038681, 1.290828982, "Propane" )]
        print("analogRead:", analogRead)
        print("Sensor value in volts:", vout)
        print("rs:", rs, "r0:", R0, "rs/r0:", rs/R0)
        for g in gas: 
                b = g[1]
                m = g[0]
                y = rs/R0
                x = 10 ** ((math.log(y, 10) - b) / m) #gas concentration real value
                
                print(f"ppm for {g[2]}: {x}")
                lat, lon = 44.494887, 11.342616
                save_data(Point("ppm")
                        .tag("location", "%s,%s".format(lat,lon))
                        .field(g[2], x))

class Temperature(resource.Resource):
    async def render_put(self, request):
        
        temp, gps, id = request.payload.decode('utf-8').split(";")
        print("received temperature", temp)
        d = [Point("env")
                .tag("device_id", id)
                .tag("location", gps)
                .field("temperature", float(temp))]
        save_data(d)
        
        return aiocoap.Message(code=aiocoap.CHANGED, payload=request.payload)

class Humidity(resource.Resource):
    async def render_put(self, request):
        
        hum, gps, id = request.payload.decode('utf-8').split(";")
        print("received humidity", hum)
        d = [Point("env")
                .tag("device_id", id)
                .tag("location", gps)
                .field("humidity", float(hum))]
        save_data(d)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=request.payload)

class RSSI(resource.Resource):
    async def render_put(self, request):
        
        rssi, gps, id = request.payload.decode('utf-8').split(";")
        print("received rssi", rssi)
        d = [Point("data")
                .tag("device_id", id)
                .tag("location", gps)
                .field("rssi", int(rssi))]
        save_data(d)
        
        return aiocoap.Message(code=aiocoap.CHANGED, payload=request.payload)

class AQI(resource.Resource):
    async def render_put(self, request):
        aqi, gps, id = request.payload.decode('utf-8').split(";")
        print("received aqi", aqi)
        d = [Point("env")
                .tag("device_id", id)
                .tag("location", gps)
                .field("aqi", int(aqi))]
        save_data(d)
        
        return aiocoap.Message(code=aiocoap.CHANGED, payload=request.payload)

class Gas(resource.Resource):
    async def render_put(self, request):

        global R0
        global START_COMPUTE_R0
        if R0 == -1:
                print("Start computing R0")
                R0 = 0
                START_COMPUTE_R0 = datetime.datetime.now()

        gas, gps, id = request.payload.decode('utf-8').split(";")
        print("received gas", gas)
        d = [Point("env")
                .tag("device_id", id)
                .tag("location", gps)
                .field("gas_concentration", int(gas))]
        save_data(d)
        compute_ppm(int(gas))
        return aiocoap.Message(code=aiocoap.CHANGED, payload=request.payload)




async def run_coap():
    # Resource tree creation
    root = resource.Site()

    # root.add_resource(['.well-known', 'core'],
    #         resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['env', 'temp'], Temperature())
    root.add_resource(['env', 'hum'], Humidity())
    root.add_resource(['env', 'gas_conc'], Gas())
    root.add_resource(['env', 'aqi'], AQI())
    root.add_resource(['data', 'rssi'], RSSI())

    print("Starting coap server on port 5683")

    await aiocoap.Context.create_server_context(root)

    # Run forever
    await asyncio.get_running_loop().create_future()

async def run_http():
    app = web.Application()
    app.add_routes([web.post('/data', httpHandler)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = 8082
    site = web.TCPSite(runner, '0.0.0.0', port)
    print(f"Starting http server on port {port}")
    await site.start()

async def httpHandler(request):
        print("Received http request")
        try:
            post_data = await request.json()
            d = [
            Point("data")
                    .tag("device_id", post_data["id"])
                    .tag("location", post_data["gps"])
                    .field("rssi", post_data["rssi"]),
            Point("env")
                    .tag("device_id", post_data["id"])
                    .tag("location", post_data["gps"])
                    .field("temperature", post_data["temp"])
                    .field("humidity", post_data["hum"])
                    .field("aqi", post_data["AQI"])
                    .field("gas_concentration", post_data["gas"])]
            
            try:
                save_data(d) 
                global R0
                global START_COMPUTE_R0
                if R0 == -1:
                        print("Start computing R0")
                        R0 = 0
                        START_COMPUTE_R0 = datetime.datetime.now()    
                
                compute_ppm(post_data["gas"])
            except:
                return web.Response(text="server error", status=500)

    
            return web.Response(text="ok", status=200)
        except:
            return web.Response(text="error", status=400)

if __name__ == "__main__":
    print("Data proxy started")
    START_COMPUTE_R0 = None
    R0 = -1
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coap_task = loop.create_task(run_coap())
    # http_task = loop.create_task(run_http())
    #loop.run_until_complete(asyncio.gather(http_task, coap_task))
    loop.run_until_complete(asyncio.gather(http_task))
    
    
