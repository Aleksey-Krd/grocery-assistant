from django.urls import include, path
from rest_framework import routers

from .services import SendTxtFileViewset
from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register(
    'recipes/download_shopping_cart',
    SendTxtFileViewset,
    basename='download_shopping_cart'
)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')
app_name = 'api'


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
