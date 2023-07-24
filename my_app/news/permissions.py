from rest_framework.permissions import BasePermission

class IsOwner_or_Admin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff is True:
            return True
        else:
            return request.user == obj.autor
    