from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
from django.core.cache import cache


from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasLubar')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            pk=10,
            text='Тестовый пост',
            group=cls.group,
            author=User.objects.get(username='StasLubar')
        )

    def setUp(self):
        self.user = PostFormTests.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,))
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_create_post_guest_client(self):
        response = self.guest_client.get(
            reverse('posts:update_post', kwargs={'post_id': 1})
        )
        self.assertRedirects(
            response,
            reverse('auth:login') + '?next=%2Fposts%2F1%2Fedit%2F'
        )

    def test_edit_post(self):
        """Проверка формы редактирования поста и его изменение
        в базе данных."""
        group_field_new = self.group.id
        edit_post_var = Post.objects.get(id=self.post.id)
        form_data = {
            'text': 'Тестовый пост',
            'group': group_field_new,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:update_post',
                kwargs={
                    'post_id': self.post.pk
                }

            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.pk
                }
            )
        )
        self.assertEqual(edit_post_var.text, form_data['text'])
        self.assertEqual(edit_post_var.author, self.post.author)

    def test_post_with_picture(self):
        # Создается пост с картинкой
        count_posts = Post.objects.count()
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
        form_data = {
            'text': 'Пост с картинкой',
            'group': self.group.id,
            'image': uploaded
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), count_posts + 1)
        post_0 = Post.objects.get(text='Пост с картинкой')
        url_addres_site = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'StasLubar'})
        ]
        for address in url_addres_site:
            response = self.authorized_client.get(address)
            test_image = response.context['page_obj'][0].image
            self.assertEqual(post_0.image, test_image)
