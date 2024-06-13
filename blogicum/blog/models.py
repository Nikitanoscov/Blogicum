from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from core.models import CreateAtModel, IsPublishedModel
from .const_for_blog import MAX_LENGTH, OUTPUT_LENGTH


User = get_user_model()


class PostQuerySet(QuerySet):

    def published(self):
        return self.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now()
        )

    def count_comment(self):
        return self.select_related(
            'author', 'category', 'location'
        ).order_by(
            '-pub_date'
        ).annotate(
            comment_count=models.Count('comments')
        )


class Category(CreateAtModel, IsPublishedModel):
    title = models.CharField(max_length=MAX_LENGTH, verbose_name='Заголовок')
    description = models.TextField('Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title[:OUTPUT_LENGTH]


class Location(CreateAtModel, IsPublishedModel):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:OUTPUT_LENGTH]


class Post(CreateAtModel, IsPublishedModel):
    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем'
            ' — можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )
    image = models.ImageField('Фото', upload_to='blog_images', blank=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:OUTPUT_LENGTH]


class Comment(CreateAtModel):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )

    class Meta(CreateAtModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:OUTPUT_LENGTH]
