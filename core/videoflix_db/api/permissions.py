from rest_framework.permissions import BasePermission

class IsEmailConfirmed(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True
        return getattr(request.user, 'email_confirmed', False)