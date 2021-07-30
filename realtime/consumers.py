from channels.generic.websocket import JsonWebsocketConsumer
import json
from asgiref.sync import async_to_sync

class RealtimeServer(JsonWebsocketConsumer):

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass