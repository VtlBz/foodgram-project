from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count, OuterRef, Prefetch, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.serializers import (
    FollowSerializer, IngredientSerializer, RecipeReadSerializer,
    RecipeShortSerializer, RecipeWriteSerializer, TagSerializer,
)
from core.filters import IngredientSearchFilter, RecipeFilter
from core.pagination import FoodGramPagination
from core.permissions import IsOwnerOrRO
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow

User = get_user_model()


class FoodGramUserViewSet(UserViewSet):
    pagination_class = FoodGramPagination

    def get_queryset(self):
        return User.objects.all()

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        user = get_object_or_404(User, username=request.user)
        author = get_object_or_404(User, id=self.kwargs.get('id'))

        if request.method == 'POST':
            if user == author:
                return Response(
                    data={'errors': 'Нарцисcизм это болезнь!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FollowSerializer(
                author, context={'request': request}
            )

            _, is_created = Follow.objects.get_or_create(
                follower=user, author=author
            )
            if not is_created:
                return Response(
                    data={'errors': 'Подписка уже оформлена.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )

        follow = get_object_or_404(
            Follow, follower=user, author=author
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        recipes_limit = int(
            self.request.GET.get('recipes_limit', default=3)
        )
        users_recipes = Recipe.objects.filter(
            author_id=OuterRef('author_id')
        )[:recipes_limit]
        prefetch_query = Prefetch(
            'recipes', queryset=Recipe.objects.filter(id__in=users_recipes)
        )
        queryset = User.objects.filter(
            followers__follower=request.user
        ).prefetch_related(prefetch_query).annotate(
            recipes_count=Count('recipes')
        )
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = FoodGramPagination
    permission_classes = (IsOwnerOrRO,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def _mark_or_unmark(self, request, model, msg_txt):
        user = get_object_or_404(User, username=request.user)
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        if request.method == 'POST':
            serializer = RecipeShortSerializer(
                recipe, context={'request': request})
            _, is_create = (
                model.objects.get_or_create(
                    foodgramuser=user, recipe=recipe
                )
            )
            if not is_create:
                return Response(data={'errors': f'Рецепт уже {msg_txt}.'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        target_recipe = model.objects.filter(
            foodgramuser=user, recipe=recipe
        )
        if not target_recipe:
            return Response(data={'errors': f'Рецепт не был в {msg_txt}!'},
                            status=status.HTTP_400_BAD_REQUEST)
        target_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        favorite_recipe = Recipe.favorited.through
        msg_place = 'в избранном'
        return self._mark_or_unmark(
            request, favorite_recipe, msg_place
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        shopping_cart_recipe = Recipe.in_shopping_cart.through
        msg_place = 'в корзине'
        return self._mark_or_unmark(
            request, shopping_cart_recipe, msg_place
        )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_cart=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = [f'Список покупок для {user.username} на '
                         f'{datetime.today().strftime("%d/%m/%y")}\n']

        filename = f'{user.username}_shopping_cart.txt'
        for ingredient in ingredients:
            shopping_list.append(
                f'{ingredient["ingredient__name"]}: '
                f'{ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
            )
        shopping_cart = '\n'.join(shopping_list)
        response = HttpResponse(
            shopping_cart, content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
