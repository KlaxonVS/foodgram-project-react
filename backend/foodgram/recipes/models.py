from django.conf import settings
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User
from .validators import validate_hex


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        'Название',
        max_length=settings.NAME_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.M_UNIT_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name=('Сочетания названия и единицы'
                      'измерения должно быть уникально')
            ),
        )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        'Название',
        unique=True,
        max_length=settings.TAG_LENGTH
    )
    color = models.CharField(
        'Цвет',
        unique=True,
        max_length=settings.HEX_LENGTH,
        validators=[validate_hex]

    )
    slug = models.SlugField(
        'Метка',
        unique=True,
        max_length=settings.SLUG_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(
        'Название',
        max_length=settings.NAME_LENGTH
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=True,
        help_text='Загрузите изображение',
    )
    text = models.TextField(
        'Описание',
        help_text='Описание приготовления',
        validators=[MaxLengthValidator(
            10000, 'Длинна текста не более 10_000 символов'
        )]
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        help_text='Время приготовления в минутах',
        validators=[MinValueValidator(
            1,
            'Время приготовления не может быть меньше 1'
        )]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель рецепт-ингредиент. Дополнительное поле количество"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    amount = models.FloatField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            0.01,
            'Количество должно быть больше нуля'
        )]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='Ингредиенты в рецепте не повторяются'
            ),
        ]

    def __str__(self):
        return (f'{self.recipe}: {self.ingredient.name} -- {self.amount}'
                f' {self.ingredient.measurement_unit}')


class FavoriteAndCart(models.Model):
    """Общая модель для рецептов в избранном и в корзине."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    
    class Meta:
        abstract = True


class Favorite(FavoriteAndCart):
    """Модель избранных рецептов."""
    class Meta:
        default_related_name = 'favorite'
        ordering = ['user']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='Нельзя дважды добавить в избранное'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил в избранное: {self.recipe}'


class ShoppingCart(FavoriteAndCart):
    """Модель корзины покупок."""
    class Meta:
        default_related_name = 'cart'
        ordering = ['id']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'{self.user.username} добывил в корзину {self.recipe.name}'
