from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_authenticated(request):
    return bool(request.user and request.user.is_authenticated)


class AllowAny(BasePermission):
    pass


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return is_authenticated(request)

    def has_object_permission(self, request, view, obj):
        return is_authenticated(request)


class IsAuthenticatedOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or is_authenticated(request))

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS


class IsOwner(BasePermission):

    def has_permission(self, request, view):
        return is_authenticated(request)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsStuff(BasePermission):

    def has_permission(self, request, view):
        return is_authenticated(request) and (
            request.user.is_admin or request.user.is_moderator
        )

    def has_object_permission(self, request, view, obj):
        return is_authenticated(request) and (
            request.user.is_admin or request.user.is_moderator
        )


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return is_authenticated(request) and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return is_authenticated(request) and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (True if request.method in SAFE_METHODS
                else is_authenticated(request) and request.user.is_admin)

    def has_object_permission(self, request, view, obj):
        return (True if request.method in SAFE_METHODS
                else is_authenticated(request) and request.user.is_admin)
