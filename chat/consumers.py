import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatGroup, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']  # usamos id o slug
        # accept connection only if group exists and user has access
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('content', '').strip()
        user = self.scope['user']

        if not content or not user.is_authenticated:
            return

        allowed = await self.user_can_send(self.group_name, user.id)
        if not allowed:
            return

        msg = await self.save_message(self.group_name, user.id, content)

        payload = {
            'sender': user.username,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'sender_id': user.id  # 🔥 CLAVE
        }

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'message': payload
            }
        )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'content': message['content'],
            'sender': message['sender'],
            'timestamp': message['timestamp'],
            'is_me': self.scope['user'].id == message['sender_id']
        }))

    @database_sync_to_async
    def user_can_send(self, group_id, user_id):
        try:
            group = ChatGroup.objects.get(id=int(group_id))
        except:
            return False
        user = User.objects.get(id=user_id)
        # anuncios special: only admin/manager can send
        if group.is_public and group.name.lower() == 'anuncios' and user.role == 'employee':
            return False
        # if public group, allow send if public; if private, user must be member
        if group.is_public:
            return True
        return user in group.members.all()

    @database_sync_to_async
    def save_message(self, group_id, user_id, content):
        group = ChatGroup.objects.get(id=int(group_id))
        user = User.objects.get(id=user_id)
        return Message.objects.create(group=group, sender=user, content=content)