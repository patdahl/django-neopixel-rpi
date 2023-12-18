
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

def doit(message):
    async_to_sync(channel_layer.group_send)('hard-work',
        message
    )
