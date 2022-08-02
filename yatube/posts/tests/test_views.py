from http import HTTPStatus
from django.core.cache import cache
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, Follow
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

User = get_user_model()


class PostPagesTest(TestCase):
    """Тесты для проверки posts.views."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='StasVlasov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTest.user)
        cache.clear()

    def test_pages_user_correct_template(self):
        template_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': 'StasVlasov'}
            ),
            'posts/create_post.html': reverse(
                'posts:update_post', kwargs={'post_id': 1}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': 1}
            )
        }
        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_page_correct_template(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_group_list_page_show_correct_context(self):
        responce = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'})
        )
        first_object = responce.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.author, PostPagesTest.user)

    def test_profile_page_show_correct_context(self):
        responce = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'StasVlasov'})
        )
        first_object = responce.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.author, PostPagesTest.user)

    def test_create_post_page_show_correct_context(self):
        responce = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = responce.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_update_post_page_show_correct_context(self):
        responce = self.authorized_client.get(
            reverse('posts:update_post', kwargs={'post_id': 1})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = responce.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_paginator_pages_all(self):
        obj_post = [
            Post(
                text='Тестовый пост',
                author=PostPagesTest.user,
                group=PostPagesTest.group,) for x in range(1, 13)
        ]
        Post.objects.bulk_create(obj_post)

        page_address = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'}
            ),
            reverse('posts:profile', kwargs={'username': 'StasVlasov'}),
            reverse('posts:profile',
                    kwargs={'username': 'StasVlasov'}),
        ]
        page_and_posts = {
            1: 10,
            2: 3,
        }
        for address_site in page_address:
            for page, number_posts in page_and_posts.items():
                with self.subTest(page=page):
                    responce = self.authorized_client.get(
                        address_site, {'page': page}
                    )
                    self.assertEqual(
                        len(responce.context['page_obj']), number_posts
                    )

    def test_additional_to_enter_posts_all(self):
        address = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'StasVlasov'})
        ]
        for one_address in address:
            first_object = self.authorized_client.get(one_address)
            for one_post in first_object.context['page_obj']:
                self.assertEqual(str(one_post), str(PostPagesTest.post))

    def test_correct_context_image(self):
        """ Шаблон сформирован с правильным контекстом  picture """
        post_image = PostPagesTest.post.image
        template_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'StasVlasov'}),
        ]
        for reverse_pages in template_pages_names:
            response = self.authorized_client.get(reverse_pages)
            first_object = response.context['page_obj'][0]
            posts_image_0 = first_object.image
            self.assertEqual(posts_image_0, post_image)
        response_2 = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        posts_image_1 = response_2.context.get('post').image
        self.assertEqual(posts_image_1, post_image)


class CacheTest(TestCase):
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
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()

    def test_home_page_cache(self):
        """ Тест кэширования страницы index.html """
        first_state = self.guest_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.text = 'Измененный текст'
        post_1.save()
        second_state = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(first_state.content, second_state.content)
        cache.clear()
        third_state = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(first_state.content, third_state.content)


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(username='follower')
        self.user_following = User.objects.create_user(username='following')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовая запись для тестирования ленты'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        self.client_auth_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_following.username}
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.client_auth_follower.get(reverse('posts:profile_unfollow',
                                      kwargs={'username':
                                              self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_feed(self):
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_auth_follower.get('/follow/')
        post_text_0 = response.context["page_obj"][0].text
        self.assertEqual(post_text_0, 'Тестовая запись для тестирования ленты')
        response = self.client_auth_following.get('/follow/')
        self.assertNotContains(response,
                               'Тестовая запись для тестирования ленты')

    def test_add_comment(self):
        self.client_auth_following.post(
            f'/posts/{self.post.id}/comment/',
            {'text': "тестовый комментарий"},
            follow=True
        )
        comment = self.post.comments.filter(text='тестовый комментарий')[0]
        self.assertEqual(comment.text, 'тестовый комментарий')
