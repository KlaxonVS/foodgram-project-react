from rest_framework import mixins, viewsets

class UserViewSetMixin(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin):
    lookup_field = 'id'