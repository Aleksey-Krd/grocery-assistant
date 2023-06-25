import django_filters
from django_filters import rest_framework
from django_filters.rest_framework import FilterSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class IngredientFilter(FilterSet):

    name = rest_framework.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(django_filters.FilterSet):

    tags = django_filters.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug')
    is_favorited = django_filters.filters.NumberFilter(
        method='favorites_filter')
    is_in_shopping_cart = django_filters.filters.NumberFilter(
        method='shoppingcart_filter')
    author = rest_framework.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )

    def new_queryset(self, queryset, value, field):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()
        obj = field.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in obj]
        new_queryset = queryset.filter(id__in=recipes)
        if not value:
            return queryset.difference(new_queryset)
        return new_queryset

    def favorites_filter(self, queryset, name, value):
        return self.new_queryset(queryset, value, Favorite)

    def shoppingcart_filter(self, queryset, name, value):
        return self.new_queryset(queryset, value, ShoppingCart)

    class Meta:
        model = Recipe
        fields = ('tags', 'author', )
