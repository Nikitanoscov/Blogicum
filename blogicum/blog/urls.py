from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('posts/<int:post_id>/', views.PostDetail.as_view(), name='post_detail'),
    path(
        'posts/<int:post_id/comment/',
        views.CommentCreate.as_view(),
        name='add_comment'
    ),
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
    path('posts/create/', views.PostCreate.as_view(), name='create_post'),
    path(
        'profile/edit',
        views.ProfileUpdate.as_view(),
        name='edit_profile'
    )
]
