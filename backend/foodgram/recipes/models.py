from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator, MinValueValidator, RegexValidator,
)
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тэгов для рецептов"""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тэга',
        help_text='Введите название тэга'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет тэга',
        help_text='Введите цветовой HEX-код тэга',
        validators=[
            RegexValidator(regex=settings.TAG_COLOR_MASK)
        ]
    )
    slug = models.SlugField(
        unique=True,
        max_length=100,
        verbose_name='Slug тэга',
        help_text='Укажите слаг для тэга. Используйте только '
                  'латиницу, цифры, дефисы и знаки подчёркивания'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиентов.
    Содержит единицу измерения для ингридиента."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингридиента',
        help_text='Введите название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения ингридиента'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Автор рецепта'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение',
        upload_to='recipes/images/',
        null=True,
        blank=True,
    )
    text = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Укажите время, '
                  'требуемое для приготовления этого рецепта (в минутах)',
        validators=[
            MinValueValidator(
                1, 'Время приготовления не может быть меньше 1 минуты!'
            ),
            MaxValueValidator(
                6000, 'Время приготовления не может быть более 100 часов!'
            ),
        ],
        default=1,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэг',
        help_text='Тэг для рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='ingredients_recipe',
        verbose_name='Ингридиенты рецепта',
        help_text='Ингридиенты в рецепте'
    )
    favorited = models.ManyToManyField(
        User,
        related_name='favorited_recipes',
        verbose_name='Избранное',
        help_text='Избранное',
        blank=True
    )
    in_shopping_cart = models.ManyToManyField(
        User,
        related_name='in_cart_recipes',
        verbose_name='Корзина',
        help_text='Корзина',
        blank=True
    )

    class Meta:
        db_table = 'recipes'
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель количества ингридиентов в рецепте.
    Добавляет количество конкретного ингридиента в конкретном рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепты',
        help_text='Рецепты'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Ингридиенты',
        help_text='Ингридиенты'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Количество продукта',
        validators=[
            MinValueValidator(
                1, 'Количество ингредиента не может быть меньше 1!'
            ),
        ],
        default=1,
    )

    class Meta:
        db_table = 'recipes_ingredients'
        verbose_name = 'Количество'
        verbose_name_plural = 'Количество'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_amount'
            )
        ]

    def __str__(self):
        return f'{self.recipe} >>> {self.ingredient} : {self.amount}'
