from core.validators import FGUsernameValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class FGUser(AbstractUser):
    """Custom user model for FoodGram project."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        verbose_name='Никнейм',
        max_length=150,
        unique=True,
        db_index=True,
        help_text=('Никнейм пользователя. Обязательное поле. '
                   'Должно быть уникальным. 150 символов или меньше. '
                   'Допустимы только буквы, цифры и символы @/./+/-/_ .'),
        validators=(FGUsernameValidator(),),
        error_messages={
            'unique': 'Пользователь с таким никнеймом уже зарегистрирован.',
        },
    )

    email = models.EmailField(
        verbose_name='E-mail адрес',
        unique=True,
        db_index=True,
        help_text='E-mail адрес пользователя. Обязательное поле. '
                  'Должно быть уникальным. 254 символа или меньше.',
        error_messages={
            'unique': 'Пользователь с таким адресом уже существует.',
        },
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )

    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )

    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации',
        help_text='Дата регистрации пользователя',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
        help_text='Дата последнего обновления профиля пользователя',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __repr__(self):
        return (f'ID: {self.pk}, '
                f'E-mail: {self.email}, '
                f'Username: {self.username}')

    def __str__(self):
        return self.username


User = get_user_model()


class Follow(models.Model):
    """Model for subscriptions to recipe authors."""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Подписчик',
        help_text='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор',
        help_text='Автор',
    )

    create_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки',
        help_text='Дата подписки',
    )

    class Meta:
        db_table = 'follows'
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('follower', 'author'),
                name='unique_follow'
            )
        ]

    # def clean(self):
    #     if self.follower == self.author:
    #         raise ValidationError('Нельзя подписаться на самого себя')
    #     super().clean()

    def __repr__(self):
        return f'ID: {self.pk}, ' \
               f'{self.follower.username} >>> {self.author.username}'

    def __str__(self):
        return f'{self.follower.username} подписан на {self.author.username}'
