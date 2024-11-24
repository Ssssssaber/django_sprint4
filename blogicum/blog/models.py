from django.db import models
from core.models import PublishedModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(PublishedModel):
    title = models.CharField(("Заголовок"), max_length=256)
    description = models.TextField(("Описание"))
    slug = models.SlugField(("Идентификатор"), unique=True,
                            help_text="Идентификатор страницы для URL; \
разрешены символы латиницы, цифры, дефис и подчёркивание.")

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(("Название места"), max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField(("Заголовок"), max_length=256)
    text = models.TextField(("Текст"))
    pub_date = models.DateTimeField(("Дата и время публикации"),
                                    auto_now=False, auto_now_add=False,
                                    help_text="Если установить дату и \
время в будущем — можно делать отложенные публикации.")
    author = models.ForeignKey(User, verbose_name=("Автор публикации"),
                               on_delete=models.CASCADE, null=False)
    location = models.ForeignKey(Location, verbose_name=("Местоположение"),
                                 on_delete=models.SET_NULL, blank=True,
                                 null=True)
    category = models.ForeignKey(Category, verbose_name=("Категория"),
                                 on_delete=models.SET_NULL, null=True)

    image = models.ImageField(verbose_name='Изображение',
                              null=True, blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(PublishedModel):
    text = models.TextField(verbose_name='текст')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='комментируемая публикация',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор комментария',
        related_name='comments'
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
