from django.contrib.auth import get_user_model
from django.urls import reverse
from core.views import page_not_found
from django.test import TestCase, Client
User = get_user_model()

# 6 sprint
from http import HTTPStatus
from urllib.parse import urljoin


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_page_404(self):
        response = self.guest_client.get('/qwerty12345/')     
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')