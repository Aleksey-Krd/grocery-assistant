from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetriveViewSet
from .paginations import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AddFavoritesSerializer, CreateRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          SubscribeSerializer, TagsSerializer)


class CustomUserViewSet(UserViewSet):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination


    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(follow__user=request.user)
        if queryset:
            pages = self.paginate_queryset(queryset)
            serializer = SubscribeSerializer(pages, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(
            {'Внимание!': 'У вас нет подписок!'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if Follow.objects.filter(user=user.id, author=author.id).exists():
                return Response(
                    {'Ошибка!': f'Вы уже подписаны на пользователя: {author}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {'Ошибка!': 'Нельзя подписаться на себя!'},
                    status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author).save()
            serializer = SubscribeSerializer(author, many=False, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if (unfollow:=Follow.objects.filter(user=user.id, author=author.id)).exists():
                unfollow.delete()
                return Response(
                    {'Успешно!': f'Вы отписались от пользователя: {author}'},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {'Ошибка!': f'Вы не подписаны на пользователя: {author}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )   


class TagViewSet(ListRetriveViewSet):
    """Вьюсет Тегов"""
    
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    http_method_names=('get',)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    http_method_names = ('get',)


class RecipeViewSet(ModelViewSet):
    """Управление рецептами"""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        """Управление подписками"""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'Ошибка!': f'Рецепт: {recipe.name} уже есть в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe).save()
            serializer = AddFavoritesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if (favorite:= Favorite.objects.filter(user=user, recipe=recipe)).exists():
            favorite.delete()
            return Response(
                {'Упешно!': f'Рецепт: {recipe.name} удалён из избранного'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'Ошибка!': f'Рецепта: {recipe.name} нет в избранном'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        """Управление списком покупок"""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'Ошибка!': f'Рецепт: {recipe.name} уже есть в списке покупок!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = AddFavoritesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if (shopcart:= ShoppingCart.objects.filter(user=user, recipe__id=pk)).exists():
            shopcart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'Ошибка!': f'Нельзя удалить рецепт: {recipe.name} - его нет в списке покупок!'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def ingredients_to_txt(ingredients):
        """Вывод рецептов списком в списке покупок"""

        shopping_list = ''
        for ingredient in ingredients:
            shopping_list += (
                f"{ingredient['ingredient__name']}  - "
                f"{ingredient['sum']}"
                f"({ingredient['ingredient__measurement_unit']})\n"
            )
        return shopping_list

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Передача файла покупок"""
        
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_recipe__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(sum=Sum('amount'))
        shopping_list = self.ingredients_to_txt(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')
