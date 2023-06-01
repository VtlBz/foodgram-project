from colorfield.widgets import ColorWidget
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

from core.forms import RecipeIngridientFormSet
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    min_num = 1
    extra = 0


class RecipeIngredientInline(admin.TabularInline):
    formset = RecipeIngridientFormSet
    model = RecipeIngredient
    min_num = 1
    extra = 0


class FavoritedInline(admin.TabularInline):
    model = User.favorited_recipes.through
    extra = 1


class InCartInline(admin.TabularInline):
    model = User.in_cart_recipes.through
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    list_editable = ('name', 'color', 'slug',)
    search_fields = ('name', 'color', 'slug',)
    list_filter = ('color',)
    empty_value_display = settings.DEFAULT_FOR_EMPTY

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'color':
            formfield.widget = ColorWidget(attrs={'style': 'height:30px'})
        return formfield


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
    exclude = ('tags', 'favorited', 'in_shopping_cart')
    list_editable = ('name',)
    search_fields = ('name', 'author',)
    list_filter = ('author', 'pub_date', 'cooking_time',)
    empty_value_display = settings.DEFAULT_FOR_EMPTY
    inlines = (
        TagInline, RecipeIngredientInline, FavoritedInline, InCartInline
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'recipe', 'ingredient', 'amount',
    )
    list_editable = ('amount',)
    search_fields = ('recipe__name', 'ingredient__name',)
    list_filter = ('recipe', 'ingredient',)
    empty_value_display = settings.DEFAULT_FOR_EMPTY
