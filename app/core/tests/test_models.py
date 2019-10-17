from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='user@company.com', password='password'):
    """create a sample user """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is succesful"""
        email = 'test@clutchcode.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@CLUTCHCODE.COM'
        user = get_user_model().objects.create_user(email, 'password')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'password')

    def test_create_new_superuser_is_successful(self):
        """Test creating a new supseruser is successful"""
        email = 'test@clutchcode.com'
        password = 'testpass123'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_str(self):
        """test tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='vegan'
        )

        self.assertEqual(str(tag), tag.name)
