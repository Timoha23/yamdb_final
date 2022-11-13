from django.db import models


class Category(models.Model):
    name = models.CharField(
        'Категория',
        max_length=150
    )
    slug = models.SlugField(
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.name}'


class Genre(models.Model):
    name = models.CharField(
        'Жанр',
        max_length=150
    )
    slug = models.SlugField(
        unique=True,
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.name}'


class Title(models.Model):
    name = models.CharField(
        'Название',
        max_length=150
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='category_titles',
        verbose_name='Категория',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='genre_titles',
        verbose_name='Жанр'
    )
    year = models.IntegerField(
        blank=True,
        verbose_name='год выхода',
        db_index=True,
    )
    description = models.TextField(
        'Описание',
        max_length=300,
        blank=True
    )
