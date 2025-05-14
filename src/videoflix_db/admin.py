from django.contrib import admin
from .models import UserProfil, Video, WatchedVideo
from .forms import ProfilUserCreationForm
from django.contrib.auth.admin import UserAdmin

admin.site.register(Video)
admin.site.register(WatchedVideo)

@admin.register(UserProfil)
class UserProfilAdmin(admin.ModelAdmin):
    add_form = ProfilUserCreationForm
    fieldsets = (
        (
            'Individuelle Daten',
            {
                'fields': (
                    'email_confirmed',
                    'preferred_size',
                    'sound_volume'
                )
            }
        ),
        *UserAdmin.fieldsets,
    )