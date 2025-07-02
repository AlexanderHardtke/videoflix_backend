from django.contrib.auth.forms import UserCreationForm
from .models import UserProfil

class ProfilUserCreationForm(UserCreationForm):
    class Meta:
        model = UserProfil
        fields = '__all__'
