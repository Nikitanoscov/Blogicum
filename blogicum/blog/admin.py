from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Comment, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'text',
        'image_tag',
        'pub_date',
        'author',
        'location',
        'category',
    )
    list_editable = (
        'category',
    )
    search_fields = (
        'title',
    )
    list_filter = (
        'category',
        'pub_date',
    )

    @admin.display(description='Изображение')
    def image_tag(self, post: Post):
        if post.image:
            return mark_safe(
                f'<img src={post.image.url} width="80" height="60">'
            )
        return 'Без фото'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
    )
    search_fields = (
        'title',
    )
    list_filter = (
        'title',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post'
    )
    list_filter = (
        'post',
    )
