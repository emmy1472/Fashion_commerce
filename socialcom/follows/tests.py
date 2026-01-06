from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User
from .models import Follow


class FollowsTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.alice = User.objects.create_user(username='alice', email='alice@example.com')
		self.bob = User.objects.create_user(username='bob', email='bob@example.com')

	def test_follow_and_unfollow(self):
		# must be authenticated
		resp = self.client.post(f'/api/follows/{self.bob.id}/follow/')
		self.assertEqual(resp.status_code, 401)

		self.client.force_authenticate(user=self.alice)
		# follow
		resp = self.client.post(f'/api/follows/{self.bob.id}/follow/')
		self.assertEqual(resp.status_code, 201)
		self.assertTrue(Follow.objects.filter(follower=self.alice, following=self.bob).exists())

		# duplicate follow returns 200
		resp = self.client.post(f'/api/follows/{self.bob.id}/follow/')
		self.assertEqual(resp.status_code, 200)

		# cannot follow self
		resp = self.client.post(f'/api/follows/{self.alice.id}/follow/')
		self.assertEqual(resp.status_code, 400)

		# list followers for bob
		resp = self.client.get(f'/api/follows/{self.bob.id}/followers/')
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp.data['count'], 1)

		# list following for alice
		resp = self.client.get(f'/api/follows/{self.alice.id}/following/')
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp.data['count'], 1)

		# unfollow
		resp = self.client.post(f'/api/follows/{self.bob.id}/unfollow/')
		self.assertEqual(resp.status_code, 200)
		self.assertFalse(Follow.objects.filter(follower=self.alice, following=self.bob).exists())
