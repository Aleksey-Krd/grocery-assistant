from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from recipes.models import IngredientInRecipe
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class SendTxtFileViewset(ViewSet):
    """Формирование и передача файла покупок"""
    def list(self, request):
        user = request.user
        if not user.shopping_user.exists():
            return Response(
                'Карзина пустая!',
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_recipe__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(sum=Sum('amount'))
        shopping_list = ''
        today = datetime.today()
        shopping_list = (
            f'Список покупок для : {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        for ingredient in ingredients:
            shopping_list += (
                f"{ingredient['ingredient__name']}  - "
                f"{ingredient['sum']}"
                f"({ingredient['ingredient__measurement_unit']})\n")
        shopping_list += f'\n Foodgram ({today:%Y})'
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
