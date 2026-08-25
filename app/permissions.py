from rest_framework.permissions import BasePermission


class IsIncidentOwner(BasePermission):
    message = "You can only access incidents that you reported."

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id