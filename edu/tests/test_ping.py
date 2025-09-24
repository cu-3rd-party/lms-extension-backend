from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class TestPing(APITestCase):
    def test_ping(self):
        url = reverse('ping')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
