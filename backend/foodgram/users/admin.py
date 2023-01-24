from django.contrib import admin

from users.models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'full_name',
        'role',
    )
    list_editable = ('role',)
    search_fields = ('email', 'username',)
    list_filter = ('role', 'email', 'username')
    empty_value_display = '-пусто-'

    def full_name(self, obj,):
        return obj.get_full_name() or 'Безымянный'

    full_name.short_description = 'Полное имя'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user',)
    list_filter = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
