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
import numpy as np
import matplotlib.pyplot as plt


HOST = '0.0.0.0'
PORT = 8080
CHUNK = 2048
RATE = 44100

wifi_rgb = [
    [255,99,71], [255,215,0], [50,205,50], [0,255,255], [30,144,255], [220,20,60]
]

if len(sys.argv) > 0:
    HOST = str(sys.argv[1])

URL = "ws://{}:{}/ws".format(HOST, PORT)
TEST_URL = "http://{}:{}".format(HOST, PORT)

plt.ion()
fig = plt.figure(figsize=(13,6))
ax = fig.add_subplot(111)
x = np.arange(0,256)
y = np.log(x/20)
y_init = np.random.rand(256)
line1, = ax.semilogy(x,y_init,'.',alpha=0.8)
plt.ylim( (10**-2,10**2) )
plt.show()



def wait_for_internet_connection():
    while True:
        try:
            print("trying {}".format(TEST_URL))
            response = urlopen(TEST_URL,timeout=1)
            break
        except URLError:
            awaiting_connection()
    return


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
                line1.set_ydata(100*(sound['data']*y))
                plt.pause(0.05)

                if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break

if __name__ == '__main__':

    wait_for_internet_connection()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
