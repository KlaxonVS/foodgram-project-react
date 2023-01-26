from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow, User
from users.validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    """Общий сериализатор для модели пользователя."""
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )
        read_only_fields = ('__all__',)
    
    def get_is_subscribed(self, user):
        """Поле для обозначения подписки на пользователя."""
        follower = self.context['request'].user
        return (
            not user.is_anonymous
            and follower.follower.filter(author=user).exists()
        )


class UserCreateSerializer(UserSerializer):
    """Сериализатор для создания модели пользователя."""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        max_length=settings.EMAIL_LENGTH,
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all()),
                    validate_username],
        max_length=settings.USERNAME_LENGTH,
    )
    first_name = serializers.CharField(
        required=True,
        max_length=settings.F_NAME_LENGTH,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=settings.L_NAME_LENGTH,
    )
    password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_LENGTH,
        write_only=True
    )
    
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )


class Login(serializers.Serializer):
    """Сериализатор для входа на сайт -- получения токена."""
    email = serializers.EmailField(
        max_length=settings.EMAIL_LENGTH,
    )
    password = serializers.CharField()

class ChangePassword(serializers.Serializer):
    """Сериализатор смены пароля."""
    new_password = serializers.CharField()
    current_password = serializers.CharField()



class TagSerializer(serializers.ModelSerializer):
    """Общий сериализатор для модели тега."""
    
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Общий сериализатор для модели ингредиента."""
    
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class RecipeIngredientViewSerializer(serializers.ModelSerializer):
    """Сериализатор для промежуточной модели рецепта-ингредиента."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name',
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
    )
    
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания промежуточной модели рецепта-ингредиента."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient')
    amount = serializers.FloatField(
        validators=
        [MinValueValidator(0.01, 'Количество должно быть больше нуля')]
    )
    
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeViewSerializer(serializers.ModelSerializer):
    """Общий сериализатор для модели рецепта."""
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientViewSerializer(
        many=True,
        source='recipe_ingredient'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        
    def get_is_favorited(self, recipe):
        """Поле для обозначения нахождения рецепта в избранном."""
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and recipe.favorite.filter(user=user).exists()
        )
    
    def get_is_in_shopping_cart(self, recipe):
        """Поле для обозначения нахождения рецепта в корзине."""
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and recipe.cart.filter(user=user, recipe=recipe.id).exists()
            )


class ShortRecipe(serializers.ModelSerializer):
    """Сокращенный сериализатор для рецепта."""
    
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания модели рецепта."""
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientCreateSerializer(
        many=True, source='recipe_ingredient'
    )
    text = serializers.CharField(
        required=True,
        validators=[MaxLengthValidator(
            10000, 'Длинна текста не более 10_000 символов'
        )]
    )
    cooking_time = serializers.IntegerField(
        required=True,
        validators=[MinValueValidator(
            1,
            'Время приготовления не может быть меньше 1'
        )]
    )
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'ingredients должны быть заданы'
            )
        unknown_ingredients = [
            ingredient.get('ingredient').id
            for ingredient in ingredients
            if not Ingredient.objects.filter(
                id=ingredient.get('ingredient').id).exists()
        ]
        if unknown_ingredients:
            raise serializers.ValidationError(
                f'ingredients с таким id нет: {unknown_ingredients}'
            )
        ingredient_ids = [
            ingredient.get('ingredient').id
            for ingredient in ingredients
        ]
        repeat_ingredients = [
            ingredient.get('ingredient').id
            for ingredient in ingredients
            if ingredient_ids.count(ingredient.get('ingredient').id) > 1
        ]
        if repeat_ingredients :
            raise serializers.ValidationError(
                f'ingredients не должны повторяться: {repeat_ingredients}'
            )
        return ingredients
        
    
    def validate_tags(self, tags):
        if type(tags) is not list:
            raise serializers.ValidationError(
                'Tag(-и) должны быть в формате list: [1, 2, 3]'
            )
        if not tags:
            raise serializers.ValidationError(
                'Tag(-и) должны быть заданы'
            )
        unknown_tags = [
            tag.id for tag in tags
            if not Tag.objects.filter(id=tag.id).exists()
        ]
        if unknown_tags:
            raise serializers.ValidationError(
                f'Tag(-ов) с таким id нет: {unknown_tags}'
            )
        return tags

    @staticmethod
    def create_ingredients(recipe, ingredients):
        def sorter(ingredient):
            return ingredient.get('ingredient').id
        ingredients.sort(key=sorter)
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('ingredient').id,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe
    
    def update(self, instance, validated_data):
        if validated_data.get('tags'):
            instance.tags.clear()
            instance.tags.set(validated_data.pop('tags'))
        if validated_data.get('recipe_ingredient'):
            RecipeIngredient.objects.filter(recipe=instance).delete()
            ingredients = validated_data.pop('recipe_ingredient')
            self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        return ShortRecipe(
            instance, context={'request': self.context.get('request')}
            ).data


class FollowSerializer(serializers.ModelSerializer):
    """Общий сериализатор для модели подписки."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count',
    )
    is_subscribed = serializers.BooleanField(default=True)
    
    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('__all__',)
        
    def get_recipes_count(self, follower):
        """Поле для обозначения общего количества рецептов пользователя."""
        return follower.author.recipes.count()

    def get_recipes(self, follower):
        """Поле сериализатора с ограниччением количества рецептов и их коротким представлением"""
        request = self.context.get('request')
        recipes_limit = int(request.query_params.get('recipes_limit')) if request.query_params.get('recipes_limit') else None
        recipes = (Recipe.objects.filter(author=follower.author)
                   if not recipes_limit 
                   else Recipe.objects.filter(author=follower.author)
                   [:recipes_limit])
        serializer = ShortRecipe(
            recipes, many=True, read_only=True,
            context={'request': self.context.get('request')}
        )
        return serializer.data