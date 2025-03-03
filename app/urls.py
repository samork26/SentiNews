from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('refresh', views.refresh_articles, name='refresh_articles'),
    path('fetch_local_news', views.fetch_local_news_view, name='fetch_local_news'),  # New local news route
    path('about', views.about, name='about'),
]
