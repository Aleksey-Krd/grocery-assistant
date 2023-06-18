from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель тегов"""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название тега'
    )

    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Неверный формат HEX!'
            )
        ],
        default='#0000ff',
        help_text='Введите цвет тега в формате: #000023',
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Уникальный слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color','slug'),
                name='uniq_tag',
            ),
        )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов"""

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название ингредиента'
    )

    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов"""


    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )

    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название рецепта'
    )

    image = models.ImageField(
        verbose_name='Фотография рецепта',
        upload_to='recipes/',
        blank=True
    )

    text = models.CharField(
        max_length=1000,
        verbose_name='Описание рецепта'
    )

    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )

    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        verbose_name='Теги'
    )

    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1, message='Минимальное заничение 1 минута!'),
        ]
    )

    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:


        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)
    
    def __str__(self):
        return self.name
    

class IngredientInRecipe(models.Model):
    """Модель количества ингредиентов в отдельных рецептах"""

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

        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='uniq_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagInRecipe(models.Model):
    """Модель тегов"""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        help_text='Выберите тег рецепта'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='uniq_tag_in_recipe'
            )
        ]

    def __str__(self):
        return f'{self.tag} {self.recipe}'
    

class ShopingCard(models.Model):
    """Модель списка покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='card_user',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='card_recipe',
        verbose_name='Рецепт'
    )

    class Meta:

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='uniq_shopingcard_user'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
    

class Follow(models.Model):
    """Модель подписок"""

    author = models.ForeignKey(
        User,
        verbose_name= 'Автор подписки',
        related_name='following',
        on_delete=models.CASCADE

    )

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE
    )

    create_date = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
    

class Favourites(models.Model):
    """Модель избранного"""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favuser',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favrecipe',
        verbose_name='Репепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='uniq_favourites'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'