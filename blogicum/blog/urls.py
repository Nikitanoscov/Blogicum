from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path(
        '',
        views.BlogListView.as_view(),
        name='index'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetail.as_view(),
        name='post_detail'
    ),
    path(
        'posts/create/',
        views.PostCreate.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDelete.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdate.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreate.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdate.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDelete.as_view(),
        name='delete_comment'
    ),
    path(
        'profile/edit/',
        views.profile_update,
        name='edit_profile'
    ),
    path(
        'profile/<str:username>/',
        views.Profile.as_view(),
        name='profile'
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryList.as_view(),
        name='category_posts'
    ),
]
