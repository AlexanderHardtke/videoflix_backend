from django.contrib import admin
from django.contrib.auth import get_user_model
from authemail.admin import EmailUserAdmin
from .models import Video, WatchedVideo
from .forms import ProfilUserCreationForm

class MyUserAdmin(EmailUserAdmin):
    add_form = ProfilUserCreationForm
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
                                    'is_superuser', 'is_verified',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom info', {'fields': ('sound_volume',)}),
    )

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), MyUserAdmin)

class VideoAdmin(admin.ModelAdmin):
    readonly_fields = ['file720p', 'file360p', 'file240p', 'file_preview144p']

admin.site.register(Video, VideoAdmin)
admin.site.register(WatchedVideo)