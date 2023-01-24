from tempfile import mkstemp

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from users.models import Follow

from .filters import NameSearchFilter, RecipeFilter
from .mixins import UserViewSetMixin
from .paginators import FoodgramPaginator
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (ChangePassword, FollowSerializer,
                          IngredientSerializer, Login, RecipeCreateSerializer,
                          RecipeViewSerializer, ShortRecipe, TagSerializer,
                          UserCreateSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(UserViewSetMixin):
    """
    ViewSet для обработки запросов к пользователям:
    получение пользователя или списка, их добавление или удаление
    в подписки, регистрации в  сервисе.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = FoodgramPaginator
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('username',)

    @action(methods=['get'], detail=False, url_path='me',
            permission_classes=[permissions.IsAuthenticated])
    def user_me_view(self, request):
        """Метод дающий доступ пользователю к данным о себе."""
        user = request.user
        serializer = self.get_serializer(user)        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False, url_path='subscriptions',
            permission_classes=[permissions.IsAuthenticated])
    def user_subscriptions(self, request):
        """Получение списка авторов на которых подписан пользователь."""
        user = request.user
        following = user.follower.all()
        serializer = FollowSerializer(
            self.paginate_queryset(following), many=True,
            context={'request': request}
        )  
        return self.get_paginated_response(serializer.data)
    
    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
            permission_classes=[permissions.IsAuthenticated])
    def user_subscribe(self, request, id):
        """Подписка и отписка от авторов"""
        author = get_object_or_404(User, id=id)
        if author == request.user:
            return Response(
                    'Вы не можете подписаться на себя.',
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'POST':
            follow, create = Follow.objects.get_or_create(
                user=request.user,
                author=author
            )
            if not create:
                return Response(
                    f'Вы уже подписаны на автора: {author}',
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FollowSerializer(follow, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False, url_path='set_password',
            permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """Смена пароля пользователем"""
        serializer = ChangePassword(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(
            serializer.validated_data.get('current_password')
        ):
            return Response(
                'Пароль неверный',
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response('Пароль изменен', status=status.HTTP_200_OK)
    
    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED, headers=headers
        )
    
    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.save()


@api_view(['post'])
@permission_classes([permissions.AllowAny,])
def login(request):
    """View-функция для получения пользователя токена через email и пароль"""
    serializer = Login(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        get_user_model(),
        email=serializer.validated_data.get('email')
    )
    if not user.check_password(serializer.validated_data.get('password')):
        return Response('Пароль неверный', status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'auth_token': str(token)}, status=status.HTTP_201_CREATED)

@api_view(['post'])
@permission_classes([permissions.IsAuthenticated,])
def logout(request):
    """View-функция для завершения действия токена пользователем вручную"""
    try:
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as error:
        return Response(str(error), status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для обработки запросов к Тегам:
    получение тегов или их списка. Только для чтения.
    """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для обработки запросов к ингредиентам:
    получение ингредиента или их списка. Только для чтения.
    """
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (NameSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для обработки запросов к рецептам:
    получение рецепта или списка, их добавление или удаление
    в избранное, корзину.
    """
    queryset = Recipe.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAdminAuthorOrReadOnly]
    pagination_class = FoodgramPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    ordering_fields = ('-pub_date',)
    
    def get_serializer_class(self):
        return (RecipeViewSerializer
                if self.request.method in permissions.SAFE_METHODS
                else RecipeCreateSerializer)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite',
            permission_classes=[permissions.IsAuthenticated])
    def user_favorite(self, request, id):
        """Функция добавления и удаления в избранное"""
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            favorite, create = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not create:
                return Response(
                    f'Вы уже добавили в избранное: {recipe.name}',
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShortRecipe(favorite.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def user_cart(self, request, id):
        """Функция добавления и удаления в корзину"""
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            in_cart, create = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not create:
                return Response(
                    f'Вы уже добавили в избранное: {in_cart.recipe.name}',
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShortRecipe(in_cart.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='download_shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def user_cart_download(self, request):
        """Функция скачивания списка покупок"""
        cart = (RecipeIngredient.objects
                .filter(recipe__cart__user=request.user)
                .order_by('ingredient__name')
                .values('ingredient__name', 'ingredient__measurement_unit')
                .annotate(amount=Sum('amount')))
        _, path = mkstemp(suffix='.txt')
        content = '\n'.join([
            (f'{ol}. {ingredient["ingredient__name"]} '
             f'{ingredient["amount"]} ' 
             f'{ingredient["ingredient__measurement_unit"]}'
             ) for ol, ingredient in enumerate(list(cart), start=1)
        ])
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment;'
            ' filename=shopping-list.txt'
        )
        return response