from rest_framework import permissions


class isStaffOrOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True
        if not request.user.is_staff:
            return False
        return True