from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        'profile/<str:username>/',
        views.Profile.as_view(),
        name='profile'
    ),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path('', views.BlogListView.as_view(), name='index'),
    path('posts/create/', views.PostCreate.as_view(), name='create_post')
]
