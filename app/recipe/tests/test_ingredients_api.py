from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def sample_user():
    return get_user_model().objects.create_user(email='user@company.com',
                                                password='password')


class PublicIngredientsApiTests(TestCase):
    """test the public ingredients api's"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required_to_retrieve_ingredient(self):
        """test that login is required to retrieve tags"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """test the authorized user ingredient API's"""

    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients"""
        Ingredient.objects.create(user=self.user, name='salami')
        Ingredient.objects.create(user=self.user, name='onion')

        res = self.client.get(INGREDIENTS_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_authenticated_user(self):
        """Test that ingredients are for authenticated user"""
        user2 = get_user_model().objects.create_user(email='user2@company.com',
                                                     password='password')

        Ingredient.objects.create(user=user2, name='bacon')
        ingredient = Ingredient.objects.create(user=self.user, name='nutmeg')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successfully(self):
        """test that new ingredient is created successfully"""
        payload = {
            'name': 'test_ingredient'
        }
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists
        self.assertTrue(exists)

    def test_create_ingredient_invalid_payload_fails(self):
        """test creating an ingredient with invalid payload

            returns valiation error"""
        payload = {
            'name': ''
        }
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
