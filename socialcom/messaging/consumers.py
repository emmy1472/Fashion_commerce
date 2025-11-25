import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import MessageSerializer

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):

    # Connect to WebSocket
    async def connect(self):
        self.conversation_id = self.scope["url_route"] ["kwargs"] ["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    # Disconnect from WebSocket
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        """
        handles different message types:
        - message
        - typing_start
        - typing_stop
        """
        data = json.loads(text_data)
        message_text = data.get("message")
        user_id = self.scope["user"].id
        user_email = self.scope["user"].email

        # user is typing
        if message_data == "typing...":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_event",
                    "status": "typing...",
                    "user_id": user_id,
                    "email": user_email
                }
            )
            return
        
        # user stopped typing
        if message_data == "typing_stop":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_event",
                    "status": "typing_stop",
                    "user_id": user_id,
                    "email": user_email
                }
            )
            return
        
        # sending a real message
        if message_data == "message":
            text = data.get("text")
            message_data = await self.save_message(user_id, text)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message_data
                }
            )
        

    # handle typing broadcast
    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            "event": "typing",
            "status": event["status"],
            "user_id": event["user_id"],
            "email": event["email"],
        }))

    
    # Handler for group send
    async def chat_message(self, event):
        message_data = event["message"]
        await self.send(text_data=json.dumps(message_data))

    # Save message to DB
    @database_sync_to_async
    def save_message(self, sender_id, text):
        sender = User.objects.get(id=sender_id)
        conversation = Conversation.objects.get(id=self.conversation_id)

        m = Message.objects.create(
            sender=sender,
            conversation=conversation,
            text=text
        )
        return MessageSerializer(m).data
