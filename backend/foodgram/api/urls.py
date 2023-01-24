from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipeViewSet, TagViewSet, UserViewSet,
                    login, logout)

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredients')


extra_patterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout')
]

urlpatterns = [
    path('', include(router_v1.urls), name='foodgram-api'),
    path('auth/token/', include(extra_patterns), name='auth')
]