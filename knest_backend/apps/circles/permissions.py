from rest_framework import permissions
from .models import CircleMembership

class IsCircleOwnerOrAdmin(permissions.BasePermission):
    """
    サークルのオーナーまたは管理者のみに許可するパーミッション
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        membership = CircleMembership.objects.filter(
            circle=obj,
            user=request.user,
            status='active'
        ).first()

        return membership and membership.role in ['owner', 'admin']

class CanJoinCircle(permissions.BasePermission):
    """
    サークルに参加可能かどうかをチェックするパーミッション
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # ユーザーの参加中のサークル数をチェック
        active_memberships = CircleMembership.objects.filter(
            user=request.user,
            status='active'
        ).count()

        return active_memberships < 4

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # サークルが参加可能な状態かチェック
        if obj.status != 'open':
            return False

        # サークルが満員でないかチェック
        active_members = obj.memberships.filter(status='active').count()
        if active_members >= 10:
            return False

        return True 