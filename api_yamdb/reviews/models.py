from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User
from title.models import Title


class ReviewAndComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Author')
    pub_date = models.DateTimeField('Дата публикации', db_index=True,
                                    auto_now_add=True)
    text = models.TextField('Текст', blank=False)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Review(ReviewAndComment):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews',
                              blank=True, null=True)
    score = models.IntegerField('Оценка', validators=[MinValueValidator(1),
                                                      MaxValueValidator(10)])

    class Meta(ReviewAndComment.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review')
        ]

    def __str__(self):
        return self.text


class Comment(ReviewAndComment):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments', blank=True,
                               null=True)

    class Meta(ReviewAndComment.Meta):
        verbose_name_plural = 'Коментарии'
        verbose_name = 'Коментарий'

    def __str__(self):
        return self.author
