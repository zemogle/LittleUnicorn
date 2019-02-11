import asyncio
import os
import json
import aiohttp

try:
    import unicornhathd
    print("unicorn hat hd detected")
except ImportError:
    from unicorn_hat_sim import unicornhathd


HOST = os.getenv('HOST', 'babymic.local')
PORT = int(os.getenv('PORT', 8080))

URL = f'ws://{HOST}:{PORT}/ws'


async def main():
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:
        while True:
            # await prompt_and_send(ws)
            await ws.send_str('')
            async for msg in ws:
                # await prompt_and_send(ws)
                await ws.send_str('')
                for i, colour in enumerate(json.loads(msg.data)):
                    x,y = divmod(i,16)
                    unicornhathd.set_pixel(x, y, colour[0], colour[1], colour[2])
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
