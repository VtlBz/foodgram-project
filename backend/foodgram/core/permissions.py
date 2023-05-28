from rest_framework.permissions import SAFE_METHODS, BasePermission


def is_authenticated(request):
    return bool(request.user and request.user.is_authenticated)


class AllowAny(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


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


class IsOwnerOrRO(BasePermission):

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or is_authenticated(request))

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)


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
