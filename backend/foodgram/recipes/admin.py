from django.contrib import admin

from .models import Ingredient, Recipe


class IngredientsInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'count_favorites',)
    inlines = (IngredientsInline, )
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('name',)
    def count_favorites(self, obj):
        return obj.favorites.count()
    count_favorites.short_description = 'Добавлений в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)

