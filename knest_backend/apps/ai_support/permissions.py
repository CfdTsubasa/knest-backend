from rest_framework import permissions

class IsSessionOwner(permissions.BasePermission):
    """
    セッションの所有者のみにアクセスを許可するパーミッション
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsMessageOwner(permissions.BasePermission):
    """
    メッセージの所有者（セッションの所有者）のみにアクセスを許可するパーミッション
    """
    def has_object_permission(self, request, view, obj):
        return obj.session.user == request.user 