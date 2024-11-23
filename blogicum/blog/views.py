from django.shortcuts import render, get_object_or_404
from .models import Category, Post
import datetime


# Create your views here.
def index(request):
    template = 'blog/index.html'
    current_date = datetime.datetime.now()
    r_posts = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=current_date).order_by('-pub_date')[:5]

    context = {
        'post_list': r_posts
    }

    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    current_date = datetime.datetime.now()
    post = get_object_or_404(
        Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=current_date
        ),
        pk=id
    )
    context = {
        'post': post
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    current_date = datetime.datetime.now()
    posts = Post.objects.filter(
        is_published=True,
        category__slug=category_slug,
        category__is_published=True,
        pub_date__lte=current_date).order_by('-pub_date')

    context = {
        'category': category,
        'post_list': posts
    }

    return render(request, template, context)
