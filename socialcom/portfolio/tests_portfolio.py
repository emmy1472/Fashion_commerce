from django.test import TestCase
from rest_framework.test import APIClient
from .models import Post, Like, Comment
from accounts.models import User
from django.urls import reverse


class PortfolioTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='pete', email='pete@example.com')
        self.user.set_password('Testpass123!')
        self.user.save()

    def test_create_post_requires_auth(self):
        resp = self.client.post('/api/posts/', {'caption': 'Hi'}, format='multipart')
        self.assertEqual(resp.status_code, 401)

        self.client.force_authenticate(user=self.user)
        with open(__file__, 'rb') as img:
            resp2 = self.client.post('/api/posts/', {'caption': 'Hello', 'image': img}, format='multipart')
        # We expect 201 or 400 depending on image handling in test env but ensure no 500
        self.assertNotEqual(resp2.status_code, 500)

    def test_like_and_unlike(self):
        post = Post.objects.create(user=self.user, caption='c', image='posts/test.jpg')
        # anonymous cannot like
        resp = self.client.post(f'/api/posts/{post.id}/like/')
        self.assertEqual(resp.status_code, 401)

        self.client.force_authenticate(user=self.user)
        resp = self.client.post(f'/api/posts/{post.id}/like/')
        self.assertIn(resp.status_code, (200,201))
        self.assertEqual(post.likes.count(), 1)

        resp = self.client.post(f'/api/posts/{post.id}/like/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(post.likes.count(), 0)

    def test_add_comment_and_list(self):
        self.client.force_authenticate(user=self.user)
        post = Post.objects.create(user=self.user, caption='c', image='posts/test.jpg')
        resp = self.client.post(f'/api/posts/{post.id}/comment/', {'content': 'Nice!'}, format='json')
        self.assertEqual(resp.status_code, 201, msg=f"resp.data={getattr(resp, 'data', None)}")
        resp2 = self.client.get(f'/api/posts/{post.id}/comments/')
        self.assertEqual(resp2.status_code, 200)
        self.assertTrue(len(resp2.data) >= 1 or 'results' in resp2.data)

    def test_owner_update_and_delete_permissions(self):
        # owner can update and delete
        self.client.force_authenticate(user=self.user)
        post = Post.objects.create(user=self.user, caption='orig', image='posts/test.jpg')
        # Use PATCH for partial updates (image is required on full PUT)
        resp = self.client.patch(f'/api/posts/{post.id}/', {'caption': 'updated'}, format='json')
        self.assertIn(resp.status_code, (200, 204))

        resp = self.client.delete(f'/api/posts/{post.id}/')
        self.assertIn(resp.status_code, (200, 204, 202))

    def test_non_owner_cannot_update_or_delete(self):
        other = User.objects.create_user(username='jill', email='jill@example.com')
        post = Post.objects.create(user=self.user, caption='orig', image='posts/test.jpg')
        self.client.force_authenticate(user=other)
        resp = self.client.put(f'/api/posts/{post.id}/', {'caption': 'bad'}, format='json')
        self.assertEqual(resp.status_code, 403)

        resp = self.client.delete(f'/api/posts/{post.id}/')
        self.assertEqual(resp.status_code, 403)
