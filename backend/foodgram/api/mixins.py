from rest_framework import mixins, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, viewsets

from recipes.models import Favorite, ShoppingCart
from users.models import Follow

from .serializers import FollowSerializer, ShortRecipe


class UserViewSetMixin(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin):
    lookup_field = 'id'


class AddDeleteMixin:
    
    handlers = {
        'follow' : [
            Follow, ['author_id'], 'Вы уже подписаны на автора.',
            'many', 
        ],
        'favorite': [
            Favorite, ['recipe_id'],
            'Вы уже добавили этот рецепт в избранное.',
        ],
        'cart': [
            ShoppingCart, ['recipe_id'],
            'Вы уже добавили этот рецепт в корзину',
        ]}

    def add_bound(self, id, handler, serializer):
        user = self.request.user
        bound = self.handlers[handler]
        from_id = get_object_or_404(self.queryset, id=id)
        as_key = dict.fromkeys(bound[1], from_id.id)
        new_obj, create = bound[0].objects.get_or_create(
                user=user,
                **as_key
        )
        if not create:
            return Response(
                bound[2],
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'many' in bound:
            serializer = serializer(
                new_obj, context={'request': self.request}
            )
        else:
            serializer = serializer(from_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
            

    def delete_bound(self, id, handler):
        bound = self.handlers[handler]
        from_id = get_object_or_404(self.queryset, id=id)
        as_key = dict.fromkeys(bound[1], from_id.id)
        get_object_or_404(
            bound[0], user=self.request.user,
            **as_key
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
