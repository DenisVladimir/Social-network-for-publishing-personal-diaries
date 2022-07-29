from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from .utils import My_paginator, Source_author, Source_posts
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.views.decorators.cache import cache_page


NUM_OF_POSTS = 10


@cache_page(20 * 2)
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    page_obj = My_paginator(
        request,
        post_list,
        NUM_OF_POSTS
    )
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    # group-object, groups-related name models, all()- all posts group
    post_list = group.groups.all()
    page_obj = My_paginator(request, post_list, NUM_OF_POSTS)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    amount_posts = post_list.count()
    all_following = Follow.objects.filter(user_id=request.user.pk)
    following = Source_author(all_following, username)
    page_obj = My_paginator(request, post_list, NUM_OF_POSTS)
    context = {
        'author': author,
        'page_obj': page_obj,
        'amount_posts': amount_posts,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)
    amount_posts_author = post.author.posts.all().count()
    comments = post.comments.all()
    form = form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'amount_posts_author': amount_posts_author,
        'comments': comments,
        'form': form
    }
    return render(request, template, context)


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
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = get_object_or_404(User, username=request.user.username)
    all_favorite_authors = user.follower.all()
    post_list = Source_posts(all_favorite_authors)
    page_obj = My_paginator(request, post_list, NUM_OF_POSTS)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=author)
