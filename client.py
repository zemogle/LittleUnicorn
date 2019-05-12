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

def display(sound):
    levels = sound['data']
    rgb = []
    if sound['max']>2.1:
        red = True
    else:
        red = False
    for i in range(1,256):
        val = levels[i]
        rgb.append(val_to_hsv(2*val, red))
    return rgb

def colourise(val, red):
    # loud is red, quiessent is blue, green is in the middle
    if val > 1:
        # Red - danger!
        val = 1
    elif val < 0:
        val = 0
    if red:
        colour = (val, 0, 0)
    else:
        colour = (0,0,val)
    return colour

def val_to_hsv(val, red):
    # val = val/255
    if val > 1:
        val = 1
        hsv = (1,1,0.5)
    elif val < 0:
        val = 0
        hsv = (0,0,0)
    else:
        hsv = (val, 1, val)
    if red:
        hsv = (val,1 ,0.6)
    return hsv


async def main():
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:
        while True:
            # await prompt_and_send(ws)
            await ws.send_str('')
            async for msg in ws:
                # await prompt_and_send(ws)
                await ws.send_str('')
                sound = json.loads(msg.data)
                colours = display(sound)
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
    for current in range(0,16):
        for y in range(0,16):
            if y == current:
                unicornhathd.set_pixel(x, y, rgb[0], rgb[1], rgb[2])
            else:
                unicornhathd.set_pixel(x, y, 0,0,0)
        unicornhathd.show()
        time.sleep(0.1)
    return

if __name__ == '__main__':

    wait_for_internet_connection()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        unicornhathd.off()
