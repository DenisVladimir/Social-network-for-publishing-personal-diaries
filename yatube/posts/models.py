from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model() #Модель отвечающая за управление пользователями

class Post(models.Model):
    
    text = models.TextField() # поле формата текст
    pub_date = models.DateTimeField(auto_now_add= True) # поле даты создания поста. auth_now_add-для автоматическогоприсваения даты посту
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='posts'
        ) # полея для указания ссылки на другую модель(другую таблицу) 
    #on_delete=models.CASCADE обеспечивает связанность данных при удаление пользователя будут удалены все посты 
    group = models.ForeignKey(
        'Group',
        blank= True,
        null= True,
        on_delete = models.SET_NULL,
        related_name = 'groups'                
    )
    # Поле для картинки  (не обязательное)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/', # Дирректория куда будут загружаться файлы
        blank=True
    )


    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        # выводим текст поста 
        return self.text[0:15]

class Group(models.Model):
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()    

    def __str__(self):        
        return self.title[0:10] # в имени группы выведет первые 10 символов

class Comment(models.Model):

    post = models.ForeignKey(
        'Post',
        null= True,
        on_delete = models.CASCADE,
        related_name = 'comments'                
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
        )
    text = models.TextField() # поле формата текст
    created = models.DateTimeField(auto_now_add= True)

class Follow(models.Model):
    """ Модель системы подписки """
    # Кто подписан
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    # На кого подписан
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )