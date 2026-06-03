import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .views import active_rooms

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # reject if more than 2 users
        if len(active_rooms.get(self.room_name, [])) > 2:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        if self.room_name in active_rooms:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_list',
                    'users': active_rooms.get(self.room_name, []),
                }
            )

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # delete room after exit
        if self.room_name in active_rooms:
            active_rooms.pop(self.room_name, None)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_list',
                    'users': active_rooms.get(self.room_name, []),
                }
            )

    async def receive(self, text_data):

        data = json.loads(text_data)
        username = data.get('username')

        if 'typing' in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'username': username,
                    'typing': data['typing'],
                }
            )
            return

        message = data.get('message')

        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                }
            )

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
        }))

    async def typing_indicator(self, event):

        await self.send(text_data=json.dumps({
            'typing': event['typing'],
            'username': event['username'],
        }))

    async def user_list(self, event):

        await self.send(text_data=json.dumps({
            'user_list': event['users'],
        }))