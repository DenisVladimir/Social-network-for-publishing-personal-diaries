from django.core.paginator import Paginator


def my_paginator(request, post_list, NUM_OF_POSTS):
    pagin = Paginator(post_list, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = pagin.get_page(page_number)
    return page_obj


def source_author(all_fallower, username):
    for follow in all_fallower:
        if str(username) == str(follow.author):
            return True
    return False


def source_posts(all_favorite_authors):
    posts_data = []
    for object_author in all_favorite_authors:
        for post in object_author.author.posts.all():
            posts_data.append(post)
    return posts_data
