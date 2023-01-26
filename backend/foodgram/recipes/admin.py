from django.conf import settings
from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)

admin.site.empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('favorite_count', 'ingredient_list')
    list_display = (
        'pub_date',
        'id',
        'name',
        'author',
        'favorite_count',
    )
    search_fields = ('name', 'author',)
    list_filter = ('tags',)
    list_per_page = settings.PAGE_LMT
    
    def ingredient_list(self, obj):
        return '\n'.join([
            f'{ol}. {recipe_i.ingredient.name}: {recipe_i.amount}'
            f'{recipe_i.ingredient.measurement_unit}.'
            for ol, recipe_i 
            in enumerate(obj.recipe_ingredient.all(), start=1)
        ])
    
    def favorite_count(self, obj):
        return obj.favorite.count() 

    favorite_count.short_description = 'Добавлено в избранное'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    list_per_page = settings.PAGE_LMT


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )
    search_fields = ('name', 'color', 'slug')
    list_per_page = settings.PAGE_LMT


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_per_page = settings.PAGE_LMT

class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient'
    )
    search_fields = ('recipe', 'ingredient')
    list_per_page = settings.PAGE_LMT


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
    )
    search_fields = ('user',)
    list_per_page = settings.PAGE_LMT


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)