from django.contrib import admin

from users.models import Follow, User


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('followers', 'recipe_count')
    list_display = (
        'email',
        'username',
        'full_name',
    )
    search_fields = ('email', 'username',)
    list_filter = ('email', 'username')

    def full_name(self, obj,):
        return obj.get_full_name() or 'Безымянный'
    
    def followers(self, obj,):
        return obj.following.count()
    
    def recipe_count(self, obj,):
        return obj.recipes.count()

    full_name.short_description = 'Полное имя'
    followers.short_description = 'Подписчиков'
    recipe_count.short_description = 'Рецептов'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user',)
    list_filter = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
