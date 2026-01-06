import asyncio
import unittest
from django.test import TransactionTestCase
try:
    from channels.testing import WebsocketCommunicator
except Exception:
    WebsocketCommunicator = None
    # Provide a fallback communicator that doesn't require daphne by using
    # asgiref.testing.ApplicationCommunicator. This allows running websocket
    # tests without installing daphne (useful for local quick runs).
    try:
        from asgiref.testing import ApplicationCommunicator
        import json

        class WebsocketCommunicatorFallback:
            def __init__(self, app, path):
                self.app = app
                self.path = path
                self.scope = {"type": "websocket", "path": path, "headers": [], "query_string": b""}
                # provide url_route kwargs similar to channels routing so consumers
                # that rely on url_route.kwargs (conversation_id) can work
                try:
                    import re

                    m = re.search(r"/ws/chat/(?P<conversation_id>\d+)/", path)
                    if m:
                        self.scope["url_route"] = {"kwargs": {"conversation_id": int(m.group("conversation_id"))}}
                    else:
                        self.scope["url_route"] = {"kwargs": {}}
                except Exception:
                    self.scope["url_route"] = {"kwargs": {}}
                self._comm = None

            async def connect(self):
                self._comm = ApplicationCommunicator(self.app, self.scope)
                await self._comm.send_input({"type": "websocket.connect"})
                try:
                    event = await self._comm.receive_output(1)
                except Exception:
                    # timed out waiting for accept
                    return False, None

                if event and event.get("type") == "websocket.accept":
                    return True, None
                # expose the event for debugging
                try:
                    extra = await self._comm.receive_output(0.1)
                    print("Websocket connect failed, extra event:", event, extra)
                except Exception:
                    print("Websocket connect failed, event:", event)
                return False, None

            async def send_json_to(self, data):
                await self._comm.send_input({"type": "websocket.receive", "text": json.dumps(data)})

            async def receive_json_from(self, timeout=None):
                event = await self._comm.receive_output(timeout)
                if event is None:
                    raise AssertionError("No event received")
                if event.get("type") == "websocket.send":
                    text = event.get("text")
                    return json.loads(text)
                return {}

            async def disconnect(self):
                await self._comm.send_input({"type": "websocket.disconnect"})

        WebsocketCommunicator = WebsocketCommunicatorFallback
    except Exception:
        WebsocketCommunicator = None
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .consumers import ChatConsumer
from channels.db import database_sync_to_async


User = get_user_model()


class ChatConsumerAsyncTests(TransactionTestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.user1 = User.objects.create_user(email="ws1@example.com", username="ws1", password="pass")
        self.user2 = User.objects.create_user(email="ws2@example.com", username="ws2", password="pass")
        # create a conversation for tests that require it; do this synchronously to
        # avoid sqlite locking issues when creating objects from async threads
        self.conv = Conversation.objects.create()
        self.conv.participants.add(self.user1, self.user2)

    def test_anonymous_connection_denied(self):
        self.loop.run_until_complete(self.async_anonymous_connection_denied())

    async def async_anonymous_connection_denied(self):
        app = ChatConsumer.as_asgi()
        comm = WebsocketCommunicator(app, "/ws/chat/999/")
        # ensure scope has url_route for consumer
        comm.scope["url_route"] = {"kwargs": {"conversation_id": 999}}
        connected, _ = await comm.connect()
        # anonymous should be rejected
        self.assertFalse(connected)
        await comm.disconnect()

    def test_message_broadcast_and_persistence(self):
        self.loop.run_until_complete(self.async_message_broadcast_and_persistence())

    async def async_message_broadcast_and_persistence(self):
        conv = self.conv

        app = ChatConsumer.as_asgi()

        comm1 = WebsocketCommunicator(app, f"/ws/chat/{conv.id}/")
        # set the authenticated user and url_route kwargs so consumer can read them
        comm1.scope["user"] = self.user1
        comm1.scope["url_route"] = {"kwargs": {"conversation_id": conv.id}}
        connected1, _ = await comm1.connect()
        self.assertTrue(connected1)

        comm2 = WebsocketCommunicator(app, f"/ws/chat/{conv.id}/")
        comm2.scope["user"] = self.user2
        comm2.scope["url_route"] = {"kwargs": {"conversation_id": conv.id}}
        connected2, _ = await comm2.connect()
        self.assertTrue(connected2)

        # send a message from user1
        await comm1.send_json_to({"event": "message", "text": "hello world"})

        # user2 should receive the broadcasted message
        msg = await comm2.receive_json_from()
        self.assertEqual(msg.get("event"), "message")
        self.assertIn("message", msg)
        self.assertEqual(msg["message"]["text"], "hello world")

        # message should be persisted (use sync wrapper to query DB safely)
        @database_sync_to_async
        def _get_message(conv_id):
            return Message.objects.filter(conversation__id=conv_id, text="hello world").values("id", "sender_id").first()

        m = await _get_message(conv.id)
        self.assertIsNotNone(m)
        self.assertEqual(m["sender_id"], self.user1.id)

        await comm1.disconnect()
        await comm2.disconnect()

    def test_typing_events_broadcast(self):
        self.loop.run_until_complete(self.async_typing_events_broadcast())

    async def async_typing_events_broadcast(self):
        conv = self.conv
        app = ChatConsumer.as_asgi()

        comm1 = WebsocketCommunicator(app, f"/ws/chat/{conv.id}/")
        comm1.scope["user"] = self.user1
        comm1.scope["url_route"] = {"kwargs": {"conversation_id": conv.id}}
        connected1, _ = await comm1.connect()
        self.assertTrue(connected1)

        comm2 = WebsocketCommunicator(app, f"/ws/chat/{conv.id}/")
        comm2.scope["user"] = self.user2
        comm2.scope["url_route"] = {"kwargs": {"conversation_id": conv.id}}
        connected2, _ = await comm2.connect()
        self.assertTrue(connected2)

        await comm1.send_json_to({"event": "typing_start"})
        ev = await comm2.receive_json_from()
        self.assertEqual(ev.get("event"), "typing")
        self.assertEqual(ev.get("status"), "typing_start")

        await comm1.send_json_to({"event": "typing_stop"})
        ev2 = await comm2.receive_json_from()
        self.assertEqual(ev2.get("event"), "typing")
        self.assertEqual(ev2.get("status"), "typing_stop")

        await comm1.disconnect()
        await comm2.disconnect()
