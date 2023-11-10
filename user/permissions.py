from rest_framework import permissions

class isStaffEditorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_staff:
            return False
        return True

class isStaffOrUserPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True
        if not request.user.is_staff:
            return False
        return True
