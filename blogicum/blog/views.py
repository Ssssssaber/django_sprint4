from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Post, Comment
import datetime
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import ProfileEditForm, CommentForm, PostForm

POSTS_PER_PAGE = 10


def _get_time():
    return datetime.datetime.now(datetime.timezone.utc)


def profile_view(request, username):
    template_name = 'blog/profile.html'

    profile = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        'location', 'author', 'category'
    ).filter(
        author=profile.pk
    ).annotate(
        comment_count=Count('comments')
    ).order_by(
        '-pub_date'
    )

    page_obj = Paginator(posts, POSTS_PER_PAGE)
    page_obj = page_obj.get_page(request.GET.get('page'))

    context = {
        'profile': profile,
        'page_obj': page_obj
    }
    return render(request, template_name, context)


@login_required
def edit_profile_view(request):

    form = ProfileEditForm(instance=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST)

        if form.is_valid():
            user = User.objects.get(pk=request.user.pk)

            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']

            user.save()

    context = {
        'form': form
    }

    return render(request, 'blog/user.html', context)


@login_required
def post_create_view(request):
    template_name = 'blog/create.html'
    form = PostForm()

    if (request.method == 'POST'):
        postForm = PostForm(request.POST, request.FILES)

        if postForm.is_valid():
            post = postForm.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user)
    context = {
        'form': form
    }
    return render(request, template_name, context)


@login_required
def post_edit_view(request, post_id):
    template_name = 'blog/create.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if request.user.pk != post.author.pk or not post_form.is_valid():
            return redirect('blog:post_detail', post_id=post_id)
        post.text = post_form.cleaned_data['text']
        post.title = post_form.cleaned_data['title']
        post.pub_date = post_form.cleaned_data['pub_date']
        post.category = post_form.cleaned_data['category']
        post.location = post_form.cleaned_data['location']
        post.image = post_form.cleaned_data['image']
        post.save()
        return redirect('blog:post_detail', post_id=post_id)
    else:
        post_form = PostForm(instance=post)

    context = {
        'form': post_form
    }

    return render(request, template_name, context)

@login_required
def post_delete_view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user.pk != post.author.pk:
        return redirect("blog:post_detail", post_id=post_id)

    post.delete()
    return redirect("blog:profile", username=request.user)


@login_required
def comment_add_view(request, post_id):
    if request.method != 'POST':
        return redirect('blog:post_detail', post_id=post_id)

    post = get_object_or_404(
        Post,
        pk=post_id
    )

    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.author = request.user
        comment.post = post

        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def comment_edit_view(request, post_id, comment_id):
    template_name = 'blog/comment.html'

    comment = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(instance=comment)

    if request.method == 'POST' and request.user.pk == comment.author.pk:
        comment_form = CommentForm(request.POST)
        if not comment_form.is_valid():
            return redirect('blog:edit_comment', post_id=comment_id)
        comment.text = comment_form.cleaned_data['text']
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)

    context = {
        'form': form,
        'comment': comment
    }
    return render(request, template_name, context)


@login_required
def comment_delete_view(request, post_id, comment_id):
    template_name = 'blog/comment.html'

    comment = get_object_or_404(Comment, pk=comment_id)

    if request.method == 'POST' and request.user.pk == comment.author.pk:
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    context = {
        'comment': comment
    }

    return render(request, template_name, context)


# Create your views here.
def index(request):
    template_name = 'blog/index.html'
    current_date = _get_time()
    posts = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=current_date).order_by('-pub_date').annotate(
        comment_count=Count('comments'))

    page_obj = Paginator(posts, POSTS_PER_PAGE)
    page_obj = page_obj.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj
    }

    return render(request, template_name, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    current_date = _get_time()
    post = get_object_or_404(
        Post,
        Q(pk=post_id, pub_date__lte=current_date,
          category__is_published=True, is_published=True) |
        Q(pk=post_id, author=request.user)
    )

    comments = Comment.objects.filter(post=post)

    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm()
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    current_date = _get_time()

    posts = Post.objects.filter(
        is_published=True,
        category__slug=category_slug,
        category__is_published=True,
        pub_date__lte=current_date).order_by('-pub_date')

    page_obj = Paginator(posts, POSTS_PER_PAGE)
    page_obj = page_obj.get_page(request.GET.get('page'))

    context = {
        'category': category,
        'page_obj': page_obj
    }

    return render(request, template, context)
