from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Post, Category, Comment
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import PostForm, CommentForm, ProfileEditForm


def index(request):
    template = 'blog/index.html'
    now = timezone.now()

    posts = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        pub_date__lte=now,
        category__is_published=True
    ).order_by('-pub_date')

    for post in posts:
        post.comment_count = post.comments.count()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    now = timezone.now()

    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        id=id
    )

    if (not post.is_published or post.pub_date > now
            or not post.category.is_published):
        if request.user != post.author:
            return redirect('blog:index')

    comments = post.comments.all()
    comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': comment_form,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    now = timezone.now()

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    posts = category.posts.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        pub_date__lte=now,
        category__is_published=True
    ).order_by('-pub_date')

    for post in posts:
        post.comment_count = post.comments.count()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'blog/profile.html'
    now = timezone.now()

    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        posts = Post.objects.select_related(
            'category', 'location', 'author'
        ).filter(
            author=profile_user
        ).order_by('-pub_date')
    else:
        posts = Post.objects.select_related(
            'category', 'location', 'author'
        ).filter(
            author=profile_user,
            is_published=True,
            pub_date__lte=now,
            category__is_published=True
        ).order_by('-pub_date')

    for post in posts:
        post.comment_count = post.comments.count()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
    }
    return render(request, template, context)

@login_required
def profile_edit(request, username):
    if request.user.username != username:
        messages.error(request, 'Вы можете редактировать только свой профиль!')
        return redirect('blog:profile', username=request.user.username)

    # Выбираем форму
    if request.user.is_staff:
        from .forms import AdminProfileEditForm
        form = AdminProfileEditForm(instance=request.user)
        if request.method == 'POST':
            form = AdminProfileEditForm(request.POST, instance=request.user)
    else:
        form = ProfileEditForm(instance=request.user)
        if request.method == 'POST':
            form = ProfileEditForm(request.POST, instance=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль успешно обновлён!')
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/user.html', {'form': form, 'user': request.user})
'''
@login_required
def profile_edit(request, username):
    if request.user.username != username:
        messages.error(request, 'Вы можете редактировать только свой профиль!')
        return redirect('blog:profile', username=request.user.username)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'blog/user.html', {'form': form})
'''
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Публикация успешно создана!')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})
'''
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Публикация успешно создана!')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()

    return render(request, 'blog/create.html', {'form': form})
'''

@login_required
def post_edit(request, id):
    post = get_object_or_404(Post, id=id)

    if post.author != request.user:
        messages.error(
            request,
            'Вы можете редактировать только свои публикации!'
        )
        return redirect('blog:post_detail', id=id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Публикация успешно обновлена!')
            return redirect('blog:post_detail', id=id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_delete(request, id):
    post = get_object_or_404(Post, id=id)

    if post.author != request.user:
        messages.error(request, 'Вы можете удалять только свои публикации!')
        return redirect('blog:post_detail', id=id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Публикация успешно удалена!')
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html', {'form': PostForm(instance=post)})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен')
        else:
            messages.error(request, 'Ошибка формы')
    return redirect('blog:post_detail', id=post_id)
'''
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий успешно добавлен!')
        else:
            messages.error(request, 'Ошибка при добавлении комментария.')
    
    return redirect('blog:post_detail', id=post_id)
'''

@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        messages.error(
            request,
            'Вы можете редактировать только свои комментарии!'
        )
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий успешно отредактирован!')
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)

    post = comment.post
    comments = post.comments.all()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/detail.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        messages.error(
            request,
            'Вы можете удалять только свои комментарии!'
        )
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий успешно удалён!')
        return redirect('blog:post_detail', id=post_id)

    post = comment.post
    comments = post.comments.all()
    comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': comment_form,
        'deleting_comment': comment,
    }
    return render(request, 'blog/detail.html', context)