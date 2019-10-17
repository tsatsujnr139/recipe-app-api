from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def sample_user():
    return get_user_model().objects.create_user(email='user@company.com',
                                                password='password')


class PublicTagsApiTests(TestCase):
    """test the public tag api's"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required_to_retrieve_tags(self):
        """test that login is required to retrieve tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """test the authorized user tag API's"""

    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_authenticated_user(self):
        """Test that tags are for authenticated user"""
        user2 = get_user_model().objects.create_user(email='user2@company.com',
                                                     password='password')

        Tag.objects.create(user=user2, name='fruity')
        tag = Tag.objects.create(user=self.user, name='comfort food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tags_successfully(self):
        """test that new tag is created successfully"""
        payload = {
            'name': 'test_tag'
        }
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """test creating a tag with invalid payload returns valiation error"""
        payload = {
            'name': ''
        }
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
