from django.core.paginator import Paginator


def my_paginator(request, post_list, NUM_OF_POSTS):
    pagin = Paginator(post_list, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = pagin.get_page(page_number)
    return page_obj
