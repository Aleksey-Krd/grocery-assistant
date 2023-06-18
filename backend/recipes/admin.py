from django.contrib import admin

from .models import Follow, IngredientInRecipe, Recipe, Tag, TagInRecipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки администратора модели Tag"""
    list_display = ('name', 'color', 'slug',)
    search_fields = ('slug',)


class TaginRecipeInline(admin.TabularInline):
    model = TagInRecipe


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки администратора модели Recipe"""
    list_display = ('author', 'name', 'text', 'image', )
    search_fields = ('author', 'name',)
    list_filter = ('name', )
    inlines = (IngredientInRecipeInline, TaginRecipeInline, )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Настройки администратора модели Follow"""
    list_display = ('author', 'user', )
    search_fields = ('author', 'user', )

