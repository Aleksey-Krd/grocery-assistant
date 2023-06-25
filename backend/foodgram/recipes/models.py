from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель тега"""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название тега')
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True,
        default='#000000',
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            )
        ],
        help_text='Введите цвет тега. Например, #006400',
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Уникальный слаг')

    class Meta:

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='Уникальный тег',
            ),
        )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название ингредиента')

    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения')

    class Meta:

        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):

        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта"""

    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        blank=False
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        blank=False,
        unique=True,
        error_messages={
            'unique': "Такое название рецепта уже есть!"
        }
    )
    image = models.ImageField(
        verbose_name='Фотография рецепта',
        upload_to='recipes/',
        blank=False
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1, message='Минимальное значение 1!'),
        ],
        blank=False
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации рецепта'
    )

    class Meta:

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)

    def __str__(self):

        return self.name


class IngredientInRecipe(models.Model):
    """Модель ингредиентов в отдельных рецептах"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='in_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1, message='Минимальное количество 1!'),
        ]
    )

    class Meta:

        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='Уникальные ингредиенты'
            )
        ]

    def __str__(self):

        return f'{self.ingredient} {self.recipe}'


class TagInRecipe(models.Model):
    """Модель тегов рецепта"""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги',
        help_text='Выберите теги рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт')

    class Meta:

        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(fields=['tag', 'recipe'],
                                    name='Уникальные теги')
        ]

    def __str__(self):

        return f'{self.tag} {self.recipe}'


class ShoppingCart(models.Model):
    """Модель корзины покупок """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт'
    )

    class Meta:

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='Уникальный список покупок'
            )
        ]

    def __str__(self):

        return f'{self.user} {self.recipe}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='Уникальное избранное'
            )
        ]

    def __str__(self):

        return f'{self.user} {self.recipe}'