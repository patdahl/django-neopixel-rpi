import asyncio, functools, json, random, string, time
from functools import partial

from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncConsumer, SyncConsumer
from channels.layers import get_channel_layer
from channels.utils import await_many_dispatch

import board, neopixel

from .pixels import PixelManager, StaticPixel, SinPixel, WanderPixel

NUM_PIXELS = 500
CLASSIC_COLORS = [
        (40,180,220),# cyan
        (230,100,0),# orangish yellow
        (230,60,65),# pink
        (255,0,0),# red
        (0,220,10),# green
    ]


SYNTHWAVE = [
    (20,200,220),
    (255,50,0),
    (150,0,155),
    (200,20,65)

]
params = [
    (random.choice(SYNTHWAVE),
        {
            't0':ii
            # 'a' : random.choice(range(5,15))

            # 'a':3
        }
    ) for ii in range(0,NUM_PIXELS)
]


pxs = [
    SinPixel(*p[0],t0=ii,a=10) for ii,p in enumerate(params)
]

class PixelController(AsyncConsumer):
    channel_layer_alias = 'pixel-controller'

    
    def __init__(self):
        # pxs = 
        self.pixels = PixelManager(pxs)
        self._neopixels = neopixel.NeoPixel(
            board.D18, NUM_PIXELS, brightness=1, auto_write=False, pixel_order=neopixel.GRB
        )
        self.frame_delay = 0.000 # in seconds

    async def __call__(self, scope, receive, send):

        """
        Dispatches incoming messages to type-based handlers asynchronously.
        """
        self.scope = scope

        # Initialize channel layer
        self.channel_layer = get_channel_layer(self.channel_layer_alias)
        if self.channel_layer is not None:
            self.channel_name = await self.channel_layer.new_channel()
            self.channel_receive = functools.partial(
                self.channel_layer.receive, self.channel_name
            )
        # Store send function
        if self._sync:
            self.base_send = async_to_sync(send)
        else:
            self.base_send = send
        # Pass messages in from channel layer or client to dispatch method
        try:
            if self.channel_layer is not None:
                await await_many_dispatch(
                    [receive, self.channel_receive, self.order_work], self.dispatch
                )
            else:
                await await_many_dispatch([receive, self.order_work], self.dispatch)
        except StopConsumer:
            # Exit cleanly
            pass

    async def dispatch(self, message):
        if message is not None:
            return await super().dispatch(message)
        else:
            pass
    
    async def order_work(self):
        await self.pixels_render(None)
        return None


    async def pixels_fill(self,message):
        color = message.get('color')
        for pixel in self.pixels:
            pixel.color = color

    async def pixels_progress(self,message):
        self.pixels.progress()

    async def pixels_render(self,message):
        await self.pixels_progress(None)
        self._neopixels[:] = self.pixels.as_colors()
        self._neopixels.show()
        # print(self._neopixels[0])

    async def delay_set(self,message):
        delay = message.get('delay')
        self.frame_delay = delay
