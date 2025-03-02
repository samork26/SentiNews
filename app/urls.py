from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Default view
    path('refresh', views.refresh_articles, name='refresh_articles'),  # Refresh articles
    path('about', views.about, name='about'),
]
