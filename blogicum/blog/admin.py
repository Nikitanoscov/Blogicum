from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Comment, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    def image_tag(self):
        if self.image:
            return mark_safe(
                f'<url src={self.image.url} width="80" height="60">'
            )
        else:
            return None

    list_display = (
        'title',
        'text',
        'image',
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
