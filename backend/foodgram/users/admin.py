from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Follow

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'username', 'email', 'first_name', 'last_name',
        'date_joined', 'updated_at',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('date_joined', 'first_name', 'last_name',)
    empty_value_display = settings.DEFAULT_FOR_EMPTY


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'follower', 'author', 'create_at'
    )
    search_fields = ('follower', 'author',)
    list_filter = ('follower', 'author', 'create_at',)
    empty_value_display = settings.DEFAULT_FOR_EMPTY
