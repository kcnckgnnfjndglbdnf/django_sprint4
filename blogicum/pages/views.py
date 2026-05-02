from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm


def home(request):
    return redirect('blog:index')


def about(request):
    return render(request, 'pages/about.html')


def rules(request):
    return render(request, 'pages/rules.html')


def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('blog:index')
    else:
        form = UserCreationForm()

    return render(
        request,
        'registration/registration_form.html',
        {'form': form}
    )


def custom_404(request, exception):
    return render(request, 'pages/404.html', status=404)


def custom_500(request):
    return render(request, 'pages/500.html', status=500)


def custom_403(request, exception):
    return render(request, 'pages/403csrf.html', status=403)
