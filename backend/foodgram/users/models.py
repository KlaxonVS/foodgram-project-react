from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя с добавлением поля роль"""

    username = models.CharField(
        'Имя пользователя',
        max_length=settings.USERNAME_LENGTH,
        unique=True,
        validators=[validate_username],
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=settings.EMAIL_LENGTH,
        unique=True,
    )

    first_name = models.CharField(
        'Имя',
        max_length=settings.F_NAME_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.L_NAME_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ('email',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Follow(models.Model):
    """Модель подписки на пользователя."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='Подписаться на автора можно только один раз'
            ),
            models.CheckConstraint(
                name='Нельзя подписаться на себя',
                check=(~models.Q(user=models.F('author'))),
            ))

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
