from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestPing(APITestCase):
    def test_ping(self):
        url = reverse('api-1.0.0:ping')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
