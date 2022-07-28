from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def test_text_max_length(self):
        """Проверка макисмальной длины
        возвращаемого значения методом str модели."""
        post = PostModelTest.post
        max_length_text = 15
        length_text = len(post.text)
        self.assertTrue(
            length_text < max_length_text,
            'Метод str модели Post возвращает более 15 символов'
        )
