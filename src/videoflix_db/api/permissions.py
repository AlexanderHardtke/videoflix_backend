from rest_framework.permissions import BasePermission

class IsEmailConfirmed(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'email_confirmed', False)