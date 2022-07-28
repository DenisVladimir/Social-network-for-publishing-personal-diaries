from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .utils import my_paginator
from .models import Comment, Post, Group, User
from .forms import CommentForm, PostForm


NUM_OF_POSTS: int = 10
COUNT_PAGE: int = 10


def index(request):
    post_list = Post.objects.all()
    page_obj = my_paginator(request, post_list, NUM_OF_POSTS)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups.all()
    page_obj = my_paginator(request, post_list, NUM_OF_POSTS)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = my_paginator(request, post_list, NUM_OF_POSTS)
    template = 'posts/profile.html'
    context = {
        'author': author,
        'page_obj': page_obj,
        'post_list': post_list,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.filter(pk=post_id)
    form = CommentForm(request.POST or None)
    # post = Post.objects.select_related('author').filter().count()
    context = {
        'post': post,
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
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post_id=post.id)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'post': post}
    )

@login_required
def add_comment(request, post_id):
    post = (get_object_or_404(Post.objects
            .select_related('author', 'group'), pk=post_id)) 
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id) 
