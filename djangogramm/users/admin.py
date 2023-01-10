from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import RegisterForm
from .models import Post, Like, Tag, Image

# from import_export.admin import ImportExportActionModelAdmin
# from import_export import resources
# from import_export import fields
# from import_export.widgets import ForeignKeyWidget

User = get_user_model()


# @admin.register(User)
class UsersAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'slug'),
        }),
    )
    add_form = RegisterForm
    prepopulated_fields = {'slug': ('username',)}
    # list_display = ('id', "username", 'first_name', 'last_name', 'avatar', 'about', 'email')
    # list_display_links = ('id', 'username')
    # search_fields = ('username', 'last_name')


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'time_create', 'user', 'is_published')
    list_display_links = ('title',)
    search_fields = ('title', )
    list_editable = ('is_published',)
    list_filter = ('title', 'user')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image')


class LikesAdmin(admin.ModelAdmin):
    autocomplete_fields = ['liked_by', 'post']
    list_display = ('post', 'liked_by', 'like', 'created')


admin.site.register(User, UsersAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikesAdmin)
admin.site.register(Tag)
admin.site.register(Image, ImageAdmin)

