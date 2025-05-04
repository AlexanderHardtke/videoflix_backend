from django.contrib import admin
from .models import UserProfil
from .forms import ProfilUserCreationForm
from django.contrib.auth.admin import UserAdmin

# Register your models here.


@admin.register(UserProfil)
class UserProfilAdmin(admin.ModelAdmin):
    add_form = ProfilUserCreationForm
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Individuelle Daten',
            {
                'fields': (
                    'preferredSize',
                )
            }
        )
    )
