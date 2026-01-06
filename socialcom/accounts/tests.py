from django.test import TestCase
from rest_framework.test import APIClient
from .models import User, EmailVerification, PasswordResetOTP
from django.utils import timezone
from datetime import timedelta
from django.core import mail


class AccountsTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_register_creates_user_and_sends_verification(self):
		url = '/api/register/'
		data = {
			'username': 'alice',
			'email': 'alice@example.com',
			'password': 'ComplexPass123!',
			'role': 'model'
		}
		resp = self.client.post(url, data, format='json')
		self.assertEqual(resp.status_code, 201)
		user = User.objects.filter(email='alice@example.com').first()
		self.assertIsNotNone(user)
		# EmailVerification created and email sent
		verification = EmailVerification.objects.filter(user=user).first()
		self.assertIsNotNone(verification)
		self.assertEqual(len(mail.outbox), 1)
		self.assertIn(verification.code, mail.outbox[0].body)

	def test_register_with_invalid_role_fails(self):
		resp = self.client.post('/api/register/', {'username': 'x', 'email': 'x@ex.com', 'password': 'StrongPass123!', 'role': 'invalid'}, format='json')
		self.assertEqual(resp.status_code, 400)
		self.assertIn('role', resp.data)

	def test_verify_email_success_and_expiry(self):
		user = User.objects.create_user(username='bob', email='bob@example.com')
		verification = EmailVerification.objects.create(user=user, code='123456')

		# successful verify
		resp = self.client.post('/api/verify-email/', {'email': user.email, 'code': '123456'}, format='json')
		self.assertEqual(resp.status_code, 200)
		user.refresh_from_db()
		self.assertTrue(user.is_verified)
		self.assertFalse(EmailVerification.objects.filter(user=user).exists())

		# expired code
		user2 = User.objects.create_user(username='c', email='c@example.com')
		expired = EmailVerification.objects.create(user=user2, code='999999')
		expired.created_at = timezone.now() - timedelta(minutes=60)
		expired.save()
		resp = self.client.post('/api/verify-email/', {'email': user2.email, 'code': '999999'}, format='json')
		self.assertEqual(resp.status_code, 400)

	def test_password_reset_flow(self):
		user = User.objects.create_user(username='dan', email='dan@example.com')
		resp = self.client.post('/api/password-reset/request/', {'email': user.email}, format='json')
		self.assertEqual(resp.status_code, 201)
		otp = PasswordResetOTP.objects.filter(user=user).first()
		self.assertIsNotNone(otp)
		self.assertEqual(len(mail.outbox), 1)

		# reset password
		resp = self.client.post('/api/password-reset/confirm/', {'email': user.email, 'code': otp.code, 'new_password': 'NewStrongPass123!'}, format='json')
		self.assertEqual(resp.status_code, 200)
		user.refresh_from_db()
		self.assertTrue(user.check_password('NewStrongPass123!'))

	def test_password_reset_request_for_unknown_email_is_generic(self):
		resp = self.client.post('/api/password-reset/request/', {'email': 'unknown@example.com'}, format='json')
		self.assertEqual(resp.status_code, 201)
		self.assertIn('message', resp.data)

	def test_login_returns_tokens(self):
		pw = 'LoginPass123!'
		user = User.objects.create_user(username='ed', email='ed@example.com')
		user.set_password(pw)
		user.save()
		resp = self.client.post('/api/login/', {'email': user.email, 'password': pw}, format='json')
		self.assertEqual(resp.status_code, 200)
		self.assertIn('access', resp.data)
		self.assertIn('refresh', resp.data)

	def test_user_list_and_profile(self):
		# create users
		for i in range(3):
			User.objects.create_user(username=f'u{i}', email=f'u{i}@example.com')

		resp = self.client.get('/api/users/')
		self.assertEqual(resp.status_code, 200)
		self.assertTrue(isinstance(resp.data, list) or 'results' in resp.data)

		# profile get/put
		user = User.objects.create_user(username='frank', email='frank@example.com')
		client = APIClient()
		client.force_authenticate(user=user)
		resp = client.get('/api/profile/')
		self.assertEqual(resp.status_code, 200)
		resp = client.put('/api/profile/', {'full_name': 'Frank Smith'}, format='json')
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp.data.get('full_name'), 'Frank Smith')
