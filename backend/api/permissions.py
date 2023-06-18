from rest_framework import permissions



class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    """Проверка прав доступа для доступа к рецептам"""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or obj.author == request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение для пользователей с правами администратора или на чтение."""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_admin
            )


class RolePermission(permissions.BasePermission):
    """Проверка ролей поьзователей"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return (request.user.is_anonymous_user
                    or request.user.is_authenticated_user
                    or request.user.is_admin)
        return (request.user.is_authenticated_user
                or request.user.is_admin)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return (request.user.is_anonymous_user
                    or request.user.is_authenticated_user
                    or request.user.is_admin)
        if obj.author == request.user.is_authenticated_user:
            return (request.user.is_authenticated_user
                    or request.user.is_admin)
        return (request.user.is_admin)