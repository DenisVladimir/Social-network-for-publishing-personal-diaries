from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import Post, Group
from django.core.cache import cache

User = get_user_model()

# 6 sprint


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasVlasov')
        # создание объекта группы
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        # создение тестового поста
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        # Неавторизированный пользователь
        self.guest_client = Client()

    def test_home_page_cache(self):
        """Тест кэширования страницы index.html"""
        first_state = self.guest_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.text = 'Измененный текст'
        post_1.save()
        second_state = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(first_state.content, second_state.content)
        cache.clear()
        third_state = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(first_state.content, third_state.content)
