from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from .utils import My_paginator, Source_author, Source_posts
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.views.decorators.cache import cache_page


NUM_OF_POSTS = 10 # количество постов для вывода на страницу

#функция обработки главной страницы
@cache_page(20 * 2)
def index(request):
    template = 'posts/index.html'
    #posts = Post.objects.select_related('author', 'group')[:NUM_OF_POSTS] # последние количество постов из базы данных
    #Запрос к базе данных 
    post_list = Post.objects.all()
    #Создание погинатора с параметрами по 10 на странице
    page_obj = My_paginator(request, post_list, NUM_OF_POSTS) # вынесли пагинатор в отдельный файл
    context = {        
        'page_obj': page_obj
    }
    return render(request, template, context)

# функция обработки групп
def group_posts(request, slug):  
    template = 'posts/group_list.html'    
    group = get_object_or_404(Group, slug=slug)
    #posts = Post.objects.filter(group=group).order_by('-pub_date')[:NUM_OF_POSTS]
    post_list= group.groups.all()# group-object, groups-related name models, all()- all posts group
    page_obj = My_paginator(request, post_list, NUM_OF_POSTS)
    context = {        
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)

def profile(request, username):
    # Код запроса к модели и создание словоря контекста  
    
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    amount_posts = post_list.count() # amount posts user
    
    all_following = Follow.objects.filter(user_id=request.user.pk) # все follow на котрых подписан пользователь
    following = Source_author(all_following, username) # самописная функция 
    """
    paginator = Paginator(post_list, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    """
    page_obj = My_paginator(request, post_list, NUM_OF_POSTS) # вынесли пагинатор в отдельный файл
    context = {
        'user': user,
        'page_obj': page_obj,
        'amount_posts': amount_posts,
        'following': following,
    }
    return render(request, template , context)
    

def post_detail(request, post_id):
    # код запроса инофрмации о конкретном посте


    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)    
    amount_posts_author = post.author.posts.all().count()
    comments = post.comments.all() # Комментарий относящийся к определенному посту
    form = form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'amount_posts_author': amount_posts_author,
        'comments': comments,
        'form': form
    }
    return render(request, template , context)

@login_required 
def post_create(request): 
    form = PostForm(request.POST or None, files=request.FILES or None) 
    if not request.method == 'POST':
        return render( 
            request, 
            'posts/create_post.html', 
            {'form': form}
        ) 
    
    if not form.is_valid(): 
        return render( 
            request, 
            'posts/create_post.html', 
            {'form': form} 
        ) 
    post = form.save(commit=False) 
    post.author = request.user 
    post.save() 
    return redirect('posts:profile', request.user.username) 
    
 
@login_required 
def post_edit(request, post_id): 
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    ) 
    if request.method == 'POST': 
        if form.is_valid():
            form.save() 
        return redirect('posts:post_detail', post_id=post.id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render( 
        request, 
        'posts/create_post.html', 
        context 
    )

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    else:
        messages.error(request,'Error')    
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    #Запрос к базе данных
    user = get_object_or_404(User, username=request.user.username)
    all_favorite_authors = user.follower.all() # все любимые авторы пользователя
    post_list = Source_posts(all_favorite_authors) # Написана в отдельном файле utils.py
    #Создание погинатора с параметрами по 10 на странице
    page_obj = My_paginator(request, post_list, NUM_OF_POSTS) # вынесли пагинатор в отдельный файл
    context = {        
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)

@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    Follow.objects.create(
        author_id = author.pk,
        user_id = request.user.pk,
    )
    return redirect('posts:profile', username=username)

@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    delete_follow = Follow.objects.filter(
        author_id=author.pk,
        user_id=request.user.pk,
    )
    delete_follow.delete()
    return redirect('posts:profile', username=username)