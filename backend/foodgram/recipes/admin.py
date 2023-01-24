from django.conf import settings
from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)

admin.site.empty_value_display = '-пусто-'


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInLine]
    readonly_fields = ('favorite_count',)
    list_display = (
        'pub_date',
        'id',
        'name',
        'author'
    )
    search_fields = ('email', 'username',)
    list_filter = ('author', 'name', 'tags')
    list_per_page = settings.PAGE_LMT
    
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
    list_filter = ('recipe', 'ingredient')
    list_per_page = settings.PAGE_LMT


class ShoppingCartAdmin(admin.ModelAdmin):
#    readonly_fields = ('shopping_list',)
    list_display = (
        'user',
    )
    search_fields = ('user',)
    list_per_page = settings.PAGE_LMT

#    def shopping_list(self, obj):
#        recipes = obj.recipes
#        data = recipes.values('ingredients').annotate(ing_sum=Sum('ingredients__recipe_iningredient__amount')).order_by()
#        return data
# recipes.aggregate(Sum('ingredients__recipe_iningredient__amount'))

admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)