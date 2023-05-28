from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    list_editable = ('name', 'color', 'slug',)
    search_fields = ('name', 'color', 'slug',)
    list_filter = ('color',)
    empty_value_display = settings.DEFAULT_FOR_EMPTY


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    list_editable = ('name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('name', 'measurement_unit',)
    empty_value_display = settings.DEFAULT_FOR_EMPTY


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'author', 'pub_date', 'cooking_time',
    )
    list_editable = ('name',)
    search_fields = ('name', 'author',)
    list_filter = ('author', 'pub_date', 'cooking_time',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass