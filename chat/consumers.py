import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    """
    диалог после подтверждения заявки (как соло, так и групповой)
    """

    async def connect(self):
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'chat_{self.conversation_id}'

        conversation = await self.get_conversation_if_allowed(
            self.conversation_id, self.user
        )
        if conversation is None:
            await self.close(code=4003)  # нет доступа / не существует
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        history = await self.get_history(self.conversation_id)
        await self.send(text_data=json.dumps({
            'type': 'history',
            'messages': history,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        text = (data.get('message') or '').strip()
        if not text:
            return

        message = await self.save_message(self.conversation_id, self.user, text)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
        }))


    @database_sync_to_async
    def get_conversation_if_allowed(self, conversation_id, user):
        from .models import Conversation
        try:
            conv = Conversation.objects.select_related(
                'application__student__user',
                'application__team__captain__user',
                'application__project__partner__user',
            ).get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return None
        return conv if conv.has_access(user) else None

    @database_sync_to_async
    def save_message(self, conversation_id, user, text):
        from .models import Conversation, Message
        conv = Conversation.objects.get(pk=conversation_id)
        msg = Message.objects.create(conversation=conv, sender=user, text=text)
        return {
            'id': msg.id,
            'sender': user.get_full_name() or user.username,
            'sender_id': user.id,
            'text': msg.text,
            'created_at': msg.created_at.strftime('%d.%m.%Y %H:%M'),
        }

    @database_sync_to_async
    def get_history(self, conversation_id):
        from .models import Message
        qs = Message.objects.filter(
            conversation_id=conversation_id
        ).select_related('sender').order_by('created_at')[:200]
        return [
            {
                'id': m.id,
                'sender': m.sender.get_full_name() or m.sender.username,
                'sender_id': m.sender_id,
                'text': m.text,
                'created_at': m.created_at.strftime('%d.%m.%Y %H:%M'),
            }
            for m in qs
        ]
