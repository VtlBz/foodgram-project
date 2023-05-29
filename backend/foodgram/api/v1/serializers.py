from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from core.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()

user_conf = settings.USER_CREDENTIAL_SETTINGS


class UserAddSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя.
    Преобразовывает данные пользователя при создании."""

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'password'
        )


class UserProfileSerializer(UserSerializer):
    """Сериализатор профиля пользователя.
    Преобразовывает данные пользователя при просмотре профиля."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        """Определяет наличие подписки.
        Показывает, подписан ли текущий пользователь
        на пользователя, чей профиль просматривается"""

        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.followings.filter(author=obj).exists()

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'is_subscribed')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор получения сокращенного представления рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserProfileSerializer):
    """Сериализатор подписок пользователей."""
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        qs = obj.recipes.all()[:int(limit)]
        serializer = RecipeShortSerializer(qs, context=self.context, many=True)
        return serializer.data

    class Meta(UserProfileSerializer.Meta):
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = ('id', 'username', 'email',
                            'first_name', 'last_name', 'is_subscribed',
                            'recipes', 'recipes_count')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингридиентов"""

    id = serializers.IntegerField(source="ingredient.id")
    amount = serializers.IntegerField()
    name = serializers.CharField(source="ingredient.name")

    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецептов."""

    author = UserProfileSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients', many=True
    )

    class Meta:
        model = Recipe
        exclude = ('pub_date', 'favorited', 'in_shopping_cart')

    def _check_exist(self, obj, model):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return model.objects.filter(
            foodgramguser=user, recipe=obj
        ).exists()

    def get_is_favorited(self, obj):
        return self._check_exist(obj, Recipe.favorited.through)

    def get_is_in_shopping_cart(self, obj):
        return self._check_exist(obj, Recipe.in_shopping_cart.through)


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField(allow_null=True)

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError('Укажите хотя бы один тег')
        return value

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'В рецепте должен быть хотя бы один ингридиент'
            )
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=user)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            for ingredient in ingredients:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount']
                )
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    class Meta:
        model = Recipe
        fields = (
            'image', 'name', 'text', 'cooking_time', 'tags', 'ingredients'
        )
