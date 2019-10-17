from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successfully(self):
        """test creating user with valid payload successfully"""
        payload = {
            'email': 'test@email.com',
            'password': 'password',
            'name': 'Kofi Avetile'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """test creating user that already exists fails"""
        payload = {
            'email': 'test@email.com',
            'password': 'password',
            'name': 'Kofi Avetile'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """test that the password is more than 5 characters"""
        payload = {
            'email': 'test@email.com',
            'password': 'pw',
            'name': 'Kofi Avetile'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_valid_user(self):
        """test that token is created for user"""
        payload = {
            'email': 'test@email.com',
            'password': 'pw'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_for_invalid_user(self):
        """test that token is not created for incorrect user credentials"""
        create_user(email='test@email.com', password='pass')
        payload = {
            'email': 'test@email.com',
            'password': 'pword'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """test that token is not created if user does not exist"""
        payload = {
            'email': 'test2@email.com',
            'password': 'pword'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """test that email and password are required"""
        payload = {
            'email': 'test',
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """test that authentication is required to access a profile"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test api's that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@email.com',
            password='password',
            name='Kofi Avetile'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_not_allowed_for_own_profile(self):
        """test that post is not allowed on own url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_own_user_profile(self):
        """test updating theuser profile for authenticated user"""
        payload = {
            'name': 'new',
            'password': 'newpass'
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
