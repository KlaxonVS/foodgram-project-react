from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from recipes.models import Favorite, ShoppingCart
from users.models import Follow


class UserViewSetMixin(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin):
    lookup_field = 'id'


class AddDeleteMixin:

    handlers = {
        'follow': [
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
        create_obj = bound[0]
        to_bound = bound[1]
        from_id = get_object_or_404(self.queryset, id=id)
        as_key = dict.fromkeys(to_bound, from_id.id)
        new_obj, create = create_obj.objects.get_or_create(
                user=user,
                **as_key
        )
        if not create:
            error = bound[2]
            return Response(
                error,
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
        create_obj = bound[0]
        from_id = get_object_or_404(self.queryset, id=id)
        as_key = dict.fromkeys(bound[1], from_id.id)
        get_object_or_404(
            create_obj, user=self.request.user,
            **as_key
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
