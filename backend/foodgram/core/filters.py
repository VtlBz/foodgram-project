from django_filters.rest_framework import (FilterSet, ModelChoiceFilter,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)
from recipes.models import Recipe, Tag, User
from rest_framework import filters


class RecipeFilter(FilterSet):
    author = ModelChoiceFilter(queryset=User.objects.all())
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = NumberFilter(method='favorited')
    is_in_shopping_cart = NumberFilter(method='in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)

    def favorited(self, qs, filter_name, value):
        user = self.request.user
        if bool(value) and user.is_authenticated:
            return qs.filter(favorited=user)
        return qs

    def in_shopping_cart(self, qs, filter_name, value):
        user = self.request.user
        if bool(value) and user.is_authenticated:
            return qs.filter(in_shopping_cart=user)
        return qs


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'
