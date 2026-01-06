from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Conversation, Message


User = get_user_model()


class MessagingViewsTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user1 = User.objects.create_user(email="u1@example.com", username="u1", password="pass")
		self.user2 = User.objects.create_user(email="u2@example.com", username="u2", password="pass")

	def test_create_conversation(self):
		self.client.force_authenticate(self.user1)
		resp = self.client.post("/api/messages/conversation/", {"user_id": self.user2.id}, format="json")
		self.assertIn(resp.status_code, (200, 201))
		data = resp.json()
		self.assertIn("id", data)
		conv = Conversation.objects.get(id=data["id"] if isinstance(data, dict) and "id" in data else data)
		participants = list(conv.participants.all())
		self.assertIn(self.user1, participants)
		self.assertIn(self.user2, participants)

	def test_send_and_list_messages(self):
		# create conversation
		conv = Conversation.objects.create()
		conv.participants.add(self.user1, self.user2)

		# send messages
		self.client.force_authenticate(self.user1)
		send_url = f"/api/messages/conversation/{conv.id}/send/"
		for i in range(30):
			r = self.client.post(send_url, {"text": f"hello {i}"}, format="json")
			self.assertEqual(r.status_code, 201)

		# list messages (paginated)
		list_url = f"/api/messages/conversation/{conv.id}/messages/"
		r = self.client.get(list_url)
		self.assertEqual(r.status_code, 200)
		data = r.json()
		# paginated response should have 'results'
		self.assertIn("results", data)
		self.assertGreaterEqual(len(data["results"]), 1)

	def test_conversation_last_message_serializer(self):
		conv = Conversation.objects.create()
		conv.participants.add(self.user1, self.user2)

		# no messages yet
		from .serializers import ConversationSerializer
		s = ConversationSerializer(conv)
		self.assertIsNone(s.data.get("last_message"))

		# add a message
		Message.objects.create(conversation=conv, sender=self.user1, text="hey")
		s = ConversationSerializer(conv)
		self.assertIsNotNone(s.data.get("last_message"))
