from django_filters.rest_framework import (
    FilterSet, ModelChoiceFilter, ModelMultipleChoiceFilter, NumberFilter,
)
from rest_framework import filters

from recipes.models import Recipe, Tag, User


class RecipeFilter(FilterSet):
    author = ModelChoiceFilter(queryset=User.objects.all())
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = NumberFilter(method='_filter_by_field')
    is_in_shopping_cart = NumberFilter(method='_filter_by_field')

    filter_field = {
        'is_favorited': 'favorited',
        'is_in_shopping_cart': 'in_shopping_cart',
    }

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)

    def _filter_by_field(self, qs, filter_name, value):
        user = self.request.user
        if bool(value) and user.is_authenticated:
            return qs.filter(**{self.filter_field[filter_name]: user})
        return qs


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'
