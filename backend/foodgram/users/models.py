from typing import Tuple

from django.contrib.auth.models import AbstractUser
from django.db import models

from core.validators import FGUsernameValidator


class FGUser(AbstractUser):
    """Модель кастомного пользователя для проекта FoodGram."""
    class Role(models.TextChoices):
        ADMIN: Tuple[str, str] = ('admin', 'Администратор',)
        MODERATOR: Tuple[str, str] = ('moderator', 'Модератор',)
        USER: Tuple[str, str] = ('user', 'Пользователь',)
        RO: Tuple[str, str] = ('readonly', 'Читатель',)

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
        help_text=('E-mail адрес пользователя. Обязательное поле. '
                   'Должно быть уникальным. 254 символа или меньше.'),
        error_messages={
            'unique': 'Пользователь с таким адресом уже зарегистрирован.',
        },
    )

    role = models.CharField(
        verbose_name='Роль',
        max_length=30,
        blank=True,
        default=Role.USER,
        choices=Role.choices,
        help_text='Роль пользователя',
    )

    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
        default='',
        help_text='Информация о пользователе (необязательно)',
    )

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    def save(self, *args, **kwargs):
        self.is_staff = True if self.is_admin else False
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
