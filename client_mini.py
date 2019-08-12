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

from pixels import CRY_GHOST_PIXELS, GHOST_COLOUR, GHOST_PIXELS, PIXELS
from graphic_eq import calculate_levels


try:
    import unicornhat
    print("unicorn hat hd detected")
except ImportError:
    from unicorn_hat_sim import unicornhat


HOST = '0.0.0.0'
PORT = 8080


x = np.arange(1,65)
calib = np.log(x)

if len(sys.argv) > 0:
    HOST = str(sys.argv[1])
    try:
        ROT = float(sys.argv[2])
    except IndexError:
        ROT = 90.
    try:
        DISP = str(sys.argv[3])
    except IndexError:
        DISP = "eq"

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
    levels = np.abs((sound['data']*calib)) #sound['data']
    rgb = []
    if np.mean(levels) > 0.07:
        cry = True
        # cry_alert(lastcry)
        gid = randint(0,len(CRY_GHOST_PIXELS)-1)
        show_pixel_image(CRY_GHOST_PIXELS[gid], GHOST_COLOUR['cry'])
    else:
        cry = False
        for i in range(1,256):
            val = levels[i]
            colour = val_to_hsv(10*val, cry)
            x,y = divmod(i,16)
            unicornhat.set_pixel_hsv(x, y, colour[0], colour[1], colour[2])
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
        hsv = (0.13, 0.7, 0.5)
    elif val > 0.7 and val <= 0.8:
        hsv = (0.07, 0.7, 0.5)
    elif val > 0.8 and val < 1:
        hsv = (0.3, 0.7, 0.5)
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
                unicorn_display(sound, lastcry)
                if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break

def unicorn_display(sound, lastcry):
    if DISP == 'eq':
        y_len = calculate_levels(sound)
        unicornhat.clear()

        for x in range(0,4):
            y_val = y_len[x]
            for y in range(0,16):
                if y < int(y_val):
                    amp = y_val/16
                    unicornhat.set_pixel(x, y, (amp*255,amp*255,amp*255))
                else:
                    unicornhat.set_pixel(x, y, 0,0,0)
    else:
        colours = display(sound, lastcry)
    try:
        # unicornhathd.rotation(ROT)
        unicornhat.show()
    except Exception as e:
        # print(msg.data)
        pass
    return

def awaiting_connection():
    # rgb = wifi_rgb[randint(0,5)]
    show_pixel_image(CRY_GHOST_PIXELS[0], GHOST_COLOUR['cry'])
    time.sleep(0.1)
    return

def show_pixel_image(pixels, colours):
    for row in range(0,4):
        for col in range(0,16):
            pixel=pixels[row][col]
            if pixel>0:
                rgb = colours[pixel]
                unicornhat.set_pixel(col, row, rgb[0], rgb[1], rgb[2])
            else:
                unicornhat.set_pixel(col, row, 0,0,0)
    unicornhat.show()
    return


if __name__ == '__main__':

    wait_for_internet_connection()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        unicornhat.off()
