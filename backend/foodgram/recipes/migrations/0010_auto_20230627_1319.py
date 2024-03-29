# Generated by Django 3.2.16 on 2023-06-27 13:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20230626_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество 1!'), django.core.validators.MaxValueValidator(3000, message='Максимальное занчени 3000!')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное значение 1!'), django.core.validators.MaxValueValidator(480, message='Максимальное значение 480!')], verbose_name='Время приготовления'),
        ),
    ]
