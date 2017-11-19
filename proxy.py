#!/usr/bin/env python

import asyncio
import websockets

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

backendurl = "wss://api.gemini.com/v1/marketdata/BTCUSD"

async def consumer_handler(websocket, backend):
    async for message in backend:
        await websocket.send(message)

async def producer_handler(websocket, backend):
    async for message in websocket:
        await backend.send(message)

async def handler(websocket, path):

    async with websockets.connect(backendurl) as backend:
        logger.info("Connected to the backend!")

        consumer_task = asyncio.ensure_future(consumer_handler(websocket, backend))
        producer_task = asyncio.ensure_future(producer_handler(websocket, backend))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

asyncio.get_event_loop().run_until_complete(
    websockets.serve(handler, 'localhost', 9876))

asyncio.get_event_loop().run_forever()
