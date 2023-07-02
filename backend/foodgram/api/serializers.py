import base64
import re

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Follow, User


class UserSerializer(UserSerializer):
    """Сериализатор для модели User проверки подписки"""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    def get_is_subscribed(self, obj):

        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')
        read_only_field = ('is_subscribed', )


class CreateUserSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password')
        extra_kwargs = {'password': {'write_only': True}}


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag"""

    class Meta:
        model = Tag
        fields = ('id',
                  'name',
                  'color',
                  'slug',)


class IngredienInRecipeSerizlizer(serializers.ModelSerializer):
    """Сариализатор ингредиентов в рецепте"""

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента"""

    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit')


class SubscribesRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор репептов подписчика"""

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')


class SubscribeSerializer(UserSerializer):
    """Сериализотор подписки"""

    recipes = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count',)

    def get_recipes(self, obj):

        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return SubscribesRecipeSerializer(recipes, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class AddFavoritesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagsSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredienInRecipeSerizlizer(
        source='ingredient_list', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def get_is_favorited(self, obj):

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецептах"""

    class Meta:
        model = IngredientInRecipe
        fields = ('id',
                  'amount',)
        extra_kwargs = {
            'id': {
                'read_only': False,
                'error_messages': {
                    'does_not_exist': 'Такого ингредиента не существует!', }
            },
            'amount': {
                'error_messages': {
                    'min_value':
                    'Минимальное количество не может быть меньше 1'}}
        }


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""
    author = UserSerializer(read_only=True)
    name = serializers.CharField()
    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all()))
    image = Base64ImageField(use_url=True)
    cooking_time = serializers.IntegerField()

    def validate_ingredients(self, value):
        ingredients = [item['id'] for item in value]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise serializers.ValidationError(
                    'Не может быть одинаковых ингредиентов в рецепте!')
        return value

    def validate_name(self, value):
        if value.isdigit():
            raise ValidationError(
                _("Название рецепта не может состоять только из цифр"),
            )
        pattern = re.compile(r'^[\wа-яА-Я]{1,200}$')
        if not pattern.match(value):
            raise ValidationError(
                _("Название рецепта не может содержать символы кроме _"),
            )
        return value

    def ingredients_in_recipe(self, recipe, ingredients):
        IngredientInRecipe.objects.bulk_create([IngredientInRecipe(
            ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
            recipe=recipe,
            amount=ingredient['amount'])for ingredient in ingredients]
        )

    def create(self, valid_data):
        author = self.context.get('request').user
        tags = valid_data.pop('tags')
        ingredients = valid_data.pop('ingredients')
        name = valid_data.pop('name')
        if Recipe.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                'Рецепт с таким названием уже есть!')
        recipe = Recipe.objects.create(author=author, name=name, **valid_data)
        recipe.tags.set(tags)
        self.ingredients_in_recipe(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, valid_data):
        tags = valid_data.pop('tags', None)
        ingredients = valid_data.pop('ingredients', None)
        instance = super().update(instance, valid_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.ingredients_in_recipe(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    class Meta:
        model = Recipe
        exclude = ('created',)
