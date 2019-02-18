import pyaudio
import numpy as np
import sys
import time
import asyncio
from aiohttp import web, WSMsgType
import json
import os


HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))

SAMPLE_RATE = 44100
CHUNK_SIZE = 4096
AUDIO_FORMAT = pyaudio.paInt16

FORMAT = np.int16

def calculate_levels(data, chunk,sample_rate):
    # Apply FFT - real data so rfft used
    fourier=np.fft.rfft(data)
    # Remove last element in array to make it the same size as chunk
    fourier=np.delete(fourier,len(fourier)-1)
    fourier = fourier[0:256]
    # Find amplitude
    power = np.log10(np.abs(fourier))**2
    # Arrange array into 256 rows for the Unicorn HAT HD
    power = np.reshape(power,(256,1))
    matrix= np.average(power,axis=1)
    return list(matrix.astype(int).astype(float))

def audio_analyse(stream):
    signal = np.frombuffer(stream.read(CHUNK_SIZE, exception_on_overflow = False), FORMAT)

    levels = calculate_levels(signal, CHUNK_SIZE, SAMPLE_RATE)
    return json.dumps(levels)

async def connection_test(request):
    return web.Response(text='Connection test')

async def websocket_handler(request):
    print('Websocket connection starting')
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    print('Websocket connection ready')

    # rgb = audio_analyse(stream)
    async for msg in ws:
        levels = audio_analyse(stream)
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(levels)

    print('Websocket connection closed')
    return ws


def main():

    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', connection_test)
    app.router.add_route('GET', '/ws', websocket_handler)
    web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stream = p.open(format=AUDIO_FORMAT, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK_SIZE)
    main()
