from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('authors/', views.authors_stats, name='authors_stats'),
    path('search/', views.search, name='search'),
    path('tag/<slug:tag_slug>/', views.tag_articles, name='tag_articles'),
]