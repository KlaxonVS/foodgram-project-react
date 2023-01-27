from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Позволяет редактировать объект только администратору и автору.
    Запрещает отправлять POST-запросы не аутентифицированным пользователям.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (obj.author == request.user
                    or request.user.is_authenticated))
