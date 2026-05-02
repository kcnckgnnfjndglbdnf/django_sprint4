from django.urls import path
from django.views.generic import TemplateView, RedirectView

app_name = 'pages'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='blog:index', permanent=False), name='home'),
    path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('rules/', TemplateView.as_view(template_name='pages/rules.html'), name='rules'),
]
