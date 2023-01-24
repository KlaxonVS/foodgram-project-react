from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя с добавлением поля роль"""
    ADMIN = 'admin'
    USER = 'user'

    ROLE_CHOICES = (
        (ADMIN, 'Администратор'),
        (USER, 'Пользователь'),
    )
    
    role = models.CharField(
        'Роль',
        max_length=max(len(role_en) for role_en, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER
    )
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

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        """Проверяет что пользователь администратор"""
        return self.role == self.ADMIN or self.is_staff

    def __str__(self):
        return self.username


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
