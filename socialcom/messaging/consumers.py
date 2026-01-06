import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import MessageSerializer
from typing import Optional, Dict

logger = logging.getLogger(__name__)

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):

    # Connect to WebSocket
    async def connect(self):
        self.conversation_id = self.scope["url_route"] ["kwargs"] ["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        # reject anonymous users
        user = self.scope.get("user")
        if not user or getattr(user, "is_anonymous", True):
            print(f"Websocket connect refused: anonymous user in scope: {user}")
            await self.close()
            return

        # ensure user is a participant in the conversation
        is_participant = await self._is_participant(user.id, self.conversation_id)
        if not is_participant:
            print(f"Websocket connect refused: user {user.id} not participant in conversation {self.conversation_id}")
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    @database_sync_to_async
    def _is_participant(self, user_id, conv_id):
        return Conversation.objects.filter(id=conv_id, participants__id=user_id).exists()

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
        try:
            data = json.loads(text_data)
        except Exception:
            logger.exception("Failed to parse incoming websocket data")
            return

        # normalized event type
        event = data.get("event") or data.get("type") or data.get("action")
        user = self.scope.get("user")
        user_id = getattr(user, "id", None)
        user_email = getattr(user, "email", None)

        # typing started
        if event == "typing_start":
            try:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "typing_event",
                        "status": "typing_start",
                        "user_id": user_id,
                        "email": user_email,
                    },
                )
            except Exception:
                logger.exception("Failed to broadcast typing_start")
            return

        # typing stopped
        if event == "typing_stop":
            try:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "typing_event",
                        "status": "typing_stop",
                        "user_id": user_id,
                        "email": user_email,
                    },
                )
            except Exception:
                logger.exception("Failed to broadcast typing_stop")
            return

        # send a new message
        if event == "message":
            text = data.get("text")
            if not text:
                # ignore empty messages
                return

            try:
                message_data = await self.save_message(user_id, text)
            except Exception:
                logger.exception("Failed to save message")
                return

            try:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message_data,
                    },
                )
            except Exception:
                logger.exception("Failed to broadcast chat_message")
            return
        

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
        # send a structured event to the client
        await self.send(text_data=json.dumps({
            "event": "message",
            "message": message_data,
        }))

    # Save message to DB
    @database_sync_to_async
    def save_message(self, sender_id: int, text: str) -> Optional[Dict]:
        """Persist a message and return serialized data.

        Returns serialized message dict or None on failure.
        """
        try:
            sender = User.objects.get(id=sender_id)
            conversation = Conversation.objects.get(id=self.conversation_id)

            m = Message.objects.create(sender=sender, conversation=conversation, text=text)
            return MessageSerializer(m).data
        except Exception:
            logger.exception("Error saving message to DB")
            return None
