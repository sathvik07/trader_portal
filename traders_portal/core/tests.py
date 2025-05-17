from django.test import TestCase

# Create your tests here.

from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from .models import Watchlist, Company

class AuthenticatedViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass1234")
        self.login_url = reverse('token_obtain_pair')
        self.watchlist_url = reverse('watchlist')
        self.company = Company.objects.create(
            company_name="Test Company",
            symbol="TEST",
            scripcode="123456"
        )

    def authenticate(self):
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "pass1234"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_register_user(self):
        response = self.client.post(reverse('register'), {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "newpass1234"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_watchlist_create_authenticated(self):
        self.authenticate()
        response = self.client.post(self.watchlist_url, {"company_id": self.company.id})
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_watchlist_create_unauthenticated(self):
        response = self.client.post(self.watchlist_url, {"company": self.company.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_watchlist_list_authenticated(self):
        self.authenticate()
        Watchlist.objects.create(user=self.user, company=self.company)
        response = self.client.get(self.watchlist_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_watchlist_delete_authenticated(self):
        self.authenticate()
        watchlist = Watchlist.objects.create(user=self.user, company=self.company)
        url = reverse('watchlist-delete', args=[watchlist.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_watchlist_prevent_duplicate(self):
        self.authenticate()
        self.client.post(self.watchlist_url, {"company_id": self.company.id})
        response = self.client.post(self.watchlist_url, {"company_id": self.company.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # or 400 if you raise ValidationError

    def test_watchlist_invalid_company(self):
        self.authenticate()
        response = self.client.post(self.watchlist_url, {"company_id": 9999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_watchlist_list_unauthenticated(self):
        response = self.client.get(self.watchlist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_watchlist_delete_unauthenticated(self):
        watchlist = Watchlist.objects.create(user=self.user, company=self.company)
        url = reverse('watchlist-delete', args=[watchlist.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


