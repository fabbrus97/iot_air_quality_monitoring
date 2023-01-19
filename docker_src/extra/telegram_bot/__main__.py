#!/usr/bin/env python3
from telegram import Bot
from telegram import InputMediaPhoto
import requests
import asyncio

import datetime
import time
import shutil
import json


"""
    Downloads different panels as pictures, with 
    data from *now* to *UPDATE_TIME* ago, every
    UPDATE_TIME seconds, and then sends them via 
    the telegram bot.
"""

def get_picture(link, dashboard, id):
    headers = {
     'Authorization': f'Bearer {GRAFANA_API_KEY}'
    }

    pic = requests.get(link, headers=headers, stream=True)
    with open(f"/tmp/iot_grafana_{dashboard}_{id}.png", 'wb') as f:
        pic.raw.decode_content = True
        shutil.copyfileobj(pic.raw, f) 

def get_data(_to, _from, _dashboard, ids):
    for id in ids:
        link = f"http://docker_src-grafana-1:3000/render/d-solo/{_dashboard}/iot?orgId=1&from={_from}&to={_to}&panelId={id}&width=1000&height=500&tz=Europe%2FRome"
        print("Downloading image panel", _dashboard, id)
        get_picture(link, _dashboard, id)

async def send_data(dashboard, ids):
    media_group = []
    for id in ids:
        print("Sending image panel", dashboard, id)
        # bot.send_photo(chat_id, open(f"/tmp/iot_grafana_{id}.png"))
        media_group.append(InputMediaPhoto(open(f"/tmp/iot_grafana_{dashboard}_{id}.png","rb")))
    await bot.send_media_group(chat_id, media=media_group)

async def send_dashboards():

    _to = int( 1000 * datetime.datetime.now().timestamp()) #now
    _from = _to - UPDATE_TIME*1000
    # _from = int( 1000 * (datetime.datetime.now() - datetime.timedelta(seconds = UPDATE_TIME)).timestamp())

    sensors_dashboard = "6pOA8ADVz"
    sensors_ids = [11, 13, 6, 4, 8, 9]
    gas_ppm_dashboard = "f7-eRNOVk"
    gas_ppm_ids = [10, 12, 2, 8, 4, 14, 6]

    get_data(_to, _from, sensors_dashboard, sensors_ids)
    get_data(_to, _from, gas_ppm_dashboard, gas_ppm_ids)
    
    await send_data(sensors_dashboard, sensors_ids)
    await send_data(gas_ppm_dashboard, gas_ppm_ids)

if __name__ == "__main__":
    SETTINGS = json.load(open("/workspace/settings.json"))
    TOKEN = SETTINGS["telegram_token"]
    GRAFANA_API_KEY = SETTINGS["grafana_api_key"]
    UPDATE_TIME = SETTINGS["telegram_update_frequency"]
    chat_id = SETTINGS["telegram_chat_id"]

    bot = Bot(token=TOKEN)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(bot.send_message(chat_id, "Bot started!"))

    while True:
        time.sleep(UPDATE_TIME)
        loop.run_until_complete(send_dashboards())
        

