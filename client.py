import asyncio
import os
import json
import aiohttp
import sys

try:
    import unicornhathd
    print("unicorn hat hd detected")
except ImportError:
    from unicorn_hat_sim import unicornhathd


HOST = '0.0.0.0'
PORT = 8080

if len(sys.argv) > 0:
    HOST = str(sys.argv[1])

URL = "ws://{}:{}/ws".format(HOST, PORT)

def display(levels):
    rgb = []
    for i in range(0,256):
        val = levels[i]
        rgb.append(colourise(val*10.))
    return rgb

def colourise(val):
    # loud is red, quiessent is blue, green is in the middle
    if val > 255:
        val = 255

    if val > 220:
        # Red - danger!
        colour = (226,88,34)
    elif val >=200 and val <= 220:
        colour = (226,136,34)
    elif val >=200 and val < 170:
        colour = (226,184,34)
    elif val < 170:
        colour = (0,0,0)
    return colour


async def main():
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:
        while True:
            # await prompt_and_send(ws)
            await ws.send_str('')
            async for msg in ws:
                # await prompt_and_send(ws)
                await ws.send_str('')
                colours = display(json.loads(msg.data))
                for i, colour in enumerate(colours):
                    x,y = divmod(i,16)
                    unicornhathd.set_pixel(x, y, colour[0], colour[1], colour[2])
                    unicornhathd.rotation(90.0)
                try:
                    unicornhathd.show()
                except Exception as e:
                    print(msg.data)

                if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break


async def prompt_and_send(ws):
    new_msg_to_send = input('Type a message to send to the server: ')
    if new_msg_to_send == 'exit':
        print('Exiting!')
        raise SystemExit(0)
    await ws.send_str(new_msg_to_send)


if __name__ == '__main__':

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        unicornhathd.off()
