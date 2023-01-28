from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .filters import NameSearchFilter, RecipeFilter
from .mixins import AddDeleteMixin, UserViewSetMixin
from .paginators import FoodgramPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (ChangePassword, FollowSerializer,
                          IngredientSerializer, Login, RecipeCreateSerializer,
                          RecipeViewSerializer, TagSerializer,
                          UserCreateSerializer, UserSerializer, ShortRecipe)
from .utils import text_cart
from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            Tag)
from users.models import User


class UserViewSet(AddDeleteMixin, UserViewSetMixin):
    """
    ViewSet для обработки запросов к пользователям:
    получение пользователя или списка, их добавление или удаление
    в подписки, регистрации в  сервисе.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
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

    @action(methods=['post'], detail=True, url_path='subscribe',
            permission_classes=[permissions.IsAuthenticated])
    def user_subscribe(self, request, id):
        """Подписка и отписка от авторов"""
        return self.add_bound(id, 'follow', FollowSerializer)

    @user_subscribe.mapping.delete
    def delete_subscribtion(self, request, id):
        return self.delete_bound(id, 'follow')

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
@permission_classes([permissions.AllowAny, ])
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
@permission_classes([permissions.IsAuthenticated, ])
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


class RecipeViewSet(AddDeleteMixin, viewsets.ModelViewSet):
    """
    ViewSet для обработки запросов к рецептам:
    получение рецепта или списка, их добавление или удаление
    в избранное, корзину.
    """
    queryset = Recipe.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = FoodgramPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    ordering_fields = ('-pub_date',)

    def get_serializer_class(self):
        return (RecipeViewSerializer
                if self.request.method in permissions.SAFE_METHODS
                else RecipeCreateSerializer)

    @action(methods=['post'], detail=True, url_path='favorite',
            permission_classes=[permissions.IsAuthenticated])
    def user_favorite(self, request, id):
        """Функция добавления и удаления в избранное"""
        return self.add_bound(id, 'favorite', ShortRecipe)

    @user_favorite.mapping.delete
    def delete_favorite(self, request, id):
        return self.delete_bound(id, 'favorite')

    @action(methods=['post'], detail=True, url_path='shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def user_cart(self, request, id):
        """Функция добавления и удаления в корзину"""
        return self.add_bound(id, 'cart', ShortRecipe)

    @user_cart.mapping.delete
    def delete_cart(self, request, id):
        return self.delete_bound(id, 'cart')

    @action(methods=['get'], detail=False, url_path='download_shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def user_cart_download(self, request):
        """Функция скачивания списка покупок"""
        cart = (RecipeIngredient.objects
                .filter(recipe__cart__user=request.user)
                .order_by('ingredient__name')
                .values('ingredient__name', 'ingredient__measurement_unit')
                .annotate(amount=Sum('amount')))
        return text_cart(cart)
