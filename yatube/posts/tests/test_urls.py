from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post
from django.core.cache import cache

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasVlasov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            pk=84,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user)
        cache.clear()

    def test_urls_availability_page(self):
        url_names = {
            '/': HTTPStatus.OK,
            f'/group/{StaticURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{StaticURLTests.user.username}/': HTTPStatus.OK,
            f'/posts/{StaticURLTests.post.pk}/': HTTPStatus.OK,
            '/unixisting_page': HTTPStatus.NOT_FOUND,
        }
        for address, st_code in url_names.items():
            with self.subTest(st_code=st_code):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, st_code)

    def test_urls_availsbility_page_post_to_the_author(self):
        test_list_urls = {
            '/posts/84/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
        }
        for address, st_code in test_list_urls.items():
            with self.subTest(st_code=st_code):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, st_code)

    def test_urls_uses_correct_template(self):
        template_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/profile.html': f'/profile/{StaticURLTests.user.username}/',
            'posts/post_detail.html':
            f'/posts/{StaticURLTests.post.pk}/',
            'posts/create_post.html': '/posts/84/edit/',
        }

        for template, address in template_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_page_create_post_correct_template(self):
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_availability_page_create_guest_user(self):
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
