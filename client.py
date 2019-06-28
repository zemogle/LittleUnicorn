from future.standard_library import install_aliases
install_aliases()

import asyncio
import os
import json
import aiohttp
import sys
from urllib.error import URLError
from urllib.request import urlopen
import time
from random import randint
from datetime import datetime
import numpy as np
import requests
import config


try:
    import unicornhathd
    print("unicorn hat hd detected")
except ImportError:
    from unicorn_hat_sim import unicornhathd


HOST = '0.0.0.0'
PORT = 8080

wifi_rgb = [
    [255,99,71], [255,215,0], [50,205,50], [0,255,255], [30,144,255], [220,20,60]
]

PIXELS   =   [
        [0,0,1,0,0,0,0,0,1,0,0],
        [0,0,0,1,0,0,0,1,0,0,0],
        [0,0,1,1,1,1,1,1,1,0,0],
        [0,1,1,0,1,1,1,0,1,1,0],
        [1,1,1,1,1,1,1,1,1,1,1],
        [1,0,1,1,1,1,1,1,1,0,1],
        [1,0,1,0,0,0,0,0,1,0,1],
        [0,0,0,1,1,0,1,1,0,0,0]
]
x = np.arange(1,257)
y = np.log(x)

if len(sys.argv) > 0:
    HOST = str(sys.argv[1])

URL = "ws://{}:{}/ws".format(HOST, PORT)
TEST_URL = "http://{}:{}".format(HOST, PORT)

def wait_for_internet_connection():
    while True:
        try:
            print("trying {}".format(TEST_URL))
            response = urlopen(TEST_URL,timeout=1)
            break
        except URLError:
            awaiting_connection()
    return

def display(sound, lastcry):
    levels = np.abs((sound['data']*y)) #sound['data']
    rgb = []
    if np.mean(levels) > 0.05:
        cry = True
        # cry_alert(lastcry)
    else:
        cry = False
    for i in range(1,256):
        val = levels[i]
        rgb.append(val_to_hsv(10*val, cry))
    return rgb

def colourise(val, cry):
    if val > 1:
        val = 1
    elif val < 0:
        val = 0
    if cry:
        colour = (val, 0, 0)
    else:
        colour = (0,0,val)
    return colour

def val_to_hsv(val, cry):
    if cry:
        hsv = (0.5,0.7,0.7)
    elif val > 1:
        val = 1
        hsv = (1,1,0.5)
    elif val < 0:
        val = 0
        hsv = (0,0,0)
    elif val < 0.6:
        hsv = (0,0,0)
    elif val >= 0.6 and val <= 0.7:
        hsv = (0.13, 0.7, 0.7)
    elif val > 0.7 and val <= 0.8:
        hsv = (0.07, 0.7, 0.7)
    elif val > 0.8 and val < 1:
        hsv = (0.07, 0, 1)
    else:
        hsv = (val, 0.7, 1)

    return hsv


async def main():
    lastcry = datetime.now()
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:
        while True:
            # await prompt_and_send(ws)
            await ws.send_str('')
            async for msg in ws:
                # await prompt_and_send(ws)
                await ws.send_str('')
                sound = json.loads(msg.data)
                colours = display(sound, lastcry)
                for i, colour in enumerate(colours):
                    x,y = divmod(i,16)
                    unicornhathd.set_pixel_hsv(x, y, colour[0], colour[1], colour[2])
                    unicornhathd.rotation(90.0)
                try:
                    unicornhathd.show()
                except Exception as e:
                    # print(msg.data)
                    pass

                if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break

def awaiting_connection():
    x = 7
    rgb = wifi_rgb[randint(0,5)]
    for row in range(0,len(PIXELS)):
        for col in range(0,len(PIXELS[row])):
            pixel=PIXELS[row][col]
            if pixel>0:
                unicornhathd.set_pixel(col, row, rgb[0], rgb[1], rgb[2])
            else:
                unicornhathd.set_pixel(col, row, 0,0,0)
    unicornhathd.show()
    time.sleep(0.1)
    return

def cry_alert(lastcry):
    if (datetime.now() - lastcry).seconds > 300:
        r = requests.post("https://api.pushover.net/1/messages.json", data = {
          "token": config.TOKEN,
          "user": config.USER_KEY,
          "message": "Crying baby!"
        })
        LASTCRY = datetime.now()

    return

if __name__ == '__main__':

    wait_for_internet_connection()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        unicornhathd.off()
